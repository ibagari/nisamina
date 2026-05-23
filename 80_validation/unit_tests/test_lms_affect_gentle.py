"""Tests for M-P3.LMS.AFFECT_GENTLE — engagement signals (privacy-respecting)."""
from __future__ import annotations
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.affect_gentle import (
    AffectState, GentleNudgeGenerator, NudgeKind,
    DEFAULT_HARD_STOP_MINUTES, DEFAULT_FRUSTRATION_WINDOW_INCORRECT,
)


def _t0() -> datetime:
    return datetime(2026, 5, 23, 9, 0, 0, tzinfo=timezone.utc)


def test_no_nudge_for_fresh_state_without_optin():
    state = AffectState(learner_id="L1", envir="belize", session_start=_t0())
    gen = GentleNudgeGenerator()
    nudge = gen.maybe_nudge(state, now=_t0() + timedelta(minutes=10))
    assert nudge is None


def test_hard_stop_enforced_regardless_of_optin():
    """California 3-hour cap is non-optional even without opt-in."""
    state = AffectState(
        learner_id="L1", envir="belize",
        session_start=_t0(),
        opt_in_engagement_signals=False,
    )
    gen = GentleNudgeGenerator()
    nudge = gen.maybe_nudge(state, now=_t0() + timedelta(minutes=DEFAULT_HARD_STOP_MINUTES + 1))
    assert nudge is not None
    assert nudge.nudge_kind == NudgeKind.HARD_STOP
    assert nudge.is_blocking is True


def test_pace_down_enforced_regardless_of_optin():
    """Frustration safety: pace-down fires even without opt-in."""
    state = AffectState(
        learner_id="L1", envir="belize",
        session_start=_t0(),
        consecutive_incorrect=DEFAULT_FRUSTRATION_WINDOW_INCORRECT,
        opt_in_engagement_signals=False,
    )
    gen = GentleNudgeGenerator()
    nudge = gen.maybe_nudge(state, now=_t0() + timedelta(minutes=10))
    assert nudge is not None
    assert nudge.nudge_kind == NudgeKind.PACE_DOWN
    assert nudge.is_blocking is False


def test_soft_break_only_with_optin():
    """Soft nudges (break, gentle return, positive surfacing) need opt-in."""
    state_no_optin = AffectState(
        learner_id="L1", envir="belize",
        session_start=_t0(),
        opt_in_engagement_signals=False,
    )
    state_optin = AffectState(
        learner_id="L1", envir="belize",
        session_start=_t0(),
        opt_in_engagement_signals=True,
    )
    gen = GentleNudgeGenerator()
    # 45 min in, no opt-in: nothing
    n1 = gen.maybe_nudge(state_no_optin, now=_t0() + timedelta(minutes=46))
    assert n1 is None
    # 45 min in, opt-in: break suggestion
    n2 = gen.maybe_nudge(state_optin, now=_t0() + timedelta(minutes=46))
    assert n2 is not None
    assert n2.nudge_kind == NudgeKind.BREAK


def test_positive_surfacing_on_streak():
    """10 consecutive correct → positive surfacing (opt-in)."""
    state = AffectState(
        learner_id="L1", envir="belize",
        session_start=_t0(),
        consecutive_correct=10,
        opt_in_engagement_signals=True,
    )
    gen = GentleNudgeGenerator()
    nudge = gen.maybe_nudge(state, now=_t0() + timedelta(minutes=15))
    assert nudge is not None
    assert nudge.nudge_kind == NudgeKind.POSITIVE_SURFACING


def test_gentle_return_after_absence():
    state = AffectState(
        learner_id="L1", envir="belize",
        session_start=_t0(),
        last_session_end=_t0() - timedelta(days=7),
        opt_in_engagement_signals=True,
    )
    gen = GentleNudgeGenerator()
    nudge = gen.maybe_nudge(state, now=_t0() + timedelta(minutes=2))
    assert nudge is not None
    assert nudge.nudge_kind == NudgeKind.GENTLE_RETURN


def test_no_repeat_nudge_within_session():
    """Same nudge shouldn't fire twice in one session."""
    state = AffectState(
        learner_id="L1", envir="belize",
        session_start=_t0(),
        consecutive_incorrect=10,
        nudges_seen_this_session=[NudgeKind.PACE_DOWN],
    )
    gen = GentleNudgeGenerator()
    nudge = gen.maybe_nudge(state, now=_t0() + timedelta(minutes=10))
    assert nudge is None or nudge.nudge_kind != NudgeKind.PACE_DOWN


def test_no_camera_no_mic_no_biometrics_in_state():
    """Privacy-first design check: AffectState has no biometric fields."""
    state = AffectState(learner_id="L1", envir="belize")
    forbidden_fields = {"camera", "mic", "biometric", "eye_track", "heart_rate", "skin_response"}
    actual_fields = set(state.__dataclass_fields__.keys())
    assert not (actual_fields & forbidden_fields), \
        f"AffectState contains forbidden biometric fields: {actual_fields & forbidden_fields}"
