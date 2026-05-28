"""MBTI Scoring Engine.

Implements the core scoring algorithm for MBTI type determination:
- Forced-choice scoring across 4 scales (E/I, S/N, T/F, J/P)
- Confidence score calculation
- Anti-cheating integrity checks (L-scale, speed, pattern detection)

Reference: PRD_TestEngine_v1.md
Formula: confidence = 0.4 * scale_clarity + 0.3 * timing_consistency + 0.3 * integrity_score
"""
from dataclasses import dataclass
from typing import Optional
import statistics


@dataclass
class ScaleScore:
    """Score for a single MBTI scale."""
    positive: int  # E, S, T, or J count
    negative: int  # I, N, F, or P count
    total: int
    percentage: float  # 0-100, towards dominant pole
    dominant: str  # The winning letter


@dataclass
class IntegrityReport:
    """Anti-cheating analysis results."""
    l_scale_violations: int
    speed_violations: int
    flat_pattern_detected: bool
    alternating_pattern_detected: bool
    is_valid: bool
    integrity_score: float  # 0.0 - 1.0


@dataclass
class MBTIResult:
    """Complete MBTI test result."""
    mbti_type: str  # e.g. "INTJ"
    scales: dict[str, ScaleScore]
    confidence_score: float  # 0.0 - 1.0
    integrity: IntegrityReport
    raw_scores: dict[str, int]  # {"E": 12, "I": 18, ...}


