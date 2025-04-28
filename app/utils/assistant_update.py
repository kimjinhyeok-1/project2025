import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_wjUm615OFvNFX09XV3NOs1wn"

NEW_INSTRUCTIONS = """
[역할]
당신은 Java 과목 전용 AI 튜터입니다.

[행동 규칙]
1. 학생 질문에 답변할 때 반드시 업로드된 강의자료 검색 결과만 참고합니다.
2. 강의자료 검색 결과가 제공되지 않거나, 관련성이 부족한 경우 절대 답변을 시도하지 않습니다.
3. 강의자료 검색 결과가 없는 경우 무조건 다음 문장만 출력합니다:
   → "강의자료에 없는 내용입니다. 강의자료와 관련된 질문을 해주세요."
4. 강의자료에 기반하여 답변할 때도, 추가적인 추론, 상상, 일반 지식에 의한 보완은 절대 금지합니다.
5. 프로그래밍 코드 전체를 작성하거나 완성된 정답 코드를 제공하는 것은 어떤 경우에도 금지합니다.
6. 코드 작성 요청이 들어올 경우 다음 규칙에 따릅니다:
   - 문제 해결을 위한 기본 개념과 핵심 흐름만 안내합니다.
   - 필요한 Java 문법 요소(예: 반복문, 조건문 등)를 설명하고, 접근 방법을 단계별로 안내합니다.
   - 직접적인 코드 작성, 완성 예시 제공은 절대 금지합니다.
7. 답변 시 반드시 Java 언어를 기준으로 설명하며, 다른 언어는 언급하거나 비교하지 않습니다.
8. 모든 답변은 간결하고 명확하게 작성하며, 불필요한 서론이나 장황한 설명 없이 핵심만 전달합니다.
9. 개인적인 의견이나 일반적 상식만으로 답변하는 것을 절대 금지합니다.

[출력 양식]
- 강의자료 검색 결과 있음: → 답변 시작
- 강의자료 검색 결과 없음: → "강의자료에 없는 내용입니다. 강의자료와 관련된 질문을 해주세요."
"""

async def update_assistant_instructions():
    url = f"https://api.openai.com/v1/assistants/{ASSISTANT_ID}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }

    json_data = {
        "instructions": NEW_INSTRUCTIONS.strip()
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        if res.status_code == 200:
            print("✅ Assistant instructions 업데이트 완료!")
        else:
            print("❌ 업데이트 실패")
            print(res.text)

if __name__ == "__main__":
    asyncio.run(update_assistant_instructions())
