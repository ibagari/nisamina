"""M-P3.LMS.B — Lesson Player state machine.

Per F-039 architecture brief + F-059 WAVE-2.A.1.1. Foundation for every other LMS sub-manifest.

Data model:
    Lesson > Unit > Step

Lesson lifecycle: PENDING → IN_PROGRESS → COMPLETED → REVIEW_DUE (cycles back via spaced_repetition).
Step kinds: instruction | example | check_for_understanding | practice | reflection.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class StepKind(str, Enum):
    INSTRUCTION = "instruction"
    EXAMPLE = "example"
    CHECK_FOR_UNDERSTANDING = "check_for_understanding"
    PRACTICE = "practice"
    REFLECTION = "reflection"


class LessonState(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEW_DUE = "review_due"


@dataclass(frozen=True)
class Step:
    step_id: str
    kind: StepKind
    headword_garifuna: Optional[str]
    prompt_text: str
    correct_response: Optional[str] = None
    attribution_refs: tuple[str, ...] = ()
    consent_ref: Optional[str] = None


@dataclass(frozen=True)
class Unit:
    unit_id: str
    title: str
    steps: tuple[Step, ...]

    def step_count(self) -> int:
        return len(self.steps)


@dataclass(frozen=True)
class Lesson:
    lesson_id: str
    envir: str  # belize | honduras | guatemala | nicaragua | svg_yurumein | garicomm
    pathway: str  # heritage | novice | l1_maintainer (per D-MAX-5)
    title: str
    units: tuple[Unit, ...]
    dialect_tag: Optional[str] = None

    def total_steps(self) -> int:
        return sum(u.step_count() for u in self.units)


@dataclass
class LessonPlayer:
    """State machine for a learner progressing through a lesson."""
    lesson: Lesson
    learner_id: str
    state: LessonState = LessonState.PENDING
    current_unit_idx: int = 0
    current_step_idx: int = 0
    completed_steps: set[str] = field(default_factory=set)
    correct_count: int = 0
    attempt_count: int = 0

    def start(self) -> None:
        if self.state != LessonState.PENDING:
            raise ValueError(f"cannot start from state {self.state}")
        self.state = LessonState.IN_PROGRESS

    def current_step(self) -> Optional[Step]:
        if self.current_unit_idx >= len(self.lesson.units):
            return None
        unit = self.lesson.units[self.current_unit_idx]
        if self.current_step_idx >= len(unit.steps):
            return None
        return unit.steps[self.current_step_idx]

    def submit_response(self, response: str) -> bool:
        """Submit learner response; advance state machine; return correctness."""
        if self.state != LessonState.IN_PROGRESS:
            raise ValueError(f"cannot submit from state {self.state}")
        step = self.current_step()
        if step is None:
            raise ValueError("no current step")

        self.attempt_count += 1
        # For non-check steps any non-empty response advances; for checks compare correct_response.
        if step.kind == StepKind.CHECK_FOR_UNDERSTANDING:
            correct = (step.correct_response is not None
                       and response.strip().lower() == step.correct_response.strip().lower())
        else:
            correct = bool(response.strip())

        if correct:
            self.correct_count += 1
            self.completed_steps.add(step.step_id)
            self._advance()
        return correct

    def _advance(self) -> None:
        unit = self.lesson.units[self.current_unit_idx]
        if self.current_step_idx + 1 < len(unit.steps):
            self.current_step_idx += 1
            return
        # End of unit; move to next unit
        if self.current_unit_idx + 1 < len(self.lesson.units):
            self.current_unit_idx += 1
            self.current_step_idx = 0
            return
        # End of lesson
        self.state = LessonState.COMPLETED

    def accuracy(self) -> float:
        return (self.correct_count / self.attempt_count) if self.attempt_count else 0.0

    def progress(self) -> float:
        total = self.lesson.total_steps()
        return len(self.completed_steps) / total if total else 0.0

    def mark_review_due(self) -> None:
        """Called by spaced_repetition scheduler when review interval elapses."""
        if self.state == LessonState.COMPLETED:
            self.state = LessonState.REVIEW_DUE
