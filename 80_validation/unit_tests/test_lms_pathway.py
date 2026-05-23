"""Tests for M-P3.LMS.PATHWAY heritage/novice/L1-maintainer differentiation."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.pathway import (
    PathwayKind, RegisterTier, LearnerProfile, PathwaySpec,
    HERITAGE_PATHWAY, NOVICE_PATHWAY, L1_MAINTAINER_PATHWAY,
    pathway_for, PathwayResolver, PathwayAdapter,
)
from lms._engine.lesson_player import Lesson, Unit, Step, StepKind


def _mk_lesson() -> Lesson:
    s1 = Step("s1", StepKind.INSTRUCTION, "buguya", "Read aloud.")
    s2 = Step("s2", StepKind.EXAMPLE, "buguya", "Buguya nuani Wamaraga.")
    s3 = Step("s3", StepKind.CHECK_FOR_UNDERSTANDING, "buguya", "Meaning?",
              correct_response="thank you my dear")
    s4 = Step("s4", StepKind.PRACTICE, "nuani", "Say nuani.")
    s5 = Step("s5", StepKind.REFLECTION, "buguya", "When would you use this?")
    u = Unit("u1", "Greetings", (s1, s2, s3, s4, s5))
    return Lesson("L1", "belize", "novice", "Day 1", (u,))


# === Pathway spec sanity ===

def test_heritage_higher_form_focus_than_novice():
    # Frontiers 2020 — HL learners need form-focused intervention
    assert HERITAGE_PATHWAY.form_focused_intensity > NOVICE_PATHWAY.form_focused_intensity


def test_novice_higher_scaffolding_than_l1_maintainer():
    # Novice needs more explicit support; fluent maintainers don't
    assert NOVICE_PATHWAY.scaffolding_intensity > L1_MAINTAINER_PATHWAY.scaffolding_intensity


def test_heritage_higher_identity_weight_than_novice():
    # HL pedagogy literature — identity is central HL motivation
    assert HERITAGE_PATHWAY.identity_relevance_weight > NOVICE_PATHWAY.identity_relevance_weight


def test_l1_maintainer_higher_threshold_than_novice():
    # Fluent speakers held to near-native literacy
    assert L1_MAINTAINER_PATHWAY.assessment_threshold > NOVICE_PATHWAY.assessment_threshold


def test_heritage_starts_with_reception():
    # HL learners typically have receptive > productive
    assert HERITAGE_PATHWAY.starts_with_reception is True
    assert NOVICE_PATHWAY.starts_with_reception is False


def test_register_focus_differs_per_pathway():
    assert HERITAGE_PATHWAY.register_focus == RegisterTier.CULTURAL_CEREMONIAL
    assert NOVICE_PATHWAY.register_focus == RegisterTier.INFORMAL
    assert L1_MAINTAINER_PATHWAY.register_focus == RegisterTier.ACADEMIC


# === Resolver ===

def test_resolver_l1_maintainer_for_native_speaker():
    profile = LearnerProfile(
        has_heritage_speaker_family=True,
        self_reported_proficiency=0.85,
        primary_language="garifuna",
    )
    assert PathwayResolver().resolve(profile) == PathwayKind.L1_MAINTAINER


def test_resolver_heritage_for_diaspora_child():
    profile = LearnerProfile(
        has_heritage_speaker_family=True,
        self_reported_proficiency=0.25,
        primary_language="english",
    )
    assert PathwayResolver().resolve(profile) == PathwayKind.HERITAGE


def test_resolver_novice_for_curious_outsider():
    profile = LearnerProfile(
        has_heritage_speaker_family=False,
        self_reported_proficiency=0.0,
        primary_language="english",
    )
    assert PathwayResolver().resolve(profile) == PathwayKind.NOVICE


# === Adapter ===

def test_adapter_heritage_prepends_anchor_and_duplicates_practice():
    base = _mk_lesson()
    adapted = PathwayAdapter().adapt(base, PathwayKind.HERITAGE)
    steps = adapted.units[0].steps
    # First step should be the heritage anchor (identity-relevance)
    assert steps[0].step_id.startswith("hr.anchor.")
    assert steps[0].kind == StepKind.INSTRUCTION
    # Practice step should be duplicated (form-focused boost)
    practice_ids = [s.step_id for s in steps if s.kind == StepKind.PRACTICE]
    assert any(p.startswith("hr.ff.") for p in practice_ids)


def test_adapter_novice_inserts_examples_before_checks():
    base = _mk_lesson()
    adapted = PathwayAdapter().adapt(base, PathwayKind.NOVICE)
    steps = adapted.units[0].steps
    kinds = [s.kind for s in steps]
    # An EXAMPLE step (nv.ex.*) should now precede each CHECK_FOR_UNDERSTANDING
    for i, s in enumerate(steps):
        if s.kind == StepKind.CHECK_FOR_UNDERSTANDING and i > 0:
            assert steps[i - 1].kind == StepKind.EXAMPLE


def test_adapter_l1_maintainer_strips_basic_instructions():
    base = _mk_lesson()
    adapted = PathwayAdapter().adapt(base, PathwayKind.L1_MAINTAINER)
    steps = adapted.units[0].steps
    # Basic INSTRUCTION steps removed; EXAMPLE/CHECK/PRACTICE/REFLECTION remain
    assert all(s.kind != StepKind.INSTRUCTION for s in steps)
    assert any(s.kind == StepKind.PRACTICE for s in steps)
    assert any(s.kind == StepKind.REFLECTION for s in steps)


def test_adapter_preserves_pathway_label():
    base = _mk_lesson()  # base.pathway == "novice"
    adapted_h = PathwayAdapter().adapt(base, PathwayKind.HERITAGE)
    adapted_l1 = PathwayAdapter().adapt(base, PathwayKind.L1_MAINTAINER)
    assert adapted_h.pathway == "heritage"
    assert adapted_l1.pathway == "l1_maintainer"


def test_pathway_for_returns_correct_spec():
    assert pathway_for(PathwayKind.HERITAGE) is HERITAGE_PATHWAY
    assert pathway_for(PathwayKind.NOVICE) is NOVICE_PATHWAY
    assert pathway_for(PathwayKind.L1_MAINTAINER) is L1_MAINTAINER_PATHWAY
