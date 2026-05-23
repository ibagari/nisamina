"""Tests for D-066 SR-aware MasteryGate extension."""
from __future__ import annotations
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.olm import OpenLearnerModel
from lms._engine.mastery import MasteryGate
from lms._engine.pathway import PathwayKind
from lms._engine.spaced_repetition import Card


def _populate_mastery(olm: OpenLearnerModel, hw: str, n: int = 20) -> None:
    for _ in range(n):
        olm.observe(hw, correct=True)


def test_no_sr_data_means_no_forgotten_at_risk():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    _populate_mastery(olm, "buguya", n=20)
    gate = MasteryGate(olm=olm, pathway=PathwayKind.NOVICE)
    result = gate.check(unit_headwords=("buguya",))
    assert result.forgotten_at_risk_headwords == ()
    assert result.can_advance is True


def test_overdue_mastered_card_flagged_at_risk():
    """Mastered headword + overdue card → flagged but can_advance still True."""
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    _populate_mastery(olm, "buguya", n=20)
    # Card with next_due 2 days ago (overdue)
    overdue = Card(
        card_id="c.buguya",
        headword_garifuna="buguya",
        envir="belize",
        next_due_at=datetime.now(timezone.utc) - timedelta(days=2),
        review_count=3,
    )
    gate = MasteryGate(
        olm=olm,
        pathway=PathwayKind.NOVICE,
        sr_cards_by_headword={"buguya": overdue},
    )
    result = gate.check(unit_headwords=("buguya",))
    # SR overdue flag set but NOT blocking
    assert "buguya" in result.forgotten_at_risk_headwords
    assert result.can_advance is True


def test_unmastered_card_not_flagged_at_risk():
    """At-risk flag only applies to PREVIOUSLY-MASTERED headwords."""
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    # Don't master "buguya"
    overdue = Card(
        card_id="c.buguya",
        headword_garifuna="buguya",
        envir="belize",
        next_due_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    gate = MasteryGate(
        olm=olm,
        pathway=PathwayKind.NOVICE,
        sr_cards_by_headword={"buguya": overdue},
    )
    result = gate.check(unit_headwords=("buguya",))
    # buguya is unmastered, so not at-risk (it's never-mastered)
    assert result.forgotten_at_risk_headwords == ()
    # Gate blocks because buguya is unmastered
    assert result.can_advance is False


def test_card_not_yet_due_not_flagged():
    """A card with next_due in the future is fine."""
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    _populate_mastery(olm, "buguya", n=20)
    future_card = Card(
        card_id="c.buguya",
        headword_garifuna="buguya",
        envir="belize",
        next_due_at=datetime.now(timezone.utc) + timedelta(days=2),
    )
    gate = MasteryGate(
        olm=olm,
        pathway=PathwayKind.NOVICE,
        sr_cards_by_headword={"buguya": future_card},
    )
    result = gate.check(unit_headwords=("buguya",))
    assert result.forgotten_at_risk_headwords == ()


def test_mixed_cards_some_overdue_some_not():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    _populate_mastery(olm, "buguya", n=20)
    _populate_mastery(olm, "nuani", n=20)
    overdue = Card(
        card_id="c.buguya", headword_garifuna="buguya", envir="belize",
        next_due_at=datetime.now(timezone.utc) - timedelta(days=5),
    )
    fresh = Card(
        card_id="c.nuani", headword_garifuna="nuani", envir="belize",
        next_due_at=datetime.now(timezone.utc) + timedelta(days=3),
    )
    gate = MasteryGate(
        olm=olm,
        pathway=PathwayKind.NOVICE,
        sr_cards_by_headword={"buguya": overdue, "nuani": fresh},
    )
    result = gate.check(unit_headwords=("buguya", "nuani"))
    assert "buguya" in result.forgotten_at_risk_headwords
    assert "nuani" not in result.forgotten_at_risk_headwords
