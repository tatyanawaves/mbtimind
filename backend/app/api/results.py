"""Results API — submit answers and get MBTI results."""
from fastapi import APIRouter, HTTPException
from datetime import datetime

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
async def submit_answer(attempt_id: str, data: SubmitAnswerRequest):
    """Submit a single answer."""
    from app.api.test_sessions import _attempts

    attempt = _attempts.get(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt["status"] != "in_progress":
        raise HTTPException(status_code=400, detail="Test is not in progress")

    attempt["answers"].append({
        "question_id": str(data.question_id),
        "selected_option": data.selected_option,
        "response_time_ms": data.response_time_ms,
    })
    attempt["current_question_index"] += 1
    attempt["answers_given"] = len(attempt["answers"])

    return {"status": "ok", "progress": len(attempt["answers"])}


@router.post("/{attempt_id}/answers/batch")
async def submit_answers_batch(attempt_id: str, data: SubmitAnswerBatchRequest):
    """Submit multiple answers at once (mobile offline sync)."""
    from app.api.test_sessions import _attempts

    attempt = _attempts.get(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt["status"] != "in_progress":
        raise HTTPException(status_code=400, detail="Test is not in progress")

    for answer in data.answers:
        attempt["answers"].append({
            "question_id": str(answer.question_id),
            "selected_option": answer.selected_option,
            "response_time_ms": answer.response_time_ms,
        })

    attempt["current_question_index"] += len(data.answers)
    return {"status": "ok", "progress": len(attempt["answers"])}


@router.post("/{attempt_id}/complete", response_model=TestResultResponse)
async def complete_test(attempt_id: str):
    """Complete the test and calculate MBTI result."""
    from app.api.test_sessions import _attempts, _sessions

    attempt = _attempts.get(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt["status"] != "in_progress":
        raise HTTPException(status_code=400, detail="Test already completed")

    if len(attempt["answers"]) < 20:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough answers ({len(attempt['answers'])}). Minimum 20 required."
        )

    # Get questions data for scoring
    questions_map = get_all_questions_map()
    questions_data = [
        questions_map[a["question_id"]]
        for a in attempt["answers"]
        if a["question_id"] in questions_map
    ]

    # Calculate MBTI result
    result = scoring_engine.calculate_result(attempt["answers"], questions_data)

    # Update attempt
    attempt["status"] = "completed"
    attempt["completed_at"] = datetime.utcnow()
    attempt["mbti_type"] = result.mbti_type
    attempt["confidence_score"] = result.confidence_score

    # Update session counters
    session = _sessions.get(attempt["session_id"])
    if session:
        session["completed_count"] += 1

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
        completed_at=attempt["completed_at"],
        type_name_ru=type_info.get("name_ru"),
        type_description_ru=type_info.get("description_ru"),
        career_recommendations=type_info.get("careers"),
    )


@router.get("/{attempt_id}", response_model=TestResultResponse)
async def get_result(attempt_id: str):
    """Get result for a completed attempt."""
    from app.api.test_sessions import _attempts

    attempt = _attempts.get(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt["status"] != "completed":
        raise HTTPException(status_code=400, detail="Test not yet completed")

    # Re-calculate from stored answers
    questions_map = get_all_questions_map()
    questions_data = [
        questions_map[a["question_id"]]
        for a in attempt["answers"]
        if a["question_id"] in questions_map
    ]
    result = scoring_engine.calculate_result(attempt["answers"], questions_data)
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
        completed_at=attempt.get("completed_at"),
        type_name_ru=type_info.get("name_ru"),
        type_description_ru=type_info.get("description_ru"),
        career_recommendations=type_info.get("careers"),
    )
