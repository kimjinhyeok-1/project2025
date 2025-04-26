from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Assignment, AssignmentQuestion
from app.schemas import AssignmentCreate, AssignmentOut, AssignmentUpdate, AssignmentQuestionListOut
from app.database import get_db
from app.auth import verify_professor
from datetime import datetime
import os
import shutil
import uuid

router = APIRouter()


# ✅ 과제 등록 (첨부파일 + 마감일 포함)
@router.post("/create", response_model=AssignmentOut, tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def create_assignment(
    title: str = Form(..., description="과제 제목"),
    description: str = Form(..., description="과제 설명"),
    deadline: str = Form(None, description="마감일 (예: 2025-05-01T23:59:00)"),
    sample_answer: str = Form("", description="예시 코드 (선택)"),
    file: UploadFile = File(None, description="부가설명 PDF 파일 (선택)"),
    db: AsyncSession = Depends(get_db)
):
    # 🔹 마감일 파싱
    try:
        parsed_deadline = datetime.fromisoformat(deadline) if deadline else None
    except ValueError:
        raise HTTPException(status_code=400, detail="마감일 형식이 올바르지 않습니다. 예: 2025-05-01T23:59:00")

    # 🔹 PDF 파일 저장
    file_path = None
    if file:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
        save_dir = "uploads/assignments"
        os.makedirs(save_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(save_dir, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    # 🔹 과제 저장
    new_assignment = Assignment(
        title=title.strip(),
        description=description.strip(),
        deadline=parsed_deadline,
        sample_answer=sample_answer.strip() if sample_answer else None,
        attached_file_path=file_path
    )
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    return new_assignment


# ✅ 과제 전체 조회
@router.get("/", response_model=list[AssignmentOut], tags=["Assignments"])
async def get_assignments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment))
    return result.scalars().all()


# ✅ 과제 상세 조회
@router.get("/{assignment_id}", response_model=AssignmentOut, tags=["Assignments"])
async def get_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
    return assignment


# ✅ 과제 수정
@router.put("/{assignment_id}", response_model=AssignmentOut, tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def update_assignment_form(
    assignment_id: int,
    title: str = Form(None),
    description: str = Form(None),
    sample_answer: str = Form(None),
    deadline: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="해당 과제를 찾을 수 없습니다.")

    if title:
        assignment.title = title.strip()
    if description:
        assignment.description = description.strip()
    if sample_answer is not None:
        assignment.sample_answer = sample_answer.strip()
    if deadline:
        try:
            assignment.deadline = datetime.fromisoformat(deadline)
        except ValueError:
            raise HTTPException(status_code=400, detail="마감일 형식이 올바르지 않습니다.")

    await db.commit()
    await db.refresh(assignment)
    return assignment


# ✅ 과제 삭제
@router.delete("/{assignment_id}", tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def delete_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="삭제할 과제를 찾을 수 없습니다.")

    await db.delete(assignment)
    await db.commit()
    return {"message": f"과제(ID={assignment_id})가 성공적으로 삭제되었습니다."}


# ✅ 과제별 질문 조회 (교수자만)
@router.get("/{assignment_id}/questions", response_model=AssignmentQuestionListOut, tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def get_questions_for_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")

    result = await db.execute(
        select(AssignmentQuestion).where(AssignmentQuestion.assignment_id == assignment_id)
    )
    questions = result.scalars().all()

    return {
        "assignment": assignment,
        "questions": questions
    }

