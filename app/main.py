from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import (
    chat_history,
    snapshots,
    assignment,     # ✅ 제출 및 피드백만 사용하는 과제 라우터 (유지) 
    vad,             # ✅ 음성 감지 라우터 (유지)
    ask_assistant
)
from app.auth import router as auth_router
from app.routes.lecture import router as lecture_router

from app.database import Base, engine

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

# ✅ Permissions-Policy 헤더
@app.middleware("http")
async def add_permissions_policy_header(request, call_next):
    response = await call_next(request)
    response.headers["Permissions-Policy"] = "microphone=(self)"
    return response

# 라우터 등록
app.include_router(chat_history.router)
app.include_router(snapshots.router, prefix="/snapshots", tags=["Snapshots"])
app.include_router(auth_router)
app.include_router(lecture_router)
app.include_router(assignment.router, prefix="/assignments", tags=["Assignments"])
app.include_router(vad.router, prefix="/vad", tags=["VAD"])
app.include_router(ask_assistant.router)

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
