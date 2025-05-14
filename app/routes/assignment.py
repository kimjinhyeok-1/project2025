from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import os
import shutil
import uuid
import aiofiles
import asyncio
import fitz  # PyMuPDF

from app.models import Assignment, AssignmentSubmission, User
from app.schemas import AssignmentOut
from app.database import get_db
from app.auth import verify_professor, get_current_user_id as get_current_user
from app.utils.gpt_feedback import generate_assignment_feedback

router = APIRouter()

# ✅ PDF에서 텍스트 추출 (fitz 사용)
def extract_text_from_pdf(contents: bytes) -> str:
    try:
        with fitz.open(stream=contents, filetype="pdf") as doc:
            return "\n".join(page.get_text("text") for page in doc)
    except Exception:
        raise HTTPException(status_code=500, detail="PDF 텍스트 추출 중 오류가 발생했습니다.")

# ✅ 과제 생성
@router.post("/create", response_model=AssignmentOut, tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def create_assignment(
    title: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(None),
    sample_answer: str = Form(""),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        parsed_deadline = datetime.fromisoformat(deadline) if deadline else None
    except ValueError:
        raise HTTPException(status_code=400, detail="마감일 형식이 올바르지 않습니다. 예: 2025-05-01T23:59:00")

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

# ✅ 과제 목록 조회
@router.get("/", response_model=list[AssignmentOut], tags=["Assignments"])
async def get_assignments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment))
    assignments = result.scalars().all()
    for assignment in assignments:
        assignment.sample_answer = None
    return assignments

# ✅ 과제 상세 조회
@router.get("/{assignment_id}", response_model=AssignmentOut, tags=["Assignments"])
async def get_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
    assignment.sample_answer = None
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
    assignment.sample_answer = None
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

# ✅ 과제 제출 + GPT 피드백 + 사용자 상태 업데이트
@router.post("/{assignment_id}/submit", tags=["Assignments"])
async def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 제출할 수 있습니다.")

    if assignment.deadline and datetime.utcnow() < assignment.deadline:
        raise HTTPException(status_code=400, detail="마감일이 지나야 제출이 가능합니다.")

    save_dir = "uploads/submissions"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{current_user.id}_{assignment_id}.pdf"
    file_path = os.path.join(save_dir, filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        contents = await file.read()
        await out_file.write(contents)

    pdf_text = extract_text_from_pdf(contents)

    try:
        feedback = await generate_assignment_feedback(assignment.description, pdf_text)
    except Exception:
        await asyncio.sleep(1)
        try:
            feedback = await generate_assignment_feedback(assignment.description, pdf_text)
        except Exception:
            raise HTTPException(status_code=500, detail="GPT 피드백 생성에 실패했습니다.")

    result = await db.execute(
        select(AssignmentSubmission).where(
            AssignmentSubmission.assignment_id == assignment.id,
            AssignmentSubmission.student_id == current_user.id
        )
    )
    existing_submission = result.scalar_one_or_none()

    if existing_submission:
        existing_submission.submitted_file_path = file_path
        existing_submission.gpt_feedback = feedback
        existing_submission.gpt_feedback_created_at = datetime.utcnow()
    else:
        new_submission = AssignmentSubmission(
            assignment_id=assignment.id,
            student_id=current_user.id,
            submitted_file_path=file_path,
            gpt_feedback=feedback,
            gpt_feedback_created_at=datetime.utcnow(),
        )
        db.add(new_submission)

    # ✅ 유저 상태 업데이트
    current_user.has_submitted_assignment = True

    await db.commit()

    return {"message": "제출 및 피드백 생성 완료", "feedback": feedback}
