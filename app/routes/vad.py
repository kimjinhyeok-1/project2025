from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.services.gpt import generate_expected_questions
from app.database import get_db_context
from app.models import GeneratedQuestion, StudentQuestion, Feedback
from sqlalchemy import select, func, desc
from datetime import datetime
import asyncio
import re

router = APIRouter()

text_buffer: list[str] = []

# 요청 스키마
class TextChunkRequest(BaseModel):
    text: str

class QuestionTriggerRequest(BaseModel):
    pass

class FeedbackRequest(BaseModel):
    user_id: int
    question_text: str
    knows: bool

class StudentQuestionRequest(BaseModel):
    user_id: int
    text: str

# 예상 질문 생성
@router.post("/trigger_question_generation")
async def trigger_question_generation(_: QuestionTriggerRequest):
    if not text_buffer:
        raise HTTPException(400, detail="누적된 텍스트가 없습니다.")
    full_text = " ".join(text_buffer)
    questions = await asyncio.to_thread(generate_expected_questions, full_text)
    questions = questions[:5]
    if not questions:
        raise HTTPException(500, detail="GPT 질문 생성 실패")

    obj = GeneratedQuestion(
        paragraph=full_text,
        questions=questions,
        created_at=datetime.utcnow()
    )
    async with get_db_context() as db:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
    text_buffer.clear()
    return {"message": "질문 생성 완료", "paragraph": full_text, "questions": questions}

# 실시간 텍스트 누적
@router.post("/upload_text_chunk")
async def upload_text_chunk(body: TextChunkRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(400, detail="텍스트가 비어있습니다.")
    text_buffer.append(text)
    return {"message": "텍스트 누적 완료"}

# 전체 질문 조회 (학생 Recent 탭용)
@router.get("/questions")
async def get_all_questions():
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).order_by(GeneratedQuestion.created_at.desc()))
        rows = result.scalars().all()
    results = []
    for r in rows:
        for q in r.questions:
            results.append({
                "text": q,
                "created_at": r.created_at,
                "type": "ai"
            })
    # 직접 질문도 포함
    async with get_db_context() as db:
        result = await db.execute(select(StudentQuestion).order_by(StudentQuestion.created_at.desc()))
        rows = result.scalars().all()
    for r in rows:
        results.append({
            "text": r.text,
            "created_at": r.created_at,
            "type": "student"
        })
    return {"results": sorted(results, key=lambda x: x["created_at"], reverse=True)}

# 직접 질문 작성 API
@router.post("/student_question")
async def add_student_question(body: StudentQuestionRequest):
    obj = StudentQuestion(
        user_id=body.user_id,
        text=body.text,
        created_at=datetime.utcnow()
    )
    async with get_db_context() as db:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
    return {"message": "저장 완료", "text": obj.text, "created_at": obj.created_at}

# 피드백 저장
@router.post("/feedback")
async def save_feedback(body: FeedbackRequest):
    obj = Feedback(
        user_id=body.user_id,
        question_text=body.question_text,
        knows=body.knows,
        created_at=datetime.utcnow()
    )
    async with get_db_context() as db:
        db.add(obj)
        await db.commit()
    return {"message": "피드백 저장 완료"}

# 인기 질문 (모름 비율 상위 2개)
@router.get("/questions/popular_summary")
async def get_popular_summary():
    async with get_db_context() as db:
        result = await db.execute(
            select(Feedback.question_text,
                   func.count().label("total"),
                   func.sum(func.cast(~Feedback.knows, int)).label("unknown_count")
                   ).group_by(Feedback.question_text)
        )
        rows = result.fetchall()

    enriched = []
    for row in rows:
        if row.total == 0 or row.unknown_count == 0:
            continue
        percent = round((row.unknown_count / row.total) * 100, 1)
        enriched.append({
            "text": row.question_text,
            "unknown_percent": percent
        })

    top2 = sorted(enriched, key=lambda x: x["unknown_percent"], reverse=True)[:2]
    return {"results": top2}
