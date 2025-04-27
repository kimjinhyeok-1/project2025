from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import os
import shutil
import uuid
import aiofiles
import asyncio
import fitz
from pydantic import BaseModel

from app.models import Assignment, AssignmentSubmission, AssignmentQuestion, AssignmentThread, User
from app.schemas import AssignmentCreate, AssignmentOut, AssignmentUpdate, AssignmentQuestionListOut
from app.database import get_db
from app.auth import verify_professor, get_current_user_id as get_current_user
from app.utils.gpt_feedback import generate_assignment_feedback, create_feedback_thread
from app.utils.gpt_qna import create_or_get_qna_thread, ask_question_to_gpt

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    thread_id: str

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

@router.get("/", response_model=list[AssignmentOut], tags=["Assignments"])
async def get_assignments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment))
    assignments = result.scalars().all()
    for assignment in assignments:
        assignment.sample_answer = None
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentOut, tags=["Assignments"])
async def get_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")

    assignment.sample_answer = None
    return assignment

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

@router.delete("/{assignment_id}", tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def delete_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="삭제할 과제를 찾을 수 없습니다.")

    await db.delete(assignment)
    await db.commit()
    return {"message": f"과제(ID={assignment_id})가 성공적으로 삭제되었습니다."}

@router.post("/assignments/{assignment_id}/submit", tags=["Assignments"])
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

    try:
        with fitz.open(stream=contents, filetype="pdf") as doc:
            pdf_text = "\n".join(page.get_text("text") for page in doc)
    except Exception:
        raise HTTPException(status_code=500, detail="PDF 텍스트 추출 실패")

    try:
        feedback = await generate_assignment_feedback(assignment.description, pdf_text)
    except Exception:
        await asyncio.sleep(1)
        try:
            feedback = await generate_assignment_feedback(assignment.description, pdf_text)
        except Exception:
            raise HTTPException(status_code=500, detail="GPT 피드백 생성에 실패했습니다.")

    thread_id = await create_feedback_thread(feedback)

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
        existing_submission.assistant_thread_id = thread_id
    else:
        new_submission = AssignmentSubmission(
            assignment_id=assignment.id,
            student_id=current_user.id,
            submitted_file_path=file_path,
            gpt_feedback=feedback,
            gpt_feedback_created_at=datetime.utcnow(),
            assistant_thread_id=thread_id,
        )
        db.add(new_submission)

    await db.commit()

    return {"message": "제출 및 피드백 생성 완료", "feedback": feedback, "thread_id": thread_id}

@router.post("/assignments/{assignment_id}/ask", response_model=AnswerResponse, tags=["Assignments"])
async def ask_assignment_question(
    assignment_id: int,
    question_req: QuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")

    thread_id = await create_or_get_qna_thread(db, assignment_id, current_user.id)

    try:
        answer = await ask_question_to_gpt(thread_id, question_req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 답변 생성 실패: {str(e)}")

    new_question = AssignmentQuestion(
        assignment_id=assignment_id,
        user_id=current_user.id,
        question_text=question_req.question,
        gpt_answer=answer,
    )
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)

    return AnswerResponse(
        answer=answer,
        thread_id=thread_id
    )

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

    return {"assignment": assignment, "questions": questions}
