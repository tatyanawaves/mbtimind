"""Test Sessions API endpoints."""
import secrets
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.schemas.test_session import (
    TestSessionCreate,
    TestSessionResponse,
    StartTestRequest,
    StartTestResponse,
    ParticipantResponse,
    SessionDetailResponse,
)

router = APIRouter()

# In-memory store for MVP (replace with DB in production)
_sessions: dict[str, dict] = {}
_attempts: dict[str, dict] = {}


def _generate_invite_code() -> str:
    """Generate a unique 6-char invite code."""
    return secrets.token_urlsafe(4)[:6].upper()


@router.post("/", response_model=TestSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(data: TestSessionCreate):
    """Create a new test session (admin endpoint)."""
    import uuid
    from datetime import datetime

    session_id = str(uuid.uuid4())
    invite_code = _generate_invite_code()

    session = {
        "id": session_id,
        "title": data.title,
        "description": data.description,
        "status": "active",
        "invite_code": invite_code,
        "questions_count": data.questions_count,
        "time_limit_minutes": data.time_limit_minutes,
        "allow_retake": data.allow_retake,
        "show_results_to_participant": data.show_results_to_participant,
        "created_at": datetime.utcnow(),
        "participants_count": 0,
        "completed_count": 0,
    }
    _sessions[session_id] = session
    return session


@router.get("/{session_id}", response_model=TestSessionResponse)
async def get_session(session_id: str):
    """Get session details (admin endpoint)."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/", response_model=list[TestSessionResponse])
async def list_sessions():
    """List all sessions for current organization."""
    return list(_sessions.values())


@router.get("/{session_id}/detail", response_model=SessionDetailResponse)
async def get_session_detail(session_id: str):
    """Get session with full participants list (admin endpoint)."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Gather all attempts for this session
    participants = []
    for attempt in _attempts.values():
        if attempt.get("session_id") == session_id:
            participants.append(ParticipantResponse(
                attempt_id=attempt["id"],
                user_name=attempt.get("user_name", "Unknown"),
                user_email=attempt.get("user_email"),
                status=attempt.get("status", "in_progress"),
                started_at=attempt.get("started_at"),
                completed_at=attempt.get("completed_at"),
                mbti_type=attempt.get("mbti_type"),
                confidence_score=attempt.get("confidence_score"),
            ))

    return {**session, "participants": participants}


@router.patch("/{session_id}/status")
async def update_session_status(session_id: str, new_status: str = "closed"):
    """Close or reactivate a session (admin endpoint)."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if new_status not in ("active", "closed"):
        raise HTTPException(status_code=400, detail="Status must be 'active' or 'closed'")

    session["status"] = new_status
    return {"status": "ok", "new_status": new_status}


@router.post("/join", response_model=StartTestResponse)
async def join_session(data: StartTestRequest):
    """Join a test session using invite code (participant endpoint)."""
    import uuid
    from datetime import datetime

    # Find session by invite code
    session = None
    for s in _sessions.values():
        if s["invite_code"] == data.invite_code:
            session = s
            break

    if not session:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Session is not active")

    # Create attempt
    attempt_id = str(uuid.uuid4())
    attempt = {
        "id": attempt_id,
        "session_id": session["id"],
        "user_name": data.full_name,
        "user_email": data.email,
        "status": "in_progress",
        "started_at": datetime.utcnow(),
        "current_question_index": 0,
        "answers": [],
    }
    _attempts[attempt_id] = attempt
    session["participants_count"] += 1

    return StartTestResponse(
        attempt_id=attempt_id,
        session_title=session["title"],
        total_questions=session["questions_count"],
        time_limit_minutes=session["time_limit_minutes"],
    )
