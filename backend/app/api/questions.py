"""Questions API using Supabase Database."""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.models import TestAttempt, TestSession
from app.models.test_session import AttemptStatus
from app.services.question_bank import get_questions_for_attempt

router = APIRouter()


@router.get("/next")
async def get_next_questions(
    attempt_id: str,
    count: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Get next batch of questions for an attempt.
    Returns `count` questions starting from current position.
    """
    try:
        attempt_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt ID format")

    stmt = select(TestAttempt).filter(TestAttempt.id == attempt_uuid)
    res = await db.execute(stmt)
    attempt = res.scalar_one_or_none()

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Test is not in progress")

    # Fetch session to get questions count config
    sess_stmt = select(TestSession).filter(TestSession.id == attempt.session_id)
    sess_res = await db.execute(sess_stmt)
    session = sess_res.scalar_one_or_none()
    
    total_questions = session.questions_count if session else 60

    current_index = attempt.current_question_index
    questions = get_questions_for_attempt(current_index, count)

    return {
        "questions": questions,
        "current_index": current_index,
        "total_questions": total_questions,
        "is_last_batch": current_index + count >= total_questions,
    }
