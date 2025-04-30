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

# 🔧 1. Thread 생성
async def create_thread():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.openai.com/v1/threads", headers=headers)
        res.raise_for_status()
        return res.json()["id"]

# 🔧 2. Thread 유효성 확인
async def is_thread_valid(thread_id: str) -> bool:
    url = f"https://api.openai.com/v1/threads/{thread_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, headers=headers)
            return res.status_code == 200
        except httpx.HTTPStatusError:
            return False

# 🔧 3. 메시지 전송
async def post_message(thread_id: str, question: str):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    data = {
        "role": "user",
        "content": question
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=data)
        res.raise_for_status()

# 🔧 4. Assistant 실행
async def run_assistant(thread_id: str, assistant_id: str):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {
        "assistant_id": assistant_id
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        res.raise_for_status()
        return res.json()["id"]

# 🔧 5. Run 완료 대기
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

# 🔧 6. 답변 가져오기
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

# 🔧 7. 파일 검색 여부 판단 (사용 중일 경우)
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

#@router.post("/ask_assistant")
async def ask_question(
    question: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.config import OPENAI_ASSISTANT_ID

    user = current_user
    thread_id = user.assistant_thread_id

    # ✅ 1. thread 유효성 확인 (없거나 삭제된 경우 새로 생성)
    if not thread_id or not await is_thread_valid(thread_id):
        thread_id = await create_thread()
        user.assistant_thread_id = thread_id
        await db.commit()

    try:
        # ✅ 2. 메시지를 먼저 thread에 추가
        await post_message(thread_id, question)

        # ✅ 3. 메시지 추가 후에 run 실행
        run_id = await run_assistant(thread_id, OPENAI_ASSISTANT_ID)

        # ✅ 4. run 완료 대기
        run_status = await wait_for_run_completion(thread_id, run_id)
        searched = was_file_search_successful(run_status)

        # ✅ 5. 답변 추출
        if not searched:
            answer = "강의자료에 해당 내용이 없습니다."
        else:
            answer = await fetch_answer(thread_id)

    except Exception as e:
        # ✅ 6. 예외 발생 시 기본 응답 반환
        answer = f"오류가 발생했습니다: {str(e)}"
        searched = False

    # ✅ 7. DB 저장
    chat = QuestionAnswer(user_id=user.id, question=question, answer=answer)
    db.add(chat)
    await db.commit()

    return {"answer": answer, "searched": searched}

