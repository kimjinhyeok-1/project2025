from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User, QuestionAnswer
from app.services.assistant import ask_assistant
import os
import httpx

router = APIRouter()
API_KEY = os.getenv("OPENAI_API_KEY")

async def create_thread():
    headers = {"Authorization": f"Bearer {API_KEY}", "OpenAI-Beta": "assistants=v2"}
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.openai.com/v1/threads", headers=headers)
        return res.json()["id"]

@router.post("/ask_assistant")
async def ask_question(
    username: str = Form(...),
    question: str = Form(...),
    db: AsyncSession = Depends(get_async_session)
):
    # 1. 사용자 조회
    result = await db.execute(select(User).where(User.name == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 2. 스레드 없으면 생성
    if not user.assistant_thread_id:
        thread_id = await create_thread()
        user.assistant_thread_id = thread_id
        await db.commit()
    else:
        thread_id = user.assistant_thread_id

    # 3. Assistant 응답 받기
    from app.config import ASSISTANT_ID  # assistant_id는 환경변수에서 불러온다고 가정
    answer = await ask_assistant(question, thread_id, ASSISTANT_ID)

    # 4. DB 저장
    chat = QuestionAnswer(user_id=user.id, question=question, answer=answer)
    db.add(chat)
    await db.commit()

    return {"answer": answer}
