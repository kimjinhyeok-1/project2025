# app/utils/gpt.py

import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def summarize_text_with_gpt(text: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": (
                "당신은 강의 주요 내용을 요약하는 AI입니다.\n"
                "- 각 주제별로 '### 제목' 형식으로 나누고\n"
                "- 각 주제 내 핵심 내용을 '- 항목' 형식으로 정리하세요.\n"
                "- 가독성 좋게 요약하고, 필요한 경우 JAVA 용어를 그대로 사용하세요."
            )},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=1200
    )
    return response.choices[0].message.content.strip()