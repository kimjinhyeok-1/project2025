from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.services.gpt import generate_expected_questions
from app.database import get_db_context
from app.models import GeneratedQuestion
import asyncio
import re
from sqlalchemy import select
from datetime import datetime

router = APIRouter()

# 전역 STT 누적 버퍼 (lecture_id 제거)
text_buffer: list[str] = []

# ────────────── 요청 스키마 ──────────────
class TextChunkRequest(BaseModel):
    text: str

class QuestionTriggerRequest(BaseModel):
    pass  # 더 이상 lecture_id 필요 없음

# ────────────── 전체 질문 조회 (학습자용) ──────────────
@router.get("/questions")
async def get_all_questions():
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).order_by(GeneratedQuestion.created_at))
        rows = result.scalars().all()
    return {
        "results": [
            {"paragraph": r.paragraph, "questions": r.questions} for r in rows
        ]
    }

# ────────────── 프리플라이트 dummy ──────────────
@router.options("/upload_text_chunk")
@router.get("/upload_text_chunk")
async def dummy_text_route():
    return JSONResponse({"message": "This endpoint only accepts POST requests."})

# ────────────── STT 누적 (질문 생성 X) ──────────────
@router.post("/upload_text_chunk")
async def upload_text_chunk(body: TextChunkRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(400, detail="텍스트가 비어있습니다.")
    text_buffer.append(text)
    return {"message": "텍스트 누적 완료"}

# ────────────── 질문 생성 트리거 (질문 있나요?) ──────────────
@router.post("/trigger_question_generation")
async def trigger_question_generation(_: QuestionTriggerRequest):
    if not text_buffer:
        raise HTTPException(400, detail="누적된 텍스트가 없습니다.")

    full_text = " ".join(text_buffer)

    # 질문 생성 (최대 5개)
    questions = await asyncio.to_thread(generate_expected_questions, full_text)
    questions = questions[:5] if len(questions) > 5 else questions

    if not questions:
        raise HTTPException(500, detail="GPT 질문 생성 실패")

    # DB 저장
    obj = GeneratedQuestion(
        paragraph=full_text,
        questions=questions,
        created_at=datetime.utcnow()
    )
    async with get_db_context() as db:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

    # 누적 버퍼 초기화
    text_buffer.clear()

    return {
        "message": "질문 생성 완료",
        "paragraph": full_text,
        "questions": questions
    }

# ────────────── 유틸 함수 ──────────────
def split_text_into_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", text) if s.strip()]

def is_valid_paragraph(text: str) -> bool:
    sentences = split_text_into_sentences(text)
    return len(sentences) >= 2 or len(text.strip()) >= 20
