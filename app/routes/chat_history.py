from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.auth import get_current_user_id, verify_student, verify_professor  # ✅ 추가됨
from app.models import QuestionAnswer
import openai
import os

router = APIRouter()

# ✅ 학생 자신의 질문 내역 확인 (학생 전용)
@router.get("/chat_history/me")
async def get_my_chat_history(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: str = Depends(verify_student)  # ✅ 학생만 접근 가능
):
    result = await db.execute(
        select(QuestionAnswer)
        .where(QuestionAnswer.user_id == user_id)
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

# ✅ 전체 질문 내역 확인 (교수자 전용, 질문자 정보 없음)
@router.get("/chat_history/all")
async def get_all_chat_history(
    db: AsyncSession = Depends(get_db),
    #_: str = Depends(verify_professor)
):
    result = await db.execute(
        select(QuestionAnswer).order_by(QuestionAnswer.created_at.desc())
    )
    records = result.scalars().all()
    print("📦 records 개수:", len(records))  # 🔍 이거 추가
    return [
        {
            "question": r.question,
            "answer": r.answer,
            "created_at": r.created_at.isoformat()
        }
        for r in records
    ]

# ✅ 질문 요약 기능 (교수자 전용)
@router.get("/chat_history/summary")
async def get_question_summary(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_professor)
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
