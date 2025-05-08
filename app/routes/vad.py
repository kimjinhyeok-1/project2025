from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.gpt import generate_expected_questions  # Assistant API 기반 함수
from app.services.embedding import get_sentence_embeddings
from app.database import get_db_context
from app.models import GeneratedQuestion, QuestionFeedback
from sqlalchemy.future import select
import numpy as np
import asyncio

router = APIRouter()

SIMILARITY_THRESHOLD = 0.8  # 문단 구분 임계값

# ──────────────────────────────────────────────────────────────
# Pydantic 요청 스키마
# ──────────────────────────────────────────────────────────────
class TextChunkRequest(BaseModel):
    text: str

class FeedbackRequest(BaseModel):
    user_id: int
    question_text: str
    knows: bool

# ──────────────────────────────────────────────────────────────
# 프리플라이트 대응
# ──────────────────────────────────────────────────────────────
@router.options("/upload_text_chunk")
@router.get("/upload_text_chunk")
async def dummy_text_route():
    return JSONResponse(
        content={"message": "This endpoint only accepts POST requests."}
    )

# ──────────────────────────────────────────────────────────────
# 텍스트 업로드 → 문단 분리 → 질문 생성 병렬 처리 → DB 저장
# ──────────────────────────────────────────────────────────────
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
        paragraphs = group_sentences_into_paragraphs(sentences, embeddings)

        # 병렬 질문 생성
        questions_list = await asyncio.gather(*[
            asyncio.to_thread(generate_expected_questions, para)
            for para in paragraphs
        ])

        results, orm_objects = [], []
        for para, questions in zip(paragraphs, questions_list):
            results.append({"paragraph": para, "questions": questions})
            orm_objects.append(GeneratedQuestion(paragraph=para, questions=questions))

        async with get_db_context() as db:
            db.add_all(orm_objects)
            await db.commit()

        return {"results": results}

    except HTTPException:
        raise
    except Exception as e:
        print("❌ 처리 중 오류:", e)
        raise HTTPException(status_code=500, detail="서버 오류")

# ──────────────────────────────────────────────────────────────
# 학생용 질문 조회 API
# ──────────────────────────────────────────────────────────────
@router.get("/questions")
async def get_all_questions():
    try:
        async with get_db_context() as db:
            result = await db.execute(
                select(GeneratedQuestion).order_by(GeneratedQuestion.created_at)
            )
            rows = result.scalars().all()

        return {
            "results": [
                {"paragraph": q.paragraph, "questions": q.questions}
                for q in rows
            ]
        }
    except Exception as e:
        print("❌ 질문 조회 실패:", e)
        raise HTTPException(status_code=500, detail="서버 오류")

# ──────────────────────────────────────────────────────────────
# 학생 피드백 저장
# ──────────────────────────────────────────────────────────────
@router.post("/feedback")
async def submit_feedback(body: FeedbackRequest):
    try:
        async with get_db_context() as db:
            db.add(
                QuestionFeedback(
                    user_id=body.user_id,
                    question_text=body.question_text,
                    knows=body.knows,
                )
            )
            await db.commit()
        return {"message": "Feedback 저장 완료"}

    except Exception as e:
        print("❌ Feedback 저장 실패:", e)
        raise HTTPException(status_code=500, detail="서버 오류")

# ──────────────────────────────────────────────────────────────
# 유틸 함수
# ──────────────────────────────────────────────────────────────
def split_text_into_sentences(text: str) -> list[str]:
    import re
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return 0.0 if denom == 0 else float(np.dot(vec1, vec2) / denom)

def group_sentences_into_paragraphs(sentences: list[str], embeddings: list[np.ndarray]) -> list[str]:
    if not sentences:
        return []
    paragraphs = [sentences[0]]
    result = []
    for i in range(1, len(sentences)):
        if cosine_similarity(embeddings[i - 1], embeddings[i]) >= SIMILARITY_THRESHOLD:
            paragraphs.append(sentences[i])
        else:
            result.append(" ".join(paragraphs))
            paragraphs = [sentences[i]]
    if paragraphs:
        result.append(" ".join(paragraphs))
    return result
