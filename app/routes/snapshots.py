import os
import aiofiles
import base64
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, delete
import tiktoken

from app.database import get_db
from app.models import Lecture, Snapshot, LectureSummary, LectureKeySummary
from app.utils.gpt import (
    summarize_text_with_gpt,
    summarize_snapshot_transcript,
    pick_top2_snapshots_by_topic
)

router = APIRouter()

# ─────────────────────────────
# Settings & Paths
# ─────────────────────────────
class Settings(BaseSettings):
    base_url: str = Field(..., env="BASE_URL")
    image_dir: str = "tmp/snapshots"
    text_log_dir: str = "data"
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()
FULL_IMAGE_DIR = os.path.join("static", settings.image_dir)
os.makedirs(FULL_IMAGE_DIR, exist_ok=True)
os.makedirs(settings.text_log_dir, exist_ok=True)
_ENCODER = tiktoken.encoding_for_model("gpt-4o")

# ─────────────────────────────
# Pydantic Models
# ─────────────────────────────
class SnapshotRequest(BaseModel):
    timestamp: str
    transcript: str
    screenshot_base64: str
    is_image: bool = True  # ✅ 추가됨

class LectureSessionResponse(BaseModel):
    lecture_id: int
    created_at: datetime

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

# ─────────────────────────────
# Helper Functions
# ─────────────────────────────
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
    
# ─────────────────────────────
# API: POST /lectures
# ─────────────────────────────
@router.post("/lectures", response_model=LectureSessionResponse)
async def create_lecture(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(text("SELECT COALESCE(MAX(id), 0) FROM lectures"))
        max_id = result.scalar_one()
        await db.execute(
            text("SELECT setval('lectures_id_seq', :new_val, false)").bindparams(new_val=max_id + 1)
        )
        lecture = Lecture()
        db.add(lecture)
    await db.refresh(lecture)
    return LectureSessionResponse(lecture_id=lecture.id, created_at=lecture.created_at)

# ─────────────────────────────
# API: POST /snapshots
# ─────────────────────────────
@router.post("/snapshots")
async def upload_snapshot(
    data: SnapshotRequest,
    lecture_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        dt = datetime.strptime(data.timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(400, "timestamp 형식 오류 (YYYY-MM-DD HH:MM:SS)")

    rel_url = ""
    abs_url = ""

    if data.is_image:
        try:
            _, encoded = data.screenshot_base64.split(",", 1) if "," in data.screenshot_base64 else ("", data.screenshot_base64)
            image_bytes = base64.b64decode(encoded)
            filename = f"{uuid.uuid4().hex}.png"
            save_path = os.path.join(FULL_IMAGE_DIR, filename)
            async with aiofiles.open(save_path, "wb") as f:
                await f.write(image_bytes)
            rel_url = f"/static/{settings.image_dir}/{filename}"
            abs_url = f"{settings.base_url.rstrip('/')}{rel_url}"
        except Exception as e:
            raise HTTPException(400, f"이미지 저장 실패: {e}")

    log_path = os.path.join(settings.text_log_dir, f"lecture_{lecture_id}.txt")
    async with aiofiles.open(log_path, "a", encoding="utf-8") as log_file:
        await log_file.write(f"{dt:%Y-%m-%d %H:%M:%S} - {data.transcript}\n")

    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=dt.strftime("%Y-%m-%d"),
        time=dt.strftime("%H:%M:%S"),
        text=data.transcript,
        summary_text=None,
        image_path=rel_url,
        is_image=data.is_image
    )
    db.add(snapshot)
    await db.commit()

    return {
        "message": "스냅샷 저장 완료",
        "lecture_id": lecture_id,
        "date": snapshot.date,
        "time": snapshot.time,
        "summary": None,
        "image_url": abs_url
    }

# ─────────────────────────────
# API: GET /generate_markdown_summary
# ─────────────────────────────

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
                "당신은 Java 강의의 핵심 키워드를 통해 수업을 정리해주는 요약 비서입니다.\n"
                "다음 지침을 반드시 따르세요:\n"
                "1. 핵심 키워드는 정확히 **3개만** 작성해야 하며, 3개를 초과하거나 미만으로 작성하면 안 됩니다.\n"
                "2. 각 키워드는 Java 문법이나 개념 중심이어야 하며, 예시 없이 **2~3문장으로 설명**합니다.\n"
                "3. 출력 형식 예시:\n"
                "   1. 클래스: Java에서 클래스를 정의하는 방법과 구성 요소(필드, 메서드 등)에 대해 설명합니다. 클래스는 객체 지향의 핵심 단위입니다.\n"
                "   2. 상속: 상속은 코드 재사용을 가능하게 하며, 자식 클래스가 부모 클래스의 속성과 메서드를 사용할 수 있도록 합니다.\n"
                "   3. 오버라이딩: 부모 클래스의 메서드를 자식 클래스에서 재정의하여 사용하는 기법입니다. 다형성을 구현할 때 활용됩니다.\n"
                "4. 키워드 외의 내용(서론, 결론, 인사말 등)은 절대 포함하지 말고, 위 형식을 엄격히 따라야 합니다.\n"
                "이 요약은 교수님이 수업 마지막 5분에 학생들에게 핵심만 전달하는 데 사용됩니다."
            )
        },
        {
            "role": "user",
            "content": f"강의 내용:\n\n{truncated}\n"
        }
    ]

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    res = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
    )

    return SummaryResponse(
        lecture_id=lecture_id,
        summary=res.choices[0].message.content.strip()
    )

