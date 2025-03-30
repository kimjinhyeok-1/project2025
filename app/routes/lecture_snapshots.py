from fastapi import APIRouter, UploadFile, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import LectureSnapshot
from datetime import datetime
import os

router = APIRouter(prefix="/lecture-snapshots", tags=["Lecture Snapshots"])

@router.post("/")
async def upload_snapshot(
    lecture_id: str = Form(...),
    transcript: str = Form(...),
    timestamp: str = Form(...),
    image: UploadFile = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # 이미지 저장
    filename = f"{lecture_id}_{datetime.now().timestamp()}.png"
    filepath = f"app/static/images/{filename}"
    with open(filepath, "wb") as f:
        f.write(await image.read())

    snapshot = LectureSnapshot(
        lecture_id=lecture_id,
        transcript=transcript,
        timestamp=timestamp,
        image_url=f"/static/images/{filename}",
    )

    db.add(snapshot)
    await db.commit()

    return {"message": "업로드 성공", "image_url": snapshot.image_url}


@router.get("/{lecture_id}")
async def get_snapshots(lecture_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LectureSnapshot).where(LectureSnapshot.lecture_id == lecture_id))
    data = result.scalars().all()
    return [
        {
            "timestamp": d.timestamp,
            "transcript": d.transcript,
            "image_url": d.image_url
        } for d in data
    ]
