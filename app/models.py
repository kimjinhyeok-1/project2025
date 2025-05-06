from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from sqlalchemy import text

# ─────────────────────────────────────────────────────────────────────────────
# JSON 또는 JSONB 타입 선택 (PostgreSQL 우선)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from sqlalchemy.dialects.postgresql import JSONB          # noqa: F401
    JSONType = JSONB                                          # Postgres
except ImportError:
    from sqlalchemy.types import JSON as JSONType             # 다른 DB

# ─────────────────────────────────────────────────────────────────────────────
# 사용자
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")   # 'student' | 'professor'
    is_admin = Column(Boolean, default=False)
    assistant_thread_id = Column(String, nullable=True)

    questions = relationship(
        "QuestionAnswer", back_populates="user", cascade="all, delete-orphan"
    )
    assignment_questions = relationship(
        "AssignmentQuestion", back_populates="user", cascade="all, delete-orphan"
    )
    assignment_threads = relationship(
        "AssignmentThread", back_populates="user", cascade="all, delete-orphan"
    )

# ─────────────────────────────────────────────────────────────────────────────
# 일반 Q&A 기록
# ─────────────────────────────────────────────────────────────────────────────
class QuestionAnswer(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=text("(now() - interval '8 hour')"))

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="questions")

# ─────────────────────────────────────────────────────────────────────────────
# 교수 → GPT가 생성한 문단·질문 저장
# ─────────────────────────────────────────────────────────────────────────────
class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"

    id = Column(Integer, primary_key=True, index=True)
    paragraph = Column(Text, nullable=False)
    questions = Column(JSONType, nullable=False)        # JSONB 배열
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ─────────────────────────────────────────────────────────────────────────────
# 강의 및 캡처
# ─────────────────────────────────────────────────────────────────────────────
class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)        # optional
    description = Column(String, nullable=True)  # optional
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recordings = relationship(
        "Recording", back_populates="lecture", cascade="all, delete-orphan"
    )
    snapshots = relationship(
        "Snapshot", back_populates="lecture", cascade="all, delete-orphan"
    )

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=func.now())

    lecture = relationship("Lecture", back_populates="recordings")

class Snapshot(Base):
    __tablename__ = "lecture_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    date = Column(String, nullable=False)   # 2025-04-28
    time = Column(String, nullable=False)   # 15:30:00
    text = Column(Text, nullable=False)     # STT 결과
    image_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lecture = relationship("Lecture", back_populates="snapshots")

# ─────────────────────────────────────────────────────────────────────────────
# 강의자료 텍스트 요약 & 임베딩
# ─────────────────────────────────────────────────────────────────────────────
class LectureMaterial(Base):
    __tablename__ = "pdf_summary"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    file_path = Column(String)
    content = Column(Text)
    embedding = Column(Text)   # TODO: pgvector(Vector(1536)) 고려

    embeddings = relationship(
        "Embedding", back_populates="material", cascade="all, delete-orphan"
    )

class Embedding(Base):
    __tablename__ = "embedding"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("pdf_summary.id"))
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding = Column(Text)   # TODO: pgvector(Vector(1536)) 고려

    material = relationship("LectureMaterial", back_populates="embeddings")

# ─────────────────────────────────────────────────────────────────────────────
# 퀴즈 (보기 배열을 JSONB로 저장)
# ─────────────────────────────────────────────────────────────────────────────
class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    options = Column(JSONType)          # ["보기1","보기2",...]
    answer = Column(String)
    material_id = Column(Integer, ForeignKey("pdf_summary.id"))

# ─────────────────────────────────────────────────────────────────────────────
# 과제 관련 테이블
# ─────────────────────────────────────────────────────────────────────────────
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    sample_answer = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    attached_file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    questions = relationship(
        "AssignmentQuestion", back_populates="assignment", cascade="all, delete-orphan"
    )
    submissions = relationship(
        "AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan"
    )
    threads = relationship(
        "AssignmentThread", back_populates="assignment", cascade="all, delete-orphan"
    )

class AssignmentQuestion(Base):
    __tablename__ = "assignment_questions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    question_text = Column(Text, nullable=True)
    code_snippet = Column(Text, nullable=True)
    gpt_answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    assignment = relationship("Assignment", back_populates="questions")
    user = relationship("User", back_populates="assignment_questions")

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    submitted_file_path = Column(String, nullable=False)
    submitted_at = Column(DateTime, default=func.now())

    gpt_feedback = Column(Text, nullable=True)
    gpt_feedback_created_at = Column(DateTime, nullable=True)
    assistant_thread_id = Column(String, nullable=True)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User")

class AssignmentThread(Base):
    __tablename__ = "assignment_threads"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thread_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    assignment = relationship("Assignment", back_populates="threads")
    user = relationship("User", back_populates="assignment_threads")

# ─────────────────────────────────────────────────────────────────────────────
# 학생 피드백 (모른다 / 안다)
# ─────────────────────────────────────────────────────────────────────────────
class QuestionFeedback(Base):
    __tablename__ = "question_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    knows = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")

# ─────────────────────────────────────────────────────────────────────────────
# 전체 요약 저장
# ─────────────────────────────────────────────────────────────────────────────
class Summary(Base):
    __tablename__ = "summary"

    id = Column(Integer, primary_key=True, index=True)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ─────────────────────────────────────────────────────────────────────────────
# Thread 메시지 저장 (지속 대화 컨텍스트)
# ─────────────────────────────────────────────────────────────────────────────
class ThreadMessage(Base):
    __tablename__ = "thread_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thread_id = Column(String, nullable=False)  # OpenAI Thread ID
    role = Column(String, nullable=False)       # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")
