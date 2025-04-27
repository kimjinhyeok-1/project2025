from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Snapshot
import os
import base64
import uuid
from datetime import datetime

router = APIRouter()

# ✅ 저장 경로 설정
IMAGE_DIR = "snapshots"
os.makedirs(IMAGE_DIR, exist_ok=True)

# ✅ 요청 바디 스키마
class SnapshotRequest(BaseModel):
    lecture_id: int
    timestamp: str
    transcript: str
    screenshot_base64: str

# ✅ /snapshots: 스크린샷 + STT 텍스트 저장
@router.post("/snapshots")
def upload_snapshot(data: SnapshotRequest, db: Session = Depends(get_db)):
    """
    수업 중 프론트가 스크린샷 + 텍스트 + 타임스탬프를 전송
    """
    print("📥 /snapshots 요청 도착")
    timestamp = data.timestamp
    text = data.transcript
    image_data = data.screenshot_base64
    lecture_id = data.lecture_id

    if not timestamp or not text or not image_data:
        raise HTTPException(status_code=400, detail="timestamp, transcript, screenshot_base64가 필요합니다.")

    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        date_group = dt.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="timestamp 형식 오류 (yyyy-MM-dd HH:mm:ss)")

    try:
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
    except Exception:
        raise HTTPException(status_code=400, detail="이미지 디코딩 실패")

    filename = f"{uuid.uuid4().hex}.png"
    file_path = os.path.join(IMAGE_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=date_group,
        time=dt.strftime("%H:%M:%S"),
        text=text,
        image_path=f"/static/{file_path}"  # ⬅️ URL 경로 수정 (정적파일로 제공할 것이기 때문에)
    )
    db.add(snapshot)
    db.commit()

    return {
        "message": "스냅샷 저장 완료",
        "lecture_id": lecture_id,
        "date": date_group,
        "time": snapshot.time,
        "text": text,
        "image_url": snapshot.image_path
    }

# ✅ /summaries: 날짜 목록 조회
@router.get("/summaries")
def get_all_summary_dates(db: Session = Depends(get_db)):
    results = db.query(Snapshot.date).distinct().order_by(Snapshot.date.desc()).all()
    return {"dates": [r.date for r in results]}

# ✅ /summaries/{date}: 특정 날짜 요약 목록
@router.get("/summaries/{date}")
def get_summary_by_date(date: str, db: Session = Depends(get_db)):
    snapshots = db.query(Snapshot).filter(Snapshot.date == date).order_by(Snapshot.time.asc()).all()
    result = []
    for snap in snapshots:
        result.append({
            "lecture_id": snap.lecture_id,
            "time": snap.time,
            "text": snap.text,
            "image_url": snap.image_path
        })
    return {
        "summary": f"{date} 강의 요약",
        "highlights": result
    }

# ✅ /snapshots/nearest: 가장 가까운 스냅샷 찾기
@router.get("/snapshots/nearest")
def get_nearest_snapshot(
    date: str = Query(..., description="yyyy-MM-dd"),
    time: str = Query(..., description="HH:mm:ss"),
    db: Session = Depends(get_db)
):
    try:
        target_time = datetime.strptime(time, "%H:%M:%S").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="time 형식 오류 (HH:mm:ss)")

    snapshots = db.query(Snapshot).filter(Snapshot.date == date).all()
    if not snapshots:
        raise HTTPException(status_code=404, detail="해당 날짜에 스냅샷 없음")

    def time_diff(snap):
        snap_time = datetime.strptime(snap.time, "%H:%M:%S").time()
        return abs(datetime.combine(datetime.today(), snap_time) - datetime.combine(datetime.today(), target_time))

    closest = min(snapshots, key=time_diff)

    return {
        "lecture_id": closest.lecture_id,
        "time": closest.time,
        "text": closest.text,
        "image_url": closest.image_path
    }
