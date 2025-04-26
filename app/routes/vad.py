from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os, time
from app.services.stt import convert_webm_to_wav, transcribe_with_whisper
from app.services.gpt import generate_expected_questions

router = APIRouter()
UPLOAD_DIR = "temp/audio_chunks"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 👉 OPTIONS 및 GET 허용 (CORS 프리플라이트 요청 대응)
@router.options("/upload_audio_chunk")
@router.get("/upload_audio_chunk")
async def dummy_chunk_route():
    return JSONResponse(content={"message": "This endpoint only accepts POST requests."})

# 👉 실제 업로드 처리
@router.post("/upload_audio_chunk")
async def upload_audio_chunk(file: UploadFile = File(...)):
    try:
        # 파일 저장
        filename = f"chunk_{int(time.time())}.webm"
        save_path = os.path.join(UPLOAD_DIR, filename)

        content = await file.read()

        # 🔥 파일 비었는지 체크
        if not content or len(content) < 100:
            raise HTTPException(status_code=400, detail="업로드된 파일이 비어있거나 너무 작습니다.")

        with open(save_path, "wb") as f:
            f.write(content)

        print(f"✅ 음성 chunk 저장 완료: {save_path}")

        # 변환
        try:
            wav_path = convert_webm_to_wav(save_path)
            print(f"🔁 변환된 WAV 경로: {wav_path}")
        except Exception as e:
            print("❌ ffmpeg 변환 실패:", e)
            os.remove(save_path)  # 🔥 실패한 webm 파일 삭제
            raise HTTPException(status_code=500, detail="ffmpeg 변환 실패: 파일이 손상되었거나 포맷이 잘못되었습니다.")

        # STT
        transcript = transcribe_with_whisper(wav_path)
        print(f"📝 변환된 텍스트: {transcript}")

        # GPT 예상 질문
        questions = generate_expected_questions(transcript)
        print(f"❓ 예상 질문 리스트: {questions}")

        return {
            "message": "Chunk received",
            "filename": filename,
            "transcript": transcript,
            "questions": questions
        }

    except HTTPException as he:
        raise he  # 명시적으로 던진 HTTPException은 그대로
    except Exception as e:
        print("❌ 처리 중 예상치 못한 오류:", str(e))
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
