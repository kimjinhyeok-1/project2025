from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 환경 변수 로드
load_dotenv()

# DB URL 설정 (Render + asyncpg용)
DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# Base 정의 (모든 모델이 상속할 클래스)
Base = declarative_base()

# 세션 팩토리
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# FastAPI 라우터용 (Depends용)
async def get_db():
    async with async_session() as session:
        yield session
        
# 일반 async with 용 (main.py의 on_startup에서만 사용)
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_context():
    async with async_session() as session:
        yield session
