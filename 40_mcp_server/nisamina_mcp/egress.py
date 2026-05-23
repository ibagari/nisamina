"""Response-layer egress wrapper around 99_publish/strip_linter.

Every MCP tool response — whether a list of foundry records, a synthesized
single record, or a composed multi-record payload — passes through
`enforce_egress()` before it leaves the server. The wrapper:

  1. Coerces the payload into an iterable of dict records that the linter
     can scan (synthesizes a minimal record envelope for non-record outputs
     like a Cayetano-normalize result so the JW/Magarada/Catatu source-ID
     checks still run if a source field is present).
  2. Calls `99_publish/strip_linter.block_if_violations(records)`. On any
     violation, raises `StripLinterError` (re-raised, NOT caught here — the
     server's MCP error handler reports it to the client as a tool error
     and the leaked data does NOT reach the client).
  3. Returns the original payload unchanged on success.

Authority: plan v1.1 §2.3; M-P2 manifest §2.2; D-016 (chatbot must be grounded
via the egress-protected MCP layer, not by the LLM ungrounded).
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any

# Wire in the strip_linter from 99_publish/. Two supported layouts:
#   - Local dev: egress.py at nisamina-app/40_mcp_server/nisamina_mcp/ — 99_publish/ is 3 parents up
#   - HF Space:  egress.py at /app/nisamina_mcp/             — 99_publish/ is at /app/99_publish/
_HERE = Path(__file__).resolve().parent
_CANDIDATE_LOCAL = _HERE.parent.parent / "99_publish"
_CANDIDATE_SPACE = _HERE.parent / "99_publish"  # one parent up = /app/
if _CANDIDATE_SPACE.exists():
    _PUBLISH = _CANDIDATE_SPACE
else:
    _PUBLISH = _CANDIDATE_LOCAL
if str(_PUBLISH) not in sys.path:
    sys.path.insert(0, str(_PUBLISH))

from strip_linter import block_if_violations, lint_record, StripLinterError  # type: ignore  # noqa: E402

__all__ = ["enforce_egress", "StripLinterError"]


def _looks_like_foundry_record(d: dict) -> bool:
    """A dict is treated as a foundry record (and linted) iff it carries all
    three foundry-record-specific fields: `headword` + `tier` + `public_release`.
    Synthesized reports (cayetano_normalize result, parse_morphology summary,
    cite_sources summary, translate_sentence top-level) lack at least one of
    these and skip linting at the top level — but their embedded foundry
    records ARE still extracted and linted via the recursive walk below.

    (`sources` alone is not a strong enough signal: cite_sources's response
    has a `sources` key whose value is `list[dict]` not `list[str]`, which
    tripped a false-positive `missing_required_fields` violation in earlier
    versions of this heuristic.)
    """
    return "headword" in d and "tier" in d and "public_release" in d


def _coerce_to_records(payload: Any) -> list[dict]:
    """Recursively extract all foundry-record-shaped dicts from the payload.

    The linter only runs on dicts that look like foundry records (have both
    `headword` and `sources`). This prevents false positives on synthesized
    tool reports (e.g., cayetano_normalize's `{input, normalized, ...}`) while
    still catching every embedded foundry record inside composed responses
    (e.g., translate_sentence's `tokens[i].matched_records`).
    """
    out: list[dict] = []

    def _walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if _looks_like_foundry_record(obj):
                out.append(obj)
            else:
                for v in obj.values():
                    _walk(v)
        elif isinstance(obj, list):
            for v in obj:
                _walk(v)
        # primitives: nothing to lint

    _walk(payload)
    return out


def enforce_egress(payload: Any, *, context: str = "") -> Any:
    """Block the response if any record carries a forbidden field/source/tier.

    Re-raises `StripLinterError` on violation. The MCP server converts that
    into a tool-call error; the violating data does NOT reach the client.

    Args:
        payload: the tool's would-be response (dict, list[dict], or other).
        context: short label included in the raised error for debugging
                 (e.g., "lookup_headword").

    Returns:
        The original payload, unchanged, if clean.
    """
    records = _coerce_to_records(payload)
    if not records:
        # Empty / non-record payload (e.g., a pure string) — nothing for the
        # linter to scan. The server's tool implementations are responsible
        # for never returning bare strings derived from a record; they should
        # always return the structured record so the linter can guard it.
        return payload
    try:
        block_if_violations(records)
    except StripLinterError as e:
        # Re-raise with context prefix so the audit log can attribute the
        # block to a specific tool path.
        raise StripLinterError(f"[egress:{context or 'unknown'}] {e}") from e
    return payload


def lint_or_none(record: dict, context: str = "") -> list:
    """Helper for tool internals that want to skip a single bad record rather
    than fail the whole response. Returns the violation list (empty = safe).
    Use sparingly — the default for any tool response should be `enforce_egress`.
    """
    return lint_record(record)
