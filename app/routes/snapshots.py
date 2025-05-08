import os
import base64
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import text, delete
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sklearn.metrics.pairwise import cosine_similarity

from openai import AsyncOpenAI
from app.database import get_db
from app.models import Lecture, Snapshot, LectureSummary

import tiktoken

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
    summary: Optional[str]

# ──────────────────────────────────────────────────────────
# 헬퍼 함수
# ──────────────────────────────────────────────────────────

def truncate_by_token(text: str, max_tokens: int = 3500) -> str:
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)
    return enc.decode(tokens[:max_tokens])

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
async def create_lecture(
    db: AsyncSession = Depends(get_db),
    body: dict = Body(None)
):
    await db.execute(text(
        "SELECT setval('lectures_id_seq', COALESCE((SELECT MAX(id) FROM lectures), 0), true)"
    ))
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
    lecture_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        dt = datetime.strptime(data.timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(400, "timestamp 형식 오류 (yyyy-MM-dd HH:mm:ss)")

    date_group = dt.strftime("%Y-%m-%d")

    try:
        _, encoded = data.screenshot_base64.split(",", 1) if "," in data.screenshot_base64 else ("", data.screenshot_base64)
        image_bytes = base64.b64decode(encoded)
        filename = f"{uuid.uuid4().hex}.png"
        save_path = os.path.join(FULL_IMAGE_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(image_bytes)
    except Exception:
        raise HTTPException(400, "이미지 디코딩 또는 저장 실패")

    rel_url = f"/static/{IMAGE_DIR}/{filename}"
    abs_url = f"https://project2025-backend.onrender.com{rel_url}"

    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    try:
        with open(text_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{dt:%Y-%m-%d %H:%M:%S} - {data.transcript}\n")
    except:
        pass

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
# 2) 리마인더 요약 API
# ──────────────────────────────────────────────────────────

@router.get("/generate_markdown_summary", response_model=SummaryResponse)
async def generate_markdown_summary(lecture_id: int = Query(...)):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "요약할 텍스트 없음")
    text = open(path, "r", encoding="utf-8").read()
    truncated = truncate_by_token(text)
    messages = [
        {"role": "system", "content": (
            "당신은 강의 마무리 리마인더를 작성합니다.\n"
            "- 핵심 키워드 3개를 정하고 각각 간결히 요약하세요.\n"
            "- JAVA 용어 사용을 우선하세요."
        )},
        {"role": "user", "content": f"강의 내용:\n```\n{truncated}\n```"}
    ]
    res = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        max_tokens=1200
    )
    return SummaryResponse(lecture_id=lecture_id, summary=res.choices[0].message.content.strip())

# ──────────────────────────────────────────────────────────
# 3) 전체 요약 + 이미지 매핑 API
# ──────────────────────────────────────────────────────────

@router.get("/lecture_summary")
async def get_lecture_summary(
    lecture_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "텍스트 파일 없음")

    # 1. 기존 요약 삭제
    await db.execute(delete(LectureSummary).where(LectureSummary.lecture_id == lecture_id))

    # 2. 요약 생성
    full_text = open(path, "r", encoding="utf-8").read()
    markdown = await summarize_text_with_gpt(full_text)

    topic_blocks = markdown.split("### ")[1:]
    topics = []
    for block in topic_blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        title = lines[0]
        summary = " ".join(line[1:].strip() for line in lines[1:] if line.strip().startswith("-"))
        topics.append({"topic": title, "summary": summary})

    # 3. 스냅샷 가져오기 및 임베딩 계산
    q = await db.execute(select(Snapshot).where(Snapshot.lecture_id == lecture_id))
    snaps = q.scalars().all()
    if not snaps:
        raise HTTPException(404, "스냅샷 없음")

    texts = [s.text for s in snaps]
    urls = [f"https://project2025-backend.onrender.com{s.image_path}" for s in snaps]
    topic_embs = await embed_texts([t["topic"] for t in topics])
    snap_embs = await embed_texts(texts)

    output = []
    for i, tp in enumerate(topics):
        sims = cosine_similarity([topic_embs[i]], snap_embs)[0]
        top_idx = sims.argsort()[-3:][::-1]
        top_imgs = [urls[j] for j in top_idx]

        db.add(LectureSummary(
            lecture_id=lecture_id,
            topic=tp["topic"],
            summary=tp["summary"],
            image_url_1=top_imgs[0] if len(top_imgs) > 0 else None,
            image_url_2=top_imgs[1] if len(top_imgs) > 1 else None,
            image_url_3=top_imgs[2] if len(top_imgs) > 2 else None,
        ))

        output.append({
            "topic": tp["topic"],
            "summary": tp["summary"],
            "highlights": [{"text": texts[j], "image_url": urls[j]} for j in top_idx]
        })

    await db.commit()
    return output
