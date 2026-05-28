"""Question model — MBTI forced-choice questions."""
from sqlalchemy import Column, String, Integer, Boolean, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin


class MBTIScale(str, enum.Enum):
    EI = "E/I"  # Extraversion / Introversion
    SN = "S/N"  # Sensing / Intuition
    TF = "T/F"  # Thinking / Feeling
    JP = "J/P"  # Judging / Perceiving


class QuestionType(str, enum.Enum):
    FORCED_CHOICE = "forced_choice"  # A or B
    L_SCALE = "l_scale"  # Lie/social desirability scale


class Question(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "questions"

    # Content
    text_ru = Column(String(500), nullable=False)  # Russian text
    text_kz = Column(String(500), nullable=True)   # Kazakh text
    text_en = Column(String(500), nullable=True)   # English text

    # Options (forced choice)
    option_a_ru = Column(String(300), nullable=False)
    option_a_kz = Column(String(300), nullable=True)
    option_b_ru = Column(String(300), nullable=False)
    option_b_kz = Column(String(300), nullable=True)

    # Scoring
    scale = Column(SAEnum(MBTIScale), nullable=True)  # Null for L-scale questions
    question_type = Column(SAEnum(QuestionType), nullable=False, default=QuestionType.FORCED_CHOICE)
    option_a_direction = Column(String(1), nullable=True)  # E, S, T, or J
    option_b_direction = Column(String(1), nullable=True)  # I, N, F, or P

    # Metadata
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    difficulty = Column(Integer, default=1)  # 1-3, for adaptive testing (future)
