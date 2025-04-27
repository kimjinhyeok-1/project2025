from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import QuestionAnswer, Embedding
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import os
import numpy as np
import faiss
import tiktoken
import pickle
from app.auth import get_current_user_id, verify_student

# ======================= 환경 설정 =======================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

# ======================= 전역 상태 =======================
cached_embeddings = []
embedding_id_map = []
faiss_index = {"index": None}
query_cache = {}

# ======================= FAISS 저장/불러오기 =======================
def save_faiss_index(path="faiss_index.bin"):
    if faiss_index["index"] is not None:
        faiss.write_index(faiss_index["index"], path)

def load_faiss_index(path="faiss_index.bin"):
    if os.path.exists(path):
        faiss_index["index"] = faiss.read_index(path)

# ======================= GPT 임베딩 + 토크나이저 =======================
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def generate_query_embedding(query: str) -> list:
    if query in query_cache:
        return query_cache[query]
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        embedding = response.data[0].embedding
        query_cache[query] = embedding
        return embedding
    except Exception as e:
        raise RuntimeError(f"임베딩 생성 실패: {e}")

# ======================= 질문 기반 요약 =======================
def summarize_chunk_with_question(chunk_text: str, question: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "아래 강의자료 내용 중 질문에 직접적으로 관련된 핵심 내용을 1~2문장으로 요약해주세요."
                },
                {
                    "role": "user",
                    "content": f"질문: {question}\n내용: {chunk_text}"
                }
            ],
            max_tokens=150,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "[요약 실패: 원문 사용] " + chunk_text[:200]

# ======================= FAISS 기반 검색 =======================
def get_top_chunks_faiss(query_vec, top_n=5):
    if faiss_index["index"] is None:
        raise RuntimeError("FAISS 인덱스가 초기화되지 않았습니다.")

    query_np = np.array([query_vec]).astype("float32")
    distances, indices = faiss_index["index"].search(query_np, top_n)

    top_chunks = []
    for idx, dist in zip(indices[0], distances[0]):
        embedding_id = embedding_id_map[idx]
        matched = next((e for e in cached_embeddings if e.id == embedding_id), None)
        if matched:
            matched.similarity = 1 - dist
            top_chunks.append(matched)
    return top_chunks

# ======================= Context 생성 =======================
def build_context(chunks, question: str, max_total_tokens=3000):
    context = ""
    total_tokens = 0
    used_ids = set()

    for chunk in chunks:
        if chunk.id in used_ids:
            continue

        chunk_text = chunk.content.strip()
        chunk_tokens = count_tokens(chunk_text)

        # 긴 chunk는 질문 기반 요약
        if chunk_tokens > 300:
            chunk_text = summarize_chunk_with_question(chunk_text, question)
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
    # 1. 캐시된 답변 확인
    existing = await db.execute(
        select(QuestionAnswer).where(
            QuestionAnswer.question == q,
            QuestionAnswer.user_id == user_id
        )
    )
    cached_answer = existing.scalar_one_or_none()
    if cached_answer:
        return {"answer": cached_answer.answer}

    # 2. 임베딩 생성
    try:
        query_embedding = generate_query_embedding(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 3. FAISS 유사도 검색
    try:
        top_chunks = get_top_chunks_faiss(query_embedding, top_n=5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FAISS 검색 실패: {e}")

    # 4. 컨텍스트 생성 (질문 기반 요약 포함)
    context = build_context(top_chunks, question=q)
    if not context:
        raise HTTPException(status_code=400, detail="관련 강의자료를 찾을 수 없습니다.")

    # 5. GPT 프롬프트 구성
    prompt = f"""
--- 강의자료 발췌 시작 ---
{context}
--- 강의자료 발췌 끝 ---

질문: {q}
답변은 친절하고 명확하게 작성해주세요.
"""

    # 6. GPT 응답 생성
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "학생의 질문에 친절하고 부드럽게 답해주세요. "
                        "답변할 때 **Markdown 포맷**을 사용해서 제목, 리스트, 코드블럭 등을 정리해주세요. "
                        "또한 리스트 항목이나 중요한 포인트 앞에는 적절한 이모지(✅, 📌, 🚀, 👉 등)를 넣어주세요. "
                        "너무 많은 이모지는 사용하지 말고, 필요한 곳에만 깔끔하게 추가해주세요. "
                        "코딩 문제는 정답 대신 단계별 힌트를 주고, 개념 설명은 명확하고 간결하게 해주세요. "
                        "질문이 강의자료와 관련이 없으면 정중히 안내만 해주세요."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7,
        )
        raw_answer = response.choices[0].message.content.strip()

        # ✅ 줄바꿈 변환 삭제
        formatted_answer = raw_answer

        # 7. 결과 저장
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
