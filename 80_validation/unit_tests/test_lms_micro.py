"""Tests for M-P3.LMS.MICRO — 5-minute microlearning units."""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.micro import (
    MicroUnitKind, MicroUnit, MicroSession, DailyMicroDelivery,
    DEFAULT_MICRO_DURATION_MINUTES, MAX_MICRO_DURATION_MINUTES,
)


def _mk_unit() -> MicroUnit:
    return MicroUnit(
        unit_id="micro.001",
        kind=MicroUnitKind.VOCAB_FLASHCARD,
        headword_garifuna="buguya",
        prompt_text="What does 'buguya' mean?",
        correct_response="thank you",
        distractors=("hello", "goodbye", "yes"),
        envir="belize",
    )


def test_micro_unit_default_duration():
    u = _mk_unit()
    assert u.target_duration_minutes == DEFAULT_MICRO_DURATION_MINUTES


def test_micro_unit_rejects_over_max_duration():
    with pytest.raises(ValueError, match="exceeds D-MAX-3 micro convention"):
        MicroUnit(
            unit_id="bad", kind=MicroUnitKind.VOCAB_FLASHCARD,
            headword_garifuna="x", prompt_text="?", correct_response="x",
            target_duration_minutes=MAX_MICRO_DURATION_MINUTES + 1,
        )


def test_micro_unit_accepts_max_duration():
    u = MicroUnit(
        unit_id="ok", kind=MicroUnitKind.VOCAB_FLASHCARD,
        headword_garifuna="x", prompt_text="?", correct_response="x",
        target_duration_minutes=MAX_MICRO_DURATION_MINUTES,
    )
    assert u.target_duration_minutes == MAX_MICRO_DURATION_MINUTES


def test_session_start_then_submit_correct():
    u = _mk_unit()
    s = MicroSession(session_id="s1", learner_id="L1", envir="belize", unit=u)
    s.start()
    assert s.submit("thank you") is True
    assert s.correct is True
    assert s.completed_at is not None


def test_session_submit_incorrect():
    u = _mk_unit()
    s = MicroSession(session_id="s1", learner_id="L1", envir="belize", unit=u)
    s.start()
    assert s.submit("hello") is False


def test_session_cannot_submit_before_start():
    u = _mk_unit()
    s = MicroSession(session_id="s1", learner_id="L1", envir="belize", unit=u)
    with pytest.raises(ValueError, match="not started"):
        s.submit("thank you")


def test_session_cannot_double_submit():
    u = _mk_unit()
    s = MicroSession(session_id="s1", learner_id="L1", envir="belize", unit=u)
    s.start()
    s.submit("thank you")
    with pytest.raises(ValueError, match="already completed"):
        s.submit("nuani")


def test_session_under_target_duration_true():
    u = _mk_unit()  # target_duration_minutes default 3 = 180 s
    s = MicroSession(session_id="s1", learner_id="L1", envir="belize", unit=u)
    t0 = datetime(2026, 5, 23, 12, 0, 0, tzinfo=timezone.utc)
    s.start(now=t0)
    s.submit("thank you", now=t0 + timedelta(seconds=60))  # 60 s
    assert s.under_target_duration() is True


def test_session_over_target_duration_false():
    u = _mk_unit()
    s = MicroSession(session_id="s1", learner_id="L1", envir="belize", unit=u)
    t0 = datetime(2026, 5, 23, 12, 0, 0, tzinfo=timezone.utc)
    s.start(now=t0)
    s.submit("thank you", now=t0 + timedelta(minutes=5))  # 300 s; over 180 s target
    assert s.under_target_duration() is False


def test_cultural_tidbit_accepts_any_nonempty_response():
    u = MicroUnit(
        unit_id="tidbit.001", kind=MicroUnitKind.CULTURAL_TIDBIT,
        headword_garifuna=None, prompt_text="Read about Settlement Day.",
        correct_response=None, envir="belize",
    )
    s = MicroSession(session_id="s1", learner_id="L1", envir="belize", unit=u)
    s.start()
    assert s.submit("read") is True
    # Empty submission would not count as engaged
    s2 = MicroSession(session_id="s2", learner_id="L1", envir="belize", unit=u)
    s2.start()
    assert s2.submit("") is False


# === DailyMicroDelivery ===


def test_delivery_envir_filter():
    delivery = DailyMicroDelivery(learner_id="L1", envir="belize")
    units = (
        _mk_unit(),  # envir=belize
        MicroUnit(
            unit_id="foreign", kind=MicroUnitKind.VOCAB_FLASHCARD,
            headword_garifuna="x", prompt_text="?", correct_response="x",
            envir="honduras",  # different envir
        ),
    )
    delivery.enqueue(units)
    # Only belize units retained
    assert len(delivery.queued_units) == 1
    assert delivery.queued_units[0].envir == "belize"


def test_delivery_max_per_day_cap():
    delivery = DailyMicroDelivery(learner_id="L1", envir="belize", max_per_day=2)
    units = tuple(
        MicroUnit(
            unit_id=f"u{i}", kind=MicroUnitKind.VOCAB_FLASHCARD,
            headword_garifuna="x", prompt_text=f"q{i}", correct_response="a",
            envir="belize",
        )
        for i in range(5)
    )
    delivery.enqueue(units)
    assert len(delivery.queued_units) == 2


def test_delivery_next_unit_pops():
    delivery = DailyMicroDelivery(learner_id="L1", envir="belize")
    delivery.enqueue((_mk_unit(),))
    next_u = delivery.next_unit()
    assert next_u is not None
    assert delivery.next_unit() is None  # queue empty after pop


def test_delivery_already_delivered_today():
    delivery = DailyMicroDelivery(learner_id="L1", envir="belize")
    assert delivery.already_delivered_today() is False
    delivery.mark_delivered(now=datetime(2026, 5, 23, 9, 0, 0, tzinfo=timezone.utc))
    # Same day check
    assert delivery.already_delivered_today(
        now=datetime(2026, 5, 23, 18, 0, 0, tzinfo=timezone.utc),
    ) is True
    # Next day check
    assert delivery.already_delivered_today(
        now=datetime(2026, 5, 24, 9, 0, 0, tzinfo=timezone.utc),
    ) is False
