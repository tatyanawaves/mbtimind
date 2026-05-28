"""Pydantic schemas for test sessions and attempts."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# --- Test Session ---

class TestSessionCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    questions_count: int = Field(default=60, ge=20, le=120)
    time_limit_minutes: Optional[int] = Field(None, ge=5, le=180)
    allow_retake: bool = False
    show_results_to_participant: bool = True


class TestSessionResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: str
    invite_code: str
    questions_count: int
    time_limit_minutes: Optional[int]
    created_at: datetime
    participants_count: int = 0
    completed_count: int = 0

    class Config:
        from_attributes = True


# --- Test Attempt ---

class StartTestRequest(BaseModel):
    invite_code: str = Field(..., min_length=6, max_length=8)
    full_name: str = Field(..., max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class StartTestResponse(BaseModel):
    attempt_id: UUID
    session_title: str
    total_questions: int
    time_limit_minutes: Optional[int]


# --- Answers ---

class SubmitAnswerRequest(BaseModel):
    question_id: UUID
    selected_option: str = Field(..., pattern="^[ab]$")
    response_time_ms: int = Field(..., ge=0, le=120000)


class SubmitAnswerBatchRequest(BaseModel):
    """Submit multiple answers at once (for offline-first mobile)."""
    answers: list[SubmitAnswerRequest] = Field(..., min_length=1, max_length=120)


# --- Results ---

class ScaleScoreResponse(BaseModel):
    scale: str  # "E/I", "S/N", etc.
    positive_label: str  # "Extraversion"
    negative_label: str  # "Introversion"
    positive_count: int
    negative_count: int
    percentage: float
    dominant: str


class TestResultResponse(BaseModel):
    attempt_id: UUID
    mbti_type: str
    confidence_score: float
    scales: list[ScaleScoreResponse]
    is_valid: bool
    completed_at: Optional[datetime]

    # Type description (populated from knowledge base)
    type_name_ru: Optional[str] = None
    type_description_ru: Optional[str] = None
    career_recommendations: Optional[list[str]] = None


# --- Admin: Participants ---

class ParticipantResponse(BaseModel):
    attempt_id: UUID
    user_name: str
    user_email: Optional[str] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    mbti_type: Optional[str] = None
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True


class SessionDetailResponse(TestSessionResponse):
    """Extended session info with participants list."""
    participants: list[ParticipantResponse] = []
