from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Snapshot
import os
import base64
import uuid
from datetime import datetime

from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

IMAGE_DIR = "tmp/snapshots"
FULL_IMAGE_DIR = os.path.join("static", IMAGE_DIR)
os.makedirs(FULL_IMAGE_DIR, exist_ok=True)

TEXT_LOG_DIR = "data"
os.makedirs(TEXT_LOG_DIR, exist_ok=True)


class SnapshotRequest(BaseModel):
    timestamp: str
    transcript: str
    screenshot_base64: str

@router.post("/snapshots")
async def upload_snapshot(data: SnapshotRequest, db: AsyncSession = Depends(get_db)):
    timestamp = data.timestamp
    text = data.transcript
    image_data = data.screenshot_base64
    lecture_id = 1

    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        date_group = dt.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="timestamp 형식 오류")

    try:
        _, encoded = image_data.split(",", 1) if "," in image_data else ("", image_data)
        image_bytes = base64.b64decode(encoded)
    except Exception:
        raise HTTPException(status_code=400, detail="이미지 디코딩 실패")

    filename = f"{uuid.uuid4().hex}.png"
    save_path = os.path.join(FULL_IMAGE_DIR, filename)
    relative_url = f"/static/{IMAGE_DIR}/{filename}"
    absolute_url = f"https://project2025-backend.onrender.com{relative_url}"

    with open(save_path, "wb") as f:
        f.write(image_bytes)

    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    with open(text_log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{dt.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")

    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=date_group,
        time=dt.strftime("%H:%M:%S"),
        text=text,
        image_path=relative_url
    )
    db.add(snapshot)
    await db.commit()

    return {
        "message": "스냅샷 저장 완료",
        "lecture_id": lecture_id,
        "date": date_group,
        "time": snapshot.time,
        "text": text,
        "image_url": absolute_url
    }

# GPT 요약 함수
async def summarize_text_with_gpt(text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 ‘교수의 강의 마무리 리마인더’를 작성하는 역할입니다.\n"
                "• 이번 강의에서 등장한 핵심 키워드 5개를 추출하고,\n"
                "• 각 키워드를 ### 헤딩으로, 간단한 설명을 bullet으로 작성하세요. (마크다운 형식)"
            )
        },
        {
            "role": "user",
            "content": f"강의 로그:\n```text\n{text[:3000]}\n```\n"
        }
    ]
    res = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=800,
    )
    return res.choices[0].message.content.strip()


@router.get("/generate_markdown_summary")
async def generate_markdown_summary(lecture_id: int = 1):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 없음")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    markdown = await summarize_text_with_gpt(text)
    return {"lecture_id": lecture_id, "markdown": markdown}


@router.get("/generate_question_summary")
async def generate_question_summary(lecture_id: int = 1):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 없음")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    summary = await summarize_text_with_gpt(text)
    return {"lecture_id": lecture_id, "summary": summary}


# ✅ 최종 API: /lecture_summary
@router.get("/lecture_summary")
async def get_lecture_summary(lecture_id: int = 1, db: AsyncSession = Depends(get_db)):
    # 1. 전체 텍스트 요약 받아오기
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="텍스트 파일 없음")

    with open(path, "r", encoding="utf-8") as f:
        full_text = f.read()

    markdown = await summarize_text_with_gpt(full_text)

    # 2. Markdown에서 주제 추출
    topics = []
    current_topic = ""
    for line in markdown.splitlines():
        if line.startswith("### "):
            current_topic = line.replace("### ", "").strip()
        elif line.startswith("-") and current_topic:
            topics.append({"topic": current_topic, "summary": line.replace("-", "").strip()})
            current_topic = ""

    # 3. DB에서 스냅샷 문장 불러오기
    result = await db.execute(select(Snapshot).where(Snapshot.lecture_id == lecture_id))
    snapshot_rows = result.scalars().all()
    if not snapshot_rows:
        raise HTTPException(status_code=404, detail="스냅샷 없음")

    snapshot_texts = [s.text for s in snapshot_rows]
    snapshot_data = [{"text": s.text, "image_url": f"https://project2025-backend.onrender.com{s.image_path}"} for s in snapshot_rows]

    # 4. 임베딩 유사도 계산
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    topic_embeddings = model.encode([t["topic"] for t in topics])
    snapshot_embeddings = model.encode(snapshot_texts)

    result = []
    for idx, topic in enumerate(topics):
        sims = cosine_similarity([topic_embeddings[idx]], snapshot_embeddings)[0]
        top_indices = sims.argsort()[-3:][::-1]
        highlights = [snapshot_data[i] for i in top_indices]
        result.append({
            "topic": topic["topic"],
            "summary": topic["summary"],
            "highlights": highlights
        })

    return result
