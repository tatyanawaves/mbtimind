"""Test Sessions API endpoints using Supabase Database."""
import secrets
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import TestSession, TestAttempt, Organization, User, Answer
from app.models.test_session import SessionStatus, AttemptStatus
from app.models.user import UserRole
from app.schemas.test_session import (
    TestSessionCreate,
    TestSessionResponse,
    StartTestRequest,
    StartTestResponse,
    ParticipantResponse,
    SessionDetailResponse,
)

router = APIRouter()


def _generate_invite_code() -> str:
    """Generate a unique 6-char invite code."""
    return secrets.token_urlsafe(4)[:6].upper()


async def _get_default_tenant(db: AsyncSession):
    """Retrieve first available Org and User to attach sessions to."""
    # Find Org
    org_stmt = select(Organization).limit(1)
    org_res = await db.execute(org_stmt)
    org = org_res.scalar_one_or_none()

    if not org:
        org = Organization(
            id=uuid.uuid4(),
            name="Default Org",
            org_type="hr",
            contact_email="default@mbtimind.ru",
            is_active=True
        )
        db.add(org)
        await db.flush()

    # Find Admin User
    user_stmt = select(User).filter(User.role == UserRole.ADMIN).limit(1)
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()

    if not user:
        user = User(
            id=uuid.uuid4(),
            email="admin@mbtimind.ru",
            full_name="Mind Admin",
            role=UserRole.ADMIN,
            organization_id=org.id,
            is_active=True
        )
        db.add(user)
        await db.flush()

    return org, user


