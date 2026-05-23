"""Tests for M-P3.LMS.TUTOR — Socratic AI tutor (D-MAX-7)."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.olm import OpenLearnerModel
from lms._engine.kgraph import KnowledgeGraph, Node, Edge, NodeKind, EdgeKind
from lms._engine.mastery import MasteryGate
from lms._engine.pathway import PathwayKind
from lms._engine.tutor import (
    SocraticTutor, ScaffoldLevel, TutorTurn, TutorState,
)


def _setup_kgraph_with_buguya() -> KnowledgeGraph:
    g = KnowledgeGraph()
    g.add_node(Node("hw.buguya", NodeKind.HEADWORD, "buguya"))
    g.add_node(Node("hw.nuani", NodeKind.HEADWORD, "nuani"))
    # buguya is a prereq for "nuani" usage in compound form (per chart-7 anchor)
    g.add_edge(Edge("hw.buguya", "hw.nuani", EdgeKind.PRECEDES))
    return g


def _mk_tutor(pathway: PathwayKind = PathwayKind.NOVICE, brain=None) -> SocraticTutor:
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    g = _setup_kgraph_with_buguya()
    gate = MasteryGate(olm=olm, kgraph=g, pathway=pathway)
    return SocraticTutor(olm=olm, kgraph=g, mastery_gate=gate, pathway=pathway, brain=brain)


# === Initial turn ===


def test_initial_turn_returns_open_scaffold():
    tutor = _mk_tutor()
    turn = tutor.initial_turn("buguya")
    assert turn.scaffold_level == ScaffoldLevel.OPEN
    assert turn.target_headword == "buguya"
    assert "buguya" in turn.prompt_text
    assert turn.pathway_kind == "novice"


def test_initial_turn_cites_kgraph_node():
    tutor = _mk_tutor()
    turn = tutor.initial_turn("buguya")
    assert "hw.buguya" in turn.kgraph_node_ids_cited


# === Scaffolding adaptation ===


def test_correct_response_relaxes_scaffold():
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.MODELED,
    )
    turn = tutor.next_turn(state, learner_response="thank you", was_correct=True)
    # After correct response, scaffold should step back toward OPEN
    assert turn.scaffold_level == ScaffoldLevel.HINTED
    assert state.correct_count == 1


def test_incorrect_response_tightens_scaffold():
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.OPEN,
    )
    turn = tutor.next_turn(state, learner_response="hello", was_correct=False)
    # After incorrect response, scaffold should step toward DIRECT_INSTRUCT
    assert turn.scaffold_level == ScaffoldLevel.GUIDING


def test_scaffold_bounded_at_open():
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.OPEN,
    )
    turn = tutor.next_turn(state, was_correct=True)
    # Already at OPEN; can't go lower
    assert turn.scaffold_level == ScaffoldLevel.OPEN


def test_scaffold_bounded_at_direct_instruct():
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.DIRECT_INSTRUCT,
    )
    turn = tutor.next_turn(state, was_correct=False)
    # Already at max; can't go higher
    assert turn.scaffold_level == ScaffoldLevel.DIRECT_INSTRUCT


# === Pathway-aware behavior ===


def test_heritage_pathway_uses_identity_anchor():
    tutor = _mk_tutor(pathway=PathwayKind.HERITAGE)
    turn = tutor.initial_turn("buguya")
    assert "family" in turn.prompt_text.lower() or "community" in turn.prompt_text.lower()


def test_novice_pathway_uses_stepwise_anchor():
    tutor = _mk_tutor(pathway=PathwayKind.NOVICE)
    turn = tutor.initial_turn("buguya")
    assert "step" in turn.prompt_text.lower() or "time" in turn.prompt_text.lower()


def test_l1_maintainer_uses_academic_register():
    tutor = _mk_tutor(pathway=PathwayKind.L1_MAINTAINER)
    turn = tutor.initial_turn("buguya")
    assert "academic" in turn.prompt_text.lower() or "literary" in turn.prompt_text.lower()


def test_cite_sources_payload_pathway_intensity():
    tutor = _mk_tutor(pathway=PathwayKind.HERITAGE)
    turn = tutor.initial_turn("buguya")
    payload = turn.cite_sources_payload
    assert payload["pathway"] == "heritage"
    # HERITAGE has scaffolding_intensity 0.6 (mid; HL learners use receptive base)
    assert payload["scaffolding_intensity"] == 0.6
    assert payload["envir"] == "belize"


# === Prerequisite-chain surfacing ===


def test_unmastered_prereqs_surface_in_prompt():
    # Learner is trying "nuani" but hasn't mastered prereq "buguya"
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="nuani",
        current_scaffold_level=ScaffoldLevel.OPEN,
    )
    turn = tutor.next_turn(state, was_correct=None)
    assert "hw.buguya" in turn.prereq_chain
    # Prompt should mention the prereq node
    assert "hw.buguya" in turn.prompt_text


def test_no_prereq_chain_when_target_unknown():
    tutor = _mk_tutor()
    turn = tutor.initial_turn("unknown_headword")
    assert turn.prereq_chain == ()
    assert turn.kgraph_node_ids_cited == ()


# === Brain integration ===


def test_brain_callable_invoked_for_hinted_scaffold():
    captured_prompts: list[str] = []
    def mock_brain(p: str) -> str:
        captured_prompts.append(p)
        return f"[brain-naturalized] {p}"
    tutor = _mk_tutor(brain=mock_brain)
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.HINTED,
    )
    turn = tutor.next_turn(state, was_correct=False)
    # Brain was called (scaffold level != OPEN)
    assert len(captured_prompts) > 0
    assert turn.prompt_text.startswith("[brain-naturalized]")


def test_brain_skipped_for_open_scaffold():
    captured_prompts: list[str] = []
    def mock_brain(p: str) -> str:
        captured_prompts.append(p)
        return f"naturalized: {p}"
    tutor = _mk_tutor(brain=mock_brain)
    turn = tutor.initial_turn("buguya")
    # OPEN scaffold uses pure template — brain NOT called
    assert len(captured_prompts) == 0
    assert not turn.prompt_text.startswith("naturalized")


def test_brain_failure_falls_back_to_template():
    def bad_brain(p: str) -> str:
        raise RuntimeError("simulated brain failure")
    tutor = _mk_tutor(brain=bad_brain)
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.HINTED,
    )
    # Should not raise; fallback to template
    turn = tutor.next_turn(state, was_correct=False)
    assert "buguya" in turn.prompt_text


# === Turn-id determinism ===


def test_turn_ids_increment():
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.OPEN,
    )
    turn1 = tutor.next_turn(state, was_correct=True)
    turn2 = tutor.next_turn(state, was_correct=True)
    assert turn1.turn_id != turn2.turn_id
    # Both should contain the learner + concept
    assert "L1" in turn1.turn_id
    assert "buguya" in turn1.turn_id
