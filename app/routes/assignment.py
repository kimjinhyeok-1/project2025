from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import os, shutil, uuid, aiofiles, asyncio
import fitz  # PyMuPDF
from pydantic import BaseModel
from typing import Optional, List
from app.models import Assignment, AssignmentSubmission, User
from app.database import get_db
from app.auth import verify_professor, get_current_user
from app.utils.gpt_feedback import generate_assignment_feedback

router = APIRouter()

# ─────────────────────────────────────────────
# ✅ Pydantic 통합 스키마
# ─────────────────────────────────────────────
class AssignmentOut(BaseModel):
    id: int
    title: str
    description: str
    sample_answer: Optional[str]
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True

class AssignmentCreate(BaseModel):
    title: str
    description: str
    sample_answer: Optional[str] = None

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sample_answer: Optional[str] = None

# ─────────────────────────────────────────────
# ✅ 유틸 함수
# ─────────────────────────────────────────────
def parse_deadline(deadline: Optional[str]) -> Optional[datetime]:
    if not deadline:
        return None
    try:
        return datetime.fromisoformat(deadline)
    except ValueError:
        raise HTTPException(status_code=400, detail="마감일 형식이 올바르지 않습니다. 예: 2025-05-01T23:59:00")

def extract_text_from_pdf(contents: bytes) -> str:
    try:
        with fitz.open(stream=contents, filetype="pdf") as doc:
            return "\n".join(page.get_text("text") for page in doc)
    except Exception:
        raise HTTPException(status_code=500, detail="PDF 텍스트 추출 오류 발생")

async def save_pdf(file: UploadFile, path: str):
    async with aiofiles.open(path, "wb") as out_file:
        contents = await file.read()
        await out_file.write(contents)
    return contents

# ─────────────────────────────────────────────
# ✅ 과제 생성
# ─────────────────────────────────────────────
@router.post("/create", response_model=AssignmentOut, dependencies=[Depends(verify_professor)], tags=["Assignments"])
async def create_assignment(
    title: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(None),
    sample_answer: str = Form(""),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    parsed_deadline = parse_deadline(deadline)
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
        sample_answer=sample_answer.strip() or None,
        attached_file_path=file_path
    )
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    return new_assignment

# ─────────────────────────────────────────────
# ✅ 과제 전체 목록
# ─────────────────────────────────────────────
@router.get("/", response_model=List[AssignmentOut], tags=["Assignments"])
async def get_assignments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment))
    assignments = result.scalars().all()
    for assignment in assignments:
        assignment.sample_answer = None  # 학생에게는 샘플 정답 비공개
    return assignments

# ─────────────────────────────────────────────
# ✅ 과제 단건 조회
# ─────────────────────────────────────────────
@router.get("/{assignment_id}", response_model=AssignmentOut, tags=["Assignments"])
async def get_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
    assignment.sample_answer = None
    return assignment

# ─────────────────────────────────────────────
# ✅ 과제 수정
# ─────────────────────────────────────────────
@router.put("/{assignment_id}", response_model=AssignmentOut, dependencies=[Depends(verify_professor)], tags=["Assignments"])
async def update_assignment(
    assignment_id: int,
    title: str = Form(None),
    description: str = Form(None),
    sample_answer: str = Form(None),
    deadline: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="해당 과제를 찾을 수 없습니다.")

    if title: assignment.title = title.strip()
    if description: assignment.description = description.strip()
    if sample_answer is not None: assignment.sample_answer = sample_answer.strip()
    if deadline: assignment.deadline = parse_deadline(deadline)

    await db.commit()
    await db.refresh(assignment)
    assignment.sample_answer = None
    return assignment

# ─────────────────────────────────────────────
# ✅ 과제 삭제
# ─────────────────────────────────────────────
@router.delete("/{assignment_id}", tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def delete_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="삭제할 과제를 찾을 수 없습니다.")
    await db.delete(assignment)
    await db.commit()
    return {"message": f"과제(ID={assignment_id}) 삭제 완료"}

