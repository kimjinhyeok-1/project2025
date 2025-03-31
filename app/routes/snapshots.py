from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.snapshots import Snapshot
import os
import base64
import uuid
from datetime import datetime

router = APIRouter()

IMAGE_DIR = "snapshots"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# ✅ /snapshots: lecture_id 없이 timestamp 기반 저장
@router.post("/snapshots")
def upload_snapshot(data: dict, db: Session = Depends(get_db)):
    print("📥 /snapshots 요청 도착!")
    print("📄 데이터 내용:", data)

    # (이후 처리 생략)

    timestamp = data.get("timestamp")  # "2024-03-30 15:02:18" 형식
    text = data.get("transcript")
    image_data = data.get("screenshot_base64")

    if not timestamp or not text or not image_data:
        raise HTTPException(status_code=400, detail="필드 누락")

    try:
        # 날짜 추출해서 yyyy-mm-dd 형식으로 그룹핑
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        date_group = dt.strftime("%Y-%m-%d")
    except:
        raise HTTPException(status_code=400, detail="timestamp 형식 오류")

    # base64 이미지 디코딩
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

# ✅ /summaries: 날짜별 스냅샷 요약 목록 조회
@router.get("/summaries")
def get_all_summary_dates(db: Session = Depends(get_db)):
    results = db.query(Snapshot.date).distinct().all()
    return {"dates": [r.date for r in results]}

# ✅ /summaries/{date}: 해당 날짜의 스냅샷 목록 반환
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
