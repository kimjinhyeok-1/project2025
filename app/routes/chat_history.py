from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from sqlalchemy.orm import selectinload       # 추가된 임포트
from app.database import get_db
from app.auth import verify_professor, get_current_user_id, verify_student
from app.models import QuestionAnswer, Summary
import openai
import os
import re
from datetime import datetime, timezone

# ✅ GPT 초기화
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

router = APIRouter()

@router.get("/chat_history/all")
async def get_all_chat_history(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_professor)
):
    """
    교수님용 전체 대화 보기:
    - user_id, user_name, question, answer, created_at 반환
    - 생성일자 내림차순 정렬
    """
    try:
        result = await db.execute(
            select(QuestionAnswer)
            .options(selectinload(QuestionAnswer.user))
            .order_by(desc(QuestionAnswer.created_at))
        )
        records = result.scalars().all()

        return [
            {
                "user_id":    qa.user_id,
                "user_name":  qa.user.name if qa.user else None,
                "question":   qa.question,
                "answer":     qa.answer,
                "created_at": qa.created_at.isoformat() if qa.created_at else None
            }
            for qa in records
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"[chat_history/all] 전체 대화 로드 중 오류: {str(e)}"
        )

def minimal_preprocess(text: str) -> str:
    text = re.sub(r"[^\w\s.,!?]", "", text)
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= 250 else text[:247] + "..."

def clean_summary(text: str) -> str:
    lines = text.strip().split("\n")
    cleaned = [
        "- " + re.sub(r"^[\d\.\-\•\●\*\s]*", "", line).strip()
        for line in lines if line.strip()
    ]
    return "\n".join(cleaned)

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
            return {"summary_for_professor": existing_summary.summary_text}

        # 2. 질문 30개 가져오기
        result = await db.execute(
            select(QuestionAnswer.question)
            .order_by(QuestionAnswer.created_at.desc())
            .limit(30)
        )
        questions = [
            row[0].strip() for row in result.all()
            if row[0] and len(row[0].strip()) > 5
        ]

        if not questions:
            return {"message": "질문 데이터가 부족합니다."}

        processed = [minimal_preprocess(q) for q in questions]
        formatted = "\n".join(f"{i+1}. {q}" for i, q in enumerate(processed))

        prompt = f"""
다음은 학생들이 최근 한 질문입니다:

{formatted}

JAVA 언어나 객체지향프로그래밍 관련 질문만 골라 요약하세요.
유사 질문은 하나로 묶고, 중복은 제거하세요.
간결한 문장으로 줄바꿈만 해주세요.
"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )
        summary_text = response.choices[0].message.content.strip()
        summary_text = clean_summary(summary_text)

        new_summary = Summary(summary_text=summary_text)
        db.add(new_summary)
        await db.commit()

        return {"summary_for_professor": summary_text}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"[chat_history/summary] 요약 생성 중 오류: {str(e)}"
        )

@router.get("/chat_history/me")
async def get_my_chat_history(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: str = Depends(verify_student)
):
    result = await db.execute(
        select(QuestionAnswer)
        .where(QuestionAnswer.user_id == user_id)
        .order_by(QuestionAnswer.created_at.desc())
    )
    records = result.scalars().all()

    return [
        {
            "question":   r.question,
            "answer":     r.answer,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]
