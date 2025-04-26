from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os, time, uuid, shutil
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
        # 파일 저장 (🔥 개선: 시간+UUID 조합으로 파일명 중복 방지)
        filename = f"chunk_{int(time.time())}_{uuid.uuid4().hex[:6]}.webm"
        save_path = os.path.join(UPLOAD_DIR, filename)

        if not file:
            raise HTTPException(status_code=400, detail="파일이 업로드되지 않았습니다.")

        # 🔥 파일 스트림 저장 (대용량 대비)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"✅ 음성 chunk 저장 완료: {save_path}")

        # 변환
        try:
            wav_path = convert_webm_to_wav(save_path)
            print(f"🔁 변환된 WAV 경로: {wav_path}")
        except Exception as e:
            print("❌ ffmpeg 변환 실패:", e)
            os.remove(save_path)
            raise HTTPException(status_code=500, detail="ffmpeg 변환 실패: 파일이 손상되었거나 포맷이 잘못되었습니다.")

        # STT
        transcript = transcribe_with_whisper(wav_path)
        print(f"📝 변환된 텍스트: {transcript}")

        # 🔥 STT 결과 체크
        if not transcript or transcript.strip() == "":
            raise HTTPException(status_code=500, detail="STT 변환 실패: 텍스트가 비어있습니다.")

        # GPT 예상 질문
        questions = generate_expected_questions(transcript)
        print(f"❓ 예상 질문 리스트: {questions}")

        # 🔥 질문 리스트 체크 (혹시라도 빈 리스트일 때)
        if not questions:
            questions = ["질문 생성을 실패했습니다."]

        return {
            "message": "Chunk received",
            "filename": filename,
            "transcript": transcript,
            "questions": questions
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print("❌ 처리 중 예상치 못한 오류:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")