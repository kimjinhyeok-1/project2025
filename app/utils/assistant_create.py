import os
import httpx
import asyncio
from dotenv import load_dotenv

# 📄 환경변수 로드
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# 📚 업로드할 여러 PDF 파일 경로 리스트
PDF_PATHS = [
    "uploads/1장_자바시작.pdf",
    "uploads/2장_자바기본프로그래밍.pdf",
    "uploads/3장_반복문배열예외처리.pdf",
    "uploads/4장_클래스와객체.pdf",
    "uploads/5장_상속.pdf",
    "uploads/6장_메소드의 모든것.pdf",
    "uploads/8장_GUI스윙기초.pdf",
    "uploads/9장_이벤트처리.pdf",
    "uploads/10장_스윙컴포넌트활용.pdf",
    "uploads/11장_그래픽.pdf",
    "uploads/12장_스레드.pdf",
    "uploads/13장_입출력스트림.pdf",
    "uploads/14장_소켓프로그래밍.pdf"
]

# ✍ Assistant 기본 instruction
NEW_INSTRUCTIONS = """
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

# 📤 파일 업로드 함수
async def upload_file(file_path):
    url = "https://api.openai.com/v1/files"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "purpose": "assistants"
    }
    files = {
        "file": open(file_path, "rb")
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, data=data, files=files)
        if res.status_code == 200:
            file_id = res.json()["id"]
            print(f"✅ 파일 업로드 완료: {file_path} → {file_id}")
            return file_id
        else:
            print(f"❌ 파일 업로드 실패: {file_path}")
            print(res.status_code, res.text)
            return None

# 📦 Vector Store 생성 함수
async def create_vector_store(file_ids):
    url = "https://api.openai.com/v1/vector_stores"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {
        "name": "Lecture Vector Store",
        "file_ids": file_ids
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        if res.status_code == 200:
            vector_store_id = res.json()["id"]
            print(f"✅ Vector Store 생성 완료: {vector_store_id}")
            return vector_store_id
        else:
            print("❌ Vector Store 생성 실패")
            print(res.status_code, res.text)
            return None

# 🧠 Assistant 생성 함수
async def create_assistant(vector_store_id):
    url = "https://api.openai.com/v1/assistants"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {
        "name": "AI 교수님",
        "instructions": NEW_INSTRUCTIONS.strip(),
        "model": "gpt-4o",
        "tools": [
            {
                "type": "file_search",
                "file_search": {
                    "max_num_results": 2
                }
            }
        ],
        "tool_resources": {
            "file_search": {
                "vector_store_ids": [vector_store_id]
            }
        }
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        if res.status_code == 200:
            assistant_id = res.json()["id"]
            print(f"✅ Assistant 생성 완료: {assistant_id}")
        else:
            print("❌ Assistant 생성 실패")
            print(res.status_code, res.text)

# 🎯 전체 실행 함수
async def main():
    # 1️⃣ 여러 파일 업로드
    file_ids = []
    for path in PDF_PATHS:
        file_id = await upload_file(path)
        if file_id:
            file_ids.append(file_id)

    if not file_ids:
        print("❌ 파일 업로드 실패: 생성 중단")
        return

    # 2️⃣ Vector Store 생성
    vector_store_id = await create_vector_store(file_ids)
    if not vector_store_id:
        print("❌ Vector Store 생성 실패: 생성 중단")
        return

    # 3️⃣ Assistant 생성
    await create_assistant(vector_store_id)

# 프로그램 시작
if __name__ == "__main__":
    asyncio.run(main())
