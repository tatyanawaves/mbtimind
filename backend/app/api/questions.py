"""Questions API — serves questions to test participants."""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from app.services.question_bank import get_questions_for_attempt

router = APIRouter()


@router.get("/next")
async def get_next_questions(
    attempt_id: str,
    count: int = Query(default=5, ge=1, le=20),
):
    """
    Get next batch of questions for an attempt.
    Returns `count` questions starting from current position.
    """
    from app.api.test_sessions import _attempts

    attempt = _attempts.get(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt["status"] != "in_progress":
        raise HTTPException(status_code=400, detail="Test is not in progress")

    current_index = attempt["current_question_index"]
    questions = get_questions_for_attempt(current_index, count)

    return {
        "questions": questions,
        "current_index": current_index,
        "total_questions": 60,  # From session config
        "is_last_batch": current_index + count >= 60,
    }
