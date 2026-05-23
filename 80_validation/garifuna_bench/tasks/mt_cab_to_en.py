"""Task: machine translate Garifuna → English.

Scoring symmetrical to mt_en_to_cab, optimized for English target.
"""

from __future__ import annotations

import re


def _normalize(s: str) -> str:
    return re.sub(r"[^\w]+", " ", s.lower()).strip()


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
    if not exp_tokens:
        return 0.0
    overlap = len(exp_tokens & res_tokens) / len(exp_tokens)
    if overlap >= 0.5:
        return 0.5 + overlap / 2  # 0.75 to 1.0
    if overlap > 0:
        return 0.3
    return 0.0
