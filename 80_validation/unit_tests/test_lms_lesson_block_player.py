"""Tests for D-067 LessonBlockPlayer — composing LessonBlocks via BlockRegistry."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.blocks import (
    BlockRegistry, VocabFlashcardBlock, LessonBlock, BlockRenderContext,
    RenderedBlock, Score, ProvenanceRef,
)
from lms._engine.lesson_block_player import (
    LessonBlockPlayer, BlockPlayerSession, BlockReference, BlockPlayerState,
)


def _mk_registry() -> BlockRegistry:
    r = BlockRegistry()
    r.register(VocabFlashcardBlock)
    return r


def _mk_session() -> BlockPlayerSession:
    return BlockPlayerSession(
        session_id="s1",
        learner_id="L1",
        envir="belize",
        pathway="novice",
        block_sequence=(
            BlockReference(
                block_id=VocabFlashcardBlock.block_id,
                block_version=VocabFlashcardBlock.block_version,
                init_kwargs={
                    "headword_garifuna": "buguya",
                    "gloss_en": "thank you",
                    "gloss_es": "gracias",
                    "distractors": ("hello", "yes", "goodbye"),
                    "attribution_refs": ("attr_055",),
                    "consent_ref": "consent_011",
                    "source_citations": ("Cayetano 1992",),
                },
            ),
            BlockReference(
                block_id=VocabFlashcardBlock.block_id,
                block_version=VocabFlashcardBlock.block_version,
                init_kwargs={
                    "headword_garifuna": "nuani",
                    "gloss_en": "our love",
                    "gloss_es": "nuestro amor",
                    "distractors": ("my home", "his foot", "their family"),
                    "attribution_refs": ("attr_055",),
                    "consent_ref": "consent_011",
                    "source_citations": ("Cayetano 1992",),
                },
            ),
        ),
    )


def test_start_renders_first_block():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = _mk_session()
    rendered = player.start(session)
    assert session.state == BlockPlayerState.PLAYING
    assert isinstance(rendered, RenderedBlock)
    assert "buguya" in rendered.rendered_prompt or "best match" in rendered.rendered_prompt.lower()


def test_cannot_start_twice():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = _mk_session()
    player.start(session)
    with pytest.raises(ValueError, match="PENDING"):
        player.start(session)


def test_submit_advances_to_next_block():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = _mk_session()
    player.start(session)
    score, next_render = player.submit(session, "thank you")
    assert score.correct is True
    assert next_render is not None
    assert session.current_index == 1
    assert session.correct_count == 1


def test_submit_session_completes_after_all_blocks():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = _mk_session()
    player.start(session)
    player.submit(session, "thank you")
    score, next_render = player.submit(session, "our love")
    assert next_render is None
    assert session.state == BlockPlayerState.COMPLETED
    assert score.correct is True


def test_incorrect_submissions_tracked():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = _mk_session()
    player.start(session)
    player.submit(session, "wrong answer")
    player.submit(session, "nope")
    assert session.incorrect_count == 2
    assert session.correct_count == 0
    assert player.accuracy(session) == 0.0


def test_aggregate_score():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = _mk_session()
    player.start(session)
    player.submit(session, "thank you")  # correct → score 1.0
    player.submit(session, "wrong")  # incorrect → score 0.0
    assert player.aggregate_score(session) == 1.0
    assert player.accuracy(session) == 0.5


def test_cite_sources_audit_chains_provenance():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = _mk_session()
    player.start(session)
    player.submit(session, "thank you")
    player.submit(session, "our love")
    audit = session.cite_sources_audit
    assert len(audit) == 2
    assert all("attribution_refs" in a for a in audit)
    assert all("consent_ref" in a for a in audit)
    assert all(a["consent_ref"] == "consent_011" for a in audit)


def test_empty_sequence_raises():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = BlockPlayerSession(
        session_id="s1", learner_id="L1", envir="belize",
        pathway="novice", block_sequence=(),
    )
    with pytest.raises(ValueError, match="empty"):
        player.start(session)


def test_unknown_block_version_raises():
    player = LessonBlockPlayer(registry=_mk_registry())
    session = BlockPlayerSession(
        session_id="s1", learner_id="L1", envir="belize", pathway="novice",
        block_sequence=(BlockReference(block_id="nonexistent", block_version="0.0.0"),),
    )
    with pytest.raises(KeyError):
        player.start(session)
