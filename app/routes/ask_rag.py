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
import tiktoken  # ✅ 토큰 계산 라이브러리
import html

# ✅ 환경변수 로드 및 OpenAI 클라이언트 생성
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

# ✅ tokenizer 설정 (gpt-3.5-turbo 기준)
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

# ✅ 질문 임베딩 생성 함수
def generate_query_embedding(query: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    return response.data[0].embedding

# ✅ 가장 유사한 chunk들을 찾기
def get_top_chunks(query_vec, embedding_objs, top_n=5):
    db_vectors = np.array([json.loads(e.embedding) for e in embedding_objs])
    similarities = cosine_similarity([query_vec], db_vectors)[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    return [embedding_objs[i] for i in top_indices]

# ✅ chunk를 토큰 기준으로 자르기
def build_context(chunks, max_total_tokens=12000):
    context = ""
    total_tokens = 0
    for chunk in chunks:
        chunk_text = chunk.content.strip()
        chunk_tokens = count_tokens(chunk_text)

        if total_tokens + chunk_tokens <= max_total_tokens:
            context += chunk_text + "\n"
            total_tokens += chunk_tokens
        else:
            break
    return context

@router.get("/ask_rag")
async def ask_rag(q: str = Query(..., description="질문을 입력하세요"), db: AsyncSession = Depends(get_db)):
    """RAG 방식으로 강의자료 기반 GPT 답변 제공"""

    try:
        query_embedding = generate_query_embedding(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질문 임베딩 실패: {str(e)}")

    result = await db.execute(select(Embedding))
    embedding_chunks = result.scalars().all()
    if not embedding_chunks:
        raise HTTPException(status_code=404, detail="저장된 임베딩이 없습니다.")

    # ✅ 유사한 chunk 선택 (최대 10개까지 시도)
    top_chunks = get_top_chunks(query_embedding, embedding_chunks, top_n=10)

    # ✅ 토큰 기준 context 구성
    context = build_context(top_chunks, max_total_tokens=12000)

    # ✅ 프롬프트: 간결하고 줄바꿈을 <br>로 표시하도록 명시
    prompt = f"""
강의자료 내용을 참고하여 간결하고 핵심적으로 답변하세요. 줄바꿈은 '\\n' 대신 '<br>'사용하세요.
[참고 내용]{context}[질문]{q}[답변]
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,  # 간결한 답변을 유도하기 위해 제한
            temperature=0.7,
        )
        raw_answer = response.choices[0].message.content.strip()
        escaped_answer = html.escape(raw_answer)
        formatted_answer = escaped_answer.replace("\n", "<br>")

        new_qa = QuestionAnswer(
            question=q,
            answer=formatted_answer,
            created_at=datetime.utcnow()
        )
        db.add(new_qa)
        await db.commit()

        return {"answer": formatted_answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 응답 실패: {str(e)}")
