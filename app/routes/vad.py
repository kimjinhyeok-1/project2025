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

# ── 하이퍼파라미터 ──────────────────────────────────────────
SIMILARITY_THRESHOLD = 0.75  # 문단 유사도 임계값
MAX_PARAGRAPH_LENGTH   = 5   # 한 문단에 허용할 최대 문장 수
MIN_PARAGRAPH_LENGTH   = 20  # 문단 최소 길이(문자)
MIN_PARAGRAPH_SENTENCES = 2  # 문단 최소 문장 수
MAX_PARALLEL_CALLS      = 3  # GPT 동시 호출 상한

# ──────────────────────────────────────────────────────────────
# 요청 스키마
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
    return JSONResponse({"message": "This endpoint only accepts POST requests."})

# ──────────────────────────────────────────────────────────────
# 핵심 엔드포인트: 텍스트 → 문단 → 질문 생성 → DB 저장
# ──────────────────────────────────────────────────────────────
@router.post("/upload_text_chunk")
async def upload_text_chunk(body: TextChunkRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")

    # 1️⃣ 문장 분리
    sentences = split_text_into_sentences(text)
    if not sentences:
        raise HTTPException(status_code=400, detail="문장 분리 실패")

    # 2️⃣ 임베딩 & 문단 묶기
    embeddings = get_sentence_embeddings(sentences)
    raw_paragraphs = group_sentences_into_paragraphs(sentences, embeddings)

    # 3️⃣ 의미 없는 문단 필터링 (OR 조건)
    paragraphs = [p for p in raw_paragraphs if is_valid_paragraph(p)]
    if not paragraphs:
        return {"results": []}  # 빈 응답이라도 200 OK 반환

    # 4️⃣ 병렬 GPT 호출 (동시 수 3개 제한)
    sem = asyncio.Semaphore(MAX_PARALLEL_CALLS)

    async def ask_gpt(para: str):
        async with sem:
            return await asyncio.to_thread(generate_expected_questions, para)

    questions_list = await asyncio.gather(*(ask_gpt(p) for p in paragraphs))

    # 5️⃣ 결과 정리 & DB 저장 (빈 질문 제외)
    results, orm_objs = [], []
    for para, qs in zip(paragraphs, questions_list):
        if not qs:
            continue
        results.append({"paragraph": para, "questions": qs})
        orm_objs.append(GeneratedQuestion(paragraph=para, questions=qs))

    async with get_db_context() as db:
        if orm_objs:
            db.add_all(orm_objs)
            await db.commit()

    return {"results": results}

# ──────────────────────────────────────────────────────────────
# 질문 전체 조회 (학생용)
# ──────────────────────────────────────────────────────────────
@router.get("/questions")
async def get_all_questions():
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).order_by(GeneratedQuestion.created_at))
        rows = result.scalars().all()
    return {"results": [{"paragraph": r.paragraph, "questions": r.questions} for r in rows]}

# ──────────────────────────────────────────────────────────────
# 학생 피드백 저장 (필요없음)
# ──────────────────────────────────────────────────────────────
@router.post("/feedback")
async def submit_feedback(body: FeedbackRequest):
    async with get_db_context() as db:
        db.add(QuestionFeedback(user_id=body.user_id, question_text=body.question_text, knows=body.knows))
        await db.commit()
    return {"message": "Feedback 저장 완료"}

# ──────────────────────────────────────────────────────────────
# 유틸 함수
# ──────────────────────────────────────────────────────────────
import re

def split_text_into_sentences(text: str) -> list[str]:
    """마침표/물음표/느낌표 + 개행을 문장 경계로 인식"""
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", text) if s.strip()]

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    return 0.0 if denom == 0 else float(np.dot(v1, v2) / denom)

def is_valid_paragraph(text: str) -> bool:
    """문장≥2개 OR 길이≥20자면 유효"""
    return len(split_text_into_sentences(text)) >= MIN_PARAGRAPH_SENTENCES or len(text.strip()) >= MIN_PARAGRAPH_LENGTH

def group_sentences_into_paragraphs(sentences: list[str], embeds: list[np.ndarray]) -> list[str]:
    if not sentences:
        return []
    para_buf, result, count = [sentences[0]], [], 1
    for i in range(1, len(sentences)):
        sim = cosine_similarity(embeds[i-1], embeds[i])
        if sim >= SIMILARITY_THRESHOLD and count < MAX_PARAGRAPH_LENGTH:
            para_buf.append(sentences[i])
            count += 1
        else:
            result.append(" ".join(para_buf))
            para_buf, count = [sentences[i]], 1
    result.append(" ".join(para_buf))
    return result
