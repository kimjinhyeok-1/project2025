from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.auth import get_current_user_id, verify_student, verify_professor
from app.models import QuestionAnswer
import openai
import os
import re

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
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]

# ✅ 전체 질문 내역 확인 (교수자 전용)
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

# ✅ minimal 전처리 함수
def minimal_preprocess(text: str) -> str:
    text = re.sub(r"[^\w\s.,!?]", "", text)
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= 250 else text[:247] + "..."

# ✅ 요약 기능 (교수자 전용)
@router.get("/chat_history/summary")
async def get_question_summary(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_professor)
):
    try:
        # 1. 최근 질문 10개 가져오기
        result = await db.execute(
            select(QuestionAnswer.question).order_by(QuestionAnswer.created_at.desc()).limit(10)
        )
        questions = [row[0].strip() for row in result.all() if row[0] and len(row[0].strip()) > 5]

        if not questions:
            return {"message": "질문 데이터가 부족합니다."}

        # 2. 전처리 적용
        processed_questions = [minimal_preprocess(q) for q in questions]

        # 3. 포맷팅
        formatted_questions = "\n".join(f"{idx+1}. {q}" for idx, q in enumerate(processed_questions))

        # 4. 프롬프트 작성 (★ 들여쓰기 수정 완료)
        prompt = f"""
아래는 학생들이 최근에 한 질문 목록입니다.

{formatted_questions}

유의사항:
"JAVA 언어" 또는 "객체지향프로그래밍" 과목과 관련된 질문만 선별하여 요약해 주세요.\n
관련 질문들은 중복 제거 및 유사 질문끼리 통합하여 간결하게 요약해 주세요.\n
markdown 형식으로 하되 제목은 적지 말고 리스트 번호는 매기지 마세요.
"""

        # 5. GPT 호출
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.5
        )
        summary = response.choices[0].message.content.strip()

        return {
            "most_common_questions": processed_questions[:5],
            "summary_for_professor": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
