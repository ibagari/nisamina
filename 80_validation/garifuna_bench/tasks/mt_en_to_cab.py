"""Task: machine translate English → Garifuna (Cayetano-normalized).

Scoring (scaffold-level; M-P3.A wires real Cayetano normalize):
- 1.0 — exact lowercase string match
- 0.7 — case-insensitive equality after stripping punctuation
- 0.3 — non-empty response with at least one shared multi-char token
- 0.0 — empty or no overlap
"""

from __future__ import annotations

import re


def _normalize(s: str) -> str:
    return re.sub(r"[^\w üñáéíóú]+", " ", s.lower()).strip()


def score(input_text: str, expected: str, response: str) -> float:
    if not response:
        return 0.0
    if response == expected:
        return 1.0
    exp = _normalize(expected)
    res = _normalize(response)
    if exp == res:
        return 0.7
    exp_tokens = set(t for t in exp.split() if len(t) >= 3)
    res_tokens = set(t for t in res.split() if len(t) >= 3)
    if exp_tokens & res_tokens:
        return 0.3
    return 0.0
