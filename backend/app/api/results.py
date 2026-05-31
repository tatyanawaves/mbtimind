"""Results API with Supabase Database support."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import TestAttempt, TestSession, Answer, User
from app.models.test_session import AttemptStatus, SessionStatus
from app.schemas.test_session import (
    SubmitAnswerRequest,
    SubmitAnswerBatchRequest,
    TestResultResponse,
    ScaleScoreResponse,
)
from app.services.scoring import MBTIScoringEngine
from app.services.question_bank import get_all_questions_map
from app.services.mbti_types import get_type_info

router = APIRouter()
scoring_engine = MBTIScoringEngine()


@router.post("/{attempt_id}/answers")
async def submit_answer(attempt_id: str, data: SubmitAnswerRequest, db: AsyncSession = Depends(get_db)):
    """Submit a single answer and save to Supabase."""
    try:
        attempt_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt ID format")

    # Fetch attempt
    stmt = select(TestAttempt).filter(TestAttempt.id == attempt_uuid)
    res = await db.execute(stmt)
    attempt = res.scalar_one_or_none()

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Test is not in progress")

    # Save answer to DB
    answer = Answer(
        id=uuid.uuid4(),
        attempt_id=attempt.id,
        question_id=uuid.UUID(str(data.question_id)),
        selected_option=data.selected_option,
        response_time_ms=data.response_time_ms,
        question_index=attempt.current_question_index,
    )
    db.add(answer)

    # Update attempt index
    attempt.current_question_index += 1
    attempt.answers_given += 1
    
    await db.commit()

    return {"status": "ok", "progress": attempt.answers_given}


@router.post("/{attempt_id}/answers/batch")
async def submit_answers_batch(attempt_id: str, data: SubmitAnswerBatchRequest, db: AsyncSession = Depends(get_db)):
    """Submit multiple answers at once (mobile offline sync)."""
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

    for answer_data in data.answers:
        answer = Answer(
            id=uuid.uuid4(),
            attempt_id=attempt.id,
            question_id=uuid.UUID(str(answer_data.question_id)),
            selected_option=answer_data.selected_option,
            response_time_ms=answer_data.response_time_ms,
            question_index=attempt.current_question_index,
        )
        db.add(answer)
        attempt.current_question_index += 1
        attempt.answers_given += 1

    await db.commit()
    return {"status": "ok", "progress": attempt.answers_given}


@router.post("/{attempt_id}/complete", response_model=TestResultResponse)
async def complete_test(attempt_id: str, db: AsyncSession = Depends(get_db)):
    """Complete the test and calculate MBTI result."""
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
        raise HTTPException(status_code=400, detail="Test already completed")

    # Load all submitted answers for this attempt
    ans_stmt = select(Answer).filter(Answer.attempt_id == attempt.id)
    ans_res = await db.execute(ans_stmt)
    answers = ans_res.scalars().all()

    if len(answers) < 20:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough answers ({len(answers)}). Minimum 20 required."
        )

    # Format answers for scoring engine
    answers_formatted = [
        {
            "question_id": str(a.question_id),
            "selected_option": a.selected_option,
            "response_time_ms": a.response_time_ms,
        }
        for a in answers
    ]

    # Get questions data for scoring
    questions_map = get_all_questions_map()
    questions_data = [
        questions_map[a["question_id"]]
        for a in answers_formatted
        if a["question_id"] in questions_map
    ]

    # Calculate MBTI result
    result = scoring_engine.calculate_result(answers_formatted, questions_data)

    # Convert Result to db format
    db_scales = {
        k: {"positive": v.positive, "negative": v.negative, "percentage": v.percentage, "dominant": v.dominant}
        for k, v in result.scales.items()
    }

    # Update attempt status
    attempt.status = AttemptStatus.COMPLETED
    attempt.completed_at = datetime.utcnow()
    attempt.mbti_type = result.mbti_type
    attempt.confidence_score = result.confidence_score
    attempt.scores = db_scales
    attempt.is_valid = result.integrity.is_valid
    
    await db.commit()

    # Get type description
    type_info = get_type_info(result.mbti_type)

    # Build response
    scale_labels = {
        "E/I": ("Экстраверсия", "Интроверсия"),
        "S/N": ("Сенсорика", "Интуиция"),
        "T/F": ("Мышление", "Чувство"),
        "J/P": ("Суждение", "Восприятие"),
    }

    scales_response = []
    for scale_name, scale_score in result.scales.items():
        pos_label, neg_label = scale_labels[scale_name]
        scales_response.append(ScaleScoreResponse(
            scale=scale_name,
            positive_label=pos_label,
            negative_label=neg_label,
            positive_count=scale_score.positive,
            negative_count=scale_score.negative,
            percentage=scale_score.percentage,
            dominant=scale_score.dominant,
        ))

    return TestResultResponse(
        attempt_id=attempt_id,
        mbti_type=result.mbti_type,
        confidence_score=result.confidence_score,
        scales=scales_response,
        is_valid=result.integrity.is_valid,
        completed_at=attempt.completed_at,
        type_name_ru=type_info.get("name_ru"),
        type_description_ru=type_info.get("description_ru"),
        career_recommendations=type_info.get("careers"),
    )


@router.get("/{attempt_id}", response_model=TestResultResponse)
async def get_result(attempt_id: str, db: AsyncSession = Depends(get_db)):
    """Get result for a completed attempt."""
    try:
        attempt_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt ID format")

    stmt = select(TestAttempt).filter(TestAttempt.id == attempt_uuid)
    res = await db.execute(stmt)
    attempt = res.scalar_one_or_none()

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != AttemptStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Test not yet completed")

    # Load submitted answers
    ans_stmt = select(Answer).filter(Answer.attempt_id == attempt.id)
    ans_res = await db.execute(ans_stmt)
    answers = ans_res.scalars().all()

    answers_formatted = [
        {
            "question_id": str(a.question_id),
            "selected_option": a.selected_option,
            "response_time_ms": a.response_time_ms,
        }
        for a in answers
    ]

    questions_map = get_all_questions_map()
    questions_data = [
        questions_map[a["question_id"]]
        for a in answers_formatted
        if a["question_id"] in questions_map
    ]

    result = scoring_engine.calculate_result(answers_formatted, questions_data)
    type_info = get_type_info(result.mbti_type)

    scale_labels = {
        "E/I": ("Экстраверсия", "Интроверсия"),
        "S/N": ("Сенсорика", "Интуиция"),
        "T/F": ("Мышление", "Чувство"),
        "J/P": ("Суждение", "Восприятие"),
    }

    scales_response = []
    for scale_name, scale_score in result.scales.items():
        pos_label, neg_label = scale_labels[scale_name]
        scales_response.append(ScaleScoreResponse(
            scale=scale_name,
            positive_label=pos_label,
            negative_label=neg_label,
            positive_count=scale_score.positive,
            negative_count=scale_score.negative,
            percentage=scale_score.percentage,
            dominant=scale_score.dominant,
        ))

    return TestResultResponse(
        attempt_id=attempt_id,
        mbti_type=result.mbti_type,
        confidence_score=result.confidence_score,
        scales=scales_response,
        is_valid=result.integrity.is_valid,
        completed_at=attempt.completed_at,
        type_name_ru=type_info.get("name_ru"),
        type_description_ru=type_info.get("description_ru"),
        career_recommendations=type_info.get("careers"),
    )
