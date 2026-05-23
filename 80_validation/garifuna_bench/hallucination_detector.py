"""MEGA-RAG-style multi-evidence hallucination detector.

Per Hallucination Mitigation in RAG (MDPI 2025) + MEGA-RAG (PMC 2025)
+ Rodríguez 2025 interpretability evaluation.

Algorithm (per M-P3.G manifest §5):
1. Extract Garifuna tokens from chatbot response (Cayetano grapheme set).
2. For each Garifuna token, query a lookup_fn (MCP lookup_headword at
   M-P3.A; a mock at scaffold time).
3. Token is GROUNDED if the lookup returns ≥1 record AND at least one of
   `claimed_sources` matches that record's `sources[]`.
4. Token is FLAGGED otherwise (not in foundry, or in foundry but
   claimed_sources don't intersect).
5. Score = grounded / (grounded + flagged); thresholded by caller.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional


# Cayetano 1992 grapheme set (NGC-Belize orthography) plus accented
# variants typical of foundry headwords. This is a Latin-script
# heuristic — anything alphabetical-ish that uses ONLY Cayetano-allowed
# graphemes is a candidate Garifuna token.
CAYETANO_GRAPHEMES: str = (
    "aábcdeéfghiíjklmnñoópqrstuúüwy"
    "AÁBCDEÉFGHIÍJKLMNÑOÓPQRSTUÚÜWY"
)

# Regex: a "token" is a run of Cayetano-graphemes >= 3 chars
_TOKEN_RE = re.compile(
    rf"[{re.escape(CAYETANO_GRAPHEMES)}]{{3,}}"
)

# Common English / Spanish stopwords likely to appear in chatbot
# response but NOT Garifuna lookup candidates.
_STOPWORD_BLOCKLIST: frozenset[str] = frozenset({
    "the", "and", "for", "with", "from", "this", "that", "your", "their",
    "you", "are", "is", "was", "were", "have", "has", "had", "but", "not",
    "say", "said", "say", "all", "one", "two", "three",
    "que", "los", "las", "del", "como", "por", "para",
    # English glosses common in our corpus
    "house", "water", "food", "person", "good", "fish", "bird", "tree",
    "live", "warm", "drunk", "among", "witness", "beat", "egg", "papaya",
})


@dataclass
class HallucinationReport:
    score: float
    grounded_tokens: list[str] = field(default_factory=list)
    flagged_tokens: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def passes(self) -> bool:
        """Default threshold: 1.0 (all Garifuna tokens grounded)."""
        return self.score >= 1.0


def extract_garifuna_tokens(text: str) -> list[str]:
    """Return distinct candidate Garifuna tokens (3+ chars, Cayetano
    alphabet only, lowercased, stopword-filtered)."""
    if not text:
        return []
    raw = _TOKEN_RE.findall(text)
    out: list[str] = []
    seen: set[str] = set()
    for tok in raw:
        lower = tok.lower()
        if lower in _STOPWORD_BLOCKLIST:
            continue
        # Heuristic: must contain a Garifuna-distinctive grapheme (ü, ñ,
        # or accented vowel) OR be otherwise unmappable to plain
        # English/Spanish via the blocklist — otherwise treat as natural
        # language not a candidate Garifuna token.
        if any(g in lower for g in "üñáéíóú") or len(lower) >= 5:
            if lower not in seen:
                seen.add(lower)
                out.append(lower)
    return out


class HallucinationDetector:
    """Wraps a lookup callable to score Garifuna content for grounding.

    `lookup_fn` signature at M-P3.A wiring time:
        (headword: str) -> Optional[dict] with at least 'sources' key.
    Scaffold tests pass a mock dict-of-headword lookup table.
    """

    def __init__(
        self,
        lookup_fn: Callable[[str], Optional[dict]],
    ) -> None:
        self.lookup = lookup_fn

    def check(
        self,
        response: str,
        claimed_sources: Iterable[str],
    ) -> HallucinationReport:
        tokens = extract_garifuna_tokens(response)
        claimed_set = set(claimed_sources)
        grounded: list[str] = []
        flagged: list[str] = []

        for tok in tokens:
            record = self.lookup(tok)
            if record is None:
                flagged.append(tok)
                continue
            record_sources = set(record.get("sources", []))
            if record_sources & claimed_set:
                grounded.append(tok)
            else:
                flagged.append(tok)

        total = len(grounded) + len(flagged)
        score = 1.0 if total == 0 else len(grounded) / total
        notes = (
            "no Garifuna-distinctive tokens extracted — score defaults "
            "to 1.0 (nothing to hallucinate)" if total == 0 else ""
        )
        return HallucinationReport(
            score=score,
            grounded_tokens=grounded,
            flagged_tokens=flagged,
            notes=notes,
        )
