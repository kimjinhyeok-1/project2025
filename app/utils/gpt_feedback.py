# app/utils/gpt_feedback.py

import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ GPT 피드백 생성
async def generate_assignment_feedback(description: str, content: str) -> str:
    prompt = f"""당신은 대학 수준의 코딩 과제를 평가하는 프로그래밍 교수입니다.

[과제 설명]
{description}

[학생 제출 코드]
{content}

이 코드를 읽고 다음에 따라 평가해주세요:
1. 코드의 논리적 오류 또는 문법 오류 여부
2. 요구된 기능을 충족하는지 여부
3. 잘 구현된 점 (예: 구조, 가독성, 효율성 등)
4. 개선할 점 (예: 누락된 부분, 코드 스타일 등)

[출력 형식]
- 총평:
- 잘한 점:
- 개선할 점:
- 제안 사항:
"""
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()