from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.auth import get_current_user_id, verify_student, verify_professor  # ✅ 추가됨
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

# ✅ minimal 전처리 함수
def minimal_preprocess(text: str) -> str:
    # 특수문자 정리 (.,!? 만 허용)
    text = re.sub(r"[^\w\s.,!?]", "", text)
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # 길이 제한
    return text if len(text) <= 250 else text[:247] + "..."

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

        # 4. 프롬프트 작성 (Markdown 지시 추가)
        prompt = f"""
아래는 학생들이 최근에 한 질문 목록입니다.

{formatted_questions}

이 질문들을 참고하여:

1. 강의 주제와 관련된 주요 개념만 요약해 주세요.
2. Markdown 형식으로 작성해 주세요. (예: # 제목, ## 소제목, - 목록, **강조** 등)
3. 요약은 명확하고 간결하게 작성해 주세요.
4. 필요 시 보충 강의가 필요한 주제도 추천해 주세요.

**[응답은 반드시 Markdown 형식으로만 작성하세요.]**
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
            "most_common_questions": processed_questions[:5],  # 프론트용 상위 5개
            "summary_for_professor": summary  # Markdown 포맷 적용된 요약
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))