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
    has_submitted_assignment = Column(Boolean, default=False)

    questions = relationship("QuestionAnswer", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("AssignmentSubmission", back_populates="student", cascade="all, delete-orphan")

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
# GPT가 생성한 문단·질문 저장
# ─────────────────────────────────────────────────────────────────────────────
class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"

    id = Column(Integer, primary_key=True, index=True)
    paragraph = Column(Text, nullable=False)
    questions = Column(JSONType, nullable=False)
    likes = Column(JSONType, nullable=False, default=dict)  # 질문별 좋아요 수 [0, 0, 0, 0, 0]
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
    snapshots = relationship("Snapshot", back_populates="lecture", cascade="all, delete-orphan")

class Snapshot(Base):
    __tablename__ = "lecture_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    image_path = Column(String, nullable=False)
    is_image = Column(Boolean, nullable=False, default=True)  # ✅ 추가된 필드
    created_at = Column(DateTime, default=datetime.utcnow)
    summary_text = Column(Text, nullable=True)  

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

    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    submitted_file_path = Column(String, nullable=False)
    submitted_at = Column(DateTime, default=func.now())
    gpt_feedback = Column(Text, nullable=True)
    gpt_feedback_created_at = Column(DateTime, nullable=True)
    professor_feedback = Column(Text, nullable=True)
    professor_feedback_created_at = Column(DateTime, nullable=True)
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")

# ─────────────────────────────────────────────────────────────────────────────
# 전체 요약 저장
# ─────────────────────────────────────────────────────────────────────────────
class Summary(Base):
    __tablename__ = "summary"

    id = Column(Integer, primary_key=True, index=True)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
    image_text_1 = Column(Text, nullable=True)

    image_url_2 = Column(String, nullable=True)
    image_text_2 = Column(Text, nullable=True)

    image_url_3 = Column(String, nullable=True)
    image_text_3 = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ─────────────────────────────────────────────────────────────────────────────
# 학생 직접 질문 테이블
# ─────────────────────────────────────────────────────────────────────────────
class StudentQuestion(Base):
    __tablename__ = "student_questions"

    id = Column(Integer, primary_key=True, index=True)
    q_id = Column(Integer, ForeignKey("generated_questions.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    question_set = relationship("GeneratedQuestion", backref="student_questions")
# ─────────────────────────────────────────────────────────────────────────────
# 리마인드 저장
# ───────────────────────────────────────────────────────────────────────────── 
class LectureKeySummary(Base):
    __tablename__ = "lecture_key_summaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())