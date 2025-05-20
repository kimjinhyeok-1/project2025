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
        created_at=datetime.utcnow()
    )
    async with get_db_context() as db:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

    text_buffer.clear()
    return {
        "message": "질문 생성 및 저장 완료",
        "paragraph": obj.paragraph,
        "questions": obj.questions,
        "created_at": obj.created_at.isoformat()
    }

# ───────── 질문 전체 조회 ─────────
@router.get("/questions")
async def get_all_questions():
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).order_by(GeneratedQuestion.created_at))
        return {
            "results": [
                {
                    "paragraph": r.paragraph,
                    "questions": r.questions,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                } for r in result.scalars().all()
            ]
        }

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
