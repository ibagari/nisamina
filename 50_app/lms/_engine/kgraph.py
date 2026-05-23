"""M-P3.LMS.KGRAPH — Knowledge graph foundation.

Per F-056 layer 1 + F-059 D-MAX-1/2/7 + GraphMASAL 2025 (RECOMMENDER substrate).

Foundation data structure for downstream:
- RECOMMENDER (GraphMASAL multi-agent): traverses for next-item ranking
- TUTOR (Socratic AI): walks prerequisites + presents Socratic chain
- MASTERY (Bloom mastery-gate): checks all-prerequisites-mastered before advance
- SR (FSRS scheduler): per-card scheduling consumes graph for related-card prefetch

Node types:
- HEADWORD (Garifuna headword from foundry V0.2)
- UNIT       (a lesson unit)
- LO         (learning objective; per-country curriculum LO)
- CONCEPT    (cross-cutting concept; e.g., 'fraction comparison')
- CHART      (visual reference per M-P3.LMS.CHARTS)
- ANCHOR     (cultural / Caribbean ecology anchor)
- DIALECT    (per-envir dialect variant marker)

Edge types:
- PRECEDES         (LO precedes LO; UNIT precedes UNIT; concept dependency)
- DEPENDS_ON       (CONCEPT depends on HEADWORD vocabulary; UNIT depends on prior CONCEPT)
- COVERS           (UNIT covers LO; CHART covers HEADWORD)
- DIALECT_VARIANT  (HEADWORD ↔ HEADWORD across dialect_tag)
- CULTURAL_ANCHOR  (HEADWORD ↔ ANCHOR; ANCHOR ↔ CHART)
- TRANSLATES_TO    (HEADWORD cab ↔ HEADWORD en/es; trilingual link)

Per F-055 axis #6 per-MOE sovereignty: graph instances are per-envir; cross-envir
queries are explicit + auditable. GariComm graph is the pan-Garifuna canonical
overlay that cross-references country envirs.
"""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional


class NodeKind(str, Enum):
    HEADWORD = "headword"
    UNIT = "unit"
    LO = "lo"
    CONCEPT = "concept"
    CHART = "chart"
    ANCHOR = "anchor"
    DIALECT = "dialect"


class EdgeKind(str, Enum):
    PRECEDES = "precedes"
    DEPENDS_ON = "depends_on"
    COVERS = "covers"
    DIALECT_VARIANT = "dialect_variant"
    CULTURAL_ANCHOR = "cultural_anchor"
    TRANSLATES_TO = "translates_to"


@dataclass(frozen=True)
class Node:
    """A graph node — opaque to the rest of the system; consumers query by id."""
    node_id: str
    kind: NodeKind
    label: str
    envir: Optional[str] = None  # which envir owns this node (None = pan-Garifuna)
    metadata: tuple[tuple[str, str], ...] = ()  # immutable key-value pairs


@dataclass(frozen=True)
class Edge:
    """A graph edge from src to dst with a kind + optional weight."""
    src: str
    dst: str
    kind: EdgeKind
    weight: float = 1.0


