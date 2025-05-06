import os
import httpx
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import ThreadMessage, User
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_CONTEXT_MESSAGES = 3

# ✅ 요약 함수
async def summarize_messages(messages: list[str]) -> str:
    summary_prompt = (
        "다음 Java 질문/답변 대화를 핵심 위주로 100자 이내로 요약해 주세요:\n\n"
        + "\n".join(messages)
    )

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": summary_prompt}],
                "temperature": 0.2
            }
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]

# ✅ 질문 실행 함수
async def ask_assistant(question: str, db: AsyncSession, user: User, assistant_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # 1. 사용자 thread 없으면 생성
        if not user.assistant_thread_id:
            res = await client.post("https://api.openai.com/v1/threads", headers=headers)
            res.raise_for_status()
            user.assistant_thread_id = res.json()["id"]
            await db.commit()

        thread_id = user.assistant_thread_id

        # 2. 질문 메시지 → OpenAI + DB 저장
        await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers,
            json={"role": "user", "content": question}
        )
        db.add(ThreadMessage(user_id=user.id, thread_id=thread_id, role="user", content=question))
        await db.commit()

        # 3. 메시지 개수 체크 → 요약
        result = await db.execute(
            select(ThreadMessage).where(ThreadMessage.thread_id == thread_id).order_by(ThreadMessage.created_at)
        )
        msg_list = result.scalars().all()
        if len(msg_list) >= MAX_CONTEXT_MESSAGES:
            combined = [m.content for m in msg_list]
            summary = await summarize_messages(combined)

            # 삭제 후 요약 메시지 삽입
            for m in msg_list:
                await db.delete(m)
            await db.commit()

            await client.post(
                f"https://api.openai.com/v1/threads/{thread_id}/messages",
                headers=headers,
                json={"role": "user", "content": f"[요약] {summary}"}
            )
            db.add(ThreadMessage(user_id=user.id, thread_id=thread_id, role="user", content=f"[요약] {summary}"))
            await db.commit()

        # 4. Run 생성
        payload = {
            "assistant_id": assistant_id,
            "instructions": (
"""
You are an AI teaching assistant for a Java programming course.  
Your role is to support students in learning Java by guiding them strictly based on the uploaded lecture materials and nothing else.

🗣️ Always respond in Korean, regardless of the user's input language.

You must follow these rules exactly and without exception:

1. ❌ Never write or generate full Java code under any circumstances.  
   Your goal is to guide students in thinking through problems, not to give direct answers.

2. ✅ Every response **must follow the exact 3-part format below**, using the section titles in **Korean**:

   - **📘 핵심 개념**: 질문과 관련된 핵심 개념을 간단히 설명하세요.  
   - **🧩 관련 문법**: 강의자료에서 다룬 관련 Java 문법이나 구조를 소개하세요.  
   - **🧭 해결 방향**: 학생이 스스로 해결할 수 있도록 단계별 접근 방법을 안내하세요.  

   👉 The section titles must be displayed in Korean **exactly as shown above**, and there must be clear separation between each section.

3. 📘 All content must be based **only on the uploaded lecture files**.  
   - If the exact content is not found, but the question involves a **combination of topics from the lecture**, you may respond using the relevant course concepts.  
   - You must **not** use any external programming knowledge or examples unless they are explicitly included in the uploaded files.

🚫 If the user's question is not related to Java or the uploaded lecture materials, **you must not answer it**.  
Instead, always reply with the following message in Korean and **only this message**:

"해당 질문은 강의자료 범위를 벗어나 있어 답변드릴 수 없습니다."

⚠️ CRITICAL SYSTEM WARNING:  
Failure to follow these rules — such as writing Java code, referencing outside knowledge, or answering unrelated questions — will result in a system integrity failure.
"""   
)
        }
        run_res = await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=headers,
            json=payload
        )
        run_res.raise_for_status()
        run_id = run_res.json()["id"]

        # 5. Run polling
        status = "queued"
        for _ in range(20):
            await asyncio.sleep(1)
            poll = await client.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}", headers=headers
            )
            status = poll.json().get("status")
            if status == "completed":
                break
        if status != "completed":
            raise RuntimeError("⛔ Run 실패 또는 시간 초과")

        # 6. 응답 추출 + DB 저장
        msg_res = await client.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers
        )
        assistant_msg = next(
            (m for m in msg_res.json().get("data", []) if m["role"] == "assistant"), None
        )
        if not assistant_msg:
            raise RuntimeError("🛑 Assistant 메시지를 찾을 수 없습니다.")

        answer = assistant_msg["content"][0]["text"]["value"]
        db.add(ThreadMessage(user_id=user.id, thread_id=thread_id, role="assistant", content=answer))
        await db.commit()

        return answer
