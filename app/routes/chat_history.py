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

    return [  # ✅ 들여쓰기 정확히 맞춤
        {
            "question": r.question,
            "answer": r.answer,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]


# ✅ 전체 질문 내역 확인 (교수자 전용, 질문자 정보 없음)
@router.get("/chat_history/all")
async def get_all_chat_history(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_professor)
):
    result = await db.execute(
        select(QuestionAnswer).order_by(QuestionAnswer.created_at.desc())
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

# ✅ 질문 요약 기능 (교수자 전용)
@router.get("/chat_history/summary")
async def get_question_summary(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_professor)
):
    try:
        # 1. 질문 불러오기
        result = await db.execute(select(QuestionAnswer.question))
        questions = [row[0].strip() for row in result.all() if row[0] and len(row[0].strip()) > 5]

        # 2. 중복 제거 및 최대 50개 제한
        unique_questions = list(set(questions))[:30]

        if not unique_questions:
            return {"message": "질문 데이터가 부족합니다."}

        # 3. 포맷팅된 프롬프트 생성
        formatted_questions = "\n".join(f"- {q}" for q in unique_questions)

        prompt = f"""
        다음은 학생들이 최근에 많이 한 질문들입니다:

        {formatted_questions}

        이 질문들을 바탕으로, 학생들이 자주 어려워하는 개념을 한글로 요약하고
        추가 설명이나 보충 강의가 필요한 주제를 교수님께 추천해 주세요.
        """

        # 4. GPT 호출
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        summary = response.choices[0].message.content.strip()

        return {
            "most_common_questions": unique_questions[:5],  # 상위 5개만 프론트로
            "summary_for_professor": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
