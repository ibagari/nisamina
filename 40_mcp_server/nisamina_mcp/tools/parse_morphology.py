"""MCP tool: parse_morphology — extract morphology decomposition for a headword.

Looks up the headword in the foundry; returns the per-sense morphology +
noun_class fields. No invention; ungrounded analysis is explicitly out of scope
(plan v1 line 170: foundry-attested examples only).
"""
from __future__ import annotations

from ..egress import enforce_egress
from ..foundry_loader import FoundryIndex
from .lookup_headword import lookup_headword


def parse_morphology(index: FoundryIndex, headword: str) -> dict:
    """Return the morphology decomposition recorded in the foundry for `headword`.

    Args:
        index: a loaded `FoundryIndex`.
        headword: the headword (or `headword_normalized`) to look up.

    Returns:
        Dict with:
          - headword: the resolved headword (from the foundry record)
          - normalized: headword_normalized
          - found: bool — whether the headword exists in public foundry
          - senses: list of {sense_index, gloss_en, pos, noun_class, morphology, source}
                    drawn directly from the foundry record's `senses[]` field.
                    Empty list if not found OR if the record has no morphology data.

    Egress: response passes through `enforce_egress`; the inner lookup also runs
    its own egress. Defense in depth.
    """
    if not isinstance(headword, str) or not headword.strip():
        return enforce_egress(
            {"headword": headword, "normalized": "", "found": False, "senses": []},
            context="parse_morphology",
        )
    matches = lookup_headword(index, headword, mode="exact", limit=1)
    if not matches:
        return enforce_egress(
            {"headword": headword, "normalized": "", "found": False, "senses": []},
            context="parse_morphology",
        )
    record = matches[0]
    senses_out = []
    for s in record.get("senses", []) or []:
        senses_out.append({
            "sense_index": s.get("sense_index"),
            "gloss_en": s.get("gloss_en"),
            "pos": s.get("pos"),
            "noun_class": s.get("noun_class"),
            "morphology": s.get("morphology"),
            "source": s.get("source"),
        })
    report = {
        "headword": record.get("headword"),
        "normalized": record.get("headword_normalized"),
        "found": True,
        "senses": senses_out,
    }
    return enforce_egress(report, context="parse_morphology")
