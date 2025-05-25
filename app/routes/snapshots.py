from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, delete
from typing import Optional, List, Dict
from datetime import datetime
import os
import aiofiles
import uuid
import base64
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken
from app.database import get_db
from app.models import Lecture, Snapshot, LectureSummary
from app.utils.gpt import summarize_text_with_gpt, summarize_snapshot_transcript, pick_top2_snapshots_by_topic

router = APIRouter()

# ────────────────
# Settings & Paths
# ────────────────

class Settings(BaseSettings):
    base_url: str = Field(..., env="BASE_URL")
    image_dir: str = "tmp/snapshots"
    text_log_dir: str = "data"
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()

settings = get_settings()
FULL_IMAGE_DIR = os.path.join("static", settings.image_dir)
os.makedirs(FULL_IMAGE_DIR, exist_ok=True)
os.makedirs(settings.text_log_dir, exist_ok=True)
_ENCODER = tiktoken.encoding_for_model("gpt-4o")

# ────────────────
# Pydantic Models
# ────────────────

class LectureSessionResponse(BaseModel):
    lecture_id: int
    created_at: datetime

class SnapshotRequest(BaseModel):
    timestamp: str
    transcript: str
    screenshot_base64: str

class SummaryResponse(BaseModel):
    lecture_id: int
    summary: Optional[str]

class Highlight(BaseModel):
    image_url: str
    text: str

class LectureSummaryResponse(BaseModel):
    topic: str
    summary: str
    created_at: datetime
    highlights: List[Highlight]

class LectureSummaryListItem(BaseModel):
    lecture_id: int
    topic: str
    created_at: datetime

# ────────────────
# Helper Functions
# ────────────────

def truncate_by_token(text: str, max_tokens: int = 3500) -> str:
    tokens = _ENCODER.encode(text)
    return _ENCODER.decode(tokens[:max_tokens])

async def embed_texts(texts: list[str]) -> list[list[float]]:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    resp = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [e.embedding for e in resp.data]

async def file_exists(path: str) -> bool:
    return await asyncio.to_thread(os.path.exists, path)

# ───────────────────────────────
# 1. POST /lectures
# ───────────────────────────────

@router.post("/lectures", response_model=LectureSessionResponse)
async def create_lecture(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(text("SELECT COALESCE(MAX(id), 0) FROM lectures"))
        max_id = result.scalar_one()
        await db.execute(text("SELECT setval('lectures_id_seq', :new_val, false)").bindparams(new_val=max_id + 1))
        lecture = Lecture()
        db.add(lecture)
    await db.refresh(lecture)
    return LectureSessionResponse(lecture_id=lecture.id, created_at=lecture.created_at)
    
# ───────────────────────────────
# 2. POST /snapshots
# ───────────────────────────────

@router.post("/snapshots")
async def upload_snapshot(data: SnapshotRequest, lecture_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    try:
        dt = datetime.strptime(data.timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(400, "timestamp \ud615\uc2dd \uc624\ub958 (YYYY-MM-DD HH:MM:SS)")

    try:
        _, encoded = data.screenshot_base64.split(",", 1) if "," in data.screenshot_base64 else ("", data.screenshot_base64)
        image_bytes = base64.b64decode(encoded)
        filename = f"{uuid.uuid4().hex}.png"
        save_path = os.path.join(FULL_IMAGE_DIR, filename)
        async with aiofiles.open(save_path, "wb") as f:
            await f.write(image_bytes)
    except Exception as e:
        raise HTTPException(400, f"\uc774\ubbf8\uc9c0 \uc800\uc7a5 \uc2e4\ud328: {e}")

    rel_url = f"/static/{settings.image_dir}/{filename}"
    abs_url = f"{settings.base_url}{rel_url}"

    log_path = os.path.join(settings.text_log_dir, f"lecture_{lecture_id}.txt")
    recent_lines = []
    if os.path.exists(log_path):
        async with aiofiles.open(log_path, "r", encoding="utf-8") as log_file:
            all_lines = await log_file.readlines()
            recent_lines = all_lines[-5:]
    context_lines = [line.split(" - ", 1)[-1].strip() for line in recent_lines]
    context_lines.append(data.transcript)
    context = truncate_by_token("\n".join(context_lines), max_tokens=300)

    summary = await summarize_snapshot_transcript(context)

    async with aiofiles.open(log_path, "a", encoding="utf-8") as log_file:
        await log_file.write(f"{dt:%Y-%m-%d %H:%M:%S} - {data.transcript}\n")

    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=dt.strftime("%Y-%m-%d"),
        time=dt.strftime("%H:%M:%S"),
        text=data.transcript,
        summary_text=summary,
        image_path=rel_url
    )
    db.add(snapshot)
    await db.commit()

    return {
        "message": "\uc2a4\ub0ed\uc0f7 \uc800\uc7a5 \uc644\ub8cc",
        "lecture_id": lecture_id,
        "date": snapshot.date,
        "time": snapshot.time,
        "summary": summary,
        "image_url": abs_url
    }
# ───────────────────────────────
# 3. GET /generate_markdown_summary
# ───────────────────────────────

@router.get("/generate_markdown_summary", response_model=SummaryResponse)
async def generate_markdown_summary(lecture_id: int = Query(...)):
    path = os.path.join(settings.text_log_dir, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "요약할 텍스트 없음")

    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        text = await f.read()

    truncated = truncate_by_token(text)
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 Java 강의 내용을 바탕으로 수업 마무리 리마인드 요약을 작성합니다.\n"
                "- 오늘 강의에서 가장 중요한 핵심 키워드 3개만 선정하세요.\n"
                "- 각 키워드에 대해 핵심 개념을 2~3문장으로 요약하세요.\n"
                "- 덜 중요한 개념은 제외하세요.\n"
                "- JAVA 용어와 코드 예시 중심으로 간결하게 요약하세요.\n"
                "- 교수님이 이 요약을 읽고 5분 안에 학생들에게 핵심 내용을 전달할 수 있어야 합니다."
            ),
        },
        {
            "role": "user",
            "content": f"강의 내용:\n```\n{truncated}\n```",
        },
    ]

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    res = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
    )

    return SummaryResponse(lecture_id=lecture_id, summary=res.choices[0].message.content.strip())


