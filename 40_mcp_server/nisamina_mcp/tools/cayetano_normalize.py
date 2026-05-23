"""MCP tool: cayetano_normalize — apply Cayetano-1992 orthography to text.

Wraps the existing `20_normalize/cayetano_1992.py` module to return a combined
report (normalization + conformance + stress-pattern) so the LLM client can
reason about whether and why a string needs normalization.
"""
from __future__ import annotations
import sys
from pathlib import Path

from ..egress import enforce_egress

_NISAMINA_APP = Path(__file__).resolve().parent.parent.parent.parent
_NORMALIZE = _NISAMINA_APP / "20_normalize"
if str(_NORMALIZE) not in sys.path:
    sys.path.insert(0, str(_NORMALIZE))

from cayetano_1992 import normalize, is_conformant, stress_pattern  # type: ignore  # noqa: E402


def cayetano_normalize(text: str) -> dict:
    """Cayetano-1992-normalize a Garifuna word/phrase and report on it.

    Args:
        text: input string (a word, or a short phrase — applied word-by-word).

    Returns:
        Dict with:
          - input: original text
          - normalized: Cayetano-normalized form
          - is_changed: bool — did normalization alter the input
          - changes: list of {pattern, replacement, occurrences, rationale}
          - is_conformant: bool — does the (normalized) form match Cayetano-1992
          - conformance_reasons: list[str] — violations (empty if conformant)
          - syllables: list[str] — syllabification of the normalized form
          - expected_stress_index: int — predicted stressed syllable
          - actual_stress_index: int | None — actual (acute-accent location)
          - is_irregular_stress: bool

    Note: the return is a synthesized report, not a foundry record. It is
    still wrapped through `enforce_egress` for consistency; nothing in this
    report would normally trigger the strip-linter (no source fields), but
    the wrapper guarantees uniformity across all 5 tools.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be str, got {type(text).__name__}")
    norm_d = normalize(text)
    normalized = norm_d["normalized"]
    ok, reasons = is_conformant(normalized)
    sp = stress_pattern(normalized)
    report = {
        "input": text,
        "normalized": normalized,
        "is_changed": norm_d["is_changed"],
        "changes": norm_d["changes"],
        "is_conformant": ok,
        "conformance_reasons": reasons,
        "syllables": sp["syllables"],
        "expected_stress_index": sp["expected_stressed_index"],
        "actual_stress_index": sp["actual_stressed_index"],
        "is_irregular_stress": sp["is_irregular"],
    }
    return enforce_egress(report, context="cayetano_normalize")
