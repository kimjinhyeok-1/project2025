from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import time

from app.services.stt import convert_webm_to_wav, transcribe_with_whisper
from app.services.gpt import generate_expected_questions

router = APIRouter()

UPLOAD_DIR = "temp/audio_chunks"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_audio_chunk")
async def upload_audio_chunk(file: UploadFile = File(...)):
    try:
        # 1. 저장
        filename = f"chunk_{int(time.time())}.webm"
        save_path = os.path.join(UPLOAD_DIR, filename)
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)
        print(f"✅ 음성 chunk 저장 완료: {save_path}")

        # 2. 변환
        wav_path = convert_webm_to_wav(save_path)
        print(f"🔁 변환된 WAV 경로: {wav_path}")

        # 3. STT
        transcript = transcribe_with_whisper(wav_path)
        print(f"📝 변환된 텍스트: '{transcript}'")

        # 4. GPT 예상 질문
        questions = generate_expected_questions(transcript)
        print(f"❓ 예상 질문 리스트: {questions}")

        return {
            "message": "Chunk received",
            "filename": filename,
            "transcript": transcript,
            "questions": questions
        }

    except Exception as e:
        print("❌ 서버 에러:", str(e))
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
