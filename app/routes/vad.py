from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os, time
from app.services.stt import transcribe_with_whisper  # ✅ Whisper API 호출
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

        if not content or len(content) < 100:
            raise HTTPException(status_code=400, detail="업로드된 파일이 비어있거나 너무 작습니다.")

        with open(save_path, "wb") as f:
            f.write(content)

        print(f"✅ 음성 chunk 저장 완료: {save_path}")

        # 🔥 OpenAI Whisper API 호출로 변환
        transcript = await transcribe_with_whisper(save_path)
        print(f"📝 변환된 텍스트: {transcript}")

        # GPT 예상 질문 생성
        questions = generate_expected_questions(transcript)
        print(f"❓ 예상 질문 리스트: {questions}")

        return {
            "message": "Chunk received",
            "filename": filename,
            "transcript": transcript,
            "questions": questions
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print("❌ 처리 중 예상치 못한 오류:", str(e))
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
