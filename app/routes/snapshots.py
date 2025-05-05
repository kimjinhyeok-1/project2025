from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Snapshot
import os
import base64
import uuid
from datetime import datetime

router = APIRouter()

# 저장 경로 설정
IMAGE_DIR = "tmp/snapshots"
FULL_IMAGE_DIR = os.path.join("static", IMAGE_DIR)
os.makedirs(FULL_IMAGE_DIR, exist_ok=True)

TEXT_LOG_DIR = "data"
os.makedirs(TEXT_LOG_DIR, exist_ok=True)

class SnapshotRequest(BaseModel):
    timestamp: str
    transcript: str
    screenshot_base64: str

    class Config:
        schema_extra = {
            "timestamp": "2025-04-28 15:30:00",
            "transcript": "이 코드는 시험에 나올 수 있습니다.",
            "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA..."
        }

@router.post("/snapshots")
async def upload_snapshot(data: SnapshotRequest, db: AsyncSession = Depends(get_db)):
    timestamp = data.timestamp
    text = data.transcript
    image_data = data.screenshot_base64
    lecture_id = 1

    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        date_group = dt.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="timestamp 형식 오류 (yyyy-MM-dd HH:mm:ss)")

    try:
        if "," in image_data:
            _, encoded = image_data.split(",", 1)
        else:
            encoded = image_data
        image_bytes = base64.b64decode(encoded)
    except Exception as e:
        raise HTTPException(status_code=400, detail="이미지 디코딩 실패")

    filename = f"{uuid.uuid4().hex}.png"
    save_path = os.path.join(FULL_IMAGE_DIR, filename)
    relative_url = f"/static/{IMAGE_DIR}/{filename}"

    try:
        with open(save_path, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail="이미지 파일 저장 실패")

    # ✅ STT 텍스트 누적 저장
    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    try:
        with open(text_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{dt.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")
    except Exception as e:
        print(f"❌ 텍스트 저장 실패: {e}")

    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=date_group,
        time=dt.strftime("%H:%M:%S"),
        text=text,
        image_path=relative_url
    )

    db.add(snapshot)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="DB 저장 실패")

    return {
        "message": "스냅샷 저장 완료",
        "lecture_id": lecture_id,
        "date": date_group,
        "time": snapshot.time,
        "text": text,
        "image_url": relative_url
    }

@router.get("/generate_question_summary")
async def generate_question_summary(lecture_id: int = 1):
    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")

    if not os.path.exists(text_log_path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 파일이 없습니다.")

    with open(text_log_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # ✨ 추후 GPT 요약 연결 가능
    dummy_summary = f"[요약 결과]\n{full_text[:300]}..."

    return {
        "lecture_id": lecture_id,
        "summary": dummy_summary
    }
