from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import LectureMaterial, QuestionAnswer
import openai
import os
from datetime import datetime

router = APIRouter()

# ✅ 최신 OpenAI 클라이언트 생성
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 학생 질문 내역 조회 API
@router.get("/ask/history")
async def get_question_history(db: AsyncSession = Depends(get_db)):
    """저장된 질문-응답 내역 조회"""
    result = await db.execute(select(QuestionAnswer).order_by(QuestionAnswer.created_at.desc()))
    history = result.scalars().all()
    
    return [
        {"question": qa.question, "answer": qa.answer, "timestamp": qa.created_at}
        for qa in history
    ]

@router.get("/ask/summary")
async def get_question_summary(db: AsyncSession = Depends(get_db)):
    """가장 많이 질문된 내용을 요약하여 교수님에게 전달 (한글 지원)"""
    try:
        # 최근 질문 데이터 가져오기
        result = await db.execute(select(QuestionAnswer.question))
        questions = [row[0] for row in result.all()]
        
        if not questions:
            return {"message": "질문 데이터가 부족합니다."}

        # ✅ GPT를 이용해 중요 질문 요약 생성 (한글 요약 적용)
        prompt = f"""
        다음은 학생들이 자주 묻는 질문입니다:
        {questions}

        교수님을 위한 요약을 한글로 작성하세요. 학생들이 어려워하는 개념을 설명하고, 보충할 내용을 추천하세요.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        summary = response.choices[0].message.content.strip()

        return {
            "most_common_questions": questions[:5],  # 상위 5개 질문만 출력
            "summary_for_professor": summary  # ✅ 한글 요약 제공
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
