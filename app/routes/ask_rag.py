from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import QuestionAnswer, Embedding
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import numpy as np
import faiss
import tiktoken
from app.auth import get_current_user_id, verify_student

# ======================= 환경 설정 =======================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

# ======================= 전역 상태 =======================
cached_embeddings = []
embedding_id_map = []
faiss_index = {"index": None}  # ✅ 딕셔너리 형태로 상태 공유

# ======================= GPT 임베딩 + 토크나이저 =======================
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def generate_query_embedding(query: str) -> list:
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"임베딩 생성 실패: {e}")

# ======================= FAISS 기반 검색 =======================
def get_top_chunks_faiss(query_vec, top_n=5):
    if faiss_index["index"] is None:
        raise RuntimeError("FAISS 인덱스가 초기화되지 않았습니다.")

    query_np = np.array([query_vec]).astype("float32")
    _, indices = faiss_index["index"].search(query_np, top_n)

    top_chunks = []
    for idx in indices[0]:
        embedding_id = embedding_id_map[idx]
        matched = next((e for e in cached_embeddings if e.id == embedding_id), None)
        if matched:
            top_chunks.append(matched)
    return top_chunks

# ======================= Context 생성 =======================
def build_context(chunks, max_total_tokens=3000):
    context = ""
    total_tokens = 0
    used_ids = set()

    for chunk in chunks:
        if chunk.id in used_ids:
            continue
        chunk_text = chunk.content.strip()
        chunk_tokens = count_tokens(chunk_text)

        if total_tokens + chunk_tokens <= max_total_tokens:
            context += chunk_text + "\n"
            total_tokens += chunk_tokens
            used_ids.add(chunk.id)
        else:
            break
    return context

# ======================= 질문 API =======================
@router.get("/ask_rag")
async def ask_rag(
    q: str = Query(..., description="질문을 입력하세요"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: str = Depends(verify_student)
):
    # 캐시된 답변 확인
    existing = await db.execute(
        select(QuestionAnswer).where(
            QuestionAnswer.question == q,
            QuestionAnswer.user_id == user_id
        )
    )
    cached_answer = existing.scalar_one_or_none()
    if cached_answer:
        return {"answer": cached_answer.answer}

    try:
        query_embedding = generate_query_embedding(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        top_chunks = get_top_chunks_faiss(query_embedding, top_n=5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FAISS 검색 실패: {e}")

    context = build_context(top_chunks)
    if not context:
        raise HTTPException(status_code=400, detail="관련 강의자료를 찾을 수 없습니다.")

    prompt = f"""
--- 강의자료 발췌 시작 ---
{context}
--- 강의자료 발췌 끝 ---

질문: {q}
답변:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "학생의 질문에 친절하고 따뜻하게 답해주세요. "
                        "코드 문제는 정답을 주지 말고, 학생이 스스로 생각해볼 수 있도록 단계별로 힌트를 주세요. "
                        "개념 설명은 명확하게 하되, 지나치게 길지 않게 해주세요. "
                        "줄바꿈은 <br>로 표시해주세요."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7,
        )
        raw_answer = response.choices[0].message.content.strip()
        formatted_answer = raw_answer.replace("\n", "<br>")

        new_qa = QuestionAnswer(
            question=q,
            answer=formatted_answer,
            created_at=datetime.utcnow(),
            user_id=user_id
        )
        db.add(new_qa)
        await db.commit()

        return {"answer": formatted_answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 응답 실패: {str(e)}")
