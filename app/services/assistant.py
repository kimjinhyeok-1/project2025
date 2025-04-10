import os
import httpx
import asyncio

API_KEY = os.getenv("OPENAI_API_KEY")

async def ask_assistant(question: str, thread_id: str, assistant_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # 1. 메시지 추가
        await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers,
            json={"role": "user", "content": question}
        )

        # 2. Run 실행
        run_res = await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=headers,
            json={"assistant_id": assistant_id}
        )
        run_id = run_res.json()["id"]

        # 3. 완료될 때까지 대기
        while True:
            status_res = await client.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers=headers
            )
            if status_res.json()["status"] == "completed":
                break
            await asyncio.sleep(1)

        # 4. 마지막 메시지 받아오기
        messages_res = await client.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers
        )
        messages = messages_res.json()["data"]
        answer = messages[-1]["content"][0]["text"]["value"]
        return answer
