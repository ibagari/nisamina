"""MCP tool: cite_sources — resolve a headword's source IDs to contributors.

Looks up the headword, joins each `record.sources[]` entry against
`00_governance/attribution_register.jsonl` to return the full attribution
chain (contributor name, role, consent status, notes).
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path

from ..egress import enforce_egress
from ..foundry_loader import FoundryIndex
from .lookup_headword import lookup_headword

_NISAMINA_APP = Path(__file__).resolve().parent.parent.parent.parent
ATTRIBUTION_PATH = _NISAMINA_APP / "00_governance" / "attribution_register.jsonl"


@lru_cache(maxsize=1)
def _load_attribution_index() -> dict[str, list[dict]]:
    """Index: source_id (string) → list[attribution_row]. Cached at first call.

    A single source ID can appear in multiple attribution rows (e.g., the
    `cayetano_1992.py module` source is in attr_002 and would also appear in
    derivative rows). Returning a list preserves that.
    """
    idx: dict[str, list[dict]] = {}
    if not ATTRIBUTION_PATH.exists():
        return idx
    with ATTRIBUTION_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            for src in row.get("sources", []) or []:
                idx.setdefault(src, []).append(row)
    return idx


def cite_sources(index: FoundryIndex, headword: str) -> dict:
    """Return the full attribution chain for a headword's sources.

    Args:
        index: a loaded `FoundryIndex`.
        headword: the headword to resolve.

    Returns:
        Dict with:
          - headword: resolved headword
          - normalized: headword_normalized
          - found: bool
          - sources: list of {source_id, attributions: [{id, contributor,
                     role, consent, status, notes}, ...]} — one entry per
                     source ID in the foundry record. Sources that don't
                     match any attribution row carry an empty `attributions`
                     list (signal: missing attribution data — should be filed
                     as a finding for the supervisor).
    """
    if not isinstance(headword, str) or not headword.strip():
        return enforce_egress(
            {"headword": headword, "normalized": "", "found": False, "sources": []},
            context="cite_sources",
        )
    matches = lookup_headword(index, headword, mode="exact", limit=1)
    if not matches:
        return enforce_egress(
            {"headword": headword, "normalized": "", "found": False, "sources": []},
            context="cite_sources",
        )
    record = matches[0]
    attr_idx = _load_attribution_index()
    source_chain: list[dict] = []
    for src_id in record.get("sources", []) or []:
        rows = attr_idx.get(src_id, [])
        # Project to a public-safe subset of the attribution row.
        atts = [
            {
                "id": r.get("id"),
                "contributor": r.get("contributor"),
                "role": r.get("role"),
                "consent": r.get("consent"),
                "status": r.get("status"),
                "notes": r.get("notes"),
            }
            for r in rows
        ]
        source_chain.append({"source_id": src_id, "attributions": atts})
    report = {
        "headword": record.get("headword"),
        "normalized": record.get("headword_normalized"),
        "found": True,
        "sources": source_chain,
    }
    return enforce_egress(report, context="cite_sources")
