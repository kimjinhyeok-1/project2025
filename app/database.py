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

# 의존성 주입용 비동기 세션 생성 함수
@asynccontextmanager
async def get_db():
    async with async_session() as session:
        yield session