@router.post("/", response_model=TestSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(data: TestSessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new test session (admin endpoint)."""
    org, admin = await _get_default_tenant(db)

    invite_code = _generate_invite_code()
    session_id = uuid.uuid4()

    session = TestSession(
        id=session_id,
        title=data.title,
        description=data.description,
        status=SessionStatus.ACTIVE,
        invite_code=invite_code,
        questions_count=data.questions_count,
        time_limit_minutes=data.time_limit_minutes,
        allow_retake=data.allow_retake,
        show_results_to_participant=data.show_results_to_participant,
        organization_id=org.id,
        created_by_id=admin.id,
    )
    db.add(session)
    await db.commit()

    return TestSessionResponse(
        id=str(session.id),
        title=session.title,
        description=session.description,
        status=session.status.value,
        invite_code=session.invite_code,
        questions_count=session.questions_count,
        time_limit_minutes=session.time_limit_minutes,
        allow_retake=session.allow_retake,
        show_results_to_participant=session.show_results_to_participant,
        created_at=session.created_at or datetime.utcnow(),
        participants_count=0,
        completed_count=0,
    )


@router.get("/{session_id}", response_model=TestSessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get session details (admin endpoint)."""
    try:
        sess_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    stmt = select(TestSession).filter(TestSession.id == sess_uuid)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Aggregate counts
    part_stmt = select(func.count(TestAttempt.id)).filter(TestAttempt.session_id == sess_uuid)
    comp_stmt = select(func.count(TestAttempt.id)).filter(
        TestAttempt.session_id == sess_uuid, TestAttempt.status == AttemptStatus.COMPLETED
    )
    
    participants_count = (await db.execute(part_stmt)).scalar() or 0
    completed_count = (await db.execute(comp_stmt)).scalar() or 0

    return TestSessionResponse(
        id=str(session.id),
        title=session.title,
        description=session.description,
        status=session.status.value,
        invite_code=session.invite_code,
        questions_count=session.questions_count,
        time_limit_minutes=session.time_limit_minutes,
        allow_retake=session.allow_retake,
        show_results_to_participant=session.show_results_to_participant,
        created_at=session.created_at,
        participants_count=participants_count,
        completed_count=completed_count,
    )


@router.get("/", response_model=list[TestSessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all sessions for current organization."""
    stmt = select(TestSession)
    res = await db.execute(stmt)
    sessions = res.scalars().all()

    result = []
    for session in sessions:
        part_stmt = select(func.count(TestAttempt.id)).filter(TestAttempt.session_id == session.id)
        comp_stmt = select(func.count(TestAttempt.id)).filter(
            TestAttempt.session_id == session.id, TestAttempt.status == AttemptStatus.COMPLETED
        )
        
        participants_count = (await db.execute(part_stmt)).scalar() or 0
        completed_count = (await db.execute(comp_stmt)).scalar() or 0

        result.append(
            TestSessionResponse(
                id=str(session.id),
                title=session.title,
                description=session.description,
                status=session.status.value,
                invite_code=session.invite_code,
                questions_count=session.questions_count,
                time_limit_minutes=session.time_limit_minutes,
                allow_retake=session.allow_retake,
                show_results_to_participant=session.show_results_to_participant,
                created_at=session.created_at,
                participants_count=participants_count,
                completed_count=completed_count,
            )
        )
    return result


@router.get("/{session_id}/detail", response_model=SessionDetailResponse)
async def get_session_detail(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get session with full participants list (admin endpoint)."""
    try:
        sess_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    stmt = select(TestSession).filter(TestSession.id == sess_uuid)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Gather attempts
    attempt_stmt = select(TestAttempt, User).join(User, TestAttempt.user_id == User.id).filter(
        TestAttempt.session_id == sess_uuid
    )
    attempts_res = await db.execute(attempt_stmt)
    rows = attempts_res.all()

    participants = []
    participants_count = 0
    completed_count = 0

    for attempt, user in rows:
        participants_count += 1
        if attempt.status == AttemptStatus.COMPLETED:
            completed_count += 1

        participants.append(
            ParticipantResponse(
                attempt_id=str(attempt.id),
                user_name=user.full_name,
                user_email=user.email,
                status=attempt.status.value,
                started_at=attempt.started_at,
                completed_at=attempt.completed_at,
                mbti_type=attempt.mbti_type,
                confidence_score=attempt.confidence_score,
            )
        )

    return SessionDetailResponse(
        id=str(session.id),
        title=session.title,
        description=session.description,
        status=session.status.value,
        invite_code=session.invite_code,
        questions_count=session.questions_count,
        time_limit_minutes=session.time_limit_minutes,
        allow_retake=session.allow_retake,
        show_results_to_participant=session.show_results_to_participant,
        created_at=session.created_at,
        participants_count=participants_count,
        completed_count=completed_count,
        participants=participants,
    )


@router.patch("/{session_id}/status")
async def update_session_status(session_id: str, new_status: str = "closed", db: AsyncSession = Depends(get_db)):
    """Close or reactivate a session (admin endpoint)."""
    try:
        sess_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    if new_status not in ("active", "closed"):
        raise HTTPException(status_code=400, detail="Status must be 'active' or 'closed'")

    db_status = SessionStatus.ACTIVE if new_status == "active" else SessionStatus.COMPLETED

    stmt = select(TestSession).filter(TestSession.id == sess_uuid)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = db_status
    await db.commit()

    return {"status": "ok", "new_status": new_status}


@router.post("/join", response_model=StartTestResponse)
async def join_session(data: StartTestRequest, db: AsyncSession = Depends(get_db)):
    """Join a test session using invite code (participant endpoint)."""
    org, _ = await _get_default_tenant(db)

    # Find session by invite code
    stmt = select(TestSession).filter(TestSession.invite_code == data.invite_code.strip())
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")

    # Create participant user
    user_id = uuid.uuid4()
    participant_user = User(
        id=user_id,
        email=data.email.strip() if data.email else f"anonymous-{uuid.uuid4().hex[:6]}@mbtimind.ru",
        full_name=data.full_name.strip(),
        role=UserRole.CANDIDATE,
        organization_id=org.id,
        is_active=True,
    )
    db.add(participant_user)
    await db.flush()

    # Create attempt
    attempt_id = uuid.uuid4()
    attempt = TestAttempt(
        id=attempt_id,
        session_id=session.id,
        user_id=participant_user.id,
        status=AttemptStatus.IN_PROGRESS,
        started_at=datetime.utcnow(),
        current_question_index=0,
        answers_given=0,
    )
    db.add(attempt)
    await db.commit()

    return StartTestResponse(
        attempt_id=str(attempt_id),
        session_title=session.title,
        total_questions=session.questions_count,
        time_limit_minutes=session.time_limit_minutes,
    )
