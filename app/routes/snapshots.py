from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Snapshot
import os
import base64
import uuid
from datetime import datetime

from openai import AsyncOpenAI  # ✅ 최신 방식
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

# 디렉터리 설정
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
    absolute_url = f"https://project2025-backend.onrender.com{relative_url}"

    try:
        with open(save_path, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail="이미지 파일 저장 실패")

    # 텍스트 누적 저장
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
        "image_url": absolute_url
    }


# ✅ 최신 OpenAI 방식으로 GPT 요약 함수
async def summarize_text_with_gpt(text: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "다음 텍스트를 한국어 강의 요약 형식으로 간결하게 정리해줘."},
                {"role": "user", "content": text[:3000]}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ GPT 요약 실패: {e}")
        return "[요약 실패] GPT 호출 중 오류가 발생했습니다."


@router.get("/generate_question_summary")
async def generate_question_summary(lecture_id: int = 1):
    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")

    if not os.path.exists(text_log_path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 파일이 없습니다.")

    with open(text_log_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    summary = await summarize_text_with_gpt(full_text)

    return {
        "lecture_id": lecture_id,
        "summary": summary
    }
