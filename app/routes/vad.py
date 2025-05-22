from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.services.gpt import generate_expected_questions
from app.database import get_db_context
from app.models import GeneratedQuestion
from sqlalchemy import select
from datetime import datetime
import asyncio
import re

router = APIRouter()
text_buffer: list[str] = []  # STT 누적 버퍼

# ───────── 요청 스키마 ─────────
class TextChunkRequest(BaseModel):
    text: str

class LikeRequest(BaseModel):
    question_id: int  # 질문 인덱스 (0~4)

# ───────── 텍스트 누적 ─────────
@router.post("/upload_text_chunk")
async def upload_text_chunk(body: TextChunkRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(400, detail="텍스트가 비어있습니다.")
    text_buffer.append(text)
    return {"message": "텍스트 누적 완료", "buffer_length": len(text_buffer)}

# ───────── 질문 생성 ─────────
@router.post("/trigger_question_generation")
async def trigger_question_generation():
    if not text_buffer:
        raise HTTPException(400, detail="누적된 텍스트가 없습니다.")

    full_text = " ".join(text_buffer)
    if not is_valid_paragraph(full_text):
        raise HTTPException(400, detail="질문 생성을 위한 텍스트가 충분하지 않습니다.")

    try:
        questions = await asyncio.to_thread(generate_expected_questions, full_text)
    except Exception as e:
        raise HTTPException(500, detail=f"질문 생성 중 오류: {e}")

    if not questions:
        raise HTTPException(500, detail="질문 생성을 실패했습니다.")

    obj = GeneratedQuestion(
        paragraph=full_text,
        questions=questions[:5],
        likes=[0] * min(5, len(questions)),
        created_at=datetime.utcnow()
    )
    async with get_db_context() as db:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

    text_buffer.clear()
    return {
        "message": "질문 생성 및 저장 완료",
        "q_id": obj.id,
        "paragraph": obj.paragraph,
        "questions": obj.questions,
        "created_at": obj.created_at.isoformat()
    }

# ───────── 특정 질문 세트 조회 (q_id) ─────────
@router.get("/questions/{q_id}")
async def get_questions_by_qid(q_id: int):
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).where(GeneratedQuestion.id == q_id))
        question_set = result.scalar()

    if not question_set:
        raise HTTPException(404, detail="해당 q_id에 대한 질문 세트를 찾을 수 없습니다.")

    return {
        "q_id": question_set.id,
        "paragraph": question_set.paragraph,
        "questions": [
            {"text": q, "likes": question_set.likes[i]} for i, q in enumerate(question_set.questions)
        ],
        "created_at": question_set.created_at.isoformat() if question_set.created_at else None
    }

# ───────── 좋아요 반영 ─────────
@router.patch("/question/{q_id}/like")
async def like_question(q_id: int, body: LikeRequest):
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).where(GeneratedQuestion.id == q_id))
        question_set = result.scalar()

        if not question_set or body.question_id >= len(question_set.likes):
            raise HTTPException(404, detail="질문 인덱스를 찾을 수 없습니다.")

        question_set.likes[body.question_id] += 1
        await db.commit()

    return {"message": "좋아요 반영 완료"}

# ───────── 인기 질문 정렬 조회 ─────────
@router.get("/questions/popular_likes")
async def get_popular_likes(q_id: int):
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).where(GeneratedQuestion.id == q_id))
        question_set = result.scalar()

    if not question_set:
        return {"results": []}

    questions_with_likes = [
        {"text": q, "likes": question_set.likes[i]}
        for i, q in enumerate(question_set.questions)
    ]
    sorted_questions = sorted(questions_with_likes, key=lambda x: x["likes"], reverse=True)
    return {"results": sorted_questions}

# ───────── OPTIONS 프리플라이트 ─────────
@router.options("/upload_text_chunk")
@router.get("/upload_text_chunk")
async def dummy_text_route():
    return JSONResponse({"message": "POST로만 요청 가능합니다."})

# ───────── 유틸 ─────────
def split_text_into_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", text) if s.strip()]

def is_valid_paragraph(text: str) -> bool:
    return len(split_text_into_sentences(text)) >= 2 or len(text.strip()) >= 20