# ─────────────────────────────────────────────
# ✅ 과제 제출 + 피드백
# ─────────────────────────────────────────────
@router.post("/{assignment_id}/submit", tags=["Assignments"])
async def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 제출 가능합니다.")

    if assignment.deadline and datetime.utcnow() < assignment.deadline:
        raise HTTPException(status_code=400, detail="마감일이 지나야 제출 가능합니다.")

    save_dir = "uploads/submissions"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{current_user.id}_{assignment_id}.pdf"
    file_path = os.path.join(save_dir, filename)
    contents = await save_pdf(file, file_path)

    pdf_text = extract_text_from_pdf(contents)

    try:
        feedback = await generate_assignment_feedback(assignment.description, pdf_text)
    except Exception:
        await asyncio.sleep(1)
        try:
            feedback = await generate_assignment_feedback(assignment.description, pdf_text)
        except Exception:
            raise HTTPException(status_code=500, detail="GPT 피드백 생성 실패")

    result = await db.execute(
        select(AssignmentSubmission).where(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == current_user.id
        )
    )
    submission = result.scalar_one_or_none()

    if submission:
        submission.submitted_file_path = file_path
        submission.gpt_feedback = feedback
        submission.gpt_feedback_created_at = datetime.utcnow()
    else:
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            submitted_file_path=file_path,
            gpt_feedback=feedback,
            gpt_feedback_created_at=datetime.utcnow()
        )
        db.add(submission)

    current_user.has_submitted_assignment = True
    await db.commit()

    return {"message": "제출 및 피드백 완료", "feedback": feedback}

# ─────────────────────────────────────────────
# ✅ 피드백 조회
# ─────────────────────────────────────────────
@router.get("/{assignment_id}/feedback", tags=["Assignments"])
async def get_assignment_feedback(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(AssignmentSubmission).where(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == current_user.id
        )
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="제출 기록이 없습니다.")
    if not submission.gpt_feedback:
        raise HTTPException(status_code=404, detail="GPT 피드백이 아직 없습니다.")

    return {
        "assignment_id": assignment_id,
        "student_id": current_user.id,
        "feedback": submission.gpt_feedback,
        "created_at": submission.gpt_feedback_created_at,
    }

# ─────────────────────────────────────────────
# ✅ 교수자용 전체 피드백 조회
# ─────────────────────────────────────────────
@router.get("/{assignment_id}/all-feedback", tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def get_all_feedbacks_for_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 학생과 제출물 LEFT OUTER JOIN
    stmt = (
        select(User, AssignmentSubmission)
        .outerjoin(AssignmentSubmission, (AssignmentSubmission.assignment_id == assignment_id) & (User.id == AssignmentSubmission.student_id))
        .where(User.role == "student")
    )
    result = await db.execute(stmt)
    rows = result.all()

    feedback_list = []
    for student, submission in rows:
        feedback_list.append({
            "student_id": student.id,
            "student_name": student.name,
            "has_submitted": bool(submission),
            "gpt_feedback": getattr(submission, "gpt_feedback", None),
            "gpt_feedback_time": getattr(submission, "gpt_feedback_created_at", None),
            "professor_feedback": getattr(submission, "professor_feedback", None),
            "professor_feedback_time": getattr(submission, "professor_feedback_created_at", None),
        })

    return {"assignment_id": assignment_id, "feedbacks": feedback_list}

# ─────────────────────────────────────────────
# ✅ 교수자 피드백 추가
# ─────────────────────────────────────────────
@router.post("/{assignment_id}/student/{student_id}/professor-feedback", tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def add_professor_feedback(
    assignment_id: int,
    student_id: int,
    feedback: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    submission = await get_submission(db, assignment_id, student_id)
    if not submission:
        raise HTTPException(status_code=404, detail="해당 학생의 제출 기록이 없습니다.")

    submission.professor_feedback = feedback.strip()
    submission.professor_feedback_created_at = datetime.utcnow()

    await db.commit()
    return {"message": "교수 피드백이 저장되었습니다."}