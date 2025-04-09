# app/routes/question.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.gpt import generate_expected_questions

router = APIRouter()

class QuestionRequest(BaseModel):
    lecture_id: str
    summary_text: str

class QuestionResponse(BaseModel):
    lecture_id: str
    questions: List[str]

@router.post("/generate_questions", response_model=QuestionResponse)
async def generate_questions(request: QuestionRequest):
    try:
        questions = generate_expected_questions(request.summary_text)
        return QuestionResponse(
            lecture_id=request.lecture_id,
            questions=questions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