# ───────────────────────────────
# 4. POST /lecture_summary
# ───────────────────────────────

@router.post("/lecture_summary", response_model=List[LectureSummaryResponse])
async def generate_lecture_summary(lecture_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    log_path = os.path.join(settings.text_log_dir, f"lecture_{lecture_id}.txt")
    if not os.path.exists(log_path):
        raise HTTPException(404, "\ud14d\uc2a4\ud2b8 \ub85c\uadf8 \uc5c6\uc74c")
    async with aiofiles.open(log_path, "r", encoding="utf-8") as f:
        full_text = await f.read()

    markdown = await summarize_text_with_gpt(full_text)
    topic_blocks = markdown.split("### ")[1:]
    topics = []
    for block in topic_blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        summary = "\n".join(line.strip() for line in lines[1:])
        if title and summary:
            topics.append({"topic": title, "summary": summary})
    if not topics:
        raise HTTPException(400, "\uc694\uc57d \ud1a0\ud53c\uac00 \uc5c6\uc74c")

    all_snapshots = (await db.execute(
        select(Snapshot).where(Snapshot.lecture_id == lecture_id)
    )).scalars().all()

    valid_snapshots = [
        s for s in all_snapshots
        if s.image_path and await file_exists(os.path.join("static", s.image_path.lstrip("/")))
    ]
    if not valid_snapshots:
        raise HTTPException(404, "\uc720\ud6a8\ud55c \uc2a4\ud06c\ub9ac\ub4dc\uc0f7 \uc5c6\uc74c")

    await db.execute(delete(LectureSummary).where(LectureSummary.lecture_id == lecture_id))
    output = []

    for topic_obj in topics:
        top2_indices = await pick_top2_snapshots_by_topic(topic_obj["topic"], valid_snapshots)
        highlights = []
        for idx in top2_indices:
            snap = valid_snapshots[idx]
            img_path = os.path.join("static", snap.image_path.lstrip("/"))
            if await file_exists(img_path):
                highlights.append({
                    "image_url": snap.image_path,
                    "text": snap.summary_text or ""
                })

        if highlights:
            db.add(LectureSummary(
                lecture_id=lecture_id,
                topic=topic_obj["topic"],
                summary=topic_obj["summary"],
                image_url_1=highlights[0]["image_url"] if len(highlights) > 0 else None,
                image_text_1=highlights[0]["text"] if len(highlights) > 0 else None,
                image_url_2=highlights[1]["image_url"] if len(highlights) > 1 else None,
                image_text_2=highlights[1]["text"] if len(highlights) > 1 else None,
            ))
            output.append({
                "topic": topic_obj["topic"],
                "summary": topic_obj["summary"],
                "created_at": datetime.utcnow(),
                "highlights": highlights
            })

    await db.commit()
    return output


# ───────────────────────────────
# 5. GET /lecture_summary (단일)
# ───────────────────────────────

@router.get("/lecture_summary", response_model=List[LectureSummaryResponse])
async def get_stored_summary(lecture_id: int, db: AsyncSession = Depends(get_db)):
    # 1. 요약된 주제 가져오기
    summaries = (await db.execute(
        select(LectureSummary).where(LectureSummary.lecture_id == lecture_id)
    )).scalars().all()
    if not summaries:
        raise HTTPException(404, "저장된 요약 없음")

    # 2. 관련된 snapshot 전부 가져오기 (STT 요약 포함)
    snapshots = (await db.execute(
        select(Snapshot).where(Snapshot.lecture_id == lecture_id)
    )).scalars().all()

    # ✅ 요약문으로 반환
    image_path_to_summary_text = {s.image_path: s.summary_text or "" for s in snapshots}

    # 3. 응답 구성
    output = []
    for s in summaries:
        highlights = []
        for image_url in [s.image_url_1, s.image_url_2]:
            if image_url:
                highlights.append({
                    "image_url": image_url,
                    "text": image_path_to_summary_text.get(image_url, "")  # ✅ STT 요약 반환
                })

        output.append({
            "topic": s.topic,
            "summary": s.summary,
            "created_at": s.created_at,
            "highlights": highlights
        })

    return output



# ───────────────────────────────
# 6. ✅ GET /snapshots/lecture_summaries (전체)
# ───────────────────────────────

@router.get(
    "/snapshots/lecture_summaries",
    response_model=Dict[int, List[LectureSummaryListItem]]
)
async def get_all_lecture_summaries_grouped(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LectureSummary))
    summaries = result.scalars().all()

    if not summaries:
        raise HTTPException(status_code=404, detail="저장된 요약 없음")

    grouped: dict[int, list] = {}
    for s in summaries:
        grouped.setdefault(s.lecture_id, []).append(
            LectureSummaryListItem(
                lecture_id=s.lecture_id,
                topic=s.topic,
                created_at=s.created_at
            )
        )

    return grouped