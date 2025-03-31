from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Recording, Lecture
from app.utils.gpt import summarize_text_with_gpt
import shutil
import os
import requests
import json
import time

router = APIRouter()

UPLOAD_DIR = "uploads"
DAGLO_API_KEY = "5eF1fuwJyKRaxgQJgUwh34zP"
DAGLO_UPLOAD_URL = "https://apis.daglo.ai/stt/v1/async/transcripts"
DAGLO_RESULT_URL = "https://apis.daglo.ai/stt/v1/async/transcripts/"

print("🔑 DAGLO KEY:", DAGLO_API_KEY)


@router.post("/upload_daglo")
async def upload_recording(
    lecture_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    print("📥 [1] 파일 업로드 요청 수신")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        print("📁 업로드 폴더 생성됨:", UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print("✅ [2] 파일 저장 완료:", file_path)

    # 🔁 Lecture 확인 없이 바로 진행
    print("📚 [3] Lecture 확인 건너뜀 → ID:", lecture_id)

    try:
        print("📤 [4] Daglo STT API에 파일 업로드 시작...")
        with open(file_path, "rb") as audio_file:
            headers = {
                "Authorization": f"Bearer {DAGLO_API_KEY}",
                "Accept": "application/json"
            }
            files = {
                "file": (file.filename, audio_file, "audio/x-m4a")
            }
            data = {
                "sttConfig": json.dumps({"model": "general"})
            }

            response = requests.post(DAGLO_UPLOAD_URL, headers=headers, files=files, data=data)
            response.raise_for_status()

            rid = response.json().get("rid")
            if not rid:
                raise HTTPException(status_code=500, detail="STT 요청 실패: rid 없음")
            print("✅ [4] Daglo rid 수신:", rid)

    except Exception as e:
        print("❌ [4] STT 업로드 실패:", str(e))
        raise HTTPException(status_code=500, detail=f"STT 요청 실패: {str(e)}")

    print("⏳ [5] 5초 대기 후 STT 결과 조회 시도")
    time.sleep(5)

    try:
        result_url = DAGLO_RESULT_URL + rid
        print("📡 [5] STT 결과 요청:", result_url)
        result_response = requests.get(result_url, headers={"Authorization": f"Bearer {DAGLO_API_KEY}"}, timeout=15)
        result_response.raise_for_status()

        result_data = result_response.json()
        transcript = result_data["sttResults"][0]["transcript"] if result_data.get("sttResults") else "(STT 결과 없음)"
        print("✅ [5] STT 텍스트 추출 완료")
        print("📄 [텍스트 본문]:", transcript[:100], "...")
    except Exception as e:
        print("❌ [5] STT 결과 요청 실패:", str(e))
        raise HTTPException(status_code=500, detail=f"STT 결과 요청 실패: {str(e)}")

    try:
        print("🧠 [6] GPT 요약 요청 시작")
        summary = summarize_text_with_gpt(transcript)
        print("✅ [6] GPT 요약 완료")
        print("📝 [요약 결과]:", summary)
    except Exception as e:
        print("❌ [6] GPT 요약 실패:", str(e))
        raise HTTPException(status_code=500, detail=f"GPT 요약 실패: {str(e)}")

    print("💾 [7] DB에 녹음 저장 중")
    new_recording = Recording(
        lecture_id=lecture_id,
        file_path=file_path
    )
    db.add(new_recording)
    await db.commit()
    await db.refresh(new_recording)
    print("✅ [7] DB 저장 완료")

    print("🚀 [8] 모든 처리 완료, 응답 반환 중")
    return {
        "message": "파일 업로드 및 STT + 요약 완료",
        "lecture_id": lecture_id,
        "file_path": file_path,
        "transcription": transcript,
        "summary": summary
    }
