"""M-P3.LMS.RECOMMENDER — F-056 layer 3 multi-agent recommender.

Per F-056 layer-3 + D-065 research §1 (MAGE-KT 2025; DAGKT; dual-graph
convolutional KT). GraphMASAL-shaped multi-agent pattern:
- PrereqAgent: prefers items whose prerequisites the learner has mastered
- DifficultyAgent: prefers items at the right difficulty for pathway
- DiversityAgent: penalizes repetition of same cultural-anchor / dialect_tag
- AffectAgent: avoids items the learner has shown frustration on
- ExploreAgent: occasional exploration of new domains (Thompson-sampling-flavored)

The ensemble combines agent scores via weighted sum + returns ranked candidates.
Consumers (lesson_player, tutor.next_turn auto-curriculum) pick top-k.

Per F-055 axis #6 sovereign-presentation: recommender does not cross envirs
unless explicitly told to via cross_envir flag. Per F-031 + Kaitiakitanga:
sacred-tier content (ELDER_GATED) never recommended without elder authority.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

try:
    from .kgraph import KnowledgeGraph, NodeKind, EdgeKind
    from .pathway import PathwayKind, pathway_for
    from .learner_model import LearnerModelHybrid
except ImportError:
    from kgraph import KnowledgeGraph, NodeKind, EdgeKind
    from pathway import PathwayKind, pathway_for
    from learner_model import LearnerModelHybrid


@dataclass(frozen=True)
class RecommendCandidate:
    """A single candidate item (headword or unit) the recommender considers."""
    item_id: str
    item_kind: str                          # "headword" | "unit" | "lesson"
    label: str
    envir: str
    dialect_tag: Optional[str] = None
    cultural_anchor: Optional[str] = None
    tier: str = "public"                    # "public" | "institutional" | "elder_gated"
    base_difficulty: float = 0.5            # [0, 1]


@dataclass(frozen=True)
class AgentScore:
    """One agent's score + rationale for a candidate."""
    agent_name: str
    raw_score: float                        # [0, 1]; 0 = strongly reject, 1 = strongly recommend
    rationale: str


@dataclass(frozen=True)
class RankedCandidate:
    """A candidate with aggregated multi-agent score + per-agent breakdown."""
    candidate: RecommendCandidate
    ensemble_score: float
    agent_breakdown: tuple[AgentScore, ...]


# === Abstract agent =======================================================


class RecommenderAgent(ABC):
    agent_name: str = ""

    @abstractmethod
    def score(
        self,
        candidate: RecommendCandidate,
        learner_id: str,
        learner_history: dict,
        kgraph: KnowledgeGraph,
        learner_model: LearnerModelHybrid,
        pathway: PathwayKind,
    ) -> AgentScore:
        """Score how strongly this agent recommends the candidate."""


# === Concrete agents ======================================================


class PrereqAgent(RecommenderAgent):
    """Prefers items whose prerequisites the learner has mastered."""
    agent_name = "prereq"

    def score(self, candidate, learner_id, learner_history, kgraph, learner_model, pathway):
        # If candidate is a kgraph node, walk prereqs
        if not kgraph.has_node(candidate.item_id):
            return AgentScore(self.agent_name, 0.5, "candidate not in kgraph — neutral")
        prereqs = kgraph.prerequisites_of(candidate.item_id)
        if not prereqs:
            return AgentScore(self.agent_name, 0.8, "no prereqs — readily learnable")
        # How many of the headword prereqs are mastered?
        mastered = 0
        total = 0
        threshold = pathway_for(pathway).assessment_threshold
        for nid in prereqs:
            node = kgraph.get_node(nid)
            if node.kind == NodeKind.HEADWORD:
                total += 1
                pred = learner_model.predict(learner_id, node.label)
                if pred.recommended_p_mastered >= threshold:
                    mastered += 1
        if total == 0:
            return AgentScore(self.agent_name, 0.7, "no headword prereqs to check")
        ratio = mastered / total
        return AgentScore(
            self.agent_name,
            ratio,
            f"{mastered}/{total} headword prereqs mastered",
        )


class DifficultyAgent(RecommenderAgent):
    """Prefers items at the right difficulty for the learner's pathway.

    HERITAGE has receptive base → prefers mid-high difficulty (0.6-0.8).
    NOVICE prefers low-mid (0.3-0.5).
    L1_MAINTAINER prefers high (0.7-0.9).
    """
    agent_name = "difficulty"

    def score(self, candidate, learner_id, learner_history, kgraph, learner_model, pathway):
        if pathway == PathwayKind.HERITAGE:
            sweet_spot = 0.7
        elif pathway == PathwayKind.NOVICE:
            sweet_spot = 0.4
        else:  # L1_MAINTAINER
            sweet_spot = 0.8
        # Closer to sweet spot → higher score
        delta = abs(candidate.base_difficulty - sweet_spot)
        score = max(0.0, 1.0 - 2.0 * delta)
        return AgentScore(
            self.agent_name,
            score,
            f"difficulty={candidate.base_difficulty:.2f} vs sweet_spot={sweet_spot}",
        )


