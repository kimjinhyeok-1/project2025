from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Assignment
from app.schemas import AssignmentOut
from app.database import get_db
import fitz  # PyMuPDF

router = APIRouter()

# ✅ PDF 업로드 기반 과제 등록 (중복 방지 포함)
@router.post("/upload", response_model=AssignmentOut)
async def upload_assignment_with_pdf(
    title: str = Form(...),
    sample_answer: str = Form(""),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    # ✅ PDF → 텍스트 추출
    contents = await file.read()
    try:
        doc = fitz.open(stream=contents, filetype="pdf")
        description = "\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 처리 중 오류 발생: {str(e)}")

    # ✅ 중복 과제 존재 여부 확인 (title + description 기준)
    result = await db.execute(
        select(Assignment).where(
            Assignment.title == title,
            Assignment.description == description
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing  # 중복 과제 있으면 그대로 반환

    # ✅ 없으면 새로 추가
    new_assignment = Assignment(
        title=title,
        description=description,
        sample_answer=sample_answer,
    )
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    return new_assignment
