from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Lecture
from pydantic import BaseModel

router = APIRouter()

# 📘 Pydantic schema for creating a lecture
class LectureCreate(BaseModel):
    title: str
    description: str

# 📘 Pydantic schema for response (등록된 강의 포함 id 반환)
class LectureResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes = True  # Pydantic v2에서 orm_mode 대신

# 🧠 강의 등록 API (비동기)
@router.post("/lectures", response_model=LectureResponse)
async def create_lecture(lecture: LectureCreate, db: AsyncSession = Depends(get_db)):
    new_lecture = Lecture(
        title=lecture.title,
        description=lecture.description
    )
    db.add(new_lecture)
    await db.commit()
    await db.refresh(new_lecture)
    return new_lecture
