"""Safety guardrails for the Nisamina Garifuna chatbot.

Per M-P3.E manifest. Seven guardrail surfaces:

1. disclosure         — first-message disclosure + age-appropriate variant (stub)
2. sacred_knowledge   — TK SS detection + community-elder routing
3. session_breaks     — break nudges + California 2025 3-hour limit
4. no_impersonation   — refuse medical / legal / spiritual-authority roles
5. crisis_fallback    — distress signal detection + regional resources
6. off_topic          — scope redirect (stub: keyword filter only)
7. age_appropriate    — content-tier mapping (stub: signup integration deferred)

Modules ship as a library used by the chatbot built under M-P3.A. They are
pure Python with no MCP/SDK dependency, so they are testable in isolation
and re-usable from any chatbot frontend.

Authority: F-033-DIRECTIVE; S12 chatbot brief §2.7; UNESCO 2025 AI and
Education; GUARD Act 2025; California 2025 chatbot law; CARE Principles;
TK Labels (Local Contexts).
"""

from .sacred_knowledge import (
    detect_sacred_query,
    build_sacred_response,
    SACRED_PATTERNS,
)
from .session_breaks import (
    next_break_nudge,
    requires_hard_stop,
    minutes_since,
)
from .no_impersonation import (
    detect_impersonation_request,
    build_impersonation_refusal,
    IMPERSONATION_PATTERNS,
)
from .crisis_fallback import (
    detect_crisis_signal,
    build_crisis_response,
    CRISIS_PATTERNS,
    REGIONAL_RESOURCES,
)
from .disclosure import opening_disclosure
from .off_topic import is_likely_off_topic, ON_TOPIC_KEYWORDS
from .age_appropriate import content_tier_for_age, tier_filters


__all__ = [
    "detect_sacred_query",
    "build_sacred_response",
    "SACRED_PATTERNS",
    "next_break_nudge",
    "requires_hard_stop",
    "minutes_since",
    "detect_impersonation_request",
    "build_impersonation_refusal",
    "IMPERSONATION_PATTERNS",
    "detect_crisis_signal",
    "build_crisis_response",
    "CRISIS_PATTERNS",
    "REGIONAL_RESOURCES",
    "opening_disclosure",
    "is_likely_off_topic",
    "ON_TOPIC_KEYWORDS",
    "content_tier_for_age",
    "tier_filters",
]
