import os
import base64
import uuid
from datetime import datetime
from typing import Optional, List

import aiofiles  # ★ MOD - 비동기 I/O
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sqlalchemy import text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken

from app.utils.gpt import summarize_text_with_gpt
from app.database import get_db
from app.models import Lecture, Snapshot, LectureSummary

# ───────────────────────────────
# 0) 환경 설정 (ENV → Settings)
# ───────────────────────────────

class Settings(BaseSettings):
    base_url: str = Field(..., env="BASE_URL")             # 예: https://project2025-backend.onrender.com
    image_dir: str = "tmp/snapshots"
    text_log_dir: str = "data"
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()  # 환경 변수 로드

FULL_IMAGE_DIR = os.path.join("static", settings.image_dir)
os.makedirs(FULL_IMAGE_DIR, exist_ok=True)
os.makedirs(settings.text_log_dir, exist_ok=True)

router = APIRouter()

# ───────────────────────────────
# 1) Pydantic 스키마
# ───────────────────────────────

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


class LectureSummaryResponse(BaseModel):
    topic: str
    summary: str
    highlights: List[dict]

# ───────────────────────────────
# 2) 헬퍼 함수
# ───────────────────────────────

# ★ MOD – 인코더 전역 캐싱
_ENCODER = tiktoken.encoding_for_model("gpt-4o")

def truncate_by_token(text: str, max_tokens: int = 3500) -> str:
    tokens = _ENCODER.encode(text)
    return _ENCODER.decode(tokens[:max_tokens])


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """OpenAI 임베딩 API를 한 번만 호출하여 모든 벡터 반환"""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    resp = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [e.embedding for e in resp.data]


# ───────────────────────────────
# 3) 세션 생성 API
# ───────────────────────────────

@router.post("/lectures", response_model=LectureSessionResponse)
async def create_lecture(db: AsyncSession = Depends(get_db)):
    """
    테이블 최대 id와 시퀀스를 항상 동기화하여,
    새로 생성되는 lecture의 id가 MAX(id)+1이 되도록 강제 설정.
    """
    async with db.begin():  # 트랜잭션 시작
        # 1️⃣ 테이블 최대 id 조회
        result = await db.execute(text("SELECT COALESCE(MAX(id), 0) FROM lectures"))
        max_id: int = result.scalar_one() or 0

        # 2️⃣ 시퀀스 강제 재설정 (무조건 setval)
        await db.execute(
            text("SELECT setval('lectures_id_seq', :new_val, true)").bindparams(new_val=max_id)
        )

        # 3️⃣ 새 레코드 INSERT
        lecture = Lecture()
        db.add(lecture)
        # 트랜잭션 종료 시 자동 commit

    # 새로 삽입된 레코드 리프레시
    await db.refresh(lecture)
    return LectureSessionResponse(lecture_id=lecture.id, created_at=lecture.created_at)


# ───────────────────────────────
# 4) 스냅샷 저장 API
# ───────────────────────────────

@router.post("/snapshots")
async def upload_snapshot(
    data: SnapshotRequest,
    lecture_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        dt = datetime.strptime(data.timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(400, "timestamp 형식 오류 (YYYY-MM-DD HH:MM:SS)")

    # 이미지 디코딩 & 저장 (비동기)
    try:
        _, encoded = (
            data.screenshot_base64.split(",", 1)
            if "," in data.screenshot_base64
            else ("", data.screenshot_base64)
        )
        image_bytes = base64.b64decode(encoded)
        filename = f"{uuid.uuid4().hex}.png"
        save_path = os.path.join(FULL_IMAGE_DIR, filename)
        async with aiofiles.open(save_path, "wb") as f:
            await f.write(image_bytes)
    except Exception as e:
        raise HTTPException(400, f"이미지 저장 실패: {e}")

    rel_url = f"/static/{settings.image_dir}/{filename}"
    abs_url = f"{settings.base_url}{rel_url}"

    # 텍스트 로그 비동기 append
    log_path = os.path.join(settings.text_log_dir, f"lecture_{lecture_id}.txt")
    async with aiofiles.open(log_path, "a", encoding="utf-8") as log_file:
        await log_file.write(f"{dt:%Y-%m-%d %H:%M:%S} - {data.transcript}\n")

    # DB Insert
    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=dt.strftime("%Y-%m-%d"),
        time=dt.strftime("%H:%M:%S"),
        text=data.transcript,
        image_path=rel_url,
    )
    db.add(snapshot)
    await db.commit()

    return {
        "message": "스냅샷 저장 완료",
        "lecture_id": lecture_id,
        "date": snapshot.date,
        "time": snapshot.time,
        "text": data.transcript,
        "image_url": abs_url,
    }


# ───────────────────────────────
# 5) 리마인더 요약 API
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
                "당신은 강의 마무리 리마인더를 작성합니다.\n"
                "- 핵심 키워드 3개를 정하고 각각 간결하게 요약하세요.\n"
                "- JAVA 용어 사용을 우선하세요."
            ),
        },
        {"role": "user", "content": f"강의 내용:\n```\n{truncated}\n```"},
    ]

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    res = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        max_tokens=1200,
    )
    return SummaryResponse(
        lecture_id=lecture_id, summary=res.choices[0].message.content.strip()
    )


