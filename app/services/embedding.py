from openai import OpenAI
import os
from dotenv import load_dotenv

# ✅ API 키 로딩
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ 문장 리스트를 받아 임베딩 벡터 리스트로 변환
def get_sentence_embeddings(sentences: list) -> list:
    if not sentences:
        return []

    texts = [s.replace("\n", " ") for s in sentences]

    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=texts
        )
        embeddings = [e.embedding for e in response.data]
        return embeddings
    except Exception as e:
        print("❌ 임베딩 실패:", str(e))
        raise
