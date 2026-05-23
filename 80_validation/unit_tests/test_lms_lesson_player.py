"""Tests for M-P3.LMS.B Lesson Player state machine."""
from __future__ import annotations
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.lesson_player import (
    Lesson, Unit, Step, StepKind, LessonState, LessonPlayer,
)


def _mk_lesson() -> Lesson:
    s1 = Step("u1.s1", StepKind.INSTRUCTION, "buguya", "Read aloud.")
    s2 = Step("u1.s2", StepKind.CHECK_FOR_UNDERSTANDING, "buguya",
              "What does buguya mean?", correct_response="thank you")
    s3 = Step("u2.s1", StepKind.PRACTICE, "nuani", "Say nuani.")
    s4 = Step("u2.s2", StepKind.CHECK_FOR_UNDERSTANDING, "nuani",
              "What does nuani mean?", correct_response="our love")
    u1 = Unit("u1", "Greetings", (s1, s2))
    u2 = Unit("u2", "Closing", (s3, s4))
    return Lesson("L1", "belize", "novice", "Day 1 — Greetings", (u1, u2))


def test_lesson_initial_state():
    lp = LessonPlayer(_mk_lesson(), "learner_001")
    assert lp.state == LessonState.PENDING
    assert lp.current_step().step_id == "u1.s1"


def test_lesson_start_transitions_to_in_progress():
    lp = LessonPlayer(_mk_lesson(), "learner_001")
    lp.start()
    assert lp.state == LessonState.IN_PROGRESS


def test_lesson_cannot_start_twice():
    lp = LessonPlayer(_mk_lesson(), "learner_001")
    lp.start()
    with pytest.raises(ValueError):
        lp.start()


def test_lesson_correct_response_advances():
    lp = LessonPlayer(_mk_lesson(), "learner_001")
    lp.start()
    # First step is INSTRUCTION; any non-empty response advances
    assert lp.submit_response("ok") is True
    assert lp.current_step().step_id == "u1.s2"


def test_lesson_check_for_understanding_requires_match():
    lp = LessonPlayer(_mk_lesson(), "learner_001")
    lp.start()
    lp.submit_response("ok")  # u1.s1 advances
    # u1.s2 is a check — wrong answer should not advance
    assert lp.submit_response("hello") is False
    assert lp.current_step().step_id == "u1.s2"
    # Correct answer advances to u2.s1
    assert lp.submit_response("thank you") is True
    assert lp.current_step().step_id == "u2.s1"


def test_lesson_completion_after_all_units():
    lp = LessonPlayer(_mk_lesson(), "learner_001")
    lp.start()
    lp.submit_response("ok")
    lp.submit_response("thank you")
    lp.submit_response("ok")
    lp.submit_response("our love")
    assert lp.state == LessonState.COMPLETED
    assert lp.progress() == 1.0


def test_lesson_accuracy_tracks_correctness():
    lp = LessonPlayer(_mk_lesson(), "learner_001")
    lp.start()
    lp.submit_response("ok")
    lp.submit_response("WRONG")  # incorrect check
    lp.submit_response("thank you")  # correct
    # 2 correct out of 3 attempts = 0.67
    assert lp.accuracy() == pytest.approx(2/3, rel=1e-3)


def test_lesson_review_due_after_completion():
    lp = LessonPlayer(_mk_lesson(), "learner_001")
    lp.start()
    lp.submit_response("ok")
    lp.submit_response("thank you")
    lp.submit_response("ok")
    lp.submit_response("our love")
    assert lp.state == LessonState.COMPLETED
    lp.mark_review_due()
    assert lp.state == LessonState.REVIEW_DUE
