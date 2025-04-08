from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Assignment, AssignmentQuestion
from app.schemas import AssignmentCreate, AssignmentOut, AssignmentUpdate, AssignmentQuestionListOut
from app.database import get_db
from app.auth import verify_professor
import fitz  # PyMuPDF

router = APIRouter()


# ✅ PDF 텍스트 추출 함수
def extract_pdf_text(contents: bytes) -> str:
    try:
        with fitz.open(stream=contents, filetype="pdf") as doc:
            text = "\n".join(page.get_text("text") for page in doc)
        return text.strip()
    except Exception:
        raise HTTPException(status_code=500, detail="PDF 파일 처리 중 오류가 발생했습니다.")


# ✅ PDF 업로드 기반 과제 등록 (중복 방지 포함)
@router.post("/upload", response_model=AssignmentOut, tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def upload_assignment_with_pdf(
    title: str = Form(..., description="과제 제목"),
    sample_answer: str = Form("", description="예시 코드 (선택)"),
    file: UploadFile = File(..., description="PDF 파일"),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    contents = await file.read()
    description = extract_pdf_text(contents)

    result = await db.execute(
        select(Assignment).where(
            Assignment.title == title.strip(),
            Assignment.description == description
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    new_assignment = Assignment(
        title=title.strip(),
        description=description,
        sample_answer=sample_answer.strip() if sample_answer else None,
    )
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    return new_assignment


# ✅ 과제 직접 입력 생성
@router.post("/create", response_model=AssignmentOut, tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def create_assignment(
    assignment: AssignmentCreate,
    db: AsyncSession = Depends(get_db)
):
    new_assignment = Assignment(
        title=assignment.title.strip(),
        description=assignment.description.strip(),
        sample_answer=assignment.sample_answer.strip() if assignment.sample_answer else None,
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


# ✅ 과제 수정 (Form 기반 - 필드 선택 수정 가능)
@router.put("/{assignment_id}", response_model=AssignmentOut, tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def update_assignment_form(
    assignment_id: int,
    title: str = Form(None),
    description: str = Form(None),
    sample_answer: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=404, detail="해당 과제를 찾을 수 없습니다.")

    if title is not None:
        assignment.title = title.strip()
    if description is not None:
        assignment.description = description.strip()
    if sample_answer is not None:
        assignment.sample_answer = sample_answer.strip()

    await db.commit()
    await db.refresh(assignment)
    return assignment


# ✅ 과제 삭제 (교수자만 가능)
@router.delete("/{assignment_id}", tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()

    if assignment is None:
        raise HTTPException(status_code=404, detail="삭제할 과제를 찾을 수 없습니다.")

    await db.delete(assignment)
    await db.commit()
    return {"message": f"과제(ID={assignment_id})가 성공적으로 삭제되었습니다."}


# ✅ 과제별 질문 전체 조회 (교수자만 가능)
@router.get("/{assignment_id}/questions", response_model=AssignmentQuestionListOut, tags=["Assignments"], dependencies=[Depends(verify_professor)])
async def get_questions_for_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db)
):
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
