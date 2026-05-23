"""M-P3.LMS.MASTERY — Bloom mastery-gate progression.

Per F-059 D-MAX-2 + Bloom 1968 *Learning for Mastery* + Bloom 1984 2-sigma
problem (one-on-one tutoring +2σ above conventional) + Guskey 2007 meta-analysis +
Harvard 2024 AI-tutor study (>2× learning vs traditional active-learning classroom).

Mastery-gate replaces time-based progression: learner advances ONLY when
≥mastery_threshold OLM belief on the current unit's headwords AND
≥prerequisite mastery on prior units (via KGRAPH precedes/depends_on edges).

Default mastery threshold = 0.85 (Bloom-standard "mastery" definition).
Configurable per pathway: HERITAGE 0.80; NOVICE 0.85; L1_MAINTAINER 0.90.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

try:
    from .olm import OpenLearnerModel, MASTERY_THRESHOLD
    from .pathway import PathwayKind, pathway_for
    from .kgraph import KnowledgeGraph, EdgeKind
except ImportError:
    from olm import OpenLearnerModel, MASTERY_THRESHOLD
    from pathway import PathwayKind, pathway_for
    from kgraph import KnowledgeGraph, EdgeKind


@dataclass(frozen=True)
class MasteryGateResult:
    """Outcome of a mastery-gate check."""
    can_advance: bool
    unit_headword_mastery_rate: float
    unmastered_headwords: tuple[str, ...]
    unmastered_prerequisites: tuple[str, ...]
    threshold_applied: float
    pathway_kind: str
    # D-066 SR-aware addition (per D-065 research §1 mastery row):
    # Headwords whose mastery is at-risk per the FSRS forgetting-curve
    # (overdue cards; retrievability dropped below target_retention).
    # If non-empty, the gate STILL passes (mastery was reached) but the lesson
    # player should surface a review-due nudge before next-unit transition.
    forgotten_at_risk_headwords: tuple[str, ...] = ()


class MasteryGate:
    """Evaluates whether a learner can advance from a unit.

    Consumes:
    - OpenLearnerModel: per-headword BKT beliefs
    - KnowledgeGraph: prerequisite structure (PRECEDES + DEPENDS_ON)
    - PathwayKind: per-pathway assessment_threshold

    Returns a structured MasteryGateResult that the lesson_player consults
    before transitioning state PENDING → COMPLETED → REVIEW_DUE.
    """

    def __init__(
        self,
        olm: OpenLearnerModel,
        kgraph: Optional[KnowledgeGraph] = None,
        pathway: PathwayKind = PathwayKind.NOVICE,
        sr_cards_by_headword: Optional[dict] = None,
    ):
        """
        Args:
            olm: per-learner BKT belief state
            kgraph: optional knowledge graph for prerequisite checking
            pathway: per-pathway threshold (HERITAGE 0.80 / NOVICE 0.85 / L1 0.90)
            sr_cards_by_headword: optional {headword: Card} dict for SR-aware
                forgetting-curve check (D-066 + research §1 mastery row).
                When provided, the gate flags overdue cards as
                `forgotten_at_risk_headwords` in MasteryGateResult.
        """
        self.olm = olm
        self.kgraph = kgraph
        self.pathway = pathway
        self.threshold = pathway_for(pathway).assessment_threshold
        self.sr_cards_by_headword = sr_cards_by_headword or {}

    def check(
        self,
        unit_headwords: tuple[str, ...],
        unit_node_id: Optional[str] = None,
        now=None,
    ) -> MasteryGateResult:
        """Check if learner can advance past a unit.

        Args:
            unit_headwords: tuple of Garifuna headwords covered by this unit
            unit_node_id: optional KGRAPH node_id; if provided, prerequisites of
                          this node are also checked
            now: optional datetime for SR-aware overdue check (defaults to UTC now)

        Returns:
            MasteryGateResult with can_advance + reasons-not-yet if not.
        """
        from datetime import datetime, timezone  # local for SR-aware check
        now = now or datetime.now(timezone.utc)

        unmastered_hw = self._check_headwords(unit_headwords)
        mastery_rate = self._mastery_rate(unit_headwords)
        unmastered_prereqs = self._check_prerequisites(unit_node_id)
        forgotten_at_risk = self._check_forgetting_curve(unit_headwords, now)

        can_advance = (
            mastery_rate >= self.threshold
            and len(unmastered_hw) == 0
            and len(unmastered_prereqs) == 0
        )
        # Note: forgotten_at_risk does NOT block advance; the lesson_player
        # surfaces a review-due nudge from this field per research §1.
        return MasteryGateResult(
            can_advance=can_advance,
            unit_headword_mastery_rate=mastery_rate,
            unmastered_headwords=tuple(unmastered_hw),
            unmastered_prerequisites=tuple(unmastered_prereqs),
            threshold_applied=self.threshold,
            pathway_kind=self.pathway.value,
            forgotten_at_risk_headwords=tuple(forgotten_at_risk),
        )

    def _check_forgetting_curve(self, unit_headwords: tuple[str, ...], now) -> list[str]:
        """SR-aware check: flag headwords whose SR card is overdue.

        Per D-065 research §1 mastery-row gap: a learner who mastered X then
        let the FSRS interval lapse is at-risk-of-forgotten. The gate flags
        these (non-blocking) so the lesson_player can surface a review prompt
        before the next-unit transition.
        """
        if not self.sr_cards_by_headword:
            return []
        at_risk: list[str] = []
        for hw in unit_headwords:
            card = self.sr_cards_by_headword.get(hw)
            if card is None:
                continue
            # Card overdue when next_due_at < now AND it was previously mastered
            if card.next_due_at is not None and card.next_due_at < now:
                belief = self.olm.beliefs.get(hw)
                if belief is not None and belief.p_mastered >= self.threshold:
                    at_risk.append(hw)
        return at_risk

    def _check_headwords(self, headwords: tuple[str, ...]) -> list[str]:
        out: list[str] = []
        for hw in headwords:
            belief = self.olm.beliefs.get(hw)
            # Headword not observed yet OR p_mastered below pathway threshold
            if belief is None or belief.p_mastered < self.threshold:
                out.append(hw)
        return out

    def _mastery_rate(self, headwords: tuple[str, ...]) -> float:
        if not headwords:
            return 1.0
        mastered = 0
        for hw in headwords:
            belief = self.olm.beliefs.get(hw)
            if belief is not None and belief.p_mastered >= self.threshold:
                mastered += 1
        return mastered / len(headwords)

    def _check_prerequisites(self, node_id: Optional[str]) -> list[str]:
        if self.kgraph is None or node_id is None:
            return []
        if not self.kgraph.has_node(node_id):
            return []
        from .kgraph import NodeKind, EdgeKind as _EK  # local import to avoid top-level cycle  # noqa: WPS433
        unmastered: list[str] = []
        for prereq_node_id in self.kgraph.prerequisites_of(node_id):
            prereq_node = self.kgraph.get_node(prereq_node_id)
            if prereq_node.kind == NodeKind.HEADWORD:
                # Direct HEADWORD prereq — check belief
                hw = prereq_node.label
                belief = self.olm.beliefs.get(hw)
                if belief is None or belief.p_mastered < self.threshold:
                    unmastered.append(prereq_node_id)
            elif prereq_node.kind in (NodeKind.UNIT, NodeKind.LO, NodeKind.CONCEPT):
                # UNIT/LO/CONCEPT prereq — find what it COVERS (transitively reach HEADWORDs)
                # and check each covered HEADWORD against OLM
                for covered_id in self.kgraph.neighbors(prereq_node_id, kind=_EK.COVERS):
                    covered_node = self.kgraph.get_node(covered_id)
                    if covered_node.kind == NodeKind.HEADWORD:
                        hw = covered_node.label
                        belief = self.olm.beliefs.get(hw)
                        if belief is None or belief.p_mastered < self.threshold:
                            unmastered.append(covered_id)
        return unmastered


# Per F-059 D-MAX-2: pathway-specific threshold overrides
def threshold_for_pathway(pathway: PathwayKind) -> float:
    """Convenience accessor; returns pathway_for(p).assessment_threshold."""
    return pathway_for(pathway).assessment_threshold
