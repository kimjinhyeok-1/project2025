from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.gpt import generate_expected_questions
from app.services.embedding import get_sentence_embeddings
from app.database import get_db_context
from app.models import GeneratedQuestion, QuestionFeedback
from sqlalchemy.future import select
import numpy as np
import asyncio
import re

router = APIRouter()

# ── 하이퍼파라미터 ──────────────────────────────────────────
SIMILARITY_THRESHOLD      = 0.3    # 문단 유사도 임계값
MAX_PARAGRAPH_LENGTH      = 5      # 한 문단 허용 최대 문장 수
MIN_PARAGRAPH_LENGTH      = 20     # 문단 최소 글자 수
MIN_PARAGRAPH_SENTENCES   = 2      # 문단 최소 문장 수
MERGE_THRESHOLD_CHARS     = 50     # 이보다 짧으면 병합 후보
MAX_PARALLEL_CALLS        = 3      # GPT 동시 호출 상한

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
# 핵심 엔드포인트
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
    embeddings     = get_sentence_embeddings(sentences)
    raw_paragraphs = group_sentences_into_paragraphs(sentences, embeddings)

    # 3️⃣ 의미 없는 문단 필터링
    paragraphs = [p for p in raw_paragraphs if is_valid_paragraph(p)]
    if not paragraphs:
        return {"results": []}

    # 4️⃣ 짧은 문단 자동 병합 (유사도 기준 포함)
    paragraphs = merge_short_paragraphs(paragraphs)

    # 5️⃣ 병렬 GPT 호출
    sem = asyncio.Semaphore(MAX_PARALLEL_CALLS)
    async def ask_gpt(para: str):
        async with sem:
            return await asyncio.to_thread(generate_expected_questions, para)
    questions_list = await asyncio.gather(*(ask_gpt(p) for p in paragraphs))

    # 6️⃣ DB 저장 및 결과 반환
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
# 전체 질문 조회
# ──────────────────────────────────────────────────────────────
@router.get("/questions")
async def get_all_questions():
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).order_by(GeneratedQuestion.created_at))
        rows = result.scalars().all()
    return {"results": [{"paragraph": r.paragraph, "questions": r.questions} for r in rows]}

# ──────────────────────────────────────────────────────────────
# 학생 피드백 저장
# ──────────────────────────────────────────────────────────────
@router.post("/feedback")
async def submit_feedback(body: FeedbackRequest):
    async with get_db_context() as db:
        db.add(QuestionFeedback(
            user_id=body.user_id,
            question_text=body.question_text,
            knows=body.knows
        ))
        await db.commit()
    return {"message": "Feedback 저장 완료"}

# ──────────────────────────────────────────────────────────────
# 유틸 함수
# ──────────────────────────────────────────────────────────────
def split_text_into_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", text) if s.strip()]

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    return 0.0 if denom == 0 else float(np.dot(v1, v2) / denom)

def is_valid_paragraph(text: str) -> bool:
    return (
        len(split_text_into_sentences(text)) >= MIN_PARAGRAPH_SENTENCES or
        len(text.strip()) >= MIN_PARAGRAPH_LENGTH
    )

def group_sentences_into_paragraphs(sentences: list[str], embeds: list[np.ndarray]) -> list[str]:
    if not sentences:
        return []
    para_buf, result, count = [sentences[0]], [], 1
    for i in range(1, len(sentences)):
        sim = cosine_similarity(embeds[i-1], embeds[i])
        if sim >= SIMILARITY_THRESHOLD and count < MAX_PARAGRAPH_LENGTH:
            para_buf.append(sentences[i]); count += 1
        else:
            result.append(" ".join(para_buf))
            para_buf, count = [sentences[i]], 1
    result.append(" ".join(para_buf))
    return result

def merge_short_paragraphs(paragraphs: list[str]) -> list[str]:
    merged = []
    merged_embeds: list[np.ndarray] = []

    for p in paragraphs:
        # 현재 문단 임베딩
        p_embed = get_sentence_embeddings([p])[0]

        if merged and len(p) < MERGE_THRESHOLD_CHARS:
            # 앞 문단과 의미 유사도 계산
            last_embed = merged_embeds[-1]
            if cosine_similarity(last_embed, p_embed) >= SIMILARITY_THRESHOLD:
                # 유사하면 병합
                merged[-1] += ' ' + p
                # 병합된 텍스트로 embedding 업데이트
                merged_embeds[-1] = get_sentence_embeddings([merged[-1]])[0]
            else:
                # 비유사하면 새 문단
                merged.append(p)
                merged_embeds.append(p_embed)
        else:
            merged.append(p)
            merged_embeds.append(p_embed)

    return merged
