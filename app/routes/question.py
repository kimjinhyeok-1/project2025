from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Assignment, AssignmentQuestion, User
from app.schemas import AssignmentQuestionCreate, AssignmentQuestionOut
from app.utils.helper import generate_gpt_response
from app.auth import get_current_user_id, verify_student  # 🔐 인증 함수 활용
from typing import List

router = APIRouter()

# ✅ 질문 등록 + GPT 응답 생성
@router.post("/ask", response_model=AssignmentQuestionOut, dependencies=[Depends(verify_student)])
async def ask_assignment_question(
    question: AssignmentQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    # 과제 존재 여부 확인
    result = await db.execute(select(Assignment).where(Assignment.id == question.assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")

    # GPT 응답 생성
    gpt_answer = await generate_gpt_response(
        assignment_description=assignment.description,
        sample_answer=assignment.sample_answer,
        question_text=question.question_text,
        code_snippet=question.code_snippet,
    )

    # 질문 저장
    new_question = AssignmentQuestion(
        assignment_id=question.assignment_id,
        user_id=current_user_id,
        question_text=question.question_text,
        code_snippet=question.code_snippet,
        gpt_answer=gpt_answer,
    )
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)
    return new_question


# ✅ 로그인한 학생의 질문 목록 조회
@router.get("/me", response_model=List[AssignmentQuestionOut], dependencies=[Depends(verify_student)])
async def get_my_questions(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    result = await db.execute(
        select(AssignmentQuestion).where(AssignmentQuestion.user_id == current_user_id)
    )
    return result.scalars().all()
