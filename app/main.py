from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import ( 
    upload, quiz, ask_rag, chat_history,
    recording, snapshots, assignment, question, ask_assistant, ex_question
)
from app.auth import router as auth_router
from app.database import Base, engine, get_db_context
from app.routes.lecture import router as lecture_router
from app.routes import vad
from app.routes.ask_rag import cached_embeddings, faiss_index, embedding_id_map

from sqlalchemy import select
from app.models import Embedding
import json
import numpy as np
import faiss

from dotenv import load_dotenv
import os

# .env 경로 설정 및 로드
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, "..", ".env")
load_dotenv(dotenv_path=env_path)

# 환경 변수 확인
print("✅ OPENAI_ASSISTANT_ID:", os.getenv("OPENAI_ASSISTANT_ID"))

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
origins = ["https://project2025-frontend.onrender.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 모델 초기화
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 앱 시작 시 실행
@app.on_event("startup")
async def on_startup():
    await init_models()

    try:
        async with get_db_context() as db:
            result = await db.execute(select(Embedding))
            cached_embeddings.clear()
            embedding_id_map.clear()

            embeddings = result.scalars().all()
            if not embeddings:
                print("❗ FAISS 초기화: 임베딩 없음")
                return

            cached_embeddings.extend(embeddings)

            vectors = []
            for e in embeddings:
                try:
                    vec = json.loads(e.embedding)
                    vectors.append(vec)
                except Exception as ve:
                    print(f"⚠️ 임베딩 파싱 실패 (id={e.id}): {ve}")

            if not vectors:
                print("❗ FAISS 초기화 실패: 벡터 없음")
                return

            vectors_np = np.array(vectors).astype("float32")
            dimension = len(vectors_np[0])
            index = faiss.IndexFlatL2(dimension)
            index.add(vectors_np)

            faiss_index["index"] = index
            embedding_id_map.extend([e.id for e in embeddings])

            print(f"✅ FAISS 인덱스 초기화 완료: {len(vectors)}개 벡터")

    except Exception as e:
        print(f"🔥 FAISS 초기화 중 예외 발생: {e}")
# ✅ 여기 추가!
@app.middleware("http")
async def add_permissions_policy_header(request, call_next):
    response = await call_next(request)
    response.headers["Permissions-Policy"] = "microphone=(self)"
    return response

# 라우터 등록
app.include_router(upload.router)
app.include_router(chat_history.router)
app.include_router(quiz.router)
app.include_router(ask_rag.router, prefix="/api")
app.include_router(recording.router, prefix="/recordings")
app.include_router(snapshots.router, prefix="/snapshots", tags=["Snapshots"])
app.include_router(auth_router)
app.include_router(lecture_router)
app.include_router(assignment.router, prefix="/assignments", tags=["Assignments"])
app.include_router(question.router)
app.include_router(ex_question.router, prefix="/questions", tags=["Questions"])
app.include_router(ask_assistant.router)
app.include_router(vad.router, prefix="/vad", tags=["VAD"])

# 정적 파일 경로 등록

static_dir = os.path.join(os.getcwd(), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 기본 엔드포인트
@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

@app.get("/ping")
def ping():
    return {"message": "Server is running"}
