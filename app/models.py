from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
    ForeignKey,
    Boolean,
    text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# ─────────────────────────────────────────────────────────────────────────────
# JSON 또는 JSONB 타입 선택 (PostgreSQL 우선)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except ImportError:
    from sqlalchemy.types import JSON as JSONType
    JSONType = JSON

# ─────────────────────────────────────────────────────────────────────────────
# 사용자
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")
    is_admin = Column(Boolean, default=False)
    assistant_thread_id = Column(String, nullable=True)

    questions = relationship("QuestionAnswer", back_populates="user", cascade="all, delete-orphan")
    assignment_questions = relationship("AssignmentQuestion", back_populates="user", cascade="all, delete-orphan")
    assignment_threads = relationship("AssignmentThread", back_populates="user", cascade="all, delete-orphan")

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
    questions = Column(JSONType, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ─────────────────────────────────────────────────────────────────────────────
# 강의 및 캡처
# ─────────────────────────────────────────────────────────────────────────────
class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recordings = relationship("Recording", back_populates="lecture", cascade="all, delete-orphan")
    snapshots = relationship("Snapshot", back_populates="lecture", cascade="all, delete-orphan")

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
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    image_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lecture = relationship("Lecture", back_populates="snapshots")

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

    questions = relationship("AssignmentQuestion", back_populates="assignment", cascade="all, delete-orphan")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")
    threads = relationship("AssignmentThread", back_populates="assignment", cascade="all, delete-orphan")

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
    thread_id = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")

# ─────────────────────────────────────────────────────────────────────────────
# 강의 요약 저장 (주제 + 이미지 매핑 포함)
# ─────────────────────────────────────────────────────────────────────────────
class LectureSummary(Base):
    __tablename__ = "lecture_summaries"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    topic = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    image_url_1 = Column(String, nullable=True)
    image_url_2 = Column(String, nullable=True)
    image_url_3 = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())