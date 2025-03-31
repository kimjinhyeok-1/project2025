from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.auth import get_current_student_name, verify_admin
from app.models import QuestionAnswer
import openai
import os

router = APIRouter()

# ✅ 학생 자신의 질문 내역 확인
@router.get("/chat_history/me")
async def get_my_chat_history(
    db: AsyncSession = Depends(get_db),
    student_name: str = Depends(get_current_student_name)
):
    result = await db.execute(
        select(QuestionAnswer)
        .where(QuestionAnswer.student_name == student_name)
        .order_by(QuestionAnswer.created_at.desc())
    )
    records = result.scalars().all()
    return [
        {
            "question": r.question,
            "answer": r.answer,
            "created_at": r.created_at.isoformat()
        }
        for r in records
    ]

# ✅ 전체 질문 내역 확인 (관리자용)
@router.get("/chat_history/all")
async def get_all_chat_history(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_admin)  # 🔐 관리자 인증 필요
):
    result = await db.execute(
        select(QuestionAnswer).order_by(QuestionAnswer.created_at.desc())
    )
    records = result.scalars().all()
    return [
        {
            "student": r.student_name,
            "question": r.question,
            "answer": r.answer,
            "created_at": r.created_at.isoformat()
        }
        for r in records
    ]

# ✅ 질문 요약 기능 (관리자 전용)
@router.get("/chat_history/summary")
async def get_question_summary(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_admin)  # 🔐 관리자 인증 필요
):
    try:
        result = await db.execute(select(QuestionAnswer.question))
        questions = [row[0] for row in result.all()]

        if not questions:
            return {"message": "질문 데이터가 부족합니다."}

        prompt = f"""
        다음은 학생들이 자주 묻는 질문입니다:
        {questions}

        교수님을 위한 요약을 한글로 작성하세요. 학생들이 어려워하는 개념을 설명하고, 보충할 내용을 추천하세요.
        """

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        summary = response.choices[0].message.content.strip()

        return {
            "most_common_questions": questions[:5],
            "summary_for_professor": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))