from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 🔽 기존 친구 라우터
from app.routes import health, upload, quiz, ask_rag, lecture_snapshots, chat_history
from app.auth import router as auth_router

# 🔽 너의 라우터 및 모델
from app.routes.recording import router as recording_router
from app.routes import snapshots
from app.database import Base, engine
from app.models import user, recording, lecture as lecture_model  # ⚠️ lecture 라우터는 제거했지만 모델은 유지 가능

app = FastAPI()

# 🔧 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# ✅ 라우터 등록 (친구 라우터들)
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(chat_history.router)
app.include_router(quiz.router)
app.include_router(ask_rag.router)
app.include_router(lecture_snapshots.router)
app.include_router(auth_router)

# ✅ 너 라우터 등록 (lecture는 제거됨)
app.include_router(recording_router, prefix="/recordings")
app.include_router(snapshots.router, prefix="/snapshots")

# ✅ 이미지 접근용 정적 파일 경로 추가
app.mount("/static", StaticFiles(directory="app/static"), name="static")

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
    allow_origins=["*"],  # 개발 시 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 로컬 실행용
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
