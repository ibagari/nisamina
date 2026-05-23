"""Tests for M-P3.LMS.BLOCKS — LessonBlock ABC + plugin contract."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.blocks import (
    BlockRenderContext, RenderedBlock, Score, ProvenanceRef,
    LessonBlock, BlockRegistry, VocabFlashcardBlock,
)


def _mk_vocab_block() -> VocabFlashcardBlock:
    return VocabFlashcardBlock(
        headword_garifuna="buguya",
        gloss_en="thank you",
        gloss_es="gracias",
        distractors=("hello", "goodbye", "yes"),
        attribution_refs=("attr_055",),
        consent_ref="consent_011",
        source_citations=("Cayetano 1992 §greetings",),
    )


def _mk_ctx(pathway: str = "novice", ui_lang: str = "en") -> BlockRenderContext:
    return BlockRenderContext(
        learner_id="L1",
        envir="belize",
        pathway=pathway,
        primary_modality="text",
        extra={"ui_lang": ui_lang},
    )


def test_concrete_block_requires_class_attributes():
    # Defining a LessonBlock subclass without block_id/version/kind raises
    with pytest.raises(ValueError, match="must set block_id"):
        class BadBlock(LessonBlock):
            block_version = "0.1.0"
            block_kind = "x"
            def render(self, ctx): return RenderedBlock(self.block_id, self.block_version, "p")
            def score(self, response, ctx=None): return Score(True, 1.0)
            def provenance(self): return ProvenanceRef((), None, ())


def test_vocab_block_render_pathway_aware():
    block = _mk_vocab_block()
    heritage = block.render(_mk_ctx(pathway="heritage"))
    novice = block.render(_mk_ctx(pathway="novice"))
    l1 = block.render(_mk_ctx(pathway="l1_maintainer"))
    # Heritage prompts use community-anchor language
    assert "community" in heritage.rendered_prompt.lower()
    # Novice prompts use explicit translation language
    assert "best match" in novice.rendered_prompt.lower()
    # L1 maintainer prompts use academic language
    assert "academic register" in l1.rendered_prompt.lower()


def test_vocab_block_score_accepts_either_language_gloss():
    block = _mk_vocab_block()
    assert block.score("thank you").correct is True
    assert block.score("gracias").correct is True
    assert block.score("goodbye").correct is False


def test_vocab_block_provenance_required():
    block = _mk_vocab_block()
    prov = block.provenance()
    assert prov.attribution_refs == ("attr_055",)
    assert prov.consent_ref == "consent_011"
    assert "Cayetano 1992" in str(prov.source_citations)


def test_render_emits_cite_sources_payload():
    block = _mk_vocab_block()
    rendered = block.render(_mk_ctx())
    assert rendered.cite_sources_payload  # non-empty
    assert "attribution_refs" in rendered.cite_sources_payload


# === BlockRegistry ===


def test_registry_register_and_get():
    r = BlockRegistry()
    r.register(VocabFlashcardBlock)
    retrieved = r.get(VocabFlashcardBlock.block_id, VocabFlashcardBlock.block_version)
    assert retrieved is VocabFlashcardBlock


def test_registry_rejects_duplicate_version():
    r = BlockRegistry()
    r.register(VocabFlashcardBlock)
    with pytest.raises(ValueError, match="already registered"):
        r.register(VocabFlashcardBlock)


def test_registry_rejects_non_lessonblock():
    r = BlockRegistry()
    class NotABlock:
        block_id = "x"
        block_version = "0.1.0"
    with pytest.raises(TypeError, match="must subclass LessonBlock"):
        r.register(NotABlock)  # type: ignore[arg-type]


def test_registry_latest_version():
    r = BlockRegistry()
    r.register(VocabFlashcardBlock)
    latest = r.latest_version_of(VocabFlashcardBlock.block_id)
    assert latest is VocabFlashcardBlock


def test_registry_list_block_ids():
    r = BlockRegistry()
    r.register(VocabFlashcardBlock)
    ids = r.list_block_ids()
    assert VocabFlashcardBlock.block_id in ids


def test_registry_get_unknown_raises():
    r = BlockRegistry()
    with pytest.raises(KeyError):
        r.get("nonexistent", "0.0.0")


def test_score_carries_affect_signal():
    """Score correctly emits affect_signal_correct_streak_delta for affect_gentle."""
    block = _mk_vocab_block()
    s_correct = block.score("thank you")
    s_wrong = block.score("nope")
    assert s_correct.affect_signal_correct_streak_delta == 1
    assert s_wrong.affect_signal_correct_streak_delta == 0
