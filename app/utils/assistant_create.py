# import httpx
# import asyncio
# import os
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("OPENAI_API_KEY")

# async def create_assistant():
#     url = "https://api.openai.com/v1/assistants"
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "OpenAI-Beta": "assistants=v2",
#         "Content-Type": "application/json"
#     }
#     json_data = {
#         "name": "AI 교수님",
#         "instructions": "넌 강의자료를 바탕으로 학생 질문에 친절하고 정확하게 대답하는 튜터야.",
#         "model": "gpt-4-1106-preview",
#         "tools": [{"type": "file_search"}]  # ✅ 여기만 바뀌었어요
#     }

#     async with httpx.AsyncClient() as client:
#         res = await client.post(url, headers=headers, json=json_data)
#         if res.status_code == 200:
#             data = res.json()
#             print("✅ Assistant 생성 완료!")
#             print("Assistant ID:", data["id"])
#         else:
#             print("❌ 에러 발생:", res.status_code)
#             print(res.text)

# if __name__ == "__main__":
#     asyncio.run(create_assistant())
import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

async def create_assignment_assistant():
    url = "https://api.openai.com/v1/assistants"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {
        "name": "과제 피드백 Assistant",
        "instructions": (
                            "너는 학생이 제출한 과제를 평가하는 교육용 AI 어시스턴트야.\n"
                            "다음과 같은 기준으로 피드백을 작성해:\n"
                            "1. 과제 설명과 학생의 제출 내용을 바탕으로 평가할 것\n"
                            "2. 잘 수행된 점과 부족한 점을 구체적으로 지적할 것\n"
                            "3. 개선할 방향이나 팁을 친절하고 명확하게 제안할 것\n"
                            "4. 점수나 채점은 하지 말 것\n"
                            "피드백은 학생이 이해하기 쉬운 자연스러운 어조로 작성해."
                            ),
        "model": "gpt-4-1106-preview",
        "tools": []  # ❌ file_search 없음
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        if res.status_code == 200:
            data = res.json()
            print("✅ 과제 Assistant 생성 완료!")
            print("Assistant ID:", data["id"])
        else:
            print("❌ 에러 발생:", res.status_code)
            print(res.text)

if __name__ == "__main__":
    asyncio.run(create_assignment_assistant())
