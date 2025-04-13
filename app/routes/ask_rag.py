from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Embedding, QuestionAnswer
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken
from app.auth import get_current_user_id, verify_student

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

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

def get_top_chunks(query_vec, embedding_objs, top_n=5):
    db_vectors = np.array([json.loads(e.embedding) for e in embedding_objs])
    similarities = cosine_similarity([query_vec], db_vectors)[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    return [embedding_objs[i] for i in top_indices]

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

@router.get("/ask_rag")
async def ask_rag(
    q: str = Query(..., description="질문을 입력하세요"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: str = Depends(verify_student)
):
    # 캐시된 질문 있으면 바로 반환
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

    result = await db.execute(select(Embedding))
    embedding_chunks = result.scalars().all()
    if not embedding_chunks:
        raise HTTPException(status_code=404, detail="강의자료 임베딩이 존재하지 않습니다.")

    top_chunks = get_top_chunks(query_embedding, embedding_chunks, top_n=5)
    context = build_context(top_chunks, max_total_tokens=3000)

    if not context:
        raise HTTPException(status_code=400, detail="질문과 관련된 강의자료를 찾지 못했습니다.")

    prompt = f"""
아래 강의자료 발췌를 참고하여 학생의 질문에 정확하고 간결하게 답변하세요. 줄바꿈은 <br>로 표시합니다.

--- 강의자료 발췌 시작 ---
{context}
--- 강의자료 발췌 끝 ---

질문: {q}
답변:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
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
