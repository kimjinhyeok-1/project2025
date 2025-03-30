from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ✅ 사용자 테이블
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# ✅ 학생 테이블
class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)  # 학번
    name = Column(String, nullable=False)

    # 질문 리스트 (1:N 관계)
    questions = relationship("QuestionAnswer", back_populates="student", cascade="all, delete-orphan")

# ✅ 강의자료 테이블
class LectureMaterial(Base):
    __tablename__ = "pdf_summary"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    file_path = Column(String)
    content = Column(Text)
    embedding = Column(Text)  # 전체 요약 임베딩 (선택사항)

    # Embedding 관계 (1:N)
    embeddings = relationship("Embedding", back_populates="material", cascade="all, delete-orphan")

# ✅ chunk 임베딩 저장 테이블
class Embedding(Base):
    __tablename__ = "embedding"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("pdf_summary.id"))
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding = Column(Text)

    material = relationship("LectureMaterial", back_populates="embeddings")

# ✅ 퀴즈 테이블
class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    options = Column(Text)  # JSON 문자열
    answer = Column(String)
    material_id = Column(Integer, ForeignKey("pdf_summary.id"))

# ✅ 질문-응답 기록 테이블
class QuestionAnswer(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # 🔗 학생 정보 외래키
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    student = relationship("Student", back_populates="questions")

# ✅ 강의 캡처/녹화 데이터
class LectureSnapshot(Base):
    __tablename__ = "lecture_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(String, index=True)
    timestamp = Column(String)
    transcript = Column(Text)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
