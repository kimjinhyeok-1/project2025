from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ✅ 과제 등록용 요청
class AssignmentCreate(BaseModel):
    title: str
    description: str
    sample_answer: Optional[str] = None

# ✅ 과제 수정용 요청 (추가)
class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sample_answer: Optional[str] = None

# ✅ 과제 조회용 응답
class AssignmentOut(BaseModel):
    id: int
    title: str
    description: str
    sample_answer: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

# ✅ 과제 질문 등록 요청
class AssignmentQuestionCreate(BaseModel):
    assignment_id: int
    content: str  # ✅ 질문 + 코드가 함께 들어있는 필드

# ✅ 과제 질문 응답
class AssignmentQuestionOut(BaseModel):
    id: int
    assignment_id: int
    user_id: int
    question_text: Optional[str]
    code_snippet: Optional[str]
    gpt_answer: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

# ✅ 과제별 질문 리스트 조회 (교수자/관리자용 등)
class AssignmentQuestionListOut(BaseModel):
    assignment: AssignmentOut
    questions: List[AssignmentQuestionOut]
