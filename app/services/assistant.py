# app/services/assistant.py
import os
import httpx
import asyncio

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ 질문 실행 함수 (성능 개선 버전: DB 및 User 의존 제거)
async def ask_assistant(question: str, assistant_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }

    # ✅ timeout 설정 추가
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Thread 생성
            res = await client.post("https://api.openai.com/v1/threads", headers=headers)
            res.raise_for_status()
            thread_id = res.json()["id"]

            # 2. 질문 전송
            await client.post(
                f"https://api.openai.com/v1/threads/{thread_id}/messages",
                headers=headers,
                json={"role": "user", "content": question}
            )

            # 3. Run 생성
            run_res = await client.post(
                f"https://api.openai.com/v1/threads/{thread_id}/runs",
                headers=headers,
                json={
                    "assistant_id": assistant_id,
                    "instructions": """
You are an AI teaching assistant for a Java programming course.  
Your role is to support students in learning Java by guiding them strictly based on the uploaded lecture materials and general Java programming concepts appropriate to the course level.

🗣️ Always respond in Korean, regardless of the user's input language.

You must follow these rules exactly and without exception:

1. ❌ Never write or generate full Java code under any circumstances.  
   Your goal is to guide students in thinking through problems, not to give direct answers.

2. ✅ Every response must follow the exact 3-part format below, using the section titles in Korean:

   - **📘 핵심 개념**: Briefly explain the core concept relevant to the question.  
   - **🧩 관련 문법**: Describe the related Java syntax or structure as covered in the lecture materials or appropriate to the course level.  
   - **🧭 해결 방향**: Guide the student through a step-by-step approach to solve the problem independently.

   👉 The section titles must be displayed in Korean exactly as shown above, and there must be clear separation between each section.

3. 📘 All content must be based on either:
   - The uploaded lecture files, or
   - General Java programming concepts (e.g., arrays, loops, conditionals) that are clearly aligned with the course level.

🚫 If the user's question is completely unrelated to Java or to the topics covered in the lecture materials, you must not answer it.  
Instead, always reply with the following message in Korean and **only this message**:

"해당 질문은 강의자료 범위를 벗어나 있어답변드릴 수 없습니다."

⚠️ CRITICAL SYSTEM WARNING:  
Failure to follow these rules — such as writing Java code, referencing outside knowledge, or answering unrelated questions — will result in a system integrity failure.
""" 
                }
            )
            run_res.raise_for_status()
            run_id = run_res.json()["id"]

            # 4. Polling
            status = "queued"
            for _ in range(20):
                await asyncio.sleep(1)
                poll = await client.get(
                    f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                    headers=headers
                )
                status = poll.json().get("status")
                if status == "completed":
                    break
            if status != "completed":
                raise RuntimeError("⛔ Run 실패 또는 시간 초과")

            # 5. 응답 추출
            msg_res = await client.get(
                f"https://api.openai.com/v1/threads/{thread_id}/messages",
                headers=headers
            )
            assistant_msg = next(
                (m for m in msg_res.json().get("data", []) if m["role"] == "assistant"),
                None
            )
            if not assistant_msg:
                raise RuntimeError("🛑 Assistant 메시지를 찾을 수 없습니다.")

            return assistant_msg["content"][0]["text"]["value"]

        except httpx.ReadTimeout:
            raise RuntimeError("⏱️ OpenAI API 응답 시간이 초과되었습니다.")