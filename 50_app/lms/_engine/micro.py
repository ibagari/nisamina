"""M-P3.LMS.MICRO — 5-minute microlearning units.

Per F-059 D-MAX-3 + higher-ed microlearning meta-analysis (g=0.74 medium-to-large
effect) + Prasittichok EFL systematic review/meta-analysis (Int J Learning
Teaching Educ Research).

5-minute daily units delivered via PWA push (per F-030 P3 #4 Workbox 7).
Mobile-first; offline-capable; runs alongside full lesson_player (alternative
pathway, not replacement). Targets adult learners + commuters + diaspora
parents short on time.

Per F-055 axis #6: per-learner micro state stays in learner envir; aggregate
analytics surface via Caliper without PII.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional


class MicroUnitKind(str, Enum):
    VOCAB_FLASHCARD = "vocab_flashcard"           # 1 headword + 3-option recognition
    FILL_IN_BLANK = "fill_in_blank"               # one short sentence with one blank
    LISTEN_REPEAT = "listen_repeat"               # MMS-TTS-CAB audio + repeat
    CULTURAL_TIDBIT = "cultural_tidbit"           # one-paragraph cultural note
    QUICK_REVIEW = "quick_review"                 # SR scheduler-derived review prompt


# Per D-MAX-3 micro convention: target ≤ 5 minutes; default 3 minutes
DEFAULT_MICRO_DURATION_MINUTES: int = 3
MAX_MICRO_DURATION_MINUTES: int = 5


@dataclass(frozen=True)
class MicroUnit:
    """A single ≤5-minute learning unit."""
    unit_id: str
    kind: MicroUnitKind
    headword_garifuna: Optional[str]
    prompt_text: str
    correct_response: Optional[str]
    distractors: tuple[str, ...] = ()
    audio_ref: Optional[str] = None              # MMS-TTS-CAB audio asset_id
    cultural_anchor: Optional[str] = None
    target_duration_minutes: int = DEFAULT_MICRO_DURATION_MINUTES
    envir: str = "garicomm"

    def __post_init__(self):
        if self.target_duration_minutes > MAX_MICRO_DURATION_MINUTES:
            raise ValueError(
                f"target_duration_minutes={self.target_duration_minutes} exceeds "
                f"D-MAX-3 micro convention max={MAX_MICRO_DURATION_MINUTES}"
            )


@dataclass
class MicroSession:
    """Per-learner micro session state. Tracks completion + score + last-attempt time."""
    session_id: str
    learner_id: str
    envir: str
    unit: MicroUnit
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    correct: Optional[bool] = None
    actual_duration_seconds: float = 0.0

    def start(self, now: Optional[datetime] = None) -> None:
        if self.started_at is not None:
            raise ValueError("micro session already started")
        self.started_at = now or datetime.now(timezone.utc)

    def submit(self, response: str, now: Optional[datetime] = None) -> bool:
        if self.started_at is None:
            raise ValueError("micro session not started")
        if self.completed_at is not None:
            raise ValueError("micro session already completed")
        now = now or datetime.now(timezone.utc)
        self.actual_duration_seconds = (now - self.started_at).total_seconds()
        if self.unit.correct_response is None:
            # CULTURAL_TIDBIT or similar: any non-empty acknowledgment counts
            self.correct = bool(response.strip())
        else:
            self.correct = response.strip().lower() == self.unit.correct_response.strip().lower()
        self.completed_at = now
        return self.correct

    def under_target_duration(self) -> bool:
        """True if completion was within target_duration_minutes."""
        return self.actual_duration_seconds <= self.unit.target_duration_minutes * 60


# === Daily delivery queue ===================================================


@dataclass
class DailyMicroDelivery:
    """Per-learner daily micro queue. Computes which micros to push today.

    Strategy:
    1. Pull review-due cards from SR scheduler (highest priority)
    2. Add new-headword micros from current lesson_player unit (if any)
    3. Mix in 1 cultural-tidbit per day
    4. Cap at 5 micros per day (5 × 3 min = 15 min total — sustainable; matches
       Prasittichok meta-analysis dose-response)
    """
    learner_id: str
    envir: str
    queued_units: tuple[MicroUnit, ...] = field(default_factory=tuple)
    max_per_day: int = 5
    last_delivery_date: Optional[str] = None  # ISO date YYYY-MM-DD

    def enqueue(self, units: tuple[MicroUnit, ...]) -> None:
        # Filter to envir; cap at max_per_day
        filtered = tuple(u for u in units if u.envir == self.envir)[: self.max_per_day]
        self.queued_units = filtered

    def next_unit(self) -> Optional[MicroUnit]:
        if not self.queued_units:
            return None
        next_u = self.queued_units[0]
        self.queued_units = self.queued_units[1:]
        return next_u

    def mark_delivered(self, now: Optional[datetime] = None) -> None:
        now = now or datetime.now(timezone.utc)
        self.last_delivery_date = now.date().isoformat()

    def already_delivered_today(self, now: Optional[datetime] = None) -> bool:
        if self.last_delivery_date is None:
            return False
        now = now or datetime.now(timezone.utc)
        return self.last_delivery_date == now.date().isoformat()
