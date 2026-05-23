"""Tests for M-P3.LMS.MASTERY — Bloom mastery-gate progression."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.olm import OpenLearnerModel
from lms._engine.mastery import (
    MasteryGate, MasteryGateResult, threshold_for_pathway,
)
from lms._engine.pathway import PathwayKind
from lms._engine.kgraph import KnowledgeGraph, Node, Edge, NodeKind, EdgeKind


def _make_olm_with_masteries(envir: str = "belize", masteries: dict[str, int] = None) -> OpenLearnerModel:
    """Helper: simulate `n` correct observations per headword to drive mastery."""
    olm = OpenLearnerModel(learner_id="L1", envir=envir)
    masteries = masteries or {}
    for hw, n_correct in masteries.items():
        for _ in range(n_correct):
            olm.observe(hw, correct=True)
    return olm


def test_threshold_per_pathway():
    assert threshold_for_pathway(PathwayKind.HERITAGE) == 0.80
    assert threshold_for_pathway(PathwayKind.NOVICE) == 0.85
    assert threshold_for_pathway(PathwayKind.L1_MAINTAINER) == 0.90


def test_gate_blocks_when_no_observations():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    gate = MasteryGate(olm=olm, pathway=PathwayKind.NOVICE)
    result = gate.check(unit_headwords=("buguya", "nuani"))
    assert result.can_advance is False
    assert set(result.unmastered_headwords) == {"buguya", "nuani"}
    assert result.unit_headword_mastery_rate == 0.0


def test_gate_passes_when_all_mastered():
    olm = _make_olm_with_masteries(masteries={"buguya": 20, "nuani": 20})
    gate = MasteryGate(olm=olm, pathway=PathwayKind.NOVICE)
    result = gate.check(unit_headwords=("buguya", "nuani"))
    assert result.can_advance is True
    assert result.unmastered_headwords == ()
    assert result.unit_headword_mastery_rate == 1.0


def test_gate_partial_mastery_blocks():
    # Only one headword mastered
    olm = _make_olm_with_masteries(masteries={"buguya": 20})
    gate = MasteryGate(olm=olm, pathway=PathwayKind.NOVICE)
    result = gate.check(unit_headwords=("buguya", "nuani"))
    assert result.can_advance is False
    # nuani is unmastered (never observed)
    assert "nuani" in result.unmastered_headwords
    assert result.unit_headword_mastery_rate == 0.5


def test_heritage_pathway_lower_threshold():
    # 0.80 threshold for HERITAGE; same data passes here that might not pass NOVICE
    olm = _make_olm_with_masteries(masteries={"buguya": 8, "nuani": 8})
    gate_h = MasteryGate(olm=olm, pathway=PathwayKind.HERITAGE)
    gate_n = MasteryGate(olm=olm, pathway=PathwayKind.NOVICE)
    result_h = gate_h.check(unit_headwords=("buguya", "nuani"))
    result_n = gate_n.check(unit_headwords=("buguya", "nuani"))
    # Heritage threshold is 0.80 (lower); same belief may pass heritage but block novice
    assert result_h.threshold_applied < result_n.threshold_applied
    assert result_h.threshold_applied == 0.80


def test_l1_maintainer_pathway_strictest():
    gate = MasteryGate(
        olm=OpenLearnerModel(learner_id="L1", envir="belize"),
        pathway=PathwayKind.L1_MAINTAINER,
    )
    assert gate.threshold == 0.90


def test_gate_checks_kgraph_prerequisites():
    # Build a kgraph with unit.b precedes-by unit.a; learner must master "hw.a"
    # before they can advance past unit.b. NodeKind.HEADWORD label = the Garifuna
    # headword (must match OLM key convention).
    g = KnowledgeGraph()
    g.add_node(Node("hw.a", NodeKind.HEADWORD, "hw.a"))  # label == OLM key
    g.add_node(Node("unit.a", NodeKind.UNIT, "Unit A"))
    g.add_node(Node("unit.b", NodeKind.UNIT, "Unit B"))
    g.add_edge(Edge("unit.a", "hw.a", EdgeKind.COVERS))
    g.add_edge(Edge("unit.a", "unit.b", EdgeKind.PRECEDES))

    # Learner has mastered the unit_b headwords but NOT the prereq hw.a
    olm = _make_olm_with_masteries(masteries={"hw.b": 20})
    gate = MasteryGate(olm=olm, kgraph=g, pathway=PathwayKind.NOVICE)
    result = gate.check(unit_headwords=("hw.b",), unit_node_id="unit.b")
    # Should NOT advance because hw.a (prerequisite) is unmastered
    assert result.can_advance is False
    assert "hw.a" in result.unmastered_prerequisites


def test_gate_with_kgraph_passes_when_prereqs_mastered():
    g = KnowledgeGraph()
    g.add_node(Node("hw.a", NodeKind.HEADWORD, "hw.a"))  # label == OLM key
    g.add_node(Node("unit.a", NodeKind.UNIT, "Unit A"))
    g.add_node(Node("unit.b", NodeKind.UNIT, "Unit B"))
    g.add_edge(Edge("unit.a", "hw.a", EdgeKind.COVERS))
    g.add_edge(Edge("unit.a", "unit.b", EdgeKind.PRECEDES))

    olm = _make_olm_with_masteries(masteries={"hw.a": 20, "hw.b": 20})
    gate = MasteryGate(olm=olm, kgraph=g, pathway=PathwayKind.NOVICE)
    result = gate.check(unit_headwords=("hw.b",), unit_node_id="unit.b")
    assert result.can_advance is True


def test_result_pathway_field_reflects_pathway():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    gate = MasteryGate(olm=olm, pathway=PathwayKind.HERITAGE)
    result = gate.check(unit_headwords=())
    assert result.pathway_kind == "heritage"
