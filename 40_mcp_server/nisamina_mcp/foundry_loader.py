"""Foundry v6 V0.2 loader + lookup index.

Loads `30_lexicon/foundry_v6/foundry_v6_v0_2.jsonl` once at server startup and
keeps a public-release-only in-memory index. Shared by `lookup_headword`,
`cite_sources`, `translate_sentence`, and `parse_morphology`.

Per plan v1.1 §2.3 the loader filters `public_release=True` at load time so
the in-memory store cannot leak gated records even if a tool forgets to call
the egress wrapper. Defense in depth: egress wrapper is still mandatory on
every tool response; this filter is the second line of protection.
"""
from __future__ import annotations
import bisect
import difflib
import json
from pathlib import Path
from typing import Iterator

_NISAMINA_APP = Path(__file__).resolve().parent.parent.parent
FOUNDRY_PATH = _NISAMINA_APP / "30_lexicon" / "foundry_v6" / "foundry_v6_v0_2.jsonl"


class FoundryIndex:
    """In-memory index over the public-release slice of foundry_v6 V0.2.

    Attributes:
        records: list of all public_release=True dict records, load order.
        by_norm: dict mapping `headword_normalized` -> list[record] (multiple
                 records can share a normalized form across distinct POS/sense
                 clusters).
        sorted_norms: sorted list of distinct `headword_normalized` keys
                      (for bisect-based prefix lookup).
    """

    def __init__(self, records: list[dict]) -> None:
        self.records: list[dict] = records
        self.by_norm: dict[str, list[dict]] = {}
        for r in records:
            k = (r.get("headword_normalized") or "").lower()
            if not k:
                continue
            self.by_norm.setdefault(k, []).append(r)
        self.sorted_norms: list[str] = sorted(self.by_norm.keys())

    # ---- lookup modes ----

    def lookup_exact(self, query: str) -> list[dict]:
        q = (query or "").strip().lower()
        if not q:
            return []
        return list(self.by_norm.get(q, []))

    def lookup_prefix(self, query: str, limit: int = 10) -> list[dict]:
        q = (query or "").strip().lower()
        if not q:
            return []
        i = bisect.bisect_left(self.sorted_norms, q)
        out: list[dict] = []
        while i < len(self.sorted_norms) and self.sorted_norms[i].startswith(q):
            out.extend(self.by_norm[self.sorted_norms[i]])
            if len(out) >= limit:
                return out[:limit]
            i += 1
        return out

    def lookup_fuzzy(self, query: str, limit: int = 10, cutoff: float = 0.7) -> list[dict]:
        q = (query or "").strip().lower()
        if not q:
            return []
        matches = difflib.get_close_matches(q, self.sorted_norms, n=limit, cutoff=cutoff)
        out: list[dict] = []
        for m in matches:
            out.extend(self.by_norm[m])
            if len(out) >= limit:
                return out[:limit]
        return out

    # ---- iteration ----

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator[dict]:
        return iter(self.records)

    def vault_attested(self) -> list[dict]:
        """Subset where `vault_attested=True` (the V_VAULT 355→542 set)."""
        return [r for r in self.records if r.get("vault_attested") is True]


def load(path: Path | str | None = None) -> FoundryIndex:
    """Load the foundry, filter to public_release=True, build index.

    Raises FileNotFoundError if `path` (or default FOUNDRY_PATH) is missing.
    """
    p = Path(path) if path else FOUNDRY_PATH
    if not p.exists():
        raise FileNotFoundError(f"foundry not found at {p}")
    records: list[dict] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("public_release") is True:
                records.append(r)
    return FoundryIndex(records)
