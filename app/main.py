from fastapi import FastAPI
from app.routes import health, upload,quiz, ask_rag, lecture_snapshots, chat_history  
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from app.auth import router as auth_router

app = FastAPI()

# 라우터 등록
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(chat_history.router)
app.include_router(quiz.router)
app.include_router(ask_rag.router)
app.include_router(lecture_snapshots.router)  
app.include_router(auth_router)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["http://localhost", "http://127.0.0.1:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 이미지 접근용 정적 파일 경로 추가
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/ping")
def ping():
    return {"message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
