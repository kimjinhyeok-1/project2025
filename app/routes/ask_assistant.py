from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, QuestionAnswer
from app.services.assistant import ask_assistant
from app.auth import get_current_user
from app.config import OPENAI_ASSISTANT_ID

router = APIRouter()

# ✅ 지속 대화 기반 질문 처리 라우터
@router.post("/ask_assistant")
async def ask_question(
    question: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = current_user

    # ✅ 지속 대화용 ask_assistant 호출 (DB + 요약 포함)
    answer = await ask_assistant(question, db, user, OPENAI_ASSISTANT_ID)

    # ✅ 질문-응답 기록 (요약은 별도 ThreadMessage로 관리되므로 최소 기록만 유지)
    chat = QuestionAnswer(user_id=user.id, question=question, answer=answer)
    db.add(chat)
    await db.commit()

    return {"answer": answer}