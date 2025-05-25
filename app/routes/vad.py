from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.services.gpt import generate_expected_questions
from app.database import get_db_context
from app.models import GeneratedQuestion, StudentQuestion
from sqlalchemy import select
from datetime import datetime
import asyncio
import re

router = APIRouter()
text_buffer: list[str] = []

# 요청 모델
class TextChunkRequest(BaseModel):
    text: str

class LikeRequest(BaseModel):
    question_id: int

class StudentQuestionRequest(BaseModel):
    q_id: int
    text: str

# 질문 세트 조회
async def get_question_set(db, q_id: Optional[int] = None) -> Optional[GeneratedQuestion]:
    if q_id is not None:
        result = await db.execute(select(GeneratedQuestion).where(GeneratedQuestion.id == q_id))
    else:
        result = await db.execute(select(GeneratedQuestion).order_by(GeneratedQuestion.id.desc()).limit(1))
    return result.scalar_one_or_none()

# STT 텍스트 누적
@router.post("/upload_text_chunk")
async def upload_text_chunk(body: TextChunkRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(400, detail="텍스트가 비어있습니다.")
    text_buffer.append(text)
    return {"message": "텍스트 누적 완료", "buffer_length": len(text_buffer)}

# 질문 생성 트리거
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

# 학생 직접 질문 등록
@router.post("/student_question")
async def post_student_question(data: StudentQuestionRequest):
    async with get_db_context() as db:
        question = StudentQuestion(
            q_id=data.q_id,
            text=data.text,
            created_at=datetime.utcnow()
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return {
            "message": "학생 질문 저장 완료",
            "id": question.id,
            "text": question.text,
            "created_at": question.created_at.isoformat()
        }

# 학생 직접 질문 전체 조회
@router.get("/student_questions")
async def get_student_questions(q_id: Optional[int] = None):
    async with get_db_context() as db:
        if q_id is not None:
            result = await db.execute(select(StudentQuestion).where(StudentQuestion.q_id == q_id).order_by(StudentQuestion.created_at.desc()))
        else:
            result = await db.execute(select(StudentQuestion).order_by(StudentQuestion.created_at.desc()))
        questions = result.scalars().all()
        return {
            "results": [
                {
                    "id": q.id,
                    "q_id": q.q_id,
                    "text": q.text,
                    "created_at": q.created_at.isoformat()
                } for q in questions
            ]
        }

# 최신 q_id 반환
@router.get("/questions/latest_id")
async def get_latest_qid():
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion.id).order_by(GeneratedQuestion.id.desc()).limit(1))
        q_id = result.scalar()
    return {"q_id": q_id}

# 최신 질문 세트 반환
@router.get("/questions/latest")
async def get_latest_questions():
    async with get_db_context() as db:
        question_set = await get_question_set(db)

    if not question_set:
        raise HTTPException(404, detail="질문 세트가 존재하지 않습니다.")

    return {
        "q_id": question_set.id,
        "paragraph": question_set.paragraph,
        "questions": [
            {"text": q, "likes": question_set.likes[i]} for i, q in enumerate(question_set.questions)
        ],
        "created_at": question_set.created_at.isoformat()
    }

# 좋아요
@router.patch("/question/{q_id}/like")
async def like_question(q_id: int, body: LikeRequest):
    async with get_db_context() as db:
        question_set = await get_question_set(db, q_id)

        if not question_set or not (0 <= body.question_id < len(question_set.likes)):
            raise HTTPException(404, detail="질문 인덱스를 찾을 수 없습니다.")

        updated_likes = question_set.likes.copy()
        updated_likes[body.question_id] += 1
        question_set.likes = updated_likes

        await db.commit()
        await db.refresh(question_set)

        print(f"[LIKE PATCH] q_id={q_id}, question_id={body.question_id}, likes={question_set.likes}")
        return {"message": "좋아요 반영 완료"}

# 좋아요 취소
@router.patch("/question/{q_id}/unlike")
async def unlike_question(q_id: int, body: LikeRequest):
    async with get_db_context() as db:
        question_set = await get_question_set(db, q_id)

        if not question_set or not (0 <= body.question_id < len(question_set.likes)):
            raise HTTPException(404, detail="질문 인덱스를 찾을 수 없습니다.")

        updated_likes = question_set.likes.copy()
        if updated_likes[body.question_id] > 0:
            updated_likes[body.question_id] -= 1
            question_set.likes = updated_likes
            await db.commit()
            await db.refresh(question_set)
            print(f"[UNLIKE PATCH] q_id={q_id}, question_id={body.question_id}, likes={question_set.likes}")
            return {"message": "좋아요 취소 완료"}
        else:
            return {"message": "이미 0입니다."}

# 좋아요 순으로 질문 정렬
@router.get("/questions/popular_likes")
async def get_popular_likes(q_id: Optional[int] = None):
    async with get_db_context() as db:
        question_set = await get_question_set(db, q_id)

    if not question_set:
        return {"results": []}

    questions_with_likes = [
        {"text": q, "likes": question_set.likes[i]} for i, q in enumerate(question_set.questions)
    ]
    sorted_questions = sorted(questions_with_likes, key=lambda x: x["likes"], reverse=True)

    print(f"[POPULAR GET] q_id={q_id}, sorted={sorted_questions}")

    return {"results": sorted_questions}

# 문장 유효성 체크
def split_text_into_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", text) if s.strip()]

def is_valid_paragraph(text: str) -> bool:
    return len(split_text_into_sentences(text)) >= 2 or len(text.strip()) >= 20
