from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.gpt import generate_expected_questions
from app.services.embedding import get_sentence_embeddings
from app.database import get_db_context
from app.models import QuestionFeedback
from sqlalchemy.future import select
import numpy as np

router = APIRouter()

SIMILARITY_THRESHOLD = 0.8  # 문단 구분 임계값

# ✨ 요청 바디 스키마
class TextChunkRequest(BaseModel):
    text: str

class FeedbackRequest(BaseModel):
    user_id: int
    question_text: str
    knows: bool

# 👉 OPTIONS 및 GET 허용 (프리플라이트 대응)
@router.options("/upload_text_chunk")
@router.get("/upload_text_chunk")
async def dummy_text_route():
    return JSONResponse(content={"message": "This endpoint only accepts POST requests."})

# 👉 텍스트 업로드 처리 (문단 묶기 + 질문 생성)
@router.post("/upload_text_chunk")
async def upload_text_chunk(body: TextChunkRequest):
    try:
        text = body.text.strip()

        if not text:
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")

        sentences = split_text_into_sentences(text)
        if not sentences:
            raise HTTPException(status_code=400, detail="문장 분리 실패")

        embeddings = get_sentence_embeddings(sentences)

        paragraphs = []
        current_paragraph = [sentences[0]]

        for i in range(1, len(sentences)):
            prev_emb = embeddings[i-1]
            curr_emb = embeddings[i]
            similarity = cosine_similarity(prev_emb, curr_emb)

            if similarity >= SIMILARITY_THRESHOLD:
                current_paragraph.append(sentences[i])
            else:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = [sentences[i]]

        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        results = []
        for paragraph in paragraphs:
            questions = generate_expected_questions(paragraph)
            results.append({
                "paragraph": paragraph,
                "questions": questions
            })

        return {
            "results": results
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print("❌ 처리 중 예상치 못한 오류:", str(e))
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ✨ 문장 분리
def split_text_into_sentences(text: str) -> list:
    import re
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

# ✨ 코사인 유사도
def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

# 👉 학생 "모른다" 피드백 제출
@router.post("/feedback")
async def submit_feedback(body: FeedbackRequest):
    try:
        async with get_db_context() as db:
            feedback = QuestionFeedback(
                user_id=body.user_id,
                question_text=body.question_text,
                knows=body.knows
            )
            db.add(feedback)
            await db.commit()

        return {"message": "Feedback 저장 완료"}

    except Exception as e:
        print("❌ Feedback 저장 실패:", str(e))
        raise HTTPException(status_code=500, detail="서버 오류")
