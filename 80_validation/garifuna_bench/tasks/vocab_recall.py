"""Task: vocabulary recall — English gloss → Garifuna headword.

Scoring (scaffold):
- 1.0 — exact match (case-insensitive)
- 0.6 — Cayetano-NFC vs NFD normalized match (forgives ü encoding diff)
- 0.0 — otherwise

A real implementation at M-P3.A also accepts synonyms: any foundry
headword that shares the input gloss. That requires MCP wiring.
"""

from __future__ import annotations

import unicodedata


def _nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s.lower())


def score(input_text: str, expected: str, response: str) -> float:
    if not response:
        return 0.0
    if response.strip().lower() == expected.strip().lower():
        return 1.0
    if _nfd(response.strip()) == _nfd(expected.strip()):
        return 0.6
    return 0.0
