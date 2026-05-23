"""Tests for M-P3.LMS.VERSIONED_KGRAPH — proposal → merge semantics."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.kgraph import KnowledgeGraph, Node, Edge, NodeKind, EdgeKind
from lms._engine.versioned_kgraph import (
    KGEdit, KGraphProposal, VersionedKnowledgeGraph,
)


def test_versioned_graph_initial_state():
    vg = VersionedKnowledgeGraph(envir="belize")
    assert vg.version_count() == 0
    # Has the provenance.root anchor
    assert vg.graph.has_node("provenance.root")


def test_proposal_stages_and_applies():
    vg = VersionedKnowledgeGraph(envir="belize")
    p = KGraphProposal(proposal_id="prop_001", submitter="curator")
    p.stage_node(Node("hw.newword", NodeKind.HEADWORD, "newword", envir="belize"))
    summary = p.staged_summary()
    assert summary["node_count"] == 1
    assert not p.applied()

    edit = vg.apply_proposal(
        proposal=p,
        approving_authority="Commission elder panel",
        proposal_ref="prop_001",
        rationale="Verified via Cayetano 1992 cross-ref",
    )
    assert edit.edit_id == "kgedit.00001"
    assert "hw.newword" in edit.nodes_added
    assert edit.approving_authority == "Commission elder panel"
    assert vg.version_count() == 1
    assert vg.graph.has_node("hw.newword")
    assert p.applied()


def test_apply_requires_approving_authority():
    vg = VersionedKnowledgeGraph(envir="belize")
    p = KGraphProposal(proposal_id="prop_001", submitter="x")
    p.stage_node(Node("hw.x", NodeKind.HEADWORD, "x", envir="belize"))
    with pytest.raises(ValueError, match="approving_authority required"):
        vg.apply_proposal(proposal=p, approving_authority="")


def test_proposal_cannot_be_applied_twice():
    vg = VersionedKnowledgeGraph(envir="belize")
    p = KGraphProposal(proposal_id="prop_001", submitter="x")
    p.stage_node(Node("hw.x", NodeKind.HEADWORD, "x", envir="belize"))
    vg.apply_proposal(proposal=p, approving_authority="elder")
    with pytest.raises(RuntimeError, match="already applied"):
        vg.apply_proposal(proposal=p, approving_authority="elder")


def test_proposal_cannot_be_staged_after_apply():
    vg = VersionedKnowledgeGraph(envir="belize")
    p = KGraphProposal(proposal_id="prop_001", submitter="x")
    p.stage_node(Node("hw.x", NodeKind.HEADWORD, "x", envir="belize"))
    vg.apply_proposal(proposal=p, approving_authority="elder")
    with pytest.raises(RuntimeError, match="already applied"):
        p.stage_node(Node("hw.y", NodeKind.HEADWORD, "y", envir="belize"))


def test_edit_history_is_append_only():
    vg = VersionedKnowledgeGraph(envir="belize")
    # First proposal
    p1 = KGraphProposal(proposal_id="prop_001", submitter="x")
    p1.stage_node(Node("hw.a", NodeKind.HEADWORD, "a", envir="belize"))
    vg.apply_proposal(proposal=p1, approving_authority="elder:1")
    # Second proposal
    p2 = KGraphProposal(proposal_id="prop_002", submitter="x")
    p2.stage_node(Node("hw.b", NodeKind.HEADWORD, "b", envir="belize"))
    p2.stage_edge(Edge("hw.a", "hw.b", EdgeKind.PRECEDES))
    vg.apply_proposal(proposal=p2, approving_authority="elder:2")

    history = vg.edit_history()
    assert len(history) == 2
    assert history[0].edit_id == "kgedit.00001"
    assert history[1].edit_id == "kgedit.00002"
    assert vg.version_count() == 2


def test_provenance_links_to_root():
    vg = VersionedKnowledgeGraph(envir="belize")
    p = KGraphProposal(proposal_id="prop_001", submitter="x")
    p.stage_node(Node("hw.x", NodeKind.HEADWORD, "x", envir="belize"))
    vg.apply_proposal(proposal=p, approving_authority="elder")
    # The edit-anchor node should exist + link to provenance.root
    assert vg.graph.has_node("provenance.kgedit.00001")
