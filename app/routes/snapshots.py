import os
import base64
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sklearn.metrics.pairwise import cosine_similarity

from openai import AsyncOpenAI
from app.database import get_db
from app.models import Lecture, Snapshot

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
    summary: str

# ──────────────────────────────────────────────────────────
# 헬퍼: 텍스트 토큰 슬라이싱
# ──────────────────────────────────────────────────────────

def truncate_by_token(text: str, max_tokens: int = 3500) -> str:
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)
    return enc.decode(tokens[:max_tokens])

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
    try:
        dt = datetime.strptime(data.timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(400, "timestamp 형식 오류 (yyyy-MM-dd HH:mm:ss)")

    date_group = dt.strftime("%Y-%m-%d")

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

    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    try:
        with open(text_log_path, "w", encoding="utf-8") as log_file:
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
# 2) GPT 요약 함수
# ──────────────────────────────────────────────────────────

async def summarize_text_with_gpt(text: str) -> str:
    truncated = truncate_by_token(text)
    system_msg = {
        "role": "system",
        "content": (
            "당신은 대학 강의의 전체 내용을 요약하는 AI 도우미입니다.\n\n"
            "목표:\n"
            "1. 수업 전체 내용을 학생들이 다시 볼 수 있도록 마크다운 형식으로 정리합니다.\n"
            "2. 주제별로 '### 주제명'을 사용하고, 그 아래에 해당 주제의 설명을 '-' 형식으로 정리합니다.\n"
            "3. 설명은 명확하고 일관되게, 복습이나 스냅샷 연결에 적합하도록 작성합니다.\n"
            "4. 논리적 흐름을 유지하며, 중요한 개념이나 정의, 예시가 있다면 간결히 포함합니다.\n"
            "5. 전체 분량은 3~5개의 주제로 구성되도록 조절하세요.\n"
            "6. 가능한 경우 주제의 순서는 수업 흐름을 반영하세요."
        )
    }
    user_msg = {
        "role": "user",
        "content": f"강의 로그:\n```text\n{truncated}\n```"
    }
    res = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_msg, user_msg],
        temperature=0.5,
        max_tokens=1200,
    )
    return res.choices[0].message.content.strip()

async def summarize_text_with_gpt_reminder(text: str) -> str:
    truncated = truncate_by_token(text)
    system_msg = {
        "role": "system",
        "content": (
            "당신은 대학교 강의의 마무리 리마인더를 작성하는 AI 비서입니다. "
            "교수자가 수업을 마치기 전에 학생들에게 오늘의 핵심 내용을 간략히 정리해 주려고 합니다.\n\n"
            "요구 사항:\n"
            "1. 강의의 핵심 키워드 5개를 선정하고, 각 키워드별로 간단한 요약 설명을 제공합니다.\n"
            "2. 출력 형식은 다음과 같습니다:\n"
            "### 키워드1\n"
            "- 간결한 요약 설명\n"
            "### 키워드2\n"
            "- 간결한 요약 설명\n"
            "...\n"
            "3. 가능하다면 Java 개념과 관련된 용어를 반영하세요."
        )
    }
    user_msg = {
        "role": "user",
        "content": f"강의 로그:\n```text\n{truncated}\n```"
    }
    res = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_msg, user_msg],
        temperature=0.5,
        max_tokens=1200,
    )
    return res.choices[0].message.content.strip()

@router.get("/generate_markdown_summary", response_model=SummaryResponse)
async def generate_markdown_summary(lecture_id: int = Query(...)):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "요약할 텍스트 없음")
    text = open(path, "r", encoding="utf-8").read()
    md = await summarize_text_with_gpt_reminder(text)
    return SummaryResponse(lecture_id=lecture_id, summary=md)

@router.get("/generate_question_summary", response_model=SummaryResponse)
async def generate_question_summary(lecture_id: int = Query(...)):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "요약할 텍스트 없음")
    text = open(path, "r", encoding="utf-8").read()
    summ = await summarize_text_with_gpt(text)
    return SummaryResponse(lecture_id=lecture_id, summary=summ)

# ──────────────────────────────────────────────────────────
# 3) 최종 요약 + 이미지 매핑 API
# ──────────────────────────────────────────────────────────

@router.get("/lecture_summary")
async def get_lecture_summary(
    lecture_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(404, "텍스트 파일 없음")
    full_text = open(path, "r", encoding="utf-8").read()
    markdown = await summarize_text_with_gpt(full_text)

    topic_blocks = markdown.split("### ")[1:]
    topics = []
    for block in topic_blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        topic_title = lines[0]
        summary_lines = [line for line in lines[1:] if line.strip().startswith("-")]
        summary = " ".join(line[1:].strip() for line in summary_lines)
        topics.append({"topic": topic_title, "summary": summary})

    q = await db.execute(select(Snapshot).where(Snapshot.lecture_id == lecture_id))
    snaps = q.scalars().all()
    if not snaps:
        raise HTTPException(404, "스냅샷 없음")

    texts = [s.text for s in snaps]
    data = [{"text": s.text, "image_url": f"https://project2025-backend.onrender.com{s.image_path}"} for s in snaps]

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
