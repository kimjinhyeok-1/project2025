from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os, time
from app.services.stt import convert_webm_to_wav, transcribe_with_whisper
from app.services.gpt import generate_expected_questions

router = APIRouter()
UPLOAD_DIR = "temp/audio_chunks"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ OPTIONS 및 GET 허용
@router.options("/upload_audio_chunk")
@router.get("/upload_audio_chunk")
async def dummy_chunk_route():
    return JSONResponse(content={"message": "This endpoint only accepts POST requests."})

# ✅ POST - 녹음 업로드 처리
@router.post("/upload_audio_chunk")
async def upload_audio_chunk(file: UploadFile = File(...)):
    filename = f"chunk_{int(time.time())}.webm"
    save_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(save_path, "wb") as f:
            f.write(await file.read())

        print(f"✅ 음성 chunk 저장 완료: {save_path}")
        wav_path = convert_webm_to_wav(save_path)
        print(f"🔁 변환된 WAV 경로: {wav_path}")

        transcript = transcribe_with_whisper(wav_path)
        print(f"📝 변환된 텍스트: {transcript}")

        questions = generate_expected_questions(transcript)
        print(f"❓ 예상 질문 리스트: {questions}")

        return {
            "message": "Chunk received",
            "filename": filename,
            "transcript": transcript,
            "questions": questions,
        }

    except Exception as e:
        print("❌ 오류 발생:", str(e))
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

    finally:
        # ✅ 녹음 파일 삭제로 메모리 관리
        if os.path.exists(save_path):
            os.remove(save_path)
        if os.path.exists(save_path.replace(".webm", ".wav")):
            os.remove(save_path.replace(".webm", ".wav"))
