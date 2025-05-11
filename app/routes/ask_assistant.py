# app/api/assistant_router.py
from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, QuestionAnswer
from app.services.assistant import ask_assistant
from app.auth import get_current_user
from app.config import OPENAI_ASSISTANT_ID

router = APIRouter()

@router.post("/ask_assistant")
async def ask_question(
    question: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 서비스 함수 호출 시에 DB나 User 의존성 제거
    answer = await ask_assistant(question, OPENAI_ASSISTANT_ID)

    # 결과 저장은 별도 Q&A 테이블에만 기록
    chat = QuestionAnswer(
        user_id=current_user.id,
        question=question,
        answer=answer
    )
    db.add(chat)
    await db.commit()

    return {"answer": answer}