class DiversityAgent(RecommenderAgent):
    """Penalizes recent repetition of same cultural-anchor or dialect_tag."""
    agent_name = "diversity"

    def score(self, candidate, learner_id, learner_history, kgraph, learner_model, pathway):
        recent_anchors: list[str] = learner_history.get("recent_anchors", [])
        recent_dialects: list[str] = learner_history.get("recent_dialect_tags", [])
        # If recent already saw this anchor + dialect, penalize
        anchor_penalty = 1.0
        if candidate.cultural_anchor and candidate.cultural_anchor in recent_anchors:
            count = recent_anchors.count(candidate.cultural_anchor)
            anchor_penalty = max(0.2, 1.0 - 0.2 * count)
        dialect_penalty = 1.0
        if candidate.dialect_tag and candidate.dialect_tag in recent_dialects:
            count = recent_dialects.count(candidate.dialect_tag)
            dialect_penalty = max(0.5, 1.0 - 0.1 * count)
        score = anchor_penalty * dialect_penalty
        return AgentScore(
            self.agent_name,
            score,
            f"anchor_penalty={anchor_penalty:.2f} dialect_penalty={dialect_penalty:.2f}",
        )


class AffectAgent(RecommenderAgent):
    """Avoids items the learner has shown frustration on.

    Reads `frustrated_anchors` + `frustrated_items` from learner_history.
    """
    agent_name = "affect"

    def score(self, candidate, learner_id, learner_history, kgraph, learner_model, pathway):
        frustrated_items: set[str] = set(learner_history.get("frustrated_items", []))
        frustrated_anchors: set[str] = set(learner_history.get("frustrated_anchors", []))
        if candidate.item_id in frustrated_items:
            return AgentScore(self.agent_name, 0.1, "learner showed frustration on this exact item")
        if candidate.cultural_anchor and candidate.cultural_anchor in frustrated_anchors:
            return AgentScore(self.agent_name, 0.4, "learner frustrated on same anchor")
        return AgentScore(self.agent_name, 0.8, "no frustration signal")


class ExploreAgent(RecommenderAgent):
    """Adds Thompson-sampling-flavored exploration boost for under-seen items."""
    agent_name = "explore"

    def score(self, candidate, learner_id, learner_history, kgraph, learner_model, pathway):
        seen_count = learner_history.get("seen_counts", {}).get(candidate.item_id, 0)
        # Inverse-frequency exploration bonus
        if seen_count == 0:
            return AgentScore(self.agent_name, 0.9, "never seen — explore")
        score = max(0.2, 1.0 / (1.0 + seen_count))
        return AgentScore(self.agent_name, score, f"seen {seen_count}× — diminishing explore")


# === Sacred-tier veto =====================================================


class SacredTierVeto:
    """Hard veto: never recommend ELDER_GATED content without explicit authority."""

    def applies(self, candidate: RecommendCandidate) -> bool:
        return candidate.tier == "elder_gated"


# === Ensemble =============================================================


@dataclass
class Recommender:
    """Multi-agent recommender ensemble.

    Per GraphMASAL pattern: each agent scores independently; ensemble combines
    via weighted sum. SacredTierVeto is a hard filter that runs first.
    """
    kgraph: KnowledgeGraph
    learner_model: LearnerModelHybrid
    pathway: PathwayKind
    agents: list[RecommenderAgent] = field(default_factory=lambda: [
        PrereqAgent(), DifficultyAgent(), DiversityAgent(), AffectAgent(), ExploreAgent(),
    ])
    agent_weights: dict[str, float] = field(default_factory=lambda: {
        "prereq": 0.30, "difficulty": 0.20, "diversity": 0.15,
        "affect": 0.20, "explore": 0.15,
    })
    veto: SacredTierVeto = field(default_factory=SacredTierVeto)
    cross_envir_allowed: bool = False

    def recommend(
        self,
        candidates: list[RecommendCandidate],
        learner_id: str,
        learner_history: Optional[dict] = None,
        top_k: int = 5,
        learner_envir: str = "garicomm",
    ) -> list[RankedCandidate]:
        """Score + rank candidates; return top-k after veto + envir filter."""
        learner_history = learner_history or {}
        # 1. Hard filters: sacred-tier veto + envir lock
        filtered: list[RecommendCandidate] = []
        for c in candidates:
            if self.veto.applies(c):
                continue
            if not self.cross_envir_allowed and c.envir != learner_envir and c.envir != "garicomm":
                # cross-envir not allowed (except GariComm canonical overlay)
                continue
            filtered.append(c)
        # 2. Score remaining via agent ensemble
        ranked: list[RankedCandidate] = []
        for c in filtered:
            agent_scores: list[AgentScore] = []
            ensemble_score = 0.0
            for agent in self.agents:
                a_score = agent.score(c, learner_id, learner_history, self.kgraph,
                                       self.learner_model, self.pathway)
                agent_scores.append(a_score)
                weight = self.agent_weights.get(agent.agent_name, 0.0)
                ensemble_score += weight * a_score.raw_score
            ranked.append(RankedCandidate(
                candidate=c,
                ensemble_score=ensemble_score,
                agent_breakdown=tuple(agent_scores),
            ))
        ranked.sort(key=lambda r: r.ensemble_score, reverse=True)
        return ranked[:top_k]