class MBTIScoringEngine:
    """Core MBTI scoring algorithm."""

    # Scale pairs
    SCALES = {
        "E/I": ("E", "I"),
        "S/N": ("S", "N"),
        "T/F": ("T", "F"),
        "J/P": ("J", "P"),
    }

    def __init__(
        self,
        min_answer_time_ms: int = 800,
        max_answer_time_ms: int = 60000,
        l_scale_threshold: int = 4,
    ):
        self.min_answer_time_ms = min_answer_time_ms
        self.max_answer_time_ms = max_answer_time_ms
        self.l_scale_threshold = l_scale_threshold

    def calculate_result(
        self,
        answers: list[dict],
        questions: list[dict],
    ) -> MBTIResult:
        """
        Calculate MBTI type from answers.

        Args:
            answers: List of {"question_id": str, "selected_option": "a"|"b", "response_time_ms": int}
            questions: List of {"id": str, "scale": str, "question_type": str,
                       "option_a_direction": str, "option_b_direction": str}

        Returns:
            MBTIResult with type, scores, confidence, and integrity report.
        """
        # Build question lookup
        q_map = {q["id"]: q for q in questions}

        # Score each scale
        raw_scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        l_scale_violations = 0
        response_times = []

        for answer in answers:
            q = q_map.get(answer["question_id"])
            if not q:
                continue

            response_times.append(answer["response_time_ms"])

            # L-scale questions — count "socially desirable" answers
            if q["question_type"] == "l_scale":
                # Option A is always the "honest" answer for L-scale
                if answer["selected_option"] == "b":
                    l_scale_violations += 1
                continue

            # Regular MBTI scoring
            if answer["selected_option"] == "a":
                direction = q["option_a_direction"]
            else:
                direction = q["option_b_direction"]

            if direction:
                raw_scores[direction] += 1

        # Calculate scale scores
        scales = {}
        mbti_letters = []
        for scale_name, (pos, neg) in self.SCALES.items():
            pos_count = raw_scores[pos]
            neg_count = raw_scores[neg]
            total = pos_count + neg_count
            if total > 0:
                dominant = pos if pos_count >= neg_count else neg
                percentage = (max(pos_count, neg_count) / total) * 100
            else:
                dominant = pos  # Default
                percentage = 50.0

            scales[scale_name] = ScaleScore(
                positive=pos_count,
                negative=neg_count,
                total=total,
                percentage=percentage,
                dominant=dominant,
            )
            mbti_letters.append(dominant)

        mbti_type = "".join(mbti_letters)

        # Integrity analysis
        integrity = self._check_integrity(answers, response_times, l_scale_violations)

        # Confidence score
        confidence = self._calculate_confidence(scales, response_times, integrity)

        return MBTIResult(
            mbti_type=mbti_type,
            scales=scales,
            confidence_score=confidence,
            integrity=integrity,
            raw_scores=raw_scores,
        )

    def _check_integrity(
        self,
        answers: list[dict],
        response_times: list[int],
        l_scale_violations: int,
    ) -> IntegrityReport:
        """Run anti-cheating checks."""
        # Speed violations: answers faster than minimum time
        speed_violations = sum(
            1 for t in response_times if t < self.min_answer_time_ms
        )

        # Flat pattern: same answer 10+ times in a row
        flat_pattern = self._detect_flat_pattern(answers, threshold=10)

        # Alternating pattern: a-b-a-b-a-b for 10+ consecutive answers
        alternating_pattern = self._detect_alternating_pattern(answers, threshold=10)

        # Overall validity
        is_valid = (
            l_scale_violations <= self.l_scale_threshold
            and speed_violations <= len(answers) * 0.1  # Max 10% speed violations
            and not flat_pattern
            and not alternating_pattern
        )

        # Integrity score (0.0 - 1.0)
        total_checks = len(answers)
        penalties = (
            l_scale_violations * 0.05
            + speed_violations * 0.03
            + (0.2 if flat_pattern else 0)
            + (0.15 if alternating_pattern else 0)
        )
        integrity_score = max(0.0, min(1.0, 1.0 - penalties))

        return IntegrityReport(
            l_scale_violations=l_scale_violations,
            speed_violations=speed_violations,
            flat_pattern_detected=flat_pattern,
            alternating_pattern_detected=alternating_pattern,
            is_valid=is_valid,
            integrity_score=integrity_score,
        )

    def _detect_flat_pattern(self, answers: list[dict], threshold: int = 10) -> bool:
        """Detect if user selected same option N times in a row."""
        if len(answers) < threshold:
            return False

        streak = 1
        for i in range(1, len(answers)):
            if answers[i]["selected_option"] == answers[i - 1]["selected_option"]:
                streak += 1
                if streak >= threshold:
                    return True
            else:
                streak = 1
        return False

    def _detect_alternating_pattern(self, answers: list[dict], threshold: int = 10) -> bool:
        """Detect a-b-a-b-a-b alternating pattern."""
        if len(answers) < threshold:
            return False

        streak = 2  # Start from index 2 to check pattern
        for i in range(2, len(answers)):
            if answers[i]["selected_option"] == answers[i - 2]["selected_option"]:
                streak += 1
                if streak >= threshold:
                    return True
            else:
                streak = 2
        return False

    def _calculate_confidence(
        self,
        scales: dict[str, ScaleScore],
        response_times: list[int],
        integrity: IntegrityReport,
    ) -> float:
        """
        Calculate confidence score.
        Formula: 0.4 * scale_clarity + 0.3 * timing_consistency + 0.3 * integrity_score
        """
        # Scale clarity: how decisive are the scale splits (away from 50/50)
        clarities = []
        for scale in scales.values():
            if scale.total > 0:
                clarity = abs(scale.positive - scale.negative) / scale.total
            else:
                clarity = 0.0
            clarities.append(clarity)
        scale_clarity = sum(clarities) / len(clarities) if clarities else 0.0

        # Timing consistency: low variance in response times indicates focused attention
        if len(response_times) > 1:
            valid_times = [
                t for t in response_times
                if self.min_answer_time_ms <= t <= self.max_answer_time_ms
            ]
            if len(valid_times) > 1:
                cv = statistics.stdev(valid_times) / statistics.mean(valid_times)
                # CV < 0.3 is very consistent, CV > 1.5 is erratic
                timing_consistency = max(0.0, min(1.0, 1.0 - (cv - 0.3) / 1.2))
            else:
                timing_consistency = 0.5
        else:
            timing_consistency = 0.5

        # Final confidence
        confidence = (
            0.4 * scale_clarity
            + 0.3 * timing_consistency
            + 0.3 * integrity.integrity_score
        )
        return round(max(0.0, min(1.0, confidence)), 3)
