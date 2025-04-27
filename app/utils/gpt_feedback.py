# app/utils/gpt_feedback.py

import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ GPT 피드백 생성
async def generate_assignment_feedback(description: str, content: str) -> str:
    prompt = f"""과제 설명:
{description}

학생 제출 내용:
{content}

이 제출물에 대해 평가하고, 잘한 점과 개선할 점을 포함한 구체적인 피드백을 작성해주세요."""
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()


# ✅ Assistant Thread 생성 + 시스템 메시지 저장
async def create_feedback_thread(feedback: str) -> str:
    assistant_id = "your-assistant-id"  # ← 실제 Assistant ID로 교체
    thread = await client.beta.threads.create()
    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="system",
        content=f"GPT가 과제를 평가한 피드백은 다음과 같습니다:\n\n{feedback}"
    )
    return thread.id