# ─────────────────────────────
# API: POST /lecture_summary
# ─────────────────────────────
@router.post("/lecture_summary", response_model=List[LectureSummaryResponse])
async def generate_lecture_summary(
    lecture_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    log_path = os.path.join(settings.text_log_dir, f"lecture_{lecture_id}.txt")
    if not os.path.exists(log_path):
        raise HTTPException(404, "텍스트 로그 없음")

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
        raise HTTPException(400, "요약 토픽 없음")

    snapshots = (await db.execute(
        select(Snapshot).where(Snapshot.lecture_id == lecture_id, Snapshot.is_image == True)
    )).scalars().all()
    if not snapshots:
        raise HTTPException(404, "스냅샷 없음")

    await db.execute(delete(LectureSummary).where(LectureSummary.lecture_id == lecture_id))
    output = []
    used_paths: Set[str] = set()

    for topic_obj in topics:
        top2_indices = await pick_top2_snapshots_by_topic(topic_obj["topic"], snapshots, used_paths=used_paths)
        highlights = []

        for idx in top2_indices:
            snap = snapshots[idx]
            full_url = f"{settings.base_url.rstrip('/')}{snap.image_path}"

            if not snap.summary_text:
                snap.summary_text = await summarize_snapshot_transcript(snap.text)
                db.add(snap)
                await db.flush()

            highlights.append({
                "image_url": snap.image_path,
                "text": snap.summary_text
            })

        db.add(LectureSummary(
            lecture_id=lecture_id,
            topic=topic_obj["topic"],
            summary=topic_obj["summary"],
            image_url_1=highlights[0]["image_url"] if len(highlights) > 0 else None,
            image_text_1=highlights[0]["text"] if len(highlights) > 0 else None,
            image_url_2=highlights[1]["image_url"] if len(highlights) > 1 else None,
            image_text_2=highlights[1]["text"] if len(highlights) > 1 else None
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
async def get_stored_summary(
    lecture_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 1. 저장된 요약 조회
    summaries = (await db.execute(
        select(LectureSummary).where(LectureSummary.lecture_id == lecture_id)
    )).scalars().all()

    if not summaries:
        raise HTTPException(404, "저장된 요약 없음")

    # 2. 관련된 snapshot 전부 조회
    snapshots = (await db.execute(
        select(Snapshot).where(Snapshot.lecture_id == lecture_id)
    )).scalars().all()
    image_path_to_summary_text = {
        s.image_path: s.summary_text or "" for s in snapshots
    }

    # 3. 응답 구성
    output = []
    for s in summaries:
        highlights = []
        for image_url in [s.image_url_1, s.image_url_2]:
            if image_url:
                highlights.append({
                    "image_url": image_url,
                    "text": image_path_to_summary_text.get(image_url, "")
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
        raise HTTPException(404, "저장된 요약 없음")

    grouped: Dict[int, List[LectureSummaryListItem]] = {}
    for s in summaries:
        grouped.setdefault(s.lecture_id, []).append(LectureSummaryListItem(
            lecture_id=s.lecture_id,
            topic=s.topic,
            created_at=s.created_at
        ))

    return grouped