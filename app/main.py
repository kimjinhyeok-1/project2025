from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import ( 
    upload, quiz, ask_rag, chat_history,
    recording, snapshots, assignment, question, ask_assistant, ex_question
)
from app.auth import router as auth_router
from app.database import Base, engine
from app.routes.lecture import router as lecture_router
from app.routes import vad
from app.routes.ask_rag import cached_embeddings, faiss_index, embedding_id_map
from app.database import get_db

# ✅ 환경 변수 로딩
from dotenv import load_dotenv
import os

# .env 파일의 정확한 경로 설정
basedir = os.path.abspath(os.path.dirname(__file__))  # app/ 디렉토리 기준
env_path = os.path.join(basedir, "..", ".env")
load_dotenv(dotenv_path=env_path)

# 로딩 확인 (선택)
print("✅ OPENAI_ASSISTANT_ID:", os.getenv("OPENAI_ASSISTANT_ID"))

app = FastAPI()

origins = ["https://project2025-frontend.onrender.com",]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,               # ✅ * 사용 금지
    allow_credentials=True,              # ✅ 인증을 위해 반드시 필요
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ 비동기 테이블 생성 함수
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ✅ FastAPI 앱 시작 시 테이블 생성
@app.on_event("startup")
async def on_startup():
    await init_models()

    # ✅ FAISS 인덱스 및 임베딩 캐싱
    async with get_db() as db:
        result = await db.execute(select(Embedding))
        cached_embeddings.clear()
        embedding_id_map.clear()

        embeddings = result.scalars().all()
        if not embeddings:
            print("❗FAISS 초기화: 임베딩이 없습니다.")
            return

        cached_embeddings.extend(embeddings)

        vectors = [json.loads(e.embedding) for e in embeddings]
        vectors_np = np.array(vectors).astype("float32")
        dimension = len(vectors_np[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors_np)

        faiss_index = index
        embedding_id_map.extend([e.id for e in embeddings])

        print(f"✅ FAISS 인덱스 초기화 완료: {len(vectors)}개 벡터")

# ✅ 라우터 등록
app.include_router(upload.router)
app.include_router(chat_history.router)
app.include_router(quiz.router)
app.include_router(ask_rag.router, prefix="/api")
app.include_router(recording.router, prefix="/recordings")
app.include_router(snapshots.router, prefix="/snapshots")
app.include_router(auth_router)
app.include_router(lecture_router)
app.include_router(assignment.router, prefix="/assignments", tags=["Assignments"])
app.include_router(question.router)
app.include_router(ex_question.router, prefix="/questions", tags=["Questions"])
app.include_router(ask_assistant.router)  # Assistant 기반 질의응답
app.include_router(vad.router, prefix="/vad", tags=["VAD"])

# ✅ 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")

# ✅ 기본 응답
@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

@app.get("/ping")
def ping():
    return {"message": "Server is running"}




# ✅ 로컬 실행용 (주의: reload=True일 땐 __main__ 무시됨)
if __name__ == "__main__":
    import uvicorn
    import asyncio

    async def run():
        await init_models()
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

    asyncio.run(run())