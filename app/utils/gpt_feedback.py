import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ GPT 피드백 생성
async def generate_assignment_feedback(description: str, content: str) -> str:
    prompt = f"""
당신은 대학 수준의 코딩 과제를 평가하는 친절한 프로그래밍 교수입니다. 학생의 성장을 돕기 위한 따뜻하고 구체적인 피드백을 작성해주세요.
출력은 Markdown형식으로 작성해주세요.
[과제 설명]
{description}

[학생 제출 코드]
{content}

다음 기준을 따라주세요:
1. 과제 요구사항 충족 여부
2. 논리/문법 오류 지적 (쉬운 설명 포함)
3. 잘한 점은 구체적으로 칭찬
4. 개선점은 제안 중심으로 부드럽게
5. 감점 요소는 실제 채점에서 주의해야 할 부분 위주로 정리
6. 선택적으로 리팩토링/확장 제안

[출력 형식]
- 총평: 전체적인 평가 및 격려
- 잘한 점: 긍정적 요소 구체적으로
- 감점 요소: 채점 기준상 감점될 수 있는 요소 명확히 제시
- 더 나아갈 수 있는 부분: 발전 방향 제시
- 제안 사항: 추가 학습/확장 아이디어 (선택 사항)
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.3,
        max_tokens=800,  # 과제 설명 + 코드 길이에 따라 조정 가능
    )
    return response.choices[0].message.content.strip()
