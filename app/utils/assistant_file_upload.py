import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# ✅ 업로드할 12개 PDF 파일 경로
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

async def upload_file(file_path):
    url = "https://api.openai.com/v1/files"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {
        "file": (file_path, open(file_path, "rb")),
        "purpose": (None, "assistants")
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, files=files)
        if res.status_code == 200:
            file_id = res.json()["id"]
            print(f"✅ 업로드 완료: {file_path} → {file_id}")
            return file_id
        else:
            print(f"❌ 업로드 실패: {file_path}")
            print(res.text)
            return None

async def attach_files_to_assistant(file_ids):
    url = f"https://api.openai.com/v1/assistants/{ASSISTANT_ID}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    json_data = {"file_ids": file_ids}

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=json_data)
        if res.status_code == 200:
            print("✅ Assistant에 파일 연결 완료")
        else:
            print("❌ 파일 연결 실패")
            print(res.text)

async def main():
    file_ids = []
    for path in PDF_PATHS:
        file_id = await upload_file(path)
        if file_id:
            file_ids.append(file_id)
    if file_ids:
        await attach_files_to_assistant(file_ids)

if __name__ == "__main__":
    asyncio.run(main())
