"""Tests for MBTI Scoring Engine."""
import pytest
from app.services.scoring import MBTIScoringEngine
from app.services.question_bank import QUESTIONS, _qid


@pytest.fixture
def engine():
    return MBTIScoringEngine()


@pytest.fixture
def sample_questions():
    """Return question data in the format the scoring engine expects."""
    return [
        {
            "id": q["id"],
            "scale": q["scale"],
            "question_type": q["question_type"],
            "option_a_direction": q["option_a_direction"],
            "option_b_direction": q["option_b_direction"],
        }
        for q in QUESTIONS
    ]


def _make_answers(questions_data, choice="a", time_ms=3000):
    """Helper: generate answers for all questions with the same choice."""
    return [
        {
            "question_id": q["id"],
            "selected_option": choice,
            "response_time_ms": time_ms,
        }
        for q in questions_data
    ]


class TestMBTIScoring:
    """Test basic scoring logic."""

    def test_all_a_gives_estj(self, engine, sample_questions):
        """Selecting all 'a' options should produce E, S, T, J."""
        answers = _make_answers(sample_questions, choice="a")
        result = engine.calculate_result(answers, sample_questions)

        # All "a" options map to E, S, T, J for MBTI scales
        assert result.mbti_type == "ESTJ"
        assert result.confidence_score > 0.5

    def test_all_b_gives_infp(self, engine, sample_questions):
        """Selecting all 'b' options should produce I, N, F, P."""
        answers = _make_answers(sample_questions, choice="b")
        result = engine.calculate_result(answers, sample_questions)

        assert result.mbti_type == "INFP"
        assert result.confidence_score > 0.5

    def test_mixed_answers(self, engine, sample_questions):
        """Mixed answers should produce valid 4-letter type."""
        import random
        random.seed(42)
        answers = [
            {
                "question_id": q["id"],
                "selected_option": random.choice(["a", "b"]),
                "response_time_ms": random.randint(2000, 8000),
            }
            for q in sample_questions
        ]
        result = engine.calculate_result(answers, sample_questions)

        assert len(result.mbti_type) == 4
        assert result.mbti_type[0] in "EI"
        assert result.mbti_type[1] in "SN"
        assert result.mbti_type[2] in "TF"
        assert result.mbti_type[3] in "JP"
        assert 0.0 <= result.confidence_score <= 1.0

    def test_confidence_high_for_clear_preference(self, engine, sample_questions):
        """Strong preference (all same) should yield high confidence."""
        answers = _make_answers(sample_questions, choice="a", time_ms=4000)
        result = engine.calculate_result(answers, sample_questions)

        # All same choice = maximum clarity on all scales
        assert result.confidence_score > 0.6


class TestIntegrityChecks:
    """Test anti-cheating mechanisms."""

    def test_speed_violations_detected(self, engine, sample_questions):
        """Answers faster than 800ms should be flagged."""
        answers = _make_answers(sample_questions, choice="a", time_ms=200)
        result = engine.calculate_result(answers, sample_questions)

        assert result.integrity.speed_violations > 0
        assert result.integrity.integrity_score < 1.0

    def test_flat_pattern_detected(self, engine, sample_questions):
        """10+ same answers in a row should trigger flat pattern."""
        answers = _make_answers(sample_questions, choice="a", time_ms=3000)
        result = engine.calculate_result(answers, sample_questions)

        # All "a" for 68 questions — definitely a flat pattern
        assert result.integrity.flat_pattern_detected is True

    def test_l_scale_violations(self, engine, sample_questions):
        """L-scale: selecting 'b' (socially desirable) flags violation."""
        # Answer all MBTI questions normally, but all L-scale with "b"
        answers = []
        for q in sample_questions:
            if q["question_type"] == "l_scale":
                answers.append({"question_id": q["id"], "selected_option": "b", "response_time_ms": 3000})
            else:
                answers.append({"question_id": q["id"], "selected_option": "a", "response_time_ms": 3000})

        result = engine.calculate_result(answers, sample_questions)
        # 8 L-scale questions, all "b" = 8 violations
        assert result.integrity.l_scale_violations == 8
        assert result.integrity.is_valid is False

    def test_valid_honest_test(self, engine, sample_questions):
        """Normal test with honest answers should be valid."""
        import random
        random.seed(123)
        answers = []
        for q in sample_questions:
            if q["question_type"] == "l_scale":
                # Honest answer = "a" for L-scale
                answers.append({"question_id": q["id"], "selected_option": "a", "response_time_ms": 4000})
            else:
                answers.append({
                    "question_id": q["id"],
                    "selected_option": random.choice(["a", "b"]),
                    "response_time_ms": random.randint(2000, 10000),
                })

        result = engine.calculate_result(answers, sample_questions)
        assert result.integrity.l_scale_violations == 0
        assert result.integrity.is_valid is True
        assert result.integrity.integrity_score > 0.8


class TestAlternatingPattern:
    """Test alternating pattern detection."""

    def test_alternating_detected(self, engine, sample_questions):
        """a-b-a-b pattern for 10+ answers should be flagged."""
        answers = [
            {
                "question_id": q["id"],
                "selected_option": "a" if i % 2 == 0 else "b",
                "response_time_ms": 3000,
            }
            for i, q in enumerate(sample_questions)
        ]
        result = engine.calculate_result(answers, sample_questions)
        assert result.integrity.alternating_pattern_detected is True
