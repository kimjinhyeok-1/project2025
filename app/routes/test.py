from fastapi import Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.database import get_db
from app.models import Snapshot

@router.get("/snapshots/by_time")
def get_snapshot_by_time(
    lecture_id: int = Query(..., description="강의 ID"),
    time: str = Query(..., description="형식: HH:MM:SS"),
    db: Session = Depends(get_db)
):
    try:
        # ⏱️ 기준 시간 파싱
        query_time = datetime.strptime(time, "%H:%M:%S").time()
    except:
        raise HTTPException(status_code=400, detail="시간 형식이 잘못되었습니다. HH:MM:SS 형식 사용")

    # 🔍 해당 강의 내에서 기준 시간보다 과거인 가장 가까운 Snapshot 조회
    snap = (
        db.query(Snapshot)
        .filter(
            and_(
                Snapshot.lecture_id == lecture_id,
                Snapshot.time < query_time
            )
        )
        .order_by(Snapshot.time.desc())
        .first()
    )

    if not snap:
        raise HTTPException(status_code=404, detail="해당 시간 이전의 스냅샷이 없습니다.")

    return {
        "image_url": f"/{snap.image_path}",
        "text": snap.text,
        "time": snap.time.strftime("%H:%M:%S")
    }
