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
        # 1. 사용자 메시지 추가
        await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers,
            json={"role": "user", "content": question}
        )

        # 2. Assistant 실행
        run_res = await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=headers,
            json={"assistant_id": assistant_id}
        )
        run_id = run_res.json()["id"]

        # 3. 실행 완료될 때까지 대기
        while True:
            status_res = await client.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers=headers
            )
            status = status_res.json()["status"]
            if status == "completed":
                break
            elif status in ("failed", "cancelled", "expired"):
                return f"Assistant 응답 실패: 상태={status}"
            await asyncio.sleep(1)

        # 4. assistant의 응답 메시지 가져오기
        messages_res = await client.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers
        )
        messages = messages_res.json()["data"]

        # ✅ role이 assistant인 메시지를 가장 먼저 찾기
        for message in messages:
            if message["role"] == "assistant":
                return message["content"][0]["text"]["value"]

        return "답변을 생성하지 못했습니다."
