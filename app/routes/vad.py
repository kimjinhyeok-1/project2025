from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.services.gpt import generate_expected_questions
from app.services.embedding import get_sentence_embeddings
from app.database import get_db_context
from app.models import GeneratedQuestion
from sqlalchemy.future import select
import numpy as np
import asyncio
import re
from collections import defaultdict
import random

router = APIRouter()

# ░ 문단 누적 버퍼 (lecture_id 없이도 작동하도록 기본 키 사용) ░
DEFAULT_LECTURE_ID = 9999
paragraph_buffers: dict[int, list[str]] = defaultdict(list)

# ░ 하이퍼파라미터 ░
SIMILARITY_THRESHOLD = 0.75
MAX_PARAGRAPH_LENGTH = 5
MIN_PARAGRAPH_LENGTH = 20
MIN_PARAGRAPH_SENTENCES = 2
MAX_PARALLEL_CALLS = 3

# ░ 요청 스키마 ░
class TextChunkRequest(BaseModel):
    text: str

# ░ OPTIONS/GET Dummy Route (프리플라이트 대응용) ░
@router.options("/upload_text_chunk")
@router.get("/upload_text_chunk")
async def dummy_text_route():
    return JSONResponse({"message": "This endpoint only accepts POST requests."})

# ░ 실시간 질문 생성 API ░
@router.post("/upload_text_chunk")
async def upload_text_chunk(
    body: TextChunkRequest,
    lecture_id: int = Query(DEFAULT_LECTURE_ID, description="선택적 lecture_id, 기본값 9999")
):
    text = body.text.strip()
    if not text:
        raise HTTPException(400, detail="텍스트가 비어있습니다.")

    new_sentences = split_text_into_sentences(text)
    if not new_sentences:
        raise HTTPException(400, detail="문장 분리 실패")

    # 문단 버퍼 누적
    paragraph_buffers[lecture_id].extend(new_sentences)
    buffered = paragraph_buffers[lecture_id]

    if len(buffered) < MIN_PARAGRAPH_SENTENCES:
        return {"message": "문단 길이 부족 → 누적만 진행", "results": []}

    # 문단 구성
    embeddings = get_sentence_embeddings(buffered)
    paragraphs = group_sentences_into_paragraphs(buffered, embeddings)

    confirmed = paragraphs[:-1] if len(paragraphs) > 1 else []
    paragraph_buffers[lecture_id] = split_text_into_sentences(paragraphs[-1]) if paragraphs else []

    results, orm_objs = [], []
    sem = asyncio.Semaphore(MAX_PARALLEL_CALLS)

    async def ask_gpt(para: str):
        async with sem:
            return await asyncio.to_thread(generate_expected_questions, para)

    tasks = [ask_gpt(p) for p in confirmed if is_valid_paragraph(p)]
    questions_list = await asyncio.gather(*tasks)

    for para, qs in zip(confirmed, questions_list):
        if not qs:
            continue
        results.append({"paragraph": para, "questions": qs})
        orm_objs.append(GeneratedQuestion(paragraph=para, questions=qs))

    if orm_objs:
        async with get_db_context() as db:
            db.add_all(orm_objs)
            await db.commit()

    return {"results": results}

# ░ 랜덤 질문 추출 API ░
@router.get("/questions/random_sample")
async def get_random_sample_questions(count: int = 2):
    async with get_db_context() as db:
        result = await db.execute(select(GeneratedQuestion).order_by(GeneratedQuestion.created_at.desc()))
        rows = result.scalars().all()

        if not rows:
            raise HTTPException(404, detail="예상 질문이 존재하지 않습니다.")

        all_questions = []
        for row in rows:
            all_questions.extend(row.questions)

        if len(all_questions) == 0:
            raise HTTPException(404, detail="생성된 질문이 없습니다.")

        sample_count = min(count, len(all_questions))
        random_questions = random.sample(all_questions, sample_count)

        return {
            "questions": random_questions
        }

# ░ 유틸 함수 ░
def split_text_into_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", text) if s.strip()]

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    return 0.0 if denom == 0 else float(np.dot(v1, v2) / denom)

def is_valid_paragraph(text: str) -> bool:
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
