"""Standalone test runner — no pytest required.

Run: python run_tests.py
Tests the scoring engine and question bank without external dependencies.
"""
import sys
import os
import random

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.scoring import MBTIScoringEngine
from app.services.question_bank import QUESTIONS, get_all_questions_map, get_questions_for_attempt
from app.services.mbti_types import get_type_info, get_all_types

passed = 0
failed = 0


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name} — {detail}")
        failed += 1


def make_answers(questions_data, choice="a", time_ms=3000):
    return [
        {"question_id": q["id"], "selected_option": choice, "response_time_ms": time_ms}
        for q in questions_data
    ]


# ============================================================
print("\n=== Question Bank Tests ===")

test("Has 68 questions total", len(QUESTIONS) == 68, f"Got {len(QUESTIONS)}")

mbti_qs = [q for q in QUESTIONS if q["question_type"] == "forced_choice"]
l_qs = [q for q in QUESTIONS if q["question_type"] == "l_scale"]
test("60 MBTI questions", len(mbti_qs) == 60, f"Got {len(mbti_qs)}")
test("8 L-scale questions", len(l_qs) == 8, f"Got {len(l_qs)}")

ei = [q for q in mbti_qs if q["scale"] == "E/I"]
sn = [q for q in mbti_qs if q["scale"] == "S/N"]
tf = [q for q in mbti_qs if q["scale"] == "T/F"]
jp = [q for q in mbti_qs if q["scale"] == "J/P"]
test("15 E/I questions", len(ei) == 15, f"Got {len(ei)}")
test("15 S/N questions", len(sn) == 15, f"Got {len(sn)}")
test("15 T/F questions", len(tf) == 15, f"Got {len(tf)}")
test("15 J/P questions", len(jp) == 15, f"Got {len(jp)}")

test("All IDs unique", len(set(q["id"] for q in QUESTIONS)) == 68)

batch = get_questions_for_attempt(0, 5)
test("get_questions_for_attempt returns 5", len(batch) == 5)
test("Batch has text_ru field", "text_ru" in batch[0])
test("Batch has NO scale field (hidden from participant)", "scale" not in batch[0])

q_map = get_all_questions_map()
test("get_all_questions_map returns 68 entries", len(q_map) == 68)

# ============================================================
print("\n=== Scoring Engine Tests ===")

engine = MBTIScoringEngine()
q_data = [
    {"id": q["id"], "scale": q["scale"], "question_type": q["question_type"],
     "option_a_direction": q["option_a_direction"], "option_b_direction": q["option_b_direction"]}
    for q in QUESTIONS
]

# All A -> ESTJ
result_a = engine.calculate_result(make_answers(q_data, "a"), q_data)
test("All 'a' -> ESTJ", result_a.mbti_type == "ESTJ", f"Got {result_a.mbti_type}")
test("Confidence > 0.5 for clear preference", result_a.confidence_score > 0.5,
     f"Got {result_a.confidence_score}")

# All B -> INFP
result_b = engine.calculate_result(make_answers(q_data, "b"), q_data)
test("All 'b' -> INFP", result_b.mbti_type == "INFP", f"Got {result_b.mbti_type}")

# Mixed -> valid type
random.seed(42)
mixed_answers = [
    {"question_id": q["id"], "selected_option": random.choice(["a", "b"]),
     "response_time_ms": random.randint(2000, 8000)}
    for q in q_data
]
result_m = engine.calculate_result(mixed_answers, q_data)
test("Mixed -> 4-letter type", len(result_m.mbti_type) == 4)
test("Mixed -> valid letters",
     result_m.mbti_type[0] in "EI" and result_m.mbti_type[1] in "SN"
     and result_m.mbti_type[2] in "TF" and result_m.mbti_type[3] in "JP",
     f"Got {result_m.mbti_type}")
test("Confidence in [0,1]", 0 <= result_m.confidence_score <= 1)

# ============================================================
print("\n=== Integrity Tests ===")

# Speed violations
fast = engine.calculate_result(make_answers(q_data, "a", time_ms=200), q_data)
test("Speed violations detected (200ms)", fast.integrity.speed_violations > 0)
test("Integrity score < 1 with speed violations", fast.integrity.integrity_score < 1.0)

# Flat pattern
test("Flat pattern detected (all same)", fast.integrity.flat_pattern_detected is True)

# Alternating pattern
alt_answers = [
    {"question_id": q["id"], "selected_option": "a" if i % 2 == 0 else "b",
     "response_time_ms": 3000}
    for i, q in enumerate(q_data)
]
result_alt = engine.calculate_result(alt_answers, q_data)
test("Alternating pattern detected", result_alt.integrity.alternating_pattern_detected is True)

# L-scale
l_bad = []
for q in q_data:
    if q["question_type"] == "l_scale":
        l_bad.append({"question_id": q["id"], "selected_option": "b", "response_time_ms": 3000})
    else:
        l_bad.append({"question_id": q["id"], "selected_option": "a", "response_time_ms": 3000})
result_l = engine.calculate_result(l_bad, q_data)
test("L-scale: 8 violations when all 'b'", result_l.integrity.l_scale_violations == 8,
     f"Got {result_l.integrity.l_scale_violations}")
test("L-scale: invalid when > threshold", result_l.integrity.is_valid is False)

# Valid honest test
random.seed(123)
honest = []
for q in q_data:
    if q["question_type"] == "l_scale":
        honest.append({"question_id": q["id"], "selected_option": "a", "response_time_ms": 4000})
    else:
        honest.append({"question_id": q["id"], "selected_option": random.choice(["a", "b"]),
                       "response_time_ms": random.randint(2000, 10000)})
result_h = engine.calculate_result(honest, q_data)
test("Honest test is valid", result_h.integrity.is_valid is True)
test("Honest integrity > 0.8", result_h.integrity.integrity_score > 0.8,
     f"Got {result_h.integrity.integrity_score}")

# ============================================================
print("\n=== MBTI Types Knowledge Base ===")

all_types = get_all_types()
test("16 types in knowledge base", len(all_types) == 16, f"Got {len(all_types)}")

for t in ["INTJ", "ENFP", "ISTP", "ESFJ"]:
    info = get_type_info(t)
    test(f"{t} has name_ru", bool(info["name_ru"]))
    test(f"{t} has 10 careers", len(info["careers"]) == 10, f"Got {len(info['careers'])}")

# ============================================================
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
if failed == 0:
    print("ALL TESTS PASSED!")
else:
    print(f"SOME TESTS FAILED!")
    sys.exit(1)
