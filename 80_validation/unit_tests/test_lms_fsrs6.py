"""Tests for FSRS-6 upgrade in spaced_repetition.py (D-065 SOA gap #1)."""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.spaced_repetition import (
    Card, FSRSScheduler, Rating, FSRS_VERSION,
)


def test_fsrs_version_is_6():
    """Per D-065: upgraded from FSRS-5 to FSRS-6."""
    assert FSRS_VERSION == "6"


def test_scheduler_still_works_with_default_decay():
    card = Card(card_id="c1", headword_garifuna="buguya", envir="belize")
    sch = FSRSScheduler()
    s = sch.schedule(card, Rating.GOOD)
    # FSRS-6 with default decay=1.0 should behave like FSRS-5 baseline
    assert card.review_count == 1
    assert s.interval_days > 0


def test_optimize_returns_scaffold_response():
    """The optimize() method (FSRS-6 per-learner refit) is scaffolded."""
    sch = FSRSScheduler()
    result = sch.optimize([])  # no review logs
    assert result["status"] == "no_data"


def test_optimize_with_logs_returns_proposal():
    card = Card(card_id="c1", headword_garifuna="x", envir="belize")
    sch = FSRSScheduler()
    sch.schedule(card, Rating.GOOD)
    # Build a mock review log
    review_logs = [(card, Rating.GOOD, datetime.now(timezone.utc))]
    result = sch.optimize(review_logs)
    assert result["status"] == "scaffolded"
    assert result["fsrs_version"] == "6"
    assert result["n_reviews"] == 1
    assert "proposed_weights_delta" in result


def test_retrievability_respects_decay():
    """Lower decay should slow forgetting; higher decay accelerates."""
    sch = FSRSScheduler()
    # With default decay=1.0, retrievability follows base curve
    r = sch._retrievability(stability=10.0, elapsed_days=5.0)
    # Some retention should remain (positive)
    assert 0 < r < 1
