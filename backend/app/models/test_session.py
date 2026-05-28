"""Test session and attempt models."""
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Enum as SAEnum, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin


class SessionStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    INVALIDATED = "invalidated"  # Failed integrity checks


class TestSession(Base, UUIDMixin, TimestampMixin):
    """Admin-created session for a group of participants."""
    __tablename__ = "test_sessions"

    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(SAEnum(SessionStatus), default=SessionStatus.DRAFT)

    # Config
    questions_count = Column(Integer, default=60)
    time_limit_minutes = Column(Integer, nullable=True)  # Null = no limit
    allow_retake = Column(Boolean, default=False)
    show_results_to_participant = Column(Boolean, default=True)

    # Access
    invite_code = Column(String(8), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Tenant
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="test_sessions")
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    attempts = relationship("TestAttempt", back_populates="session")


class TestAttempt(Base, UUIDMixin, TimestampMixin):
    """Individual test attempt by a participant."""
    __tablename__ = "test_attempts"

    status = Column(SAEnum(AttemptStatus), default=AttemptStatus.IN_PROGRESS)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Progress
    current_question_index = Column(Integer, default=0)
    answers_given = Column(Integer, default=0)

    # Results (populated on completion)
    mbti_type = Column(String(4), nullable=True)  # e.g. "INTJ"
    scores = Column(JSON, nullable=True)  # {"E": 12, "I": 18, "S": 8, ...}
    confidence_score = Column(Float, nullable=True)  # 0.0 - 1.0

    # Integrity
    l_scale_violations = Column(Integer, default=0)
    speed_violations = Column(Integer, default=0)
    flat_pattern_detected = Column(Boolean, default=False)
    is_valid = Column(Boolean, default=True)

    # Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="test_attempts")
    session_id = Column(UUID(as_uuid=True), ForeignKey("test_sessions.id"), nullable=False)
    session = relationship("TestSession", back_populates="attempts")
    answers = relationship("Answer", back_populates="attempt")


class Answer(Base, UUIDMixin):
    """Individual answer to a question."""
    __tablename__ = "answers"

    attempt_id = Column(UUID(as_uuid=True), ForeignKey("test_attempts.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    selected_option = Column(String(1), nullable=False)  # "a" or "b"
    response_time_ms = Column(Integer, nullable=False)  # Time to answer in ms
    question_index = Column(Integer, nullable=False)  # Order in which it was shown

    # Relations
    attempt = relationship("TestAttempt", back_populates="answers")
