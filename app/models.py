from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# ✅ 사용자 (학생 / 교수자)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")  # 'student' 또는 'professor'
    is_admin = Column(Boolean, default=False)

    questions = relationship("QuestionAnswer", back_populates="user", cascade="all, delete-orphan")
    assignment_questions = relationship("AssignmentQuestion", back_populates="user", cascade="all, delete-orphan")


# ✅ 질문-응답 기록 (일반 대화형)
class QuestionAnswer(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="questions")


# ✅ 강의
class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    recordings = relationship("Recording", back_populates="lecture", cascade="all, delete-orphan")
    snapshots = relationship("LectureSnapshot", back_populates="lecture", cascade="all, delete-orphan")


# ✅ 녹음 파일 (음성 업로드)
class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=func.now())

    lecture = relationship("Lecture", back_populates="recordings")


# ✅ 강의 중간 이미지 및 텍스트 캡처
class LectureSnapshot(Base):
    __tablename__ = "lecture_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    timestamp = Column(String)
    transcript = Column(Text)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    lecture = relationship("Lecture", back_populates="snapshots")


# ✅ 강의자료 텍스트 전체 요약
class LectureMaterial(Base):
    __tablename__ = "pdf_summary"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    file_path = Column(String)
    content = Column(Text)
    embedding = Column(Text)

    embeddings = relationship("Embedding", back_populates="material", cascade="all, delete-orphan")


# ✅ chunk 임베딩 저장
class Embedding(Base):
    __tablename__ = "embedding"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("pdf_summary.id"))
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding = Column(Text)

    material = relationship("LectureMaterial", back_populates="embeddings")


# ✅ 퀴즈
class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    options = Column(Text)
    answer = Column(String)
    material_id = Column(Integer, ForeignKey("pdf_summary.id"))


# ✅ 과제 정보
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    sample_answer = Column(Text)  # 정답/예시코드 (GPT 참고용)

    created_at = Column(DateTime, default=func.now())

    questions = relationship("AssignmentQuestion", back_populates="assignment", cascade="all, delete-orphan")


# ✅ 과제 질문 + GPT 응답 저장
class AssignmentQuestion(Base):
    __tablename__ = "assignment_questions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    question_text = Column(Text, nullable=True)     # 학생 질문
    code_snippet = Column(Text, nullable=True)      # 코드 질문
    gpt_answer = Column(Text, nullable=True)        # GPT 응답
    created_at = Column(DateTime, default=func.now())

    assignment = relationship("Assignment", back_populates="questions")
    user = relationship("User", back_populates="assignment_questions")
