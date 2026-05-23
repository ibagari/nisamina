"""Tests for M-P3.LMS.SR FSRS v5 spaced-repetition scheduler."""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.spaced_repetition import (
    Card, FSRSScheduler, Rating, DEFAULT_RETENTION,
)


def test_first_review_initialises_stability():
    card = Card(card_id="c1", headword_garifuna="buguya", envir="belize")
    sch = FSRSScheduler()
    s = sch.schedule(card, Rating.GOOD)
    assert card.review_count == 1
    assert card.stability > 0
    assert s.interval_days > 0


def test_easy_rating_yields_longer_interval_than_again():
    sch = FSRSScheduler()
    card_easy = Card(card_id="ce", headword_garifuna="x", envir="belize")
    card_again = Card(card_id="ca", headword_garifuna="y", envir="belize")
    s_easy = sch.schedule(card_easy, Rating.EASY)
    s_again = sch.schedule(card_again, Rating.AGAIN)
    assert s_easy.interval_days > s_again.interval_days


def test_again_increments_lapse_count():
    card = Card(card_id="c1", headword_garifuna="buguya", envir="belize")
    sch = FSRSScheduler()
    sch.schedule(card, Rating.GOOD)
    sch.schedule(card, Rating.AGAIN)
    assert card.lapse_count == 1


def test_difficulty_increases_after_again():
    card = Card(card_id="c1", headword_garifuna="buguya", envir="belize")
    sch = FSRSScheduler()
    sch.schedule(card, Rating.GOOD)
    d0 = card.difficulty
    sch.schedule(card, Rating.AGAIN)
    assert card.difficulty > d0


def test_difficulty_decreases_after_easy():
    card = Card(card_id="c1", headword_garifuna="buguya", envir="belize")
    sch = FSRSScheduler()
    sch.schedule(card, Rating.GOOD)
    d0 = card.difficulty
    sch.schedule(card, Rating.EASY)
    assert card.difficulty < d0


def test_difficulty_bounded():
    card = Card(card_id="c1", headword_garifuna="x", envir="belize")
    sch = FSRSScheduler()
    sch.schedule(card, Rating.GOOD)
    for _ in range(100):
        sch.schedule(card, Rating.AGAIN)
    assert 1.0 <= card.difficulty <= 10.0


def test_invalid_retention_raises():
    with pytest.raises(ValueError):
        FSRSScheduler(target_retention=0.4)
    with pytest.raises(ValueError):
        FSRSScheduler(target_retention=1.5)


def test_next_due_in_future():
    card = Card(card_id="c1", headword_garifuna="x", envir="belize")
    sch = FSRSScheduler()
    now = datetime(2026, 5, 23, 12, 0, 0)
    s = sch.schedule(card, Rating.GOOD, now=now)
    assert s.next_due_at > now
