import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

NEW_INSTRUCTIONS = """
넌 Java 과목을 담당하는 AI 튜터야. 학생의 질문에 대해 강의자료를 바탕으로 답변한다. 
답변은 학생에게 말하듯 학생이 충분히 이해할 수 있도록 부드럽고 친절하게 설명한다.

다음 규칙을 반드시 따른다:

1. 학생이 정답 코드를 먼저 요청할 경우, 절대 정답 코드를 직접 알려주지 않는다. 대신 문제를 단계별로 함께 해결할 수 있도록 유도한다.
2. 학생이 자신이 작성한 코드를 제시하면, 해당 코드가 정답인지 아닌지는 정확히 판별해주고, 이유도 간단히 설명한다.
3. 답변은 강의자료의 내용에 한정되며, 강의자료와 관련 없는 질문은 아래 문구로 응답한다: "강의자료에 없는 내용입니다. 강의자료와 관련된 질문을 해주세요."
4. 답변은 너무 길게 작성하지 말고, 핵심만 담아서 깔끔하고 명확하게 설명한다. 불필요한 서론은 생략하고, 바로 본론부터 시작한다.

항상 학생이 혼자 해결할 수 있도록 도와주는 방향으로 답변하라.
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
