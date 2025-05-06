import os
import base64
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from openai import AsyncOpenAI
from sklearn.metrics.pairwise import cosine_similarity

from app.database import get_db
from app.models import Snapshot

# ──────────────────────────────────────────────────────────
# 전역 설정
# ──────────────────────────────────────────────────────────

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMAGE_DIR = "tmp/snapshots"
FULL_IMAGE_DIR = os.path.join("static", IMAGE_DIR)
os.makedirs(FULL_IMAGE_DIR, exist_ok=True)

TEXT_LOG_DIR = "data"
os.makedirs(TEXT_LOG_DIR, exist_ok=True)

router = APIRouter()


# ──────────────────────────────────────────────────────────
# Pydantic 스키마
# ──────────────────────────────────────────────────────────

class SnapshotRequest(BaseModel):
    timestamp: str
    transcript: str
    screenshot_base64: str

class SummaryResponse(BaseModel):
    lecture_id: int
    summary: str


# ──────────────────────────────────────────────────────────
# 헬퍼: OpenAI Embeddings 호출
# ──────────────────────────────────────────────────────────

async def embed_texts(texts: list[str]) -> list[list[float]]:
    clean_texts = [t for t in texts if t and t.strip()]
    if not clean_texts:
        raise HTTPException(status_code=400, detail="빈 텍스트로 임베딩 요청 불가")
    resp = await client.embeddings.create(
        model="text-embedding-ada-002",
        input=clean_texts
    )
    return [e.embedding for e in resp.data]


# ──────────────────────────────────────────────────────────
# 1) 스냅샷 저장 API
# ──────────────────────────────────────────────────────────

@router.post("/snapshots")
async def upload_snapshot(
    data: SnapshotRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        dt = datetime.strptime(data.timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="timestamp 형식 오류 (yyyy-MM-dd HH:mm:ss)")

    date_group = dt.strftime("%Y-%m-%d")

    try:
        _, encoded = data.screenshot_base64.split(",", 1) if "," in data.screenshot_base64 else ("", data.screenshot_base64)
        image_bytes = base64.b64decode(encoded)
        filename = f"{uuid.uuid4().hex}.png"
        save_path = os.path.join(FULL_IMAGE_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(image_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="이미지 디코딩 또는 저장 실패")

    relative_url = f"/static/{IMAGE_DIR}/{filename}"
    absolute_url = f"https://project2025-backend.onrender.com{relative_url}"

    lecture_id = 1
    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    try:
        with open(text_log_path, "w", encoding="utf-8") as log_file:
            log_file.write(f"{dt:%Y-%m-%d %H:%M:%S} - {data.transcript}\n")
    except Exception:
        pass

    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=date_group,
        time=dt.strftime("%H:%M:%S"),
        text=data.transcript,
        image_path=relative_url
    )
    db.add(snapshot)
    await db.commit()

    return {
        "message": "스냅샷 저장 완료",
        "lecture_id": lecture_id,
        "date": date_group,
        "time": snapshot.time,
        "text": data.transcript,
        "image_url": absolute_url
    }


# ──────────────────────────────────────────────────────────
# 2) GPT 요약 (Markdown 형식)
# ──────────────────────────────────────────────────────────

async def summarize_text_with_gpt(text: str) -> str:
    system_msg = {
        "role": "system",
        "content": (
            "너는 수업 마지막에 보여줄 요약 카드를 만드는 조교야. "
            "학생들이 오늘 수업을 이해하기 쉽도록 오늘 배운 핵심 개념 5개를 Markdown 형식으로 정리해줘.  "
            "형식은 반드시 아래처럼 써:\n\n"
            "## 개념명 (예: Overloading, Void 타입)\n\n"
            "- 간단한 한 줄 설명 (학생이 바로 이해 가능하게)\n\n"
            "개념명은 번역체 대신 정확한 개발 용어로 써줘. 설명은 한 문장만."
        )
    }
    user_msg = {
        "role": "user",
        "content": f"강의 로그 (최대 3000자):\n```text\n{text[:3000]}\n```"
    }
    res = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_msg, user_msg],
        temperature=0.5,
        max_tokens=800,
    )
    return res.choices[0].message.content.strip()


@router.get("/generate_markdown_summary", response_model=SummaryResponse)
async def generate_markdown_summary(lecture_id: int = 1):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 없음")
    text = open(path, "r", encoding="utf-8").read()
    markdown = await summarize_text_with_gpt(text)
    return SummaryResponse(lecture_id=lecture_id, summary=markdown)


# ──────────────────────────────────────────────────────────
# 3) 마크다운 요약 + 스냅샷 매핑
# ──────────────────────────────────────────────────────────

@router.get("/lecture_summary")
async def get_lecture_summary(
    lecture_id: int = 1,
    db: AsyncSession = Depends(get_db)
):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="텍스트 파일 없음")

    full_text = open(path, "r", encoding="utf-8").read()
    markdown = await summarize_text_with_gpt(full_text)

    topics: list[dict] = []
    current_topic = ""
    for line in markdown.splitlines():
        if line.startswith("## "):
            current_topic = line.replace("## ", "").strip()
        elif line.startswith("-") and current_topic:
            topics.append({
                "topic": current_topic,
                "summary": line.replace("-", "").strip()
            })
            current_topic = ""

    valid_topics = [t["topic"] for t in topics if t.get("topic") and t["topic"].strip()]
    if not valid_topics:
        raise HTTPException(status_code=400, detail="요약된 토픽이 없습니다.")

    q = await db.execute(select(Snapshot).where(Snapshot.lecture_id == lecture_id))
    snaps = q.scalars().all()
    if not snaps:
        raise HTTPException(status_code=404, detail="스냅샷 없음")

    texts = [s.text for s in snaps if s.text and s.text.strip()]
    if not texts:
        raise HTTPException(status_code=400, detail="스냅샷 텍스트가 유효하지 않습니다.")

    data = [
        {"text": s.text, "image_url": f"https://project2025-backend.onrender.com{s.image_path}"}
        for s in snaps
    ]

    topic_embs = await embed_texts(valid_topics)
    snap_embs = await embed_texts(texts)

    output = []
    for i, tp in enumerate(valid_topics):
        sims = cosine_similarity([topic_embs[i]], snap_embs)[0]
        top_idx = sims.argsort()[-3:][::-1]
        highlights = [data[j] for j in top_idx]
        output.append({
            "topic": tp,
            "summary": topics[i]["summary"],
            "highlights": highlights
        })

    return output
