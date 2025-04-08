from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Snapshot  # Snapshot 모델을 사용 중
import os
import base64
import uuid
from datetime import datetime

router = APIRouter()

IMAGE_DIR = "snapshots"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# ✅ /snapshots: 스크린샷 + STT 텍스트 저장
@router.post("/snapshots")
def upload_snapshot(data: dict, db: Session = Depends(get_db)):
    print("📥 /snapshots 요청 도착!")
    print("📄 데이터 내용:", data)

    timestamp = data.get("timestamp")  # "2024-03-30 15:02:18" 형식
    text = data.get("transcript")
    image_data = data.get("screenshot_base64")

    if not timestamp or not text or not image_data:
        raise HTTPException(status_code=400, detail="필드 누락")

    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        date_group = dt.strftime("%Y-%m-%d")
    except:
        raise HTTPException(status_code=400, detail="timestamp 형식 오류")

    try:
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
    except Exception as e:
        raise HTTPException(status_code=400, detail="이미지 디코딩 실패")

    filename = f"{uuid.uuid4().hex}.png"
    file_path = os.path.join(IMAGE_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    snapshot = Snapshot(
        date=date_group,
        time=dt.strftime("%H:%M:%S"),
        text=text,
        image_path=file_path
    )
    db.add(snapshot)
    db.commit()

    return {
        "message": "스냅샷 저장 완료",
        "date": date_group,
        "time": snapshot.time,
        "text": text,
        "image_path": file_path
    }

# ✅ /summaries: 날짜 목록 조회
@router.get("/summaries")
def get_all_summary_dates(db: Session = Depends(get_db)):
    results = db.query(Snapshot.date).distinct().all()
    return {"dates": [r.date for r in results]}

# ✅ /summaries/{date}: 해당 날짜의 스냅샷 요약 목록
@router.get("/summaries/{date}")
def get_summary_by_date(date: str, db: Session = Depends(get_db)):
    snapshots = db.query(Snapshot).filter(Snapshot.date == date).all()
    result = []
    for snap in snapshots:
        result.append({
            "time": snap.time,
            "text": snap.text,
            "image_url": f"/{snap.image_path}"
        })
    return {
        "summary": f"{date} 강의 요약",
        "highlights": result
    }

# ✅ /snapshots/nearest: 요약문 클릭 시 가장 가까운 스냅샷 반환
@router.get("/snapshots/nearest")
def get_nearest_snapshot(
    date: str = Query(..., description="예: 2024-03-30"),
    time: str = Query(..., description="예: 15:02:18"),
    db: Session = Depends(get_db)
):
    try:
        target_time = datetime.strptime(time, "%H:%M:%S").time()
    except:
        raise HTTPException(status_code=400, detail="time 형식 오류")

    snapshots = db.query(Snapshot).filter(Snapshot.date == date).all()
    if not snapshots:
        raise HTTPException(status_code=404, detail="해당 날짜에 저장된 스냅샷이 없습니다.")

    # 가장 가까운 스냅샷 찾기
    def time_diff(snap):
        snap_time = datetime.strptime(snap.time, "%H:%M:%S").time()
        return abs(datetime.combine(datetime.today(), snap_time) - datetime.combine(datetime.today(), target_time))

    closest = min(snapshots, key=time_diff)

    return {
        "time": closest.time,
        "text": closest.text,
        "image_url": f"/{closest.image_path}"
    }
