from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.recording import Recording
from app.models.lecture import Lecture
from app.utils.gpt import summarize_text_with_gpt
import shutil
import os
import whisper

router = APIRouter()

UPLOAD_DIR = "uploads"

# Whisper 모델 로드
model = whisper.load_model("base")  # small, medium, large 가능

@router.post("/upload")
async def upload_recording(
    lecture_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print("📥 [1] 파일 업로드 요청 수신")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        print("📁 업로드 폴더 생성됨:", UPLOAD_DIR)

    # 2. 파일 저장
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print("✅ [2] 파일 저장 완료:", file_path)

    # 3. 강의 존재 여부 확인
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=400, detail="해당 강의 ID가 존재하지 않습니다.")
    print("✅ [3] 강의 ID 확인됨:", lecture_id)

    # 4. Whisper로 STT 수행
    try:
        print("🎧 [4] Whisper 모델로 STT 처리 시작...")
        result = model.transcribe(file_path)
        transcript = result["text"]
        print("✅ [4] Whisper 텍스트 추출 완료")
        print("📄 [텍스트 본문]:", transcript[:100], "...")
    except Exception as e:
        print("❌ [4] Whisper STT 실패:", str(e))
        raise HTTPException(status_code=500, detail=f"STT 처리 실패: {str(e)}")

    # 5. GPT 요약 생성
    try:
        print("🧠 [5] GPT 요약 요청 시작")
        summary = summarize_text_with_gpt(transcript)
        print("✅ [5] GPT 요약 완료")
        print("📝 [요약 결과]:", summary)
    except Exception as e:
        print("❌ [5] GPT 요약 실패:", str(e))
        raise HTTPException(status_code=500, detail=f"GPT 요약 실패: {str(e)}")

    # 6. DB 저장
    print("💾 [6] DB에 녹음 저장 중")
    new_recording = Recording(
        lecture_id=lecture_id,
        file_path=file_path
    )
    db.add(new_recording)
    db.commit()
    db.refresh(new_recording)
    print("✅ [6] DB 저장 완료")

    # 7. 응답 반환
    print("🚀 [7] 응답 반환 중")
    return {
        "message": "파일 업로드 및 STT + 요약 완료",
        "lecture_id": lecture_id,
        "file_path": file_path,
        "transcription": transcript,
        "summary": summary
    }
