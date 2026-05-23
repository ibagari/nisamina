"""M-P3.LMS.GAMES — Mobile-first learning games.

Per F-059 D-MAX-4 + mobile-games meta-analysis (38 studies / N=4,102; g=0.962
large effect) + mobile-assisted vocabulary meta-analysis (65 studies / 2010-2024;
g=1.28 long-term ≥10 weeks).

Four game families share a common state machine + scoring layer:

1. **VocabMatchGame**       — match Garifuna headword ↔ English/Spanish gloss
2. **SentenceBuildGame**    — reorder shuffled Garifuna tokens into a grammatical sentence
3. **DialogueChooseGame**   — pick the culturally-appropriate response from 3 options
4. **CulturalContextQuiz**  — multiple-choice quiz with cultural anchor + dialect tag

Per F-055 axis #6: per-envir + per-dialect content; no cross-envir leak.
Per F-059 D-MAX-5: pathway-aware difficulty (HERITAGE / NOVICE / L1_MAINTAINER).
Per F-030 P3 #4: offline-capable via Workbox 7 — game state lives in IndexedDB,
syncs via Caliper events when online.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from random import Random
from typing import Optional

try:
    from .pathway import PathwayKind, pathway_for
except ImportError:
    from pathway import PathwayKind, pathway_for


class GameKind(str, Enum):
    VOCAB_MATCH = "vocab_match"
    SENTENCE_BUILD = "sentence_build"
    DIALOGUE_CHOOSE = "dialogue_choose"
    CULTURAL_CONTEXT_QUIZ = "cultural_context_quiz"


@dataclass(frozen=True)
class GameItem:
    """A single playable item (one round of a game)."""
    item_id: str
    kind: GameKind
    prompt: str
    correct_answer: str
    distractors: tuple[str, ...]
    cultural_anchor: Optional[str] = None
    dialect_tag: Optional[str] = None


@dataclass
class GameSession:
    """Per-learner per-game session state machine.

    Lifecycle: NEW → PLAYING → COMPLETED. Score is sum of correct - 0.5*incorrect
    (lightly penalizes guessing).
    """
    session_id: str
    learner_id: str
    kind: GameKind
    pathway: PathwayKind
    envir: str
    items: tuple[GameItem, ...]
    correct_count: int = 0
    incorrect_count: int = 0
    current_index: int = 0
    finished: bool = False
    _rng_seed: int = 0

    def current_item(self) -> Optional[GameItem]:
        if self.finished or self.current_index >= len(self.items):
            return None
        return self.items[self.current_index]

    def submit(self, answer: str) -> bool:
        """Submit an answer; advance the session; return correctness."""
        item = self.current_item()
        if item is None:
            raise ValueError("session is finished or has no current item")
        correct = answer.strip().lower() == item.correct_answer.strip().lower()
        if correct:
            self.correct_count += 1
        else:
            self.incorrect_count += 1
        self.current_index += 1
        if self.current_index >= len(self.items):
            self.finished = True
        return correct

    def score(self) -> float:
        # Mild guess penalty per IRT-style scoring
        return self.correct_count - 0.5 * self.incorrect_count

    def accuracy(self) -> float:
        total = self.correct_count + self.incorrect_count
        return self.correct_count / total if total else 0.0

    def progress(self) -> float:
        return self.current_index / len(self.items) if self.items else 0.0

    def shuffled_options(self, item: GameItem) -> list[str]:
        """Return (correct + distractors) shuffled deterministically by item_id + seed.

        Determinism enables replay + cohort-comparison + reproducible tests.
        """
        rng = Random(f"{item.item_id}:{self._rng_seed}")
        opts = [item.correct_answer, *item.distractors]
        rng.shuffle(opts)
        return opts


def difficulty_for_pathway(pathway: PathwayKind, base_difficulty: float) -> float:
    """Adjust a base difficulty for a learner pathway.

    Per F-059 D-MAX-5: HERITAGE needs less scaffolding (higher difficulty OK
    because they have receptive knowledge); NOVICE needs the most scaffolding
    (lower difficulty); L1_MAINTAINER expects near-native challenge (highest).
    """
    spec = pathway_for(pathway)
    # Scaling factor: novice gets reduced difficulty; L1 maintainer gets raised
    factor = 1.0 - (spec.scaffolding_intensity - 0.5)  # [0.1 .. 1.2]
    return max(0.0, min(1.0, base_difficulty * factor))


def make_session(
    *,
    session_id: str,
    learner_id: str,
    kind: GameKind,
    pathway: PathwayKind,
    envir: str,
    items: tuple[GameItem, ...],
    rng_seed: int = 0,
) -> GameSession:
    """Constructor with light validation."""
    if not items:
        raise ValueError("game session requires at least 1 item")
    # All items must match the game kind
    for it in items:
        if it.kind != kind:
            raise ValueError(f"item {it.item_id} has kind {it.kind} but session is {kind}")
    return GameSession(
        session_id=session_id,
        learner_id=learner_id,
        kind=kind,
        pathway=pathway,
        envir=envir,
        items=items,
        _rng_seed=rng_seed,
    )
