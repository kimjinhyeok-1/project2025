from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import os
import fitz
import uuid
import aiofiles

from app.database import get_db
from app.auth import get_current_user
from app.models import Assignment, AssignmentSubmission, User
from app.utils.gpt_feedback import generate_assignment_feedback, create_feedback_thread

router = APIRouter()

@router.post("/assignments/{assignment_id}/submit", tags=["Assignments"])
async def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 과제 존재 확인
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")

    # 2. 파일 확인
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 제출할 수 있습니다.")

    # 3. 저장 경로 생성
    save_dir = "uploads/submissions"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{current_user.id}_{assignment_id}.pdf"
    file_path = os.path.join(save_dir, filename)

    # 4. 파일 저장
    async with aiofiles.open(file_path, "wb") as out_file:
        contents = await file.read()
        await out_file.write(contents)

    # 5. PDF 텍스트 추출
    try:
        with fitz.open(stream=contents, filetype="pdf") as doc:
            pdf_text = "\n".join(page.get_text("text") for page in doc)
    except Exception:
        raise HTTPException(status_code=500, detail="PDF 텍스트 추출 실패")

    # 6. GPT 피드백 생성
    feedback = await generate_assignment_feedback(assignment.description, pdf_text)

    # 7. Assistant Thread 생성 + 피드백 저장
    thread_id = await create_feedback_thread(feedback)

    # 8. DB 저장
    submission = AssignmentSubmission(
        assignment_id=assignment.id,
        student_id=current_user.id,
        submitted_file_path=file_path,
        gpt_feedback=feedback,
        gpt_feedback_created_at=datetime.utcnow(),
        assistant_thread_id=thread_id,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    return {
        "message": "제출 및 피드백 생성 완료",
        "feedback": feedback,
        "thread_id": thread_id
    }
