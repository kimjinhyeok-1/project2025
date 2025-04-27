# import os
# import httpx
# import asyncio
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("OPENAI_API_KEY")

# NEW_INSTRUCTIONS = """
# 넌 Java 과목을 담당하는 AI 튜터야. 학생의 질문에 대해 반드시 업로드된 강의자료를 검색해서 답변해야 한다.
# 검색된 강의자료 내용에 근거하지 않은 답변은 절대 하지 않는다.

# 다음 규칙을 반드시 따른다:

# 1. 학생의 질문에 답변할 때, 강의자료 파일 검색 결과를 반드시 참고하여 답변한다.
# 2. 파일 검색 결과가 없거나 관련 정보가 없으면, 아래 문구로 답변한다: "강의자료에 없는 내용입니다. 강의자료와 관련된 질문을 해주세요."
# 3. 학생이 정답 코드를 먼저 요청할 경우, 절대 정답 코드를 직접 알려주지 않는다. 대신 문제를 단계별로 함께 해결할 수 있도록 유도한다.
# 4. 학생이 자신이 작성한 코드를 제시하면, 해당 코드가 정답인지 아닌지를 정확히 판별하고, 이유를 간단히 설명한다.
# 5. 답변은 학생이 충분히 이해할 수 있도록 부드럽고 친절하게 설명하되, 너무 길게 작성하지 않고 핵심만 담아서 깔끔하고 명확하게 답변한다. 불필요한 서론은 생략하고 바로 본론부터 시작한다.

# 항상 학생이 혼자 해결할 수 있도록 도와주는 방향으로 답변하라.
# """

# async def create_assistant():
#     url = "https://api.openai.com/v1/assistants"
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "OpenAI-Beta": "assistants=v2",
#         "Content-Type": "application/json"
#     }
#     json_data = {
#         "name": "AI 교수님",
#         "instructions": NEW_INSTRUCTIONS.strip(),
#         "model": "gpt-4o",
#         "tools": [
#             {
#                 "type": "file_search",
#                 "file_search": {
#                     "max_num_results": 2  # ✅ 검색 결과 수만 설정 가능
#                 }
#             }
#         ]
#     }

#     async with httpx.AsyncClient() as client:
#         res = await client.post(url, headers=headers, json=json_data)
#         if res.status_code == 200:
#             data = res.json()
#             print("✅ Assistant 생성 완료!")
#             print("Assistant ID:", data["id"])
#         else:
#             print("❌ Assistant 생성 실패")
#             print(res.status_code, res.text)

# if __name__ == "__main__":
#     asyncio.run(create_assistant())

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
#         "model": "gpt-4o",
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

import os
import httpx
import asyncio
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")  # 기존 API_KEY는 그대로 사용

# 🧠 요약용 Assistant Instructions
NEW_INSTRUCTIONS = """
🧠 당신은 학생들에게 수업 내용을 쉽고 깔끔하게 요약하는 AI입니다.

🎯 목표:
- 수업과 관련된 **핵심 개념**, **중요한 설명**, **주요 사례**만 정리합니다.
- 강의와 관련 없는 **잡담**이나 **불필요한 대화**는 요약에 포함하지 않습니다.

✨ 작성 스타일:
- 요약은 **깔끔한 문단**으로 정리합니다. (1문단당 3~5줄 이내)
- **가독성**을 위해 적절히 **이모지**(✔️, ✏️, 📝 등)와 **글머리표(•)**를 사용합니다.
- 필요하면 소제목을 사용해 내용을 정리합니다. (예: ✏️ 주요 개념, 📚 사례 소개 등)

🔥 특별 주의사항:
- 수업 주제와 관계없는 내용은 요약에서 과감히 제외합니다.
- 요약은 학생이 쉽게 이해할 수 있도록 **친절하고 부드러운 어투**로 작성합니다.
- 너무 딱딱하거나 명령조 느낌이 들지 않게 주의합니다.
"""

async def create_summary_assistant():
    url = "https://api.openai.com/v1/assistants"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {
        "name": "Lecture Summary Assistant",
        "instructions": NEW_INSTRUCTIONS.strip(),
        "model": "gpt-4o"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        if res.status_code == 200:
            data = res.json()
            assistant_id = data["id"]
            print("✅ Assistant 생성 완료!")
            print(f"Assistant ID: {assistant_id}")

            # 생성된 Assistant ID를 파일로 저장하기
            save_assistant_id(assistant_id)

        else:
            print("❌ Assistant 생성 실패")
            print(res.status_code, res.text)

def save_assistant_id(assistant_id):
    # .env 파일에 저장
    env_path = ".env"
    key_name = "LECTURE_SUMMARY_ASSISTANT_ID"  # 🧠 여기 따로 변수명 설정

    # 기존 .env 읽고 새로운 줄 추가
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # 기존에 LECTURE_SUMMARY_ASSISTANT_ID가 있으면 삭제
    lines = [line for line in lines if not line.startswith(f"{key_name}=")]

    # 새로운 Assistant ID 추가
    lines.append(f"{key_name}={assistant_id}\n")

    # 다시 저장
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ {key_name}={assistant_id} 로 .env 파일 업데이트 완료!")

if __name__ == "__main__":
    asyncio.run(create_summary_assistant())
