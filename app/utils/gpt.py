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
                    """
                    당신은 JAVA 강의 내용을 요약하는 AI입니다.\n
                    - 주요 개념 중 2~3개만 선택하여 요약하세요.\n
                    - 각 개념은 '### 주제명' 형식으로 제목을 붙이세요.\n
                    - 각 주제 아래에는 '-' 기호로 요점을 3~5줄 나열하세요.\n
                    - 각 문장은 '핵심 내용:' 없이 요점 문장으로 바로 시작하세요.\n
                    - JAVA 용어, 예시, 클래스 구조, 흐름도(→) 등을 포함하면 좋습니다.\n
                    - 학습자가 복습하기 쉽게 간결하고 일관성 있게 작성하세요.
                    """
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()