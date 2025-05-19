import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def summarize_text_with_gpt(text: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 강의 주요 내용을 요약하는 AI입니다.\n"
                    "- 총 2~3개의 주제만 선택하여 요약하세요.\n"
                    "- 각 주제는 '### 주제명' 형식으로 시작하세요.\n"
                    "- 각 주제에는 '- 핵심 내용' 형식으로 3~5줄로 요약하세요.\n"
                    "- JAVA 용어나 흐름도(→)를 포함하면 좋습니다."
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()