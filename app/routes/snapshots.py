import os
import base64
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from openai import AsyncOpenAI
from sklearn.metrics.pairwise import cosine_similarity

from app.database import get_db
from app.models import Lecture, Snapshot

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

class LectureSessionResponse(BaseModel):
    lecture_id: int
    created_at: datetime

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
    resp = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [e.embedding for e in resp.data]

# ──────────────────────────────────────────────────────────
# 0) 세션 생성 API
# ──────────────────────────────────────────────────────────

@router.post("/lectures", response_model=LectureSessionResponse)
async def create_lecture(db: AsyncSession = Depends(get_db)):
    """
    새로운 강의 세션을 생성하고 lecture_id, 생성일시를 반환합니다.
    """
    lecture = Lecture()
    db.add(lecture)
    await db.commit()
    await db.refresh(lecture)
    return LectureSessionResponse(
        lecture_id=lecture.id,
        created_at=lecture.created_at
    )

# ──────────────────────────────────────────────────────────
# 1) 스냅샷 저장 API
# ──────────────────────────────────────────────────────────

@router.post("/snapshots")
async def upload_snapshot(
    data: SnapshotRequest,
    lecture_id: int = Query(..., description="lecture_id from /lectures"),
    db: AsyncSession = Depends(get_db)
):
    # 1) timestamp 파싱
    try:
        dt = datetime.strptime(data.timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(400, "timestamp 형식 오류 (yyyy-MM-dd HH:mm:ss)")

    date_group = dt.strftime("%Y-%m-%d")

    # 2) 이미지 디코딩 & 저장
    try:
        _, encoded = data.screenshot_base64.split(",", 1) \
            if "," in data.screenshot_base64 else ("", data.screenshot_base64)
        image_bytes = base64.b64decode(encoded)
        filename = f"{uuid.uuid4().hex}.png"
        save_path = os.path.join(FULL_IMAGE_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(image_bytes)
    except Exception:
        raise HTTPException(400, "이미지 디코딩 또는 저장 실패")

    rel_url = f"/static/{IMAGE_DIR}/{filename}"
    abs_url = f"https://project2025-backend.onrender.com{rel_url}"

    # 3) 텍스트 로그 덮어쓰기
    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    try:
        with open(text_log_path, "w", encoding="utf-8") as log_file:
            log_file.write(f"{dt:%Y-%m-%d %H:%M:%S} - {data.transcript}\n")
    except:
        pass

    # 4) DB에 저장
    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=date_group,
        time=dt.strftime("%H:%M:%S"),
        text=data.transcript,
        image_path=rel_url
    )
    db.add(snapshot)
    await db.commit()

    return {
        "message": "스냅샷 저장 완료",
        "lecture_id": lecture_id,
        "date": date_group,
        "time": snapshot.time,
        "text": data.transcript,
        "image_url": abs_url
    }

# ──────────────────────────────────────────────────────────
# 2) 마크다운 요약 API
# ──────────────────────────────────────────────────────────

async def summarize_text_with_gpt(text: str) -> str:
    system_msg = {
        "role": "system",
        "content": (
            "당신은 ‘교수의 강의 마무리 리마인더’를 작성합니다.\n"
            "핵심 키워드 5개를 ### 헤딩으로, bullet 설명으로 요약하세요."
        )
    }
    user_msg = {
        "role": "user",
        "content": f"강의 로그:\n```text\n{text[:3000]}\n```"
    }
    res = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_msg, user_msg],
        temperature=0.5,
        max_tokens=800,
    )
    return res.choices[0].message.content.strip()

@router.get("/generate_markdown_summary", response_model=SummaryResponse)
async def generate_markdown_summary(
    lecture_id: int = Query(...)
):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "요약할 텍스트 없음")
    text = open(path, "r", encoding="utf-8").read()
    md = await summarize_text_with_gpt(text)
    return SummaryResponse(lecture_id=lecture_id, summary=md)

@router.get("/generate_question_summary", response_model=SummaryResponse)
async def generate_question_summary(
    lecture_id: int = Query(...)
):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "요약할 텍스트 없음")
    text = open(path, "r", encoding="utf-8").read()
    summ = await summarize_text_with_gpt(text)
    return SummaryResponse(lecture_id=lecture_id, summary=summ)

# ──────────────────────────────────────────────────────────
# 3) 최종 주제별 요약 + 스냅샷 매핑 API
# ──────────────────────────────────────────────────────────

@router.get("/lecture_summary")
async def get_lecture_summary(
    lecture_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # 1) 전체 텍스트 읽기 & GPT 마크다운 요약
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "텍스트 파일 없음")
    full_text = open(path, "r", encoding="utf-8").read()
    markdown = await summarize_text_with_gpt(full_text)

    # 2) Markdown에서 주제+요약 추출
    topics, current = [], ""
    for line in markdown.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
        elif line.startswith("-") and current:
            topics.append({"topic": current, "summary": line[1:].strip()})
            current = ""

    # 3) DB에서 스냅샷 불러오기
    q = await db.execute(select(Snapshot).where(Snapshot.lecture_id == lecture_id))
    snaps = q.scalars().all()
    if not snaps:
        raise HTTPException(404, "스냅샷 없음")

    texts = [s.text for s in snaps]
    data = [{"text": s.text, "image_url": f"https://project2025-backend.onrender.com{s.image_path}"} for s in snaps]

    # 4) Embedding API & 유사도 매핑
    topic_embs = await embed_texts([t["topic"] for t in topics])
    snap_embs  = await embed_texts(texts)

    output = []
    for i, tp in enumerate(topics):
        sims = cosine_similarity([topic_embs[i]], snap_embs)[0]
        top_idx = sims.argsort()[-3:][::-1]
        highlights = [data[j] for j in top_idx]
        output.append({
            "topic": tp["topic"],
            "summary": tp["summary"],
            "highlights": highlights
        })

    return output
