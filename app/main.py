from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import health, upload, quiz, ask_rag, chat_history, recording, snapshots, assignment, question
from app.auth import router as auth_router
from app.database import Base, engine
from app.routes.lecture import router as lecture_router
from app.routes import question
app = FastAPI()

# ✅ 비동기 테이블 생성 함수
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ✅ FastAPI 앱 시작 시 테이블 생성
@app.on_event("startup")
async def on_startup():
    await init_models()

# ✅ 라우터 등록
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(chat_history.router)
app.include_router(quiz.router)
app.include_router(ask_rag.router, prefix="/api")
app.include_router(recording.router, prefix="/recordings")
app.include_router(snapshots.router, prefix="/snapshots")
app.include_router(auth_router)
app.include_router(lecture_router)
app.include_router(assignment.router, prefix="/assignments", tags=["Assignments"])
app.include_router(question.router, prefix="/questions", tags=["Questions"])
app.include_router(question.router)
# ✅ 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ✅ ✅ 스냅샷 이미지 정적 파일 서빙 경로 추가
app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")

# ✅ 기본 응답
@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

@app.get("/ping")
def ping():
    return {"message": "Server is running"}

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 로컬 실행용 (주의: 이 방식은 reload=True일 땐 무시됨)
if __name__ == "__main__":
    import uvicorn
    import asyncio

    async def run():
        await init_models()
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

    asyncio.run(run())
