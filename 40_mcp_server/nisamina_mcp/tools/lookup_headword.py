"""MCP tool: lookup_headword — exact/prefix/fuzzy search over foundry_v6.

Returns matched records (already public_release-filtered at load time;
additionally passed through `enforce_egress` so the response cannot leak
gated fields or sources even if a future foundry build accidentally lets
something through).
"""
from __future__ import annotations
from typing import Literal

from ..egress import enforce_egress
from ..foundry_loader import FoundryIndex

Mode = Literal["exact", "prefix", "fuzzy"]
DEFAULT_LIMIT = 10


def lookup_headword(
    index: FoundryIndex,
    query: str,
    mode: Mode = "exact",
    limit: int = DEFAULT_LIMIT,
) -> list[dict]:
    """Search the foundry by `headword_normalized`.

    Args:
        index: a loaded `FoundryIndex` (built by `foundry_loader.load()`).
        query: the search string (case-insensitive; will be lowercased).
        mode: one of `exact` (default), `prefix`, `fuzzy` (difflib close-match).
        limit: max records to return (default 10).

    Returns:
        List of dict records, each carrying the full foundry_v6 V0.2 schema
        (headword, headword_normalized, senses, examples, sources, n_sources,
        tier, vault_attested, public_release, ...). Empty list if no match.

    Egress: response passes through `enforce_egress(context="lookup_headword")`;
    any leaked gated field/source raises `StripLinterError` and the response
    does NOT reach the caller.
    """
    if limit < 1 or limit > 100:
        limit = DEFAULT_LIMIT
    if mode == "exact":
        results = index.lookup_exact(query)[:limit]
    elif mode == "prefix":
        results = index.lookup_prefix(query, limit=limit)
    elif mode == "fuzzy":
        results = index.lookup_fuzzy(query, limit=limit)
    else:
        raise ValueError(f"unknown mode: {mode!r} (expected exact|prefix|fuzzy)")
    return enforce_egress(results, context="lookup_headword")
