from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.services.gpt import generate_expected_questions
from app.database import get_db_context
from app.models import GeneratedQuestion
import asyncio
import re
from sqlalchemy import select

router = APIRouter()

# 요청 스키마
class TextChunkRequest(BaseModel):
    text: str

@router.get("/questions")
async def get_all_questions():
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).order_by(GeneratedQuestion.created_at))
        rows = result.scalars().all()
    return {"results": [{"paragraph": r.paragraph, "questions": r.questions} for r in rows]}

# OPTIONS/GET Dummy Route
@router.options("/upload_text_chunk")
@router.get("/upload_text_chunk")
async def dummy_text_route():
    return JSONResponse({"message": "This endpoint only accepts POST requests."})

# 질문 생성 API (1문단씩 바로 생성)
@router.post("/upload_text_chunk")
async def upload_text_chunk(body: TextChunkRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(400, detail="텍스트가 비어있습니다.")

    if not is_valid_paragraph(text):
        return {"message": "문단 길이 부족", "results": []}

    # 동기 GPT 질문 생성 (1개 문단만)
    questions = await asyncio.to_thread(generate_expected_questions, text)
    if not questions:
        return {"message": "질문 생성 실패", "results": []}

    # DB 저장
    obj = GeneratedQuestion(paragraph=text, questions=questions)
    async with get_db_context() as db:
        db.add(obj)
        await db.commit()

    return {"results": [{"paragraph": text, "questions": questions}]}

# 유틸 함수
def split_text_into_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", text) if s.strip()]

def is_valid_paragraph(text: str) -> bool:
    sentences = split_text_into_sentences(text)
    return len(sentences) >= 2 or len(text) >= 20
