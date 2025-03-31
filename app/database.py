from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# DB URL 설정
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# Base 정의 (모든 모델이 상속할 기본 클래스)
Base = declarative_base()

# 세션 생성
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# DB 세션 생성 함수 (비동기)
async def get_db():
    async with async_session() as session:
        yield session
