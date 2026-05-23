"""Tier-gated multi-evidence rules.

Per M-P3.B §4. The foundry V0.2 tier system already encodes source-count by
construction (Tier-A = 4+ sources, Tier-B = 2-3 sources, Tier-C = 1 source),
so the gates here verify the invariants + decide trust posture per tier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# Conventional minimums (mirrors foundry V0.2 D-010 + D-012 tier definitions)
MIN_SOURCES_TIER_A: int = 4
MIN_SOURCES_TIER_B: int = 2
MIN_SOURCES_TIER_C: int = 1


@dataclass
class MultiEvidenceCheck:
    """Per-record verdict from the multi-evidence pass."""

    headword: str
    tier: str
    n_sources: int
    is_authoritative: bool
    needs_flag: bool
    flag_message: Optional[str]


def check_tier_evidence(record: dict) -> MultiEvidenceCheck:
    """Apply tier-gated rules to a single foundry record.

    Returns:
        MultiEvidenceCheck — verdict + optional flag message ready to surface
        in RAGResult.warnings.
    """
    headword = record.get("headword_normalized", "?")
    tier = str(record.get("tier", "?"))
    n_sources = int(record.get("n_sources", 0))
    vault_attested = bool(record.get("vault_attested", False))

    if tier == "5":
        # Director-attested V_VAULT — authoritative by definition;
        # no multi-source rule applies (the director IS the source).
        return MultiEvidenceCheck(
            headword=headword,
            tier=tier,
            n_sources=n_sources,
            is_authoritative=True,
            needs_flag=False,
            flag_message=None,
        )

    if tier == "A":
        if n_sources < MIN_SOURCES_TIER_A:
            # Schema invariant violation; surface for engineer review
            return MultiEvidenceCheck(
                headword=headword,
                tier=tier,
                n_sources=n_sources,
                is_authoritative=False,
                needs_flag=True,
                flag_message=(
                    f"INVARIANT: {headword!r} is Tier-A but has "
                    f"{n_sources} sources (< MIN_SOURCES_TIER_A={MIN_SOURCES_TIER_A})"
                ),
            )
        return MultiEvidenceCheck(
            headword=headword,
            tier=tier,
            n_sources=n_sources,
            is_authoritative=True,
            needs_flag=False,
            flag_message=None,
        )

    if tier == "B":
        if n_sources < MIN_SOURCES_TIER_B:
            return MultiEvidenceCheck(
                headword=headword,
                tier=tier,
                n_sources=n_sources,
                is_authoritative=False,
                needs_flag=True,
                flag_message=(
                    f"INVARIANT: {headword!r} is Tier-B but has "
                    f"{n_sources} sources (< MIN_SOURCES_TIER_B={MIN_SOURCES_TIER_B})"
                ),
            )
        return MultiEvidenceCheck(
            headword=headword,
            tier=tier,
            n_sources=n_sources,
            is_authoritative=True,
            needs_flag=False,
            flag_message=None,
        )

    if tier == "C":
        # Single-source — surface a community-verification warning.
        return MultiEvidenceCheck(
            headword=headword,
            tier=tier,
            n_sources=n_sources,
            is_authoritative=False,
            needs_flag=True,
            flag_message=(
                f"Tier-C single-source: {headword!r} attested by one source only. "
                "Verify with a Garifuna elder or the Commission before treating as canonical."
            ),
        )

    if tier == "X":
        # Contamination tier — should not reach RAG (public_release=False
        # excludes at foundry-loader time); flag if we do hit it.
        return MultiEvidenceCheck(
            headword=headword,
            tier=tier,
            n_sources=n_sources,
            is_authoritative=False,
            needs_flag=True,
            flag_message=(
                f"INVARIANT: {headword!r} is Tier-X (contamination) but "
                "reached the RAG layer; foundry loader should have excluded it"
            ),
        )

    return MultiEvidenceCheck(
        headword=headword,
        tier=tier,
        n_sources=n_sources,
        is_authoritative=False,
        needs_flag=True,
        flag_message=f"Unknown tier {tier!r} for {headword!r}",
    )
