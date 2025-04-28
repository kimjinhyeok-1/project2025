from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.database import get_db
from app.auth import verify_professor, get_current_user_id
from app.models import QuestionAnswer, Summary
import openai
import os
import re
from datetime import datetime, timezone

# ✅ 상단 초기화
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

router = APIRouter()

def minimal_preprocess(text: str) -> str:
    text = re.sub(r"[^\w\s.,!?]", "", text)
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= 250 else text[:247] + "..."

@router.get("/chat_history/summary")
async def get_question_summary(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_professor)
):
    try:
        # 1. 오늘 생성된 요약 있는지 확인
        result = await db.execute(
            select(Summary).order_by(desc(Summary.created_at)).limit(1)
        )
        existing_summary = result.scalars().first()

        now = datetime.now(timezone.utc)
        today = now.date()

        if existing_summary and existing_summary.created_at.date() == today:
            return {
                "summary_for_professor": existing_summary.summary_text
            }

        # 2. 질문 30개 가져오기
        result = await db.execute(
            select(QuestionAnswer.question)
            .order_by(QuestionAnswer.created_at.desc())
            .limit(30)
        )
        questions = [row[0].strip() for row in result.all() if row[0] and len(row[0].strip()) > 5]

        if not questions:
            return {"message": "질문 데이터가 부족합니다."}

        processed_questions = [minimal_preprocess(q) for q in questions]
        formatted_questions = "\n".join(f"{idx+1}. {q}" for idx, q in enumerate(processed_questions))

        prompt = f"""
아래는 학생들이 최근에 한 질문 목록입니다.

{formatted_questions}

유의사항:
"JAVA 언어" 또는 "객체지향프로그래밍" 과목과 관련된 질문만 선별하여 요약해 주세요.
관련 질문들은 중복 제거 및 유사 질문끼리 통합하여 간결하게 요약해 주세요.
markdown 형식으로 하되 제목은 적지 말고 리스트 번호는 매기지 마세요.
"""

        # 3. GPT 호출
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.5
        )
        summary_text = response.choices[0].message.content.strip()

        # 4. 새 summary 저장
        new_summary = Summary(summary_text=summary_text)
        db.add(new_summary)
        await db.commit()

        return {
            "summary_for_professor": summary_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[chat_history/summary] 요약 생성 중 오류: {str(e)}")

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