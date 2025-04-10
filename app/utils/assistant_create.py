import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

async def create_assistant():
    url = "https://api.openai.com/v1/assistants"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {
        "name": "AI 교수님",
        "instructions": "넌 강의자료를 바탕으로 학생 질문에 친절하고 정확하게 대답하는 튜터야.",
        "model": "gpt-4-1106-preview",
        "tools": [{"type": "file_search"}]  # ✅ 여기만 바뀌었어요
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        if res.status_code == 200:
            data = res.json()
            print("✅ Assistant 생성 완료!")
            print("Assistant ID:", data["id"])
        else:
            print("❌ 에러 발생:", res.status_code)
            print(res.text)

if __name__ == "__main__":
    asyncio.run(create_assistant())
