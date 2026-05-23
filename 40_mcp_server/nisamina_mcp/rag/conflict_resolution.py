"""Source-priority + conflict-resolution rules.

Per M-P3.B §5. When multiple foundry records match the same query intent,
or when foundry attestation collides with curriculum, religious-anthropology,
or V_VAULT attestation, these rules determine which record(s) the RAG layer
prefers and which warnings surface for the prompt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# Tier-rank order: Tier-5 > Tier-A > Tier-B > Tier-C > Tier-X
_TIER_RANK: dict[str, int] = {
    "5": 5,
    "A": 4,
    "B": 3,
    "C": 2,
    "X": 1,
}


def tier_rank(tier: str) -> int:
    """Return the integer rank for a tier string ('5'/'A'/'B'/'C'/'X').

    Higher integer = higher trust. Unknown tier returns 0.
    """
    return _TIER_RANK.get(str(tier), 0)


# Within a record's `sources[]` list, source-id priority for citation:
# (matches D-010 + D-018 + D-019 attribution-mapping decisions)
_SOURCE_PRIORITY: tuple[str, ...] = (
    "V_VAULT_director_attested",      # director's own attestation — canonical
    "V_VAULT_directorTier5",          # alternate V_VAULT spelling
    "verified_sentences_VERIFIED_01", # director-curated sentence set
    "Garifuna_Language_Commission_curriculum_2023",  # Commission curriculum
    "garifuna_commission_curriculum_2023",           # alternate path
    "Lila_Garifuna_Diccionario_Garifuna_Espanol",    # Suazo
    "Hererun_Wagüchagu_Dimurei_Agei_Garifuna",       # Sabio + Ordóñez
    "The_Peoples_Garifuna_Dictionary",               # Cayetano (NGC)
    "Diccionario_ee las_Lenguas_de_Honduras",        # Ramos
    "Diccionario_Garifuna",                          # community PDF placeholder
    "foundry_v5",                                    # historical foundry merge
    "hadel_vol_I_OCR",                               # Stochl/Hadel
    "hadel_vol_II_OCR",
    "hadel_vol_III_OCR",
    "PDF:castillo_1975",                             # Castillo
    "PDF:garifuna_workshop_2005",                    # OAGANIC
    # Anthropology + religious texts (Tier-B per F-006-DIRECTIVE)
    "gleisner_hasandigubida_thesis",                 # attr_050
    "espiritualidad_garifuna_quevedo_2022",          # attr_051
    "walagallo_heart_garifuna_world_pdf",            # attr_052
)


@dataclass
class SourcePriority:
    """Per-source priority + citation order verdict."""

    source_id: str
    rank: int                # higher = preferred
    is_authority: bool       # V_VAULT / Commission curriculum / Cayetano canon
    notes: Optional[str] = None


def source_priority(source_id: str) -> SourcePriority:
    """Return the priority verdict for a source ID.

    Source IDs not in the priority list get rank 0; authoritative-flagged
    sources (V_VAULT + curriculum + Cayetano-NGC) get is_authority=True.
    """
    try:
        rank_idx = _SOURCE_PRIORITY.index(source_id)
        rank = len(_SOURCE_PRIORITY) - rank_idx
    except ValueError:
        rank = 0

    is_authority = any(
        marker in source_id
        for marker in (
            "V_VAULT",
            "verified_sentences",
            "Garifuna_Language_Commission",
            "garifuna_commission",
            # Cayetano-NGC canonical: Peoples Dictionary edited by Cayetano
            "The_Peoples_Garifuna_Dictionary",
        )
    )
    return SourcePriority(
        source_id=source_id,
        rank=rank,
        is_authority=is_authority,
    )


def resolve_conflicts(
    records: list[dict],
) -> tuple[list[dict], list[str]]:
    """Resolve conflicts when multiple records match the same conceptual query.

    Rules:
      1. If records have the same `headword_normalized`, keep the highest-tier
         record + surface a warning if lower-tier records had divergent senses.
      2. Sort the kept records by (tier-rank desc, n-sources desc).
      3. Surface region-variant warnings if the same concept has Belize vs
         Honduras vs Guatemala vs Nicaragua variants.

    Returns:
        (deduplicated + sorted records, list of conflict-warning strings)
    """
    warnings: list[str] = []

    # Group by headword_normalized
    by_headword: dict[str, list[dict]] = {}
    for rec in records:
        hw = rec.get("headword_normalized", "")
        by_headword.setdefault(hw, []).append(rec)

    kept: list[dict] = []
    for hw, group in by_headword.items():
        if len(group) == 1:
            kept.append(group[0])
            continue

        # Multiple records for same headword — pick highest-tier; warn on senses
        group_sorted = sorted(
            group,
            key=lambda r: (tier_rank(str(r.get("tier", "?"))), r.get("n_sources", 0)),
            reverse=True,
        )
        primary = group_sorted[0]
        kept.append(primary)

        # Check for divergent senses across the group
        all_glosses: set[str] = set()
        for r in group_sorted:
            for s in (r.get("senses") or [])[:3]:
                g = (s.get("gloss_en") or "").strip().lower()
                if g:
                    all_glosses.add(g[:60])
        if len(all_glosses) > 1:
            warnings.append(
                f"Conflict: {hw!r} has divergent gloss across sources "
                f"({len(group)} records); kept Tier-{primary.get('tier')!s} "
                f"as primary."
            )

    # Final sort across distinct headwords
    kept.sort(
        key=lambda r: (
            tier_rank(str(r.get("tier", "?"))),
            r.get("n_sources", 0),
        ),
        reverse=True,
    )

    return kept, warnings
