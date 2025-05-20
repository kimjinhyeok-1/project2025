# app/utils/gpt_feedback.py

import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ GPT 피드백 생성
async def generate_assignment_feedback(description: str, content: str) -> str:
    prompt = f"""당신은 대학 수준의 코딩 과제를 평가하는 프로그래밍 교수이며, 학생의 성장을 돕기 위한 따뜻하고 구체적인 피드백을 제공하는 것이 목표입니다.

[과제 설명]
{description}

[학생 제출 코드]
{content}

다음 기준에 따라 코드를 평가하고 피드백을 작성해주세요:

1. 코드가 과제의 요구사항을 충족하는지 확인하세요.
2. 논리적 또는 문법적 오류가 있는 경우, 학생이 이해하기 쉽게 설명해주세요.
3. 코드에서 잘 구현된 점을 구체적으로 칭찬해주세요.
4. 개선할 점은 비판보다는 '더 발전시킬 수 있는 부분'이나 '고려해볼 점'으로 표현해주세요.
5. 선택적으로 확장하거나 리팩토링할 수 있는 방향이 있다면 제안해주세요.

[출력 형식]

- 총평: 전체적인 평가와 격려를 중심으로 작성하세요.
- 잘한 점: 코드의 장점과 긍정적인 요소를 구체적으로 설명하세요.
- 더 나아갈 수 있는 부분: 코드를 더 발전시킬 수 있는 방향이나 선택적인 개선점을 제시하세요.
- 제안 사항: 추가로 학습하거나 확장할 수 있는 주제를 제안하세요. (선택 사항)

친절하고 학생 중심의 피드백을 제공해주세요.
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()