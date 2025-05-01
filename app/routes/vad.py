import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.gpt import generate_expected_questions
from app.services.embedding import get_sentence_embeddings
from app.database import get_db_context
from app.models import GeneratedQuestion
from sqlalchemy.future import select
import numpy as np
import openai

router = APIRouter()

# GPT API Key 설정 (환경변수에 반드시 설정되어 있어야 합니다)
openai.api_key = os.getenv("OPENAI_API_KEY")

SIMILARITY_THRESHOLD = 0.8  # 문단 구분 임계값

# ──────────────────────────────────────────────────────────────
# Pydantic 요청 스키마
# ──────────────────────────────────────────────────────────────
class TextChunkRequest(BaseModel):
    text: str

# `/api/evaluate_snapshot` 응답은 "중요" 또는 "무시"로 단순 반환
# ──────────────────────────────────────────────────────────────
@router.get("/evaluate_snapshot")
async def evaluate_snapshot(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="q 파라미터가 필요합니다.")
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "넌 강의 내용을 분석해서, 중요한 문장이면 '중요', 중요하지 않으면 '무시'라고만 대답해."},
                {"role": "user", "content": f"이 문장이 강의에서 중요한 내용인가요? '{q}'"}
            ]
        )
        answer = resp.choices[0].message.content.strip()
        if answer not in ("중요", "무시"):
            # GPT 응답 형식이 다를 경우 기본값으로 처리
            answer = "무시"
        return JSONResponse(content=answer)
    except Exception as e:
        print("❌ 평가 중 오류:", e)
        raise HTTPException(status_code=500, detail="서버 오류")

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
# 텍스트 업로드 → 문단 분리 → 예상 질문 생성 → DB 저장
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

        # 문단 단위로 묶기
        paragraphs = []
        current_paragraph = [sentences[0]]
        for i in range(1, len(sentences)):
            if cosine_similarity(embeddings[i - 1], embeddings[i]) >= SIMILARITY_THRESHOLD:
                current_paragraph.append(sentences[i])
            else:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = [sentences[i]]
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        # 질문 생성 & DB 저장
        results = []
        orm_objects = []
        for paragraph in paragraphs:
            questions = generate_expected_questions(paragraph)
            results.append({"paragraph": paragraph, "questions": questions})
            orm_objects.append(
                GeneratedQuestion(paragraph=paragraph, questions=questions)
            )

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
    """
    학생 페이지에서 생성된 문단·질문 전체를 읽기 전용으로 반환
    """
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
# 유틸 함수
# ──────────────────────────────────────────────────────────────
def split_text_into_sentences(text: str) -> list[str]:
    import re
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return 0.0 if denom == 0 else float(np.dot(vec1, vec2) / denom)
