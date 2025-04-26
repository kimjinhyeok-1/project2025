from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import vad

# ✅ FastAPI 앱 생성
app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://project2025-frontend.onrender.com"],  # 정확한 프론트 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ VAD 라우터 등록
app.include_router(vad.router, prefix="/vad", tags=["VAD"])

# ✅ 기본 엔드포인트
@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

# ✅ 로컬 실행용
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
