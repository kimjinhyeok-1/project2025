from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, QuestionAnswer
from app.services.assistant import ask_assistant
from app.auth import get_current_user
from app.config import OPENAI_ASSISTANT_ID

router = APIRouter()

# 🔹 질문 요청 라우터
@router.post("/ask_assistant")
async def ask_question(
    question: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = current_user

    # ✅ 질문마다 새 Thread로 처리 (비용/성능 최적화)
    answer = await ask_assistant(question, OPENAI_ASSISTANT_ID)

    # ✅ DB에 질문/답변 기록
    chat = QuestionAnswer(user_id=user.id, question=question, answer=answer)
    db.add(chat)
    await db.commit()

    return {"answer": answer}
