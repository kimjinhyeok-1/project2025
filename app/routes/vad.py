from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.gpt import generate_expected_questions
from app.services.embedding import get_sentence_embeddings
import numpy as np

router = APIRouter()

SIMILARITY_THRESHOLD = 0.8  # 문단 구분 임계값

# 👉 OPTIONS 및 GET 허용 (CORS 프리플라이트 요청 대응)
@router.options("/upload_text_chunk")
@router.get("/upload_text_chunk")
async def dummy_text_route():
    return JSONResponse(content={"message": "This endpoint only accepts POST requests."})

# 👉 텍스트 업로드 처리
@router.post("/upload_text_chunk")
async def upload_text_chunk(request: Request):
    try:
        body = await request.json()
        text = body.get("text", "").strip()

        # 🔥 텍스트 비었는지 체크
        if not text:
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")

        print(f"✅ 받은 텍스트: {text}")

        # 1. 문장 분리
        sentences = split_text_into_sentences(text)
        if not sentences:
            raise HTTPException(status_code=400, detail="문장 분리 실패")

        # 2. 문장 임베딩
        embeddings = get_sentence_embeddings(sentences)

        # 3. 문단 묶기
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

        print(f"✅ 생성된 문단 수: {len(paragraphs)}")

        # 4. 문단별 예상 질문 생성
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

# ✨ 문장 나누기 함수
def split_text_into_sentences(text: str) -> list:
    import re
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

# ✨ 코사인 유사도 계산 함수
def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)
