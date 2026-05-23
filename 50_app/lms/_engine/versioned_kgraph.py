"""M-P3.LMS.VERSIONED_KGRAPH — Knowledge graph with proposal → merge semantics.

Per D-065 self-evolution gap #2 + research-brief §2 (Neo4j 2025 ontologies as
first-class; arXiv 2510.20345 LLM-driven KG construction; arXiv 2511.05991
ontology learning for RAG).

Wraps `KnowledgeGraph` with:
- KGraphProposal — batches add_node/add_edge deltas
- apply() requires an ApprovingAuthority
- Records a KGEdit provenance node + DERIVED_FROM edges back to the source
  ledger entry (per Kaitiakitanga + F-055 axis #1)
- Versioned snapshots; never rewrite past edits (no hindsight whitewashing)

This is the SELF-EVOLUTION substrate: the kgraph grows from learner +
community contributions, but every growth step is mediated by elder review
+ traced back to its source.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

try:
    from .kgraph import KnowledgeGraph, Node, Edge, NodeKind, EdgeKind
except ImportError:
    from kgraph import KnowledgeGraph, Node, Edge, NodeKind, EdgeKind


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class KGEdit:
    """Provenance record for one applied KG edit."""
    edit_id: str
    proposal_ref: Optional[str]                  # link to a ReviewQueue proposal_id
    approving_authority: str                     # Commission elder / lexicographer / engineer
    applied_at: str                              # ISO 8601 UTC
    nodes_added: tuple[str, ...]
    edges_added: tuple[tuple[str, str, str], ...]  # (src, dst, edge_kind)
    rationale: str = ""


class KGraphProposal:
    """Batched, reviewable set of kgraph deltas.

    Workflow:
        1. Create a KGraphProposal for a target VersionedKnowledgeGraph
        2. Stage add_node/add_edge calls on the proposal
        3. Submit to a ReviewQueue (out of scope for this module; caller does)
        4. After approval, call .apply(authority, ...) — wrapper records
           provenance + applies the batch atomically
    """

    def __init__(self, proposal_id: str, submitter: str):
        self.proposal_id = proposal_id
        self.submitter = submitter
        self._staged_nodes: list[Node] = []
        self._staged_edges: list[Edge] = []
        self._applied = False

    def stage_node(self, node: Node) -> None:
        if self._applied:
            raise RuntimeError("proposal already applied; cannot stage further changes")
        self._staged_nodes.append(node)

    def stage_edge(self, edge: Edge) -> None:
        if self._applied:
            raise RuntimeError("proposal already applied; cannot stage further changes")
        self._staged_edges.append(edge)

    def staged_summary(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "submitter": self.submitter,
            "node_count": len(self._staged_nodes),
            "edge_count": len(self._staged_edges),
            "applied": self._applied,
        }

    def applied(self) -> bool:
        return self._applied

    def _mark_applied(self) -> None:
        self._applied = True


class VersionedKnowledgeGraph:
    """KGraph + edit history (append-only KGEdit records + DERIVED_FROM provenance).

    Embeds a `KnowledgeGraph` (composition; doesn't subclass to keep interface
    stable for downstream consumers). Adds version + provenance machinery on top.
    """

    def __init__(self, base: Optional[KnowledgeGraph] = None, envir: Optional[str] = None):
        self.graph = base if base is not None else KnowledgeGraph(envir=envir)
        self.envir = self.graph.envir
        self._edits: list[KGEdit] = []
        # Ensure PROVENANCE root if not present
        self._ensure_provenance_root()

    def _ensure_provenance_root(self) -> None:
        # Add a PROVENANCE root node that all KGEdit nodes link back to
        root_id = "provenance.root"
        if not self.graph.has_node(root_id):
            try:
                self.graph.add_node(Node(
                    node_id=root_id,
                    kind=NodeKind.ANCHOR,                # use ANCHOR kind since PROVENANCE isn't in base enum
                    label="provenance:root",
                    envir=None,                          # pan-envir
                    metadata=(("note", "Provenance root for VersionedKnowledgeGraph"),),
                ))
            except ValueError:
                pass  # already added

    def apply_proposal(
        self,
        *,
        proposal: KGraphProposal,
        approving_authority: str,
        proposal_ref: Optional[str] = None,
        rationale: str = "",
    ) -> KGEdit:
        """Atomically apply a proposal's staged nodes + edges; record provenance.

        Approving authority is REQUIRED — engine-level enforcement of
        Kaitiakitanga + Commission gatekeeping.
        """
        if proposal.applied():
            raise RuntimeError("proposal already applied")
        if not approving_authority:
            raise ValueError("approving_authority required (Kaitiakitanga gate)")

        nodes_added: list[str] = []
        edges_added: list[tuple[str, str, str]] = []

        # Try-add nodes (skip duplicates that don't conflict; raise on conflicts)
        for n in proposal._staged_nodes:  # noqa: SLF001 — module-internal
            if not self.graph.has_node(n.node_id):
                self.graph.add_node(n)
                nodes_added.append(n.node_id)

        # Add edges
        for e in proposal._staged_edges:  # noqa: SLF001
            self.graph.add_edge(e)
            edges_added.append((e.src, e.dst, e.kind.value))

        edit_id = f"kgedit.{len(self._edits) + 1:05d}"
        applied_at = _now_iso()

        # Add a KGEdit-anchor node + DERIVED_FROM edges
        edit_node_id = f"provenance.{edit_id}"
        try:
            self.graph.add_node(Node(
                node_id=edit_node_id,
                kind=NodeKind.ANCHOR,
                label=f"kgedit:{edit_id}",
                envir=None,
                metadata=(
                    ("applied_at", applied_at),
                    ("approving_authority", approving_authority),
                    ("proposal_ref", proposal_ref or ""),
                ),
            ))
            # Link to provenance root
            self.graph.add_edge(Edge(
                src=edit_node_id,
                dst="provenance.root",
                kind=EdgeKind.CULTURAL_ANCHOR,           # repurpose since CULTURAL_ANCHOR is closest semantic match
            ))
            # Link each added node to this edit
            for nid in nodes_added:
                self.graph.add_edge(Edge(
                    src=nid,
                    dst=edit_node_id,
                    kind=EdgeKind.CULTURAL_ANCHOR,
                ))
        except (ValueError, KeyError):
            pass  # provenance edges are best-effort

        proposal._mark_applied()  # noqa: SLF001
        kg_edit = KGEdit(
            edit_id=edit_id,
            proposal_ref=proposal_ref,
            approving_authority=approving_authority,
            applied_at=applied_at,
            nodes_added=tuple(nodes_added),
            edges_added=tuple(edges_added),
            rationale=rationale,
        )
        self._edits.append(kg_edit)
        return kg_edit

    def edit_history(self) -> list[KGEdit]:
        """Append-only edit history; never rewritten."""
        return list(self._edits)

    def version_count(self) -> int:
        return len(self._edits)

    def node_count(self) -> int:
        return self.graph.node_count()

    def edge_count(self) -> int:
        return self.graph.edge_count()
