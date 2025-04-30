import os
import httpx
import asyncio

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def ask_assistant(question: str, assistant_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # ✅ 1. 질문마다 새로운 Thread 생성 (비용 최적화)
        thread_res = await client.post("https://api.openai.com/v1/threads", headers=headers)
        thread_res.raise_for_status()
        thread_id = thread_res.json()["id"]

        # ✅ 2. 사용자 질문 메시지 추가
        await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers,
            json={"role": "user", "content": question}
        )

        # ✅ 3. Run 생성
        payload = {
            "assistant_id": assistant_id,
            "instructions": (
                "You are a Java course AI tutor. You must only answer questions based on the uploaded lecture material using the File Search tool. "
                "Do not use general knowledge or inference.\n\n"
                "- If the answer is not in the lecture files, reply with:\n"
                "→ \"강의자료에 없는 내용입니다. 강의자료와 관련된 질문을 해주세요.\"\n"
                "- Never write or generate complete code. Only explain concepts, syntax, and approach step-by-step.\n"
                "- Only use Java. Do not mention Python, Kotlin, or any other languages."
            )
        }
        run_res = await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=headers,
            json=payload
        )
        run_res.raise_for_status()
        run_id = run_res.json()["id"]

        # ✅ 4. Run 상태 polling
        status = "queued"
        for _ in range(20):
            await asyncio.sleep(1)
            poll_res = await client.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers=headers
            )
            status = poll_res.json().get("status", "unknown")
            if status == "completed":
                break
        if status != "completed":
            raise RuntimeError(f"❌ Run 실패 또는 시간 초과")

        # ✅ 5. Assistant 메시지 추출
        msg_res = await client.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers
        )
        messages = msg_res.json().get("data", [])
        assistant_msg = next((m for m in messages if m["role"] == "assistant"), None)
        if not assistant_msg:
            raise RuntimeError("🛑 Assistant 메시지를 찾을 수 없습니다.")

        return assistant_msg["content"][0]["text"]["value"]
