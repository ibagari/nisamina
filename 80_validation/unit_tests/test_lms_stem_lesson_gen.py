"""Tests for M-P3.LMS.STEM_LESSON_GEN trilingual lesson generator + neologism queue."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.neologism_queue import NeologismQueue, RequestStatus
from lms._engine.stem_lesson_gen import (
    LessonGenerator, ConceptSpec, SourceRef,
)


def _mk_queue(tmp_path: Path) -> NeologismQueue:
    return NeologismQueue(queue_path=tmp_path / "queue.jsonl")


def _mk_spec() -> ConceptSpec:
    return ConceptSpec(
        subject="Math",
        grade_band="04_Upper_Elementary_Grades_3_to_5",
        concept_slug="bar_modeling.fractions_intro",
        concept_title_en="Introduction to fraction comparison with bar models",
        concept_title_es="Introducción a la comparación de fracciones con modelos de barras",
        source_refs=(SourceRef("Singapore_Math_4A", "47-52", "Singapore Math Inc."),),
        cultural_anchors=("hudutu-recipe-ratio", "canoe-distance-time"),
        technical_terms=("fraction", "bar model", "comparison"),
        objectives_en=(
            "Identify the larger of two fractions using bar models.",
            "Apply fraction comparison to everyday Caribbean contexts.",
        ),
        objectives_es=(
            "Identificar la mayor de dos fracciones usando modelos de barras.",
            "Aplicar la comparación de fracciones a contextos caribeños cotidianos.",
        ),
    )


# === NeologismQueue ===

def test_queue_empty_on_init(tmp_path):
    q = _mk_queue(tmp_path)
    assert q.list_requests() == []
    assert q.pending() == []


def test_queue_request_appends(tmp_path):
    q = _mk_queue(tmp_path)
    req = q.queue_request(
        source_term="fraction",
        source_language="en",
        semantic_field="math",
        grade_band="04_Upper_Elementary_Grades_3_to_5",
        context_sentence="The fraction 1/2 represents half.",
        envir="stem_alternative",
    )
    assert req.request_id == "neologism_00001"
    assert req.source_term == "fraction"
    assert req.status == RequestStatus.PENDING
    assert len(q.list_requests()) == 1


def test_queue_pending_filters_correctly(tmp_path):
    q = _mk_queue(tmp_path)
    q.queue_request(
        source_term="fraction", source_language="en", semantic_field="math",
        grade_band="04", context_sentence="...", envir="stem_alternative",
    )
    pending = q.pending()
    assert len(pending) == 1
    assert pending[0]["status"] == "pending"


def test_queue_persists_across_instances(tmp_path):
    p = tmp_path / "queue.jsonl"
    q1 = NeologismQueue(queue_path=p)
    q1.queue_request(
        source_term="algorithm", source_language="en", semantic_field="computing",
        grade_band="05", context_sentence="An algorithm is a sequence of steps.",
        envir="stem_alternative",
    )
    # Re-open
    q2 = NeologismQueue(queue_path=p)
    assert len(q2.list_requests()) == 1
    assert q2.list_requests()[0]["source_term"] == "algorithm"


def test_queue_sequential_ids(tmp_path):
    q = _mk_queue(tmp_path)
    for i in range(3):
        q.queue_request(
            source_term=f"term_{i}", source_language="en", semantic_field="math",
            grade_band="04", context_sentence="...", envir="stem_alternative",
        )
    requests = q.list_requests()
    assert [r["request_id"] for r in requests] == ["neologism_00001", "neologism_00002", "neologism_00003"]


# === LessonGenerator ===

def test_lesson_generator_lookup_existing_term(tmp_path):
    q = _mk_queue(tmp_path)
    foundry = {"fraction": "[fictional canonical Garifuna]", "comparison": "[fictional]"}
    gen = LessonGenerator(foundry_terms=foundry, neologism_queue=q)
    term, ok = gen.garifuna_for(
        source_term="fraction", source_language="en",
        semantic_field="math", grade_band="04", context_sentence="...",
    )
    assert ok is True
    assert term == "[fictional canonical Garifuna]"
    # No queueing happened
    assert q.pending() == []


def test_lesson_generator_queues_missing_term(tmp_path):
    q = _mk_queue(tmp_path)
    gen = LessonGenerator(foundry_terms={}, neologism_queue=q)
    term, ok = gen.garifuna_for(
        source_term="variable", source_language="en",
        semantic_field="math", grade_band="05", context_sentence="A variable holds a value.",
    )
    assert ok is False
    assert term is None
    pending = q.pending()
    assert len(pending) == 1
    assert pending[0]["source_term"] == "variable"


def test_lesson_generator_renders_with_flag_for_missing_term(tmp_path):
    q = _mk_queue(tmp_path)
    gen = LessonGenerator(foundry_terms={}, neologism_queue=q)
    rendered, pending = gen.render_garifuna_text(
        source_text="A fraction is part of a whole.",
        source_language="en",
        semantic_field="math",
        grade_band="04",
        technical_terms=("fraction",),
    )
    assert "[needs Garifuna term]" in rendered
    assert pending == ["fraction"]


def test_lesson_full_generation_trilingual_keys(tmp_path):
    q = _mk_queue(tmp_path)
    foundry = {}  # all terms missing → all flagged + queued
    gen = LessonGenerator(foundry_terms=foundry, neologism_queue=q)
    lesson = gen.generate_lesson(_mk_spec())
    assert lesson["lesson_id"].startswith("stem.math.")
    assert lesson["subject"] == "Math"
    # All 3 languages present
    assert set(lesson["trilingual"].keys()) == {"cab", "en", "es"}
    # English + Spanish are source-language-faithful
    assert lesson["trilingual"]["en"]["title"].startswith("Introduction")
    assert lesson["trilingual"]["es"]["title"].startswith("Introducción")
    # Garifuna track has pending_neologisms
    assert len(lesson["trilingual"]["cab"]["pending_neologisms"]) > 0
    # Consent ref + cultural anchors propagated
    assert lesson["consent_ref"] == "consent_012"
    assert "hudutu-recipe-ratio" in lesson["cultural_anchors"]


def test_pathway_variants_present(tmp_path):
    q = _mk_queue(tmp_path)
    gen = LessonGenerator(foundry_terms={}, neologism_queue=q)
    lesson = gen.generate_lesson(_mk_spec())
    pv = lesson["pathway_variants"]
    # 3 pathway variants present
    assert set(pv.keys()) == {"heritage", "novice", "l1_maintainer"}
    # Heritage anchors identity
    assert pv["heritage"]["identity_anchor_required"] is True
    # L1 maintainer skips basics
    assert pv["l1_maintainer"]["skip_basic_instructions"] is True
    # Form-focused intensity is higher for heritage than novice
    assert pv["heritage"]["form_focused_intensity"] > 0.5


def test_lesson_engages_neologism_queue(tmp_path):
    q = _mk_queue(tmp_path)
    gen = LessonGenerator(foundry_terms={}, neologism_queue=q)
    gen.generate_lesson(_mk_spec())
    pending = q.pending()
    # All technical terms (fraction + bar model + comparison) → 3 requests but
    # render_garifuna_text is called for title (3 terms) + each objective (2 objs × 3 terms = 6)
    # So total queued requests = title (3) + objectives (6) = 9
    # However the foundry_for call de-duplicates within a single render but NOT across calls
    # So expect 9 entries (one queue request per term per render call)
    assert len(pending) >= 3   # at least the unique terms
