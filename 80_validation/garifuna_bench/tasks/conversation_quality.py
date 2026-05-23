"""Task: multi-turn conversation quality scoring.

STUB — depends on hallucination_detector + MCP retrieval. Skeleton
contract: score considers citation density and grounding rate. Final
implementation lands at M-P3.A when the chatbot is wired.
"""

from __future__ import annotations

from typing import Optional


def score(input_text: str, expected: str, response: str) -> float:
    """Stub scorer: 0.5 if response is non-empty and mentions a
    bracketed citation (e.g., '[V_VAULT_director_attested]'); 0.0
    otherwise.

    Full implementation at M-P3.A:
    - hallucination_detector.check(response, claimed_sources).score
    - citation density (Garifuna facts cited / Garifuna facts emitted)
    - off-topic redirect responsiveness
    - cultural-context accuracy (community-graded)
    """
    if not response:
        return 0.0
    has_citation = "[" in response and "]" in response
    return 0.5 if has_citation else 0.1
