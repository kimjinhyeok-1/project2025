from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.database import get_db
from app.models import Student
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ✅ JWT 토큰에서 사용자 이름 추출
async def get_current_student_name(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_name = payload.get("sub")
        if student_name is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
        return student_name
    except JWTError:
        raise HTTPException(status_code=401, detail="토큰 오류")

# ✅ 관리자 권한 확인용 디펜던시
async def verify_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    except JWTError:
        raise HTTPException(status_code=403, detail="토큰 오류 또는 관리자 아님")

# ✅ 회원가입 엔드포인트
@router.post("/register")
async def register(name: str, password: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.name == name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 등록된 사용자입니다")

    hashed_pw = pwd_context.hash(password)
    student = Student(name=name, password=hashed_pw)
    db.add(student)
    await db.commit()
    return {"message": "회원가입 완료"}

# ✅ 로그인 엔드포인트
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.name == form.username))
    student = result.scalar_one_or_none()

    if not student or not pwd_context.verify(form.password, student.password):
        raise HTTPException(status_code=401, detail="이름 또는 비밀번호가 올바르지 않습니다")

    access_token = jwt.encode(
        {
            "sub": student.name,
            "admin": student.is_admin,  # ✅ 관리자 여부 포함
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer"}
