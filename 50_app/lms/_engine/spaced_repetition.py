"""M-P3.LMS.SR — FSRS v5 spaced repetition scheduler.

Per F-059 D-MAX-1 + Kim & Webb 2022 (spaced g=1.71 vs massed g=0.58, N=3,411).
Reference: FSRS v5 (Free Spaced Repetition Scheduler; open-source state-of-art).

Simplified FSRS-style implementation:
- Per-card stability (S) + difficulty (D); review intervals computed from retention target.
- Default retention 0.9 (Anki convention).
- Update step uses 4-button rating: AGAIN | HARD | GOOD | EASY (FSRS standard).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from math import exp, log
from typing import Optional


class Rating(IntEnum):
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


# FSRS v5 default weights (subset; full FSRS has 21 weights — these are the dominant ones for scaffold)
_W = {
    "init_stability_again": 0.4,
    "init_stability_hard": 0.9,
    "init_stability_good": 2.3,
    "init_stability_easy": 10.9,
    "init_difficulty": 5.0,
    "difficulty_decay": 0.5,
    "stability_again_factor": 0.2,
    "stability_grow_easy_bonus": 1.3,
}
DEFAULT_RETENTION = 0.9


@dataclass
class Card:
    """A single review card — typically one headword + one form."""
    card_id: str
    headword_garifuna: str
    envir: str
    dialect_tag: Optional[str] = None
    stability: float = 0.0  # days; how long until retention drops below target
    difficulty: float = _W["init_difficulty"]  # 1..10 (higher = harder)
    last_reviewed_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None
    review_count: int = 0
    lapse_count: int = 0


@dataclass(frozen=True)
class ReviewSchedule:
    card_id: str
    next_due_at: datetime
    interval_days: float


class FSRSScheduler:
    """Per-learner card scheduler. Operates on (Card, Rating, now) triples."""

    def __init__(self, target_retention: float = DEFAULT_RETENTION):
        if not 0.5 <= target_retention <= 0.99:
            raise ValueError("target_retention must be in [0.5, 0.99]")
        self.target_retention = target_retention

    def schedule(self, card: Card, rating: Rating, now: Optional[datetime] = None) -> ReviewSchedule:
        """Update card stability + difficulty; compute next-due timestamp."""
        now = now or datetime.utcnow()

        if card.review_count == 0:
            # First review — initialise stability from rating
            stability_key = {
                Rating.AGAIN: "init_stability_again",
                Rating.HARD: "init_stability_hard",
                Rating.GOOD: "init_stability_good",
                Rating.EASY: "init_stability_easy",
            }[rating]
            card.stability = _W[stability_key]
            card.difficulty = _W["init_difficulty"]
        else:
            elapsed_days = 0.0
            if card.last_reviewed_at is not None:
                elapsed_days = (now - card.last_reviewed_at).total_seconds() / 86400.0
            retrievability = self._retrievability(card.stability, elapsed_days)
            card.stability = self._next_stability(card.stability, card.difficulty, retrievability, rating)
            card.difficulty = self._next_difficulty(card.difficulty, rating)

        if rating == Rating.AGAIN:
            card.lapse_count += 1
        card.review_count += 1
        card.last_reviewed_at = now

        interval_days = self._interval_from_stability(card.stability)
        card.next_due_at = now + timedelta(days=interval_days)
        return ReviewSchedule(card_id=card.card_id, next_due_at=card.next_due_at, interval_days=interval_days)

    def _retrievability(self, stability: float, elapsed_days: float) -> float:
        if stability <= 0:
            return 0.0
        return exp(-elapsed_days / stability * log(2))

    def _next_stability(self, stability: float, difficulty: float, retrievability: float, rating: Rating) -> float:
        if rating == Rating.AGAIN:
            return max(0.1, stability * _W["stability_again_factor"])
        # FSRS post-success stability growth:  S' = S * (1 + factor)
        # factor depends on D, R, and rating; simplified scaffold below
        factor = (1.0 / difficulty) * (1.0 - retrievability) * 5.0
        if rating == Rating.EASY:
            factor *= _W["stability_grow_easy_bonus"]
        return max(0.1, stability * (1.0 + factor))

    def _next_difficulty(self, difficulty: float, rating: Rating) -> float:
        # FSRS: difficulty updates by rating; bounded [1, 10]
        delta = {Rating.AGAIN: 1.0, Rating.HARD: 0.5, Rating.GOOD: -0.2, Rating.EASY: -0.6}[rating]
        return max(1.0, min(10.0, difficulty + delta))

    def _interval_from_stability(self, stability: float) -> float:
        """Solve retrievability=target_retention for elapsed_days given stability.

        Stability is the half-life (R drops from 1.0 to 0.5 over S days under simple
        exponential decay). Interval where R == target_retention:
            target = 2^(-t/S)  →  t = S * log(target) / log(0.5)
        """
        if stability <= 0:
            return 0.1
        return stability * log(self.target_retention) / log(0.5)