class KnowledgeGraph:
    """In-memory directed graph with kind-tagged nodes + edges.

    Operations:
    - add_node / add_edge
    - neighbors / predecessors with edge-kind filter
    - prerequisites_of (BFS via PRECEDES + DEPENDS_ON)
    - topological_sort (for ordering units in a path)
    - shortest_path (BFS) between two nodes
    - dialect_variants (find translations of a HEADWORD across envirs)
    - coverage_of (which LOs are covered by a UNIT or CHART)
    """

    def __init__(self, envir: Optional[str] = None):
        self.envir = envir
        self._nodes: dict[str, Node] = {}
        # adjacency: out_edges[src][kind] -> list of (dst, weight)
        self._out: dict[str, dict[EdgeKind, list[tuple[str, float]]]] = defaultdict(lambda: defaultdict(list))
        # reverse adjacency for predecessors
        self._in: dict[str, dict[EdgeKind, list[tuple[str, float]]]] = defaultdict(lambda: defaultdict(list))

    # === Mutation =========================================================

    def add_node(self, node: Node) -> None:
        if node.node_id in self._nodes:
            raise ValueError(f"duplicate node_id: {node.node_id}")
        # Per F-055 axis #6: envir-locked graphs reject foreign-envir nodes
        if self.envir is not None and node.envir is not None and node.envir != self.envir:
            raise ValueError(
                f"envir mismatch: graph={self.envir}, node.envir={node.envir}"
            )
        self._nodes[node.node_id] = node

    def add_edge(self, edge: Edge) -> None:
        # Both endpoints must exist
        if edge.src not in self._nodes:
            raise KeyError(f"edge src not found: {edge.src}")
        if edge.dst not in self._nodes:
            raise KeyError(f"edge dst not found: {edge.dst}")
        self._out[edge.src][edge.kind].append((edge.dst, edge.weight))
        self._in[edge.dst][edge.kind].append((edge.src, edge.weight))

    # === Query ============================================================

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def get_node(self, node_id: str) -> Node:
        return self._nodes[node_id]

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return sum(len(v) for src in self._out.values() for v in src.values())

    def neighbors(
        self,
        node_id: str,
        kind: Optional[EdgeKind] = None,
    ) -> list[str]:
        """Successors of node_id, optionally filtered by edge kind."""
        if node_id not in self._out:
            return []
        if kind is None:
            return [dst for kind_map in self._out[node_id].values() for dst, _ in kind_map]
        return [dst for dst, _ in self._out[node_id].get(kind, [])]

    def predecessors(
        self,
        node_id: str,
        kind: Optional[EdgeKind] = None,
    ) -> list[str]:
        if node_id not in self._in:
            return []
        if kind is None:
            return [src for kind_map in self._in[node_id].values() for src, _ in kind_map]
        return [src for src, _ in self._in[node_id].get(kind, [])]

    def prerequisites_of(self, node_id: str) -> list[str]:
        """All nodes reachable as prerequisites via PRECEDES + DEPENDS_ON edges (BFS).

        Does NOT include the node itself. Order is BFS-discovery (closer prereqs first).
        """
        seen: set[str] = set()
        out: list[str] = []
        q: deque[str] = deque()
        for kind in (EdgeKind.PRECEDES, EdgeKind.DEPENDS_ON):
            for pred in self.predecessors(node_id, kind=kind):
                if pred not in seen:
                    seen.add(pred)
                    q.append(pred)
                    out.append(pred)
        while q:
            cur = q.popleft()
            for kind in (EdgeKind.PRECEDES, EdgeKind.DEPENDS_ON):
                for pred in self.predecessors(cur, kind=kind):
                    if pred not in seen:
                        seen.add(pred)
                        q.append(pred)
                        out.append(pred)
        return out

    def topological_sort(self, kind: EdgeKind = EdgeKind.PRECEDES) -> list[str]:
        """Kahn's algorithm topo sort over a single edge kind.

        Raises ValueError if a cycle is detected.
        """
        indeg: dict[str, int] = {n: 0 for n in self._nodes}
        for src, kind_map in self._out.items():
            for dst, _ in kind_map.get(kind, []):
                indeg[dst] += 1
        q: deque[str] = deque(n for n, d in indeg.items() if d == 0)
        out: list[str] = []
        while q:
            cur = q.popleft()
            out.append(cur)
            for dst, _ in self._out[cur].get(kind, []):
                indeg[dst] -= 1
                if indeg[dst] == 0:
                    q.append(dst)
        if len(out) != len(self._nodes):
            raise ValueError(f"cycle detected over edge kind={kind.value}")
        return out

    def shortest_path(
        self,
        src: str,
        dst: str,
        kind: Optional[EdgeKind] = None,
    ) -> Optional[list[str]]:
        """BFS shortest path (uniform-weight); None if unreachable.

        Returns list of node_ids including endpoints, or None if no path.
        """
        if src == dst:
            return [src]
        prev: dict[str, str] = {}
        seen: set[str] = {src}
        q: deque[str] = deque([src])
        while q:
            cur = q.popleft()
            for nb in self.neighbors(cur, kind=kind):
                if nb in seen:
                    continue
                seen.add(nb)
                prev[nb] = cur
                if nb == dst:
                    # Reconstruct path
                    path = [dst]
                    while path[-1] != src:
                        path.append(prev[path[-1]])
                    return list(reversed(path))
                q.append(nb)
        return None

    def dialect_variants(self, node_id: str) -> list[str]:
        """Return all dialect-variant counterparts of a HEADWORD."""
        return self.neighbors(node_id, kind=EdgeKind.DIALECT_VARIANT)

    def covers(self, node_id: str) -> list[str]:
        """Return all nodes that node_id COVERS (e.g., LOs covered by a UNIT or CHART)."""
        return self.neighbors(node_id, kind=EdgeKind.COVERS)

    def translations_of(self, node_id: str) -> list[str]:
        """Return all TRANSLATES_TO targets (cab → en/es links + cross-language pairs)."""
        return self.neighbors(node_id, kind=EdgeKind.TRANSLATES_TO)
