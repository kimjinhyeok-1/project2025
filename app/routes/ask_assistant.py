from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, QuestionAnswer
from app.auth import get_current_user
import os
import httpx
import asyncio

router = APIRouter()
API_KEY = os.getenv("OPENAI_API_KEY")

# 🧠 Thread 생성 함수
async def create_thread():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.openai.com/v1/threads", headers=headers)
        res.raise_for_status()
        return res.json()["id"]

# 🧠 Assistant Run 실행 함수
async def run_assistant(thread_id: str, assistant_id: str):
    url = "https://api.openai.com/v1/runs"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {
        "assistant_id": assistant_id,
        "thread_id": thread_id
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        res.raise_for_status()
        return res.json()["id"]

# 🧠 Run 완료 대기 함수
async def wait_for_run_completion(thread_id: str, run_id: str):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    async with httpx.AsyncClient() as client:
        while True:
            res = await client.get(url, headers=headers)
            res.raise_for_status()
            data = res.json()
            if data["status"] == "completed":
                return data
            await asyncio.sleep(1)

# 🧠 답변 가져오기 함수
async def fetch_answer(thread_id: str):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        messages = res.json()["data"]

    for message in reversed(messages):
        if message["role"] == "assistant":
            return message["content"][0]["text"]["value"]

# 🧠 file_search 성공 여부 검사 함수
def was_file_search_successful(run_status: dict) -> bool:
    tool_calls = run_status.get("required_action", {}).get("submit_tool_outputs", {}).get("tool_calls", [])
    if not tool_calls:
        return False

    for tool_call in tool_calls:
        function = tool_call.get("function", {})
        arguments = function.get("arguments", "")
        if '"query":' in arguments and arguments.strip() != "":
            return True

    return False

# 🎯 최종 ask_assistant API
@router.post("/ask_assistant")
async def ask_question(
    question: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = current_user

    # 1. 스레드 없으면 새로 생성
    if not user.assistant_thread_id:
        thread_id = await create_thread()
        user.assistant_thread_id = thread_id
        await db.commit()
    else:
        thread_id = user.assistant_thread_id

    # 2. 사용자 질문 메시지 전송
    url_post_message = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    message_data = {
        "role": "user",
        "content": question
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url_post_message, headers=headers, json=message_data)
        res.raise_for_status()

    # 3. Assistant 실행
    from app.config import OPENAI_ASSISTANT_ID
    run_id = await run_assistant(thread_id, OPENAI_ASSISTANT_ID)

    # 4. Run 완료 대기
    run_status = await wait_for_run_completion(thread_id, run_id)

    # 5. file_search 성공 여부 판단
    if not was_file_search_successful(run_status):
        answer = "강의자료에 해당 내용이 없습니다."
        # 질문과 답변 DB 저장
        chat = QuestionAnswer(user_id=user.id, question=question, answer=answer)
        db.add(chat)
        await db.commit()
        return {"answer": answer}

    # 6. file_search 성공 시 답변 가져오기
    answer = await fetch_answer(thread_id)

    # 7. 질문과 답변 DB 저장
    chat = QuestionAnswer(user_id=user.id, question=question, answer=answer)
    db.add(chat)
    await db.commit()

    return {"answer": answer}
