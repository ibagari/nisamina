"""Tests for D-066 cognitive_load_signal on TutorState — Sweller-aware scaffold."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.olm import OpenLearnerModel
from lms._engine.kgraph import KnowledgeGraph, Node, NodeKind
from lms._engine.mastery import MasteryGate
from lms._engine.pathway import PathwayKind
from lms._engine.tutor import (
    SocraticTutor, ScaffoldLevel, TutorState, CognitiveLoadSignal,
)


def _mk_tutor() -> SocraticTutor:
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    g = KnowledgeGraph()
    g.add_node(Node("hw.buguya", NodeKind.HEADWORD, "buguya"))
    gate = MasteryGate(olm=olm, kgraph=g, pathway=PathwayKind.NOVICE)
    return SocraticTutor(olm=olm, kgraph=g, mastery_gate=gate, pathway=PathwayKind.NOVICE)


def test_tutor_state_has_cognitive_load_default():
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
    )
    assert state.cognitive_load.consecutive_attempts_on_same_concept == 0
    assert state.cognitive_load.consecutive_hints_requested == 0
    assert state.cognitive_load.average_response_latency_seconds == 0.0
    assert state.cognitive_load.self_reported_difficulty is None


def test_high_consecutive_attempts_triggers_proactive_tighten():
    """3+ attempts on same concept WITHOUT explicit was_correct should still tighten."""
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.OPEN,
        cognitive_load=CognitiveLoadSignal(consecutive_attempts_on_same_concept=4),
    )
    turn = tutor.next_turn(state, was_correct=None)
    # Proactive tighten from cognitive_load — OPEN → GUIDING
    assert turn.scaffold_level == ScaffoldLevel.GUIDING


def test_high_hint_count_triggers_tighten():
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.GUIDING,
        cognitive_load=CognitiveLoadSignal(consecutive_hints_requested=3),
    )
    turn = tutor.next_turn(state, was_correct=None)
    # GUIDING → HINTED
    assert turn.scaffold_level == ScaffoldLevel.HINTED


def test_self_reported_difficulty_triggers_tighten():
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.GUIDING,
        cognitive_load=CognitiveLoadSignal(self_reported_difficulty=5),
    )
    turn = tutor.next_turn(state, was_correct=None)
    assert turn.scaffold_level == ScaffoldLevel.HINTED


def test_slow_response_triggers_tighten():
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.OPEN,
        cognitive_load=CognitiveLoadSignal(average_response_latency_seconds=45.0),
    )
    turn = tutor.next_turn(state, was_correct=None)
    # 45s > 30s threshold → tighten
    assert turn.scaffold_level == ScaffoldLevel.GUIDING


def test_low_cognitive_load_no_proactive_change():
    """With normal cognitive load + no was_correct signal, scaffold stays."""
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.GUIDING,
        cognitive_load=CognitiveLoadSignal(
            average_response_latency_seconds=10.0,
            consecutive_hints_requested=0,
            consecutive_attempts_on_same_concept=1,
            self_reported_difficulty=2,
        ),
    )
    turn = tutor.next_turn(state, was_correct=None)
    # No proactive change — scaffold stays at GUIDING
    assert turn.scaffold_level == ScaffoldLevel.GUIDING


def test_was_correct_overrides_cognitive_load():
    """Explicit was_correct=True (success) should relax, not tighten, even with high load."""
    tutor = _mk_tutor()
    state = TutorState(
        learner_id="L1", envir="belize", target_concept="buguya",
        current_scaffold_level=ScaffoldLevel.HINTED,
        cognitive_load=CognitiveLoadSignal(consecutive_attempts_on_same_concept=5),
    )
    turn = tutor.next_turn(state, was_correct=True)
    # Explicit was_correct=True relaxes regardless of cognitive load
    assert turn.scaffold_level == ScaffoldLevel.GUIDING
