from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Assignment
from app.schemas import AssignmentCreate, AssignmentOut
from database import get_db

router = APIRouter()


# ✅ 과제 등록
@router.post("/create", response_model=AssignmentOut)
async def create_assignment(
    assignment: AssignmentCreate,
    db: AsyncSession = Depends(get_db)
):
    new_assignment = Assignment(
        title=assignment.title,
        description=assignment.description,
        sample_answer=assignment.sample_answer,
    )
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    return new_assignment


# ✅ 전체 과제 목록
@router.get("/", response_model=list[AssignmentOut])
async def get_assignments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment))
    return result.scalars().all()


# ✅ 과제 상세 조회
@router.get("/{assignment_id}", response_model=AssignmentOut)
async def get_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
    return assignment
