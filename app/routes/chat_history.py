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

@router.get("/chat_history/summary")
async def get_question_summary(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_professor)
):
    try:
        # 1. 질문 불러오기
        result = await db.execute(select(QuestionAnswer.question))
        questions = [row[0].strip() for row in result.all() if row[0] and len(row[0].strip()) > 5]

        if not questions:
            return {"message": "질문 데이터가 없습니다."}

        # 2. 강의 주제 키워드 설정
        lecture_keywords = ["다형성", "오버라이딩", "오버로딩", "상속", "객체지향", "OOP", "Java"]

        # 3. 강의 관련 질문 + 길이 짧은 질문만 필터링
        filtered_questions = [
            q for q in set(questions)  # 중복 제거
            if any(keyword.lower() in q.lower() for keyword in lecture_keywords) and len(q) <= 100
        ]

        if not filtered_questions:
            return {"message": "강의 주제와 관련된 질문이 없습니다."}

        # 4. 최종 10개까지만 사용
        final_questions = filtered_questions[:10]

        # 5. 포맷팅된 프롬프트 생성
        formatted_questions = "\n".join(f"- {q}" for q in final_questions)

        prompt = f"""
        다음은 학생들이 최근에 남긴 질문입니다:

        {formatted_questions}

        ✅ 강의 주제(객체지향 프로그래밍, 다형성, 상속, 오버라이딩, 오버로딩 등)과 관련된 질문만 요약해 주세요.
        ✅ 강의와 무관한 잡담, 수업 범위 외 질문은 무시하세요.
        ✅ 학생들이 헷갈려하는 부분과 추가 설명이 필요한 부분 중심으로 요약해 주세요.

        답변은 한글로 작성해 주세요.
        """

        # 6. GPT 호출
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",  # 필요시 gpt-4o로 변경 가능
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        summary = response.choices[0].message.content.strip()

        return {
            "most_common_questions": final_questions,  # 상위 질문들도 같이 반환
            "summary_for_professor": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))