from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text  # text() 임포트 추가
from app.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "Database connected"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
