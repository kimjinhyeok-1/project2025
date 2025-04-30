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

# 🔹 OpenAI Thread가 없을 경우 새로 생성
async def create_thread():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.openai.com/v1/threads", headers=headers)
        res.raise_for_status()
        thread_data = res.json()
        print(f"🧵 새 Thread 생성됨: {thread_data}")
        return thread_data["id"]

# 🔹 질문 요청 라우터
@router.post("/ask_assistant")
async def ask_question(
    question: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = current_user

    # 1. 스레드가 없으면 새로 생성
    if not user.assistant_thread_id:
        thread_id = await create_thread()
        user.assistant_thread_id = thread_id
        await db.commit()
    else:
        thread_id = user.assistant_thread_id

    # 2. Assistant 호출
    from app.config import OPENAI_ASSISTANT_ID
    answer = await ask_assistant(question, thread_id, OPENAI_ASSISTANT_ID)

    # 3. DB에 기록
    chat = QuestionAnswer(user_id=user.id, question=question, answer=answer)
    db.add(chat)
    await db.commit()

    return {"answer": answer}
