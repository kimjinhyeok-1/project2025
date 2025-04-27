from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, QuestionAnswer
from app.services.assistant import ask_assistant
from app.auth import get_current_user  # 현재 로그인한 사용자 가져오기
import os
import httpx

router = APIRouter()
API_KEY = os.getenv("OPENAI_API_KEY")

async def create_thread():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.openai.com/v1/threads", headers=headers)
        res.raise_for_status()  # 오류 방지용 추가
        return res.json()["id"]

@router.post("/ask_assistant")
async def ask_question(
    question: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = current_user  # 바로 현재 로그인한 사용자 사용

    # 1. 스레드 없으면 새로 생성
    if not user.assistant_thread_id:
        thread_id = await create_thread()
        user.assistant_thread_id = thread_id
        await db.commit()
    else:
        thread_id = user.assistant_thread_id

    # 2. Assistant에게 질문
    from app.config import OPENAI_ASSISTANT_ID
    answer = await ask_assistant(question, thread_id, OPENAI_ASSISTANT_ID)

    # 3. 질문과 답변 DB 저장
    chat = QuestionAnswer(user_id=user.id, question=question, answer=answer)
    db.add(chat)
    await db.commit()

    return {"answer": answer}
