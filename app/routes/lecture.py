from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Lecture
from app.auth import verify_professor  # ✅ 교수자 권한 확인
from pydantic import BaseModel
from typing import List

router = APIRouter()

# ✅ 입력용 스키마
class LectureCreate(BaseModel):
    title: str
    description: str

# ✅ 응답용 스키마
class LectureResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes = True  # Pydantic v2 대응

# ✅ 강의 등록 API (교수자만 가능)
@router.post("/lectures", response_model=LectureResponse)
async def create_lecture(
    lecture: LectureCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_professor)  # 🔐 교수자 권한 필요
):
    new_lecture = Lecture(
        title=lecture.title,
        description=lecture.description
    )
    db.add(new_lecture)
    await db.commit()
    await db.refresh(new_lecture)
    return new_lecture

# ✅ 전체 강의 목록 조회 API
@router.get("/lectures", response_model=List[LectureResponse])
async def get_all_lectures(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Lecture))
    lectures = result.scalars().all()
    return lectures
