"""Tests for M-P3.LMS.GAMES — mobile-first learning games."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.games import (
    GameKind, GameItem, GameSession, make_session, difficulty_for_pathway,
)
from lms._engine.pathway import PathwayKind


def _vocab_items() -> tuple[GameItem, ...]:
    return (
        GameItem("v1", GameKind.VOCAB_MATCH, "buguya = ?", "thank you",
                 ("hello", "goodbye", "yes")),
        GameItem("v2", GameKind.VOCAB_MATCH, "nuani = ?", "our love",
                 ("my home", "your friend", "their family")),
    )


def test_make_session_requires_items():
    with pytest.raises(ValueError, match="at least 1 item"):
        make_session(
            session_id="s1", learner_id="L1",
            kind=GameKind.VOCAB_MATCH, pathway=PathwayKind.NOVICE,
            envir="belize", items=(),
        )


def test_make_session_rejects_mismatched_kind():
    bad = (GameItem("v1", GameKind.SENTENCE_BUILD, "?", "a", ("b",)),)
    with pytest.raises(ValueError, match="kind"):
        make_session(
            session_id="s1", learner_id="L1",
            kind=GameKind.VOCAB_MATCH, pathway=PathwayKind.NOVICE,
            envir="belize", items=bad,
        )


def test_session_initial_state():
    s = make_session(
        session_id="s1", learner_id="L1",
        kind=GameKind.VOCAB_MATCH, pathway=PathwayKind.NOVICE,
        envir="belize", items=_vocab_items(),
    )
    assert not s.finished
    assert s.current_index == 0
    assert s.current_item().item_id == "v1"


def test_correct_answer_advances():
    s = make_session(
        session_id="s1", learner_id="L1",
        kind=GameKind.VOCAB_MATCH, pathway=PathwayKind.NOVICE,
        envir="belize", items=_vocab_items(),
    )
    assert s.submit("thank you") is True
    assert s.current_index == 1
    assert s.correct_count == 1


def test_incorrect_advances_but_penalizes_score():
    s = make_session(
        session_id="s1", learner_id="L1",
        kind=GameKind.VOCAB_MATCH, pathway=PathwayKind.NOVICE,
        envir="belize", items=_vocab_items(),
    )
    s.submit("hello")  # wrong
    s.submit("our love")  # correct
    # Correct 1, incorrect 1 → score = 1 - 0.5 = 0.5
    assert s.score() == 0.5
    assert s.accuracy() == 0.5


def test_session_finishes_after_all_items():
    s = make_session(
        session_id="s1", learner_id="L1",
        kind=GameKind.VOCAB_MATCH, pathway=PathwayKind.NOVICE,
        envir="belize", items=_vocab_items(),
    )
    s.submit("thank you")
    s.submit("our love")
    assert s.finished is True
    assert s.progress() == 1.0


def test_shuffled_options_are_deterministic():
    s = make_session(
        session_id="s1", learner_id="L1",
        kind=GameKind.VOCAB_MATCH, pathway=PathwayKind.NOVICE,
        envir="belize", items=_vocab_items(), rng_seed=42,
    )
    item = s.current_item()
    a = s.shuffled_options(item)
    b = s.shuffled_options(item)
    assert a == b
    # All options present
    assert sorted(a) == sorted(["thank you", "hello", "goodbye", "yes"])


def test_difficulty_adjustment_per_pathway():
    base = 0.5
    novice_diff = difficulty_for_pathway(PathwayKind.NOVICE, base)
    l1_diff = difficulty_for_pathway(PathwayKind.L1_MAINTAINER, base)
    heritage_diff = difficulty_for_pathway(PathwayKind.HERITAGE, base)
    # L1 maintainer expects higher challenge; novice gets lower
    assert l1_diff > novice_diff
    # Heritage in middle
    assert novice_diff < heritage_diff < l1_diff


def test_score_with_all_correct():
    s = make_session(
        session_id="s1", learner_id="L1",
        kind=GameKind.VOCAB_MATCH, pathway=PathwayKind.NOVICE,
        envir="belize", items=_vocab_items(),
    )
    s.submit("thank you")
    s.submit("our love")
    assert s.score() == 2.0
    assert s.accuracy() == 1.0