# ───────────────────────────────
# 6) 전체 요약 생성 & 저장 API
# ───────────────────────────────

@router.post("/lecture_summary", response_model=List[LectureSummaryResponse])
async def generate_lecture_summary(
    lecture_id: int = Query(...), db: AsyncSession = Depends(get_db)
):
    path = os.path.join(settings.text_log_dir, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "텍스트 파일 없음")

    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        full_text = await f.read()

    markdown = await summarize_text_with_gpt(full_text)

    topic_blocks = markdown.split("### ")[1:]
    topics = []
    for block in topic_blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        summary = " ".join(
            line[1:].strip() for line in lines[1:] if line.strip().startswith("-")
        )
        topics.append({"topic": title, "summary": summary})

    snaps = (
        (
            await db.execute(select(Snapshot).where(Snapshot.lecture_id == lecture_id))
        )
        .scalars()
        .all()
    )
    if not snaps:
        raise HTTPException(404, "스냅샷 없음")

    texts = [s.text for s in snaps]
    urls = [f"{settings.base_url}{s.image_path}" for s in snaps]

    # ★ MOD – 임베딩 한 번에 처리
    combined_inputs = [t["topic"] for t in topics] + texts
    embeddings = await embed_texts(combined_inputs)
    topic_embs = embeddings[: len(topics)]
    snap_embs = embeddings[len(topics) :]

    await db.execute(delete(LectureSummary).where(LectureSummary.lecture_id == lecture_id))

    output = []
    for i, tp in enumerate(topics):
        sims = cosine_similarity([topic_embs[i]], snap_embs)[0]
        top_idx = sims.argsort()[-3:][::-1]
        top_imgs = [urls[j] for j in top_idx]

        db.add(
            LectureSummary(
                lecture_id=lecture_id,
                topic=tp["topic"],
                summary=tp["summary"],
                image_url_1=top_imgs[0] if len(top_imgs) > 0 else None,
                image_url_2=top_imgs[1] if len(top_imgs) > 1 else None,
                image_url_3=top_imgs[2] if len(top_imgs) > 2 else None,
            )
        )

        output.append(
            {
                "topic": tp["topic"],
                "summary": tp["summary"],
                "highlights": [
                    {"text": texts[j], "image_url": urls[j]} for j in top_idx
                ],
            }
        )

    await db.commit()
    return output


# ───────────────────────────────
# 7) 저장된 요약 조회 API
# ───────────────────────────────

@router.get("/lecture_summary", response_model=List[LectureSummaryResponse])
async def get_stored_summary(lecture_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LectureSummary).where(LectureSummary.lecture_id == lecture_id)
    )
    summaries = result.scalars().all()
    if not summaries:
        raise HTTPException(404, "저장된 요약 없음")

    output = []
    for s in summaries:
        highlights = []
        if s.image_url_1:
            highlights.append({"image_url": s.image_url_1})
        if s.image_url_2:
            highlights.append({"image_url": s.image_url_2})
        if s.image_url_3:
            highlights.append({"image_url": s.image_url_3})

        output.append({
            "topic": s.topic,
            "summary": s.summary,
            "highlights": highlights
        })

    return output
