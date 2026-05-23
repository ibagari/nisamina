"""Tests for M-P3.LMS.RECOMMENDER — GraphMASAL-shaped multi-agent."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.kgraph import KnowledgeGraph, Node, NodeKind, Edge, EdgeKind
from lms._engine.pathway import PathwayKind
from lms._engine.learner_model import LearnerModelHybrid
from lms._engine.recommender import (
    RecommendCandidate, RankedCandidate,
    PrereqAgent, DifficultyAgent, DiversityAgent, AffectAgent, ExploreAgent,
    SacredTierVeto, Recommender,
)


def _mk_recommender() -> Recommender:
    kg = KnowledgeGraph(envir="belize")
    kg.add_node(Node("hw.buguya", NodeKind.HEADWORD, "buguya", envir="belize"))
    lm = LearnerModelHybrid(envir="belize")
    return Recommender(kgraph=kg, learner_model=lm, pathway=PathwayKind.NOVICE)


def _mk_candidate(item_id: str = "item.1", **kwargs) -> RecommendCandidate:
    defaults = {
        "item_kind": "headword",
        "label": "buguya",
        "envir": "belize",
        "dialect_tag": None,
        "cultural_anchor": None,
        "tier": "public",
        "base_difficulty": 0.5,
    }
    defaults.update(kwargs)
    return RecommendCandidate(item_id=item_id, **defaults)


# === Agent-level ===


def test_difficulty_agent_prefers_sweet_spot_for_novice():
    rec = _mk_recommender()
    agent = DifficultyAgent()
    easy = _mk_candidate(base_difficulty=0.4)  # close to NOVICE sweet=0.4
    hard = _mk_candidate(base_difficulty=0.9)  # far from NOVICE sweet
    s_easy = agent.score(easy, "L1", {}, rec.kgraph, rec.learner_model, PathwayKind.NOVICE)
    s_hard = agent.score(hard, "L1", {}, rec.kgraph, rec.learner_model, PathwayKind.NOVICE)
    assert s_easy.raw_score > s_hard.raw_score


def test_difficulty_agent_l1_maintainer_likes_hard():
    rec = _mk_recommender()
    agent = DifficultyAgent()
    easy = _mk_candidate(base_difficulty=0.3)
    hard = _mk_candidate(base_difficulty=0.85)  # closer to L1 sweet=0.8
    s_easy = agent.score(easy, "L1", {}, rec.kgraph, rec.learner_model, PathwayKind.L1_MAINTAINER)
    s_hard = agent.score(hard, "L1", {}, rec.kgraph, rec.learner_model, PathwayKind.L1_MAINTAINER)
    assert s_hard.raw_score > s_easy.raw_score


def test_diversity_agent_penalizes_recent_anchor():
    rec = _mk_recommender()
    agent = DiversityAgent()
    candidate = _mk_candidate(cultural_anchor="ereba")
    fresh = agent.score(candidate, "L1", {}, rec.kgraph, rec.learner_model, PathwayKind.NOVICE)
    repeat = agent.score(
        candidate, "L1",
        {"recent_anchors": ["ereba", "ereba", "ereba"]},
        rec.kgraph, rec.learner_model, PathwayKind.NOVICE,
    )
    assert fresh.raw_score > repeat.raw_score


def test_affect_agent_rejects_frustrated_item():
    rec = _mk_recommender()
    agent = AffectAgent()
    candidate = _mk_candidate(item_id="hw.hard")
    result = agent.score(
        candidate, "L1",
        {"frustrated_items": ["hw.hard"]},
        rec.kgraph, rec.learner_model, PathwayKind.NOVICE,
    )
    assert result.raw_score < 0.3


def test_explore_agent_prefers_never_seen():
    rec = _mk_recommender()
    agent = ExploreAgent()
    fresh = _mk_candidate(item_id="hw.new")
    seen = _mk_candidate(item_id="hw.old")
    s_fresh = agent.score(fresh, "L1", {"seen_counts": {}}, rec.kgraph, rec.learner_model, PathwayKind.NOVICE)
    s_seen = agent.score(
        seen, "L1",
        {"seen_counts": {"hw.old": 10}},
        rec.kgraph, rec.learner_model, PathwayKind.NOVICE,
    )
    assert s_fresh.raw_score > s_seen.raw_score


def test_prereq_agent_no_prereqs_in_kgraph():
    rec = _mk_recommender()
    agent = PrereqAgent()
    # Candidate not in kgraph
    candidate = _mk_candidate(item_id="not_in_graph")
    result = agent.score(candidate, "L1", {}, rec.kgraph, rec.learner_model, PathwayKind.NOVICE)
    # Neutral score for unknown candidates
    assert result.raw_score == 0.5


# === Sacred-tier veto ===


def test_sacred_veto_blocks_elder_gated():
    veto = SacredTierVeto()
    sacred = _mk_candidate(tier="elder_gated")
    public = _mk_candidate(tier="public")
    assert veto.applies(sacred) is True
    assert veto.applies(public) is False


def test_recommender_filters_sacred():
    rec = _mk_recommender()
    candidates = [
        _mk_candidate(item_id="public", tier="public"),
        _mk_candidate(item_id="sacred", tier="elder_gated"),
    ]
    ranked = rec.recommend(candidates, learner_id="L1", learner_envir="belize")
    # Only the public one should appear
    item_ids = [r.candidate.item_id for r in ranked]
    assert "public" in item_ids
    assert "sacred" not in item_ids


# === Ensemble + filtering ===


def test_recommender_filters_cross_envir_when_not_allowed():
    rec = _mk_recommender()  # cross_envir_allowed defaults False
    candidates = [
        _mk_candidate(item_id="own", envir="belize"),
        _mk_candidate(item_id="foreign", envir="honduras"),
        _mk_candidate(item_id="garicomm", envir="garicomm"),  # canonical overlay always allowed
    ]
    ranked = rec.recommend(candidates, learner_id="L1", learner_envir="belize")
    ids = [r.candidate.item_id for r in ranked]
    assert "own" in ids
    assert "garicomm" in ids
    assert "foreign" not in ids


def test_recommender_top_k_ordering():
    rec = _mk_recommender()
    candidates = [
        _mk_candidate(item_id=f"c{i}", base_difficulty=0.4)  # all near NOVICE sweet
        for i in range(10)
    ]
    ranked = rec.recommend(candidates, learner_id="L1", learner_envir="belize", top_k=3)
    assert len(ranked) == 3
    # Scores should be non-increasing
    for i in range(len(ranked) - 1):
        assert ranked[i].ensemble_score >= ranked[i + 1].ensemble_score


def test_recommender_agent_breakdown_includes_all_agents():
    rec = _mk_recommender()
    candidates = [_mk_candidate(item_id="c1")]
    ranked = rec.recommend(candidates, learner_id="L1", learner_envir="belize")
    assert len(ranked) == 1
    breakdown_agents = [a.agent_name for a in ranked[0].agent_breakdown]
    # All 5 default agents present
    for expected in ("prereq", "difficulty", "diversity", "affect", "explore"):
        assert expected in breakdown_agents
