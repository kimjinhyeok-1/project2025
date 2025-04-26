import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

NEW_INSTRUCTIONS = """
넌 Java 과목을 담당하는 AI 튜터야. 학생의 질문에 대해 반드시 업로드된 강의자료를 검색해서 답변해야 한다.
검색된 강의자료 내용에 근거하지 않은 답변은 절대 하지 않는다.

다음 규칙을 반드시 따른다:

1. 학생의 질문에 답변할 때, 강의자료 파일 검색 결과를 반드시 참고하여 답변한다.
2. 파일 검색 결과가 없거나 관련 정보가 없으면, 아래 문구로 답변한다: "강의자료에 없는 내용입니다. 강의자료와 관련된 질문을 해주세요."
3. 학생이 정답 코드를 먼저 요청할 경우, 절대 정답 코드를 직접 알려주지 않는다. 대신 문제를 단계별로 함께 해결할 수 있도록 유도한다.
4. 학생이 자신이 작성한 코드를 제시하면, 해당 코드가 정답인지 아닌지를 정확히 판별하고, 이유를 간단히 설명한다.
5. 답변은 학생이 충분히 이해할 수 있도록 부드럽고 친절하게 설명하되, 너무 길게 작성하지 않고 핵심만 담아서 깔끔하고 명확하게 답변한다. 불필요한 서론은 생략하고 바로 본론부터 시작한다.

항상 학생이 혼자 해결할 수 있도록 도와주는 방향으로 답변하라.
"""

async def create_assistant():
    url = "https://api.openai.com/v1/assistants"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {
        "name": "AI 교수님",
        "instructions": NEW_INSTRUCTIONS.strip(),
        "model": "gpt-4-1106-preview",
        "tools": [
            {
                "type": "file_search",
                "file_search": {
                    "max_num_results": 2  # ✅ 검색 결과 수만 설정 가능
                }
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        if res.status_code == 200:
            data = res.json()
            print("✅ Assistant 생성 완료!")
            print("Assistant ID:", data["id"])
        else:
            print("❌ Assistant 생성 실패")
            print(res.status_code, res.text)

if __name__ == "__main__":
    asyncio.run(create_assistant())

# import httpx
# import asyncio
# import os
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("OPENAI_API_KEY")

# async def create_assignment_assistant():
#     url = "https://api.openai.com/v1/assistants"
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "OpenAI-Beta": "assistants=v2",
#         "Content-Type": "application/json"
#     }
#     json_data = {
#         "name": "과제 피드백 Assistant",
#         "instructions": (
#                             "너는 학생이 제출한 과제를 평가하는 교육용 AI 어시스턴트야.\n"
#                             "다음과 같은 기준으로 피드백을 작성해:\n"
#                             "1. 과제 설명과 학생의 제출 내용을 바탕으로 평가할 것\n"
#                             "2. 잘 수행된 점과 부족한 점을 구체적으로 지적할 것\n"
#                             "3. 개선할 방향이나 팁을 친절하고 명확하게 제안할 것\n"
#                             "4. 점수나 채점은 하지 말 것\n"
#                             "피드백은 학생이 이해하기 쉬운 자연스러운 어조로 작성해."
#                             ),
#         "model": "gpt-4-1106-preview",
#         "tools": []  # ❌ file_search 없음
#     }

#     async with httpx.AsyncClient() as client:
#         res = await client.post(url, headers=headers, json=json_data)
#         if res.status_code == 200:
#             data = res.json()
#             print("✅ 과제 Assistant 생성 완료!")
#             print("Assistant ID:", data["id"])
#         else:
#             print("❌ 에러 발생:", res.status_code)
#             print(res.text)

# if __name__ == "__main__":
#     asyncio.run(create_assignment_assistant())
