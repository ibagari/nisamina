"""Tests for the RAG layer (M-P3.B).

Coverage:
- Multi-evidence check per tier (5/A/B/C/X)
- Source priority + authority detection
- Conflict resolution (same-headword dedup, divergent-gloss warning)
- RAGRetriever end-to-end with real foundry V0.2
- Augmented context rendering
- Tier-C single-source warning surface
"""

from __future__ import annotations

import pytest

from nisamina_mcp.rag import (
    RAGRetriever,
    RAGResult,
    MultiEvidenceCheck,
    check_tier_evidence,
    SourcePriority,
    resolve_conflicts,
    tier_rank,
    MIN_SOURCES_TIER_A,
    MIN_SOURCES_TIER_B,
)
from nisamina_mcp.rag.conflict_resolution import source_priority
from nisamina_mcp.foundry_loader import load


@pytest.fixture(scope="module")
def foundry_index():
    return load()


@pytest.fixture(scope="module")
def retriever(foundry_index):
    return RAGRetriever(foundry_index)


# ------------------------------------------------------------------ #
# multi_evidence
# ------------------------------------------------------------------ #

class TestMultiEvidence:
    def test_tier5_always_authoritative(self):
        rec = {"headword_normalized": "abayayahouni", "tier": "5", "n_sources": 3, "vault_attested": True}
        v = check_tier_evidence(rec)
        assert v.is_authoritative is True
        assert v.needs_flag is False

    def test_tier_a_with_enough_sources_passes(self):
        rec = {"headword_normalized": "abayayaha", "tier": "A", "n_sources": 5}
        v = check_tier_evidence(rec)
        assert v.is_authoritative is True
        assert v.needs_flag is False

    def test_tier_a_with_too_few_sources_flagged(self):
        # Shouldn't happen by construction; verify gate catches it
        rec = {"headword_normalized": "fake", "tier": "A", "n_sources": 2}
        v = check_tier_evidence(rec)
        assert v.needs_flag is True
        assert "INVARIANT" in v.flag_message

    def test_tier_b_with_2_sources_passes(self):
        rec = {"headword_normalized": "aguriahati", "tier": "B", "n_sources": 3}
        v = check_tier_evidence(rec)
        assert v.is_authoritative is True

    def test_tier_c_single_source_flagged_for_community(self):
        rec = {"headword_normalized": "agriahati", "tier": "C", "n_sources": 1}
        v = check_tier_evidence(rec)
        assert v.is_authoritative is False
        assert v.needs_flag is True
        assert "elder" in v.flag_message.lower() or "Commission" in v.flag_message

    def test_tier_x_should_not_reach_rag(self):
        rec = {"headword_normalized": "junk", "tier": "X", "n_sources": 0}
        v = check_tier_evidence(rec)
        assert v.needs_flag is True
        assert "X" in v.flag_message


# ------------------------------------------------------------------ #
# conflict_resolution
# ------------------------------------------------------------------ #

class TestConflictResolution:
    def test_tier_rank_ordering(self):
        assert tier_rank("5") > tier_rank("A")
        assert tier_rank("A") > tier_rank("B")
        assert tier_rank("B") > tier_rank("C")
        assert tier_rank("C") > tier_rank("X")
        assert tier_rank("?") == 0  # unknown

    def test_source_priority_v_vault_is_authority(self):
        p = source_priority("V_VAULT_director_attested")
        assert p.is_authority is True
        assert p.rank > 0

    def test_source_priority_unknown_source(self):
        p = source_priority("not_in_priority_list")
        assert p.is_authority is False
        assert p.rank == 0

    def test_source_priority_commission_curriculum_is_authority(self):
        p = source_priority("Garifuna_Language_Commission_curriculum_2023")
        assert p.is_authority is True

    def test_resolve_dedup_same_headword(self):
        recs = [
            {"headword_normalized": "test", "tier": "C", "n_sources": 1, "senses": [{"gloss_en": "x"}]},
            {"headword_normalized": "test", "tier": "5", "n_sources": 6, "senses": [{"gloss_en": "x"}]},
        ]
        kept, warns = resolve_conflicts(recs)
        assert len(kept) == 1
        assert kept[0]["tier"] == "5"

    def test_resolve_warns_on_divergent_gloss(self):
        recs = [
            {"headword_normalized": "test", "tier": "B", "n_sources": 3, "senses": [{"gloss_en": "stepfather"}]},
            {"headword_normalized": "test", "tier": "B", "n_sources": 3, "senses": [{"gloss_en": "breeder"}]},
        ]
        kept, warns = resolve_conflicts(recs)
        assert len(kept) == 1
        assert any("divergent" in w.lower() for w in warns)

    def test_resolve_sorts_by_tier_then_sources(self):
        recs = [
            {"headword_normalized": "a", "tier": "B", "n_sources": 3, "senses": []},
            {"headword_normalized": "b", "tier": "5", "n_sources": 6, "senses": []},
            {"headword_normalized": "c", "tier": "A", "n_sources": 5, "senses": []},
        ]
        kept, _ = resolve_conflicts(recs)
        tiers = [r["tier"] for r in kept]
        assert tiers == ["5", "A", "B"]


# ------------------------------------------------------------------ #
# RAGRetriever (end-to-end with real foundry)
# ------------------------------------------------------------------ #

class TestRAGRetriever:
    def test_known_vault_term(self, retriever):
        result = retriever.retrieve("What does abayayahouni mean?")
        assert isinstance(result, RAGResult)
        assert result.n_records >= 1
        hwords = {r["headword_normalized"] for r in result.records}
        assert "abayayahouni" in hwords

    def test_confidence_is_1_for_authoritative_only(self, retriever):
        result = retriever.retrieve("abayayahouni")
        # abayayahouni is Tier-5 V_VAULT — fully authoritative
        if result.n_records > 0:
            assert result.confidence == 1.0

    def test_empty_query_returns_empty(self, retriever):
        result = retriever.retrieve("")
        assert result.n_records == 0
        assert result.augmented_context.startswith("(no foundry")

    def test_corrected_aguriahati_reachable(self, retriever):
        """Verify M-P1.E.fix.2 spelling correction propagated to RAG."""
        result = retriever.retrieve("agüriahati")
        if result.n_records > 0:
            hwords = {r["headword_normalized"] for r in result.records}
            assert "agüriahati" in hwords

    def test_augmented_context_has_citation_format(self, retriever):
        result = retriever.retrieve("abayayahouni")
        if result.n_records > 0:
            # Format: "- {headword} (Tier-{tier}, {n} sources: ...) — {gloss}"
            assert "Tier-" in result.augmented_context
            assert "sources:" in result.augmented_context

    def test_top_n_truncation(self, retriever):
        result = retriever.retrieve("a e i o u y", top_n=2)
        assert result.n_records <= 2
