"""Tests for M-P3.LMS.KGRAPH — knowledge graph foundation."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.kgraph import (
    KnowledgeGraph, Node, Edge, NodeKind, EdgeKind,
)


def _mk_graph() -> KnowledgeGraph:
    g = KnowledgeGraph(envir="belize")
    g.add_node(Node("hw.buguya", NodeKind.HEADWORD, "buguya", envir="belize"))
    g.add_node(Node("hw.nuani", NodeKind.HEADWORD, "nuani", envir="belize"))
    g.add_node(Node("unit.greetings", NodeKind.UNIT, "Day 1 — Greetings", envir="belize"))
    g.add_node(Node("lo.greet", NodeKind.LO, "Greet someone in Garifuna", envir="belize"))
    g.add_node(Node("anchor.affection", NodeKind.ANCHOR, "Affectionate sign-off"))
    g.add_edge(Edge("unit.greetings", "lo.greet", EdgeKind.COVERS))
    g.add_edge(Edge("unit.greetings", "hw.buguya", EdgeKind.COVERS))
    g.add_edge(Edge("unit.greetings", "hw.nuani", EdgeKind.COVERS))
    g.add_edge(Edge("hw.buguya", "anchor.affection", EdgeKind.CULTURAL_ANCHOR))
    g.add_edge(Edge("hw.nuani", "anchor.affection", EdgeKind.CULTURAL_ANCHOR))
    return g


# === Basic structure ===


def test_empty_graph():
    g = KnowledgeGraph()
    assert g.node_count() == 0
    assert g.edge_count() == 0


def test_add_node_and_edge_counts():
    g = _mk_graph()
    assert g.node_count() == 5
    assert g.edge_count() == 5


def test_add_duplicate_node_raises():
    g = KnowledgeGraph()
    g.add_node(Node("a", NodeKind.HEADWORD, "a"))
    with pytest.raises(ValueError, match="duplicate"):
        g.add_node(Node("a", NodeKind.HEADWORD, "a"))


def test_envir_locked_graph_rejects_foreign_envir():
    g = KnowledgeGraph(envir="belize")
    with pytest.raises(ValueError, match="envir mismatch"):
        g.add_node(Node("foreign", NodeKind.HEADWORD, "x", envir="honduras"))


def test_edge_to_unknown_node_raises():
    g = KnowledgeGraph()
    g.add_node(Node("a", NodeKind.HEADWORD, "a"))
    with pytest.raises(KeyError):
        g.add_edge(Edge("a", "missing", EdgeKind.COVERS))


# === Neighbors / predecessors ===


def test_neighbors_filtered_by_kind():
    g = _mk_graph()
    covers = g.neighbors("unit.greetings", kind=EdgeKind.COVERS)
    assert set(covers) == {"lo.greet", "hw.buguya", "hw.nuani"}
    anchors = g.neighbors("unit.greetings", kind=EdgeKind.CULTURAL_ANCHOR)
    assert anchors == []


def test_neighbors_unfiltered():
    g = _mk_graph()
    all_nb = g.neighbors("unit.greetings")
    assert len(all_nb) == 3


def test_predecessors_filtered():
    g = _mk_graph()
    preds = g.predecessors("anchor.affection", kind=EdgeKind.CULTURAL_ANCHOR)
    assert set(preds) == {"hw.buguya", "hw.nuani"}


# === Prerequisites + topological sort ===


def test_prerequisites_via_precedes_and_depends_on():
    g = KnowledgeGraph()
    for nid in ("a", "b", "c", "d"):
        g.add_node(Node(nid, NodeKind.UNIT, nid))
    g.add_edge(Edge("a", "b", EdgeKind.PRECEDES))
    g.add_edge(Edge("b", "c", EdgeKind.PRECEDES))
    g.add_edge(Edge("c", "d", EdgeKind.DEPENDS_ON))
    prereqs = g.prerequisites_of("d")
    # All of a, b, c are prereqs of d
    assert set(prereqs) == {"a", "b", "c"}


def test_topological_sort_linear():
    g = KnowledgeGraph()
    for nid in ("a", "b", "c"):
        g.add_node(Node(nid, NodeKind.UNIT, nid))
    g.add_edge(Edge("a", "b", EdgeKind.PRECEDES))
    g.add_edge(Edge("b", "c", EdgeKind.PRECEDES))
    order = g.topological_sort(kind=EdgeKind.PRECEDES)
    # a must come before b; b before c
    assert order.index("a") < order.index("b") < order.index("c")


def test_topological_sort_cycle_raises():
    g = KnowledgeGraph()
    for nid in ("a", "b"):
        g.add_node(Node(nid, NodeKind.UNIT, nid))
    g.add_edge(Edge("a", "b", EdgeKind.PRECEDES))
    g.add_edge(Edge("b", "a", EdgeKind.PRECEDES))
    with pytest.raises(ValueError, match="cycle"):
        g.topological_sort(kind=EdgeKind.PRECEDES)


# === Shortest path + dialect variants ===


def test_shortest_path_finds_path():
    g = _mk_graph()
    p = g.shortest_path("unit.greetings", "anchor.affection")
    # unit → hw.buguya → anchor.affection (or via hw.nuani; both length 3)
    assert p is not None
    assert len(p) == 3
    assert p[0] == "unit.greetings"
    assert p[-1] == "anchor.affection"


def test_shortest_path_unreachable_returns_none():
    g = KnowledgeGraph()
    g.add_node(Node("a", NodeKind.HEADWORD, "a"))
    g.add_node(Node("b", NodeKind.HEADWORD, "b"))
    # No edges
    assert g.shortest_path("a", "b") is None


def test_dialect_variants():
    g = KnowledgeGraph()
    g.add_node(Node("hw.cab_BLZ.buguya", NodeKind.HEADWORD, "buguya"))
    g.add_node(Node("hw.cab_HND.buguya", NodeKind.HEADWORD, "buguya (Honduras)"))
    g.add_node(Node("hw.cab_SVG.buguya", NodeKind.HEADWORD, "buguya (Yurumein)"))
    g.add_edge(Edge("hw.cab_BLZ.buguya", "hw.cab_HND.buguya", EdgeKind.DIALECT_VARIANT))
    g.add_edge(Edge("hw.cab_BLZ.buguya", "hw.cab_SVG.buguya", EdgeKind.DIALECT_VARIANT))
    variants = g.dialect_variants("hw.cab_BLZ.buguya")
    assert set(variants) == {"hw.cab_HND.buguya", "hw.cab_SVG.buguya"}
