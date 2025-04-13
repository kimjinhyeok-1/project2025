from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.database import get_db
from app.models import User
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto",bcrypt__rounds=10) # 로그인 속도 향상
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # ⚠️ Swagger 인증 정상 작동용

# ✅ 역할 Enum 정의
class UserRole(str, Enum):
    student = "student"
    professor = "professor"

# ✅ 현재 사용자 ID 반환
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="토큰 오류")

# ✅ 교수자 권한 확인
async def verify_professor(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        is_admin = payload.get("admin", False)
        if role != "professor" and not is_admin:
            raise HTTPException(status_code=403, detail="교수자 권한이 필요합니다.")
    except JWTError:
        raise HTTPException(status_code=403, detail="토큰 오류 또는 교수자 아님")

# ✅ 학생 권한 확인
async def verify_student(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        is_admin = payload.get("admin", False)
        if role != "student" and not is_admin:
            raise HTTPException(status_code=403, detail="학생 전용 기능입니다.")
    except JWTError:
        raise HTTPException(status_code=403, detail="토큰 오류 또는 학생 아님")

# ✅ 회원가입
@router.post("/register")
async def register(
    name: str,
    password: str,
    role: UserRole = UserRole.student,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.name == name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 등록된 사용자입니다")

    hashed_pw = pwd_context.hash(password)
    user = User(name=name, password=hashed_pw, role=role.value, is_admin=False)
    db.add(user)
    await db.commit()
    return {"message": f"{'교수자' if role.value == 'professor' else '학생'} 회원가입 완료"}

# ✅ 로그인
# login 함수 안에 시간 측정 로그 추가
import time

@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    t0 = time.perf_counter()
    result = await db.execute(select(User).where(User.name == form.username))
    t1 = time.perf_counter()
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(form.password, user.password):
        raise HTTPException(status_code=401, detail="이름 또는 비밀번호가 올바르지 않습니다")

    t2 = time.perf_counter()
    access_token = jwt.encode(
        {
            "sub": user.name,
            "user_id": user.id,
            "role": user.role,
            "admin": user.is_admin,
            "exp": datetime.utcnow() + timedelta(minutes=180)
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    t3 = time.perf_counter()
    return {"access_token": access_token, "token_type": "bearer"}


# ✅ 관리자 권한 부여 (검증 없음)
@router.post("/set_admin")
async def set_admin(
    user_name: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.name == user_name))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    user.is_admin = True
    await db.commit()
    return {"message": f"{user_name}에게 관리자 권한을 부여했습니다."}
