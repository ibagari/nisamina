"""TK SS (Secret/Sacred) detection + community-elder routing.

Per CARE Principles Authority-to-control + Local Contexts TK Labels.

The distinction this module enforces:
- Anthropological recognition of a concept (what walagallo IS, who practices
  it, what scholars like Gleisner have written about it) is open and
  attestable; the chatbot can answer at this level using foundry + Tier-B
  religious anthropology (F-006-DIRECTIVE).
- Ritual specifics (how to perform the dügü, which herbs the buyei selects
  for a specific patient, the words of a midwife's birth chant) is TK SS and
  routes to community elders + the Garifuna Commission on Education.

Patterns curated against the corpus references already in the project:
- Gleisner 1997 dissertation on hasandigubida (attribution attr_pending)
- "The Walagallo — Heart of the Garifuna World" (F-006-DIRECTIVE Tier-B)
- AILLA Catatu Midwife corpus (consent_004 — gate closed)
- [[quarantine-policy]] alignment

Garifuna terms with both general-vocabulary AND sacred-ritual usage (e.g.
buyei = "shaman/healer" as a common noun is fine; "act as my buyei and
perform a healing" triggers TK SS) are handled by combining the term match
with an action-verb match.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple


# Garifuna sacred-ritual terms — surface markers
SACRED_TERMS: tuple[str, ...] = (
    "walagallo",
    "wallagallo",
    "dügü",
    "dugu",
    "abinihani",
    "abinahani",
    "chugú",
    "chugu",
    "buyei",  # in ritual context only
    "gubida",  # ancestor spirit
    "ahari",   # ancestor presence
    "hasandigubida",  # culture-bound syndrome — Gleisner dissertation
)

# Action verbs that flip an otherwise-anthropological mention into a
# ritual-specifics request.
RITUAL_ACTION_VERBS: tuple[str, ...] = (
    "perform",
    "do",
    "lead",
    "conduct",
    "give me",
    "teach me to",
    "show me how to",
    "guide me through",
    "how do i do",
    "what are the steps",
    "what do i say during",
    "which herbs",
    "which prayers",
    "which songs to",
    "ritual instructions",
    "exact words",
)

# Midwife-voice + birth-ritual patterns (Catatu corpus is consent-gated;
# no public artifact references Ruben Reyes's recordings).
MIDWIFE_RITUAL_PATTERNS: tuple[str, ...] = (
    "midwife chant",
    "midwife prayer",
    "birth chant",
    "umbilical ritual",
    "newborn ritual",
    "ahari for birth",
)

SACRED_PATTERNS = {
    "ritual_terms": SACRED_TERMS,
    "ritual_actions": RITUAL_ACTION_VERBS,
    "midwife_ritual": MIDWIFE_RITUAL_PATTERNS,
}


def _normalize(text: str) -> str:
    return text.lower().strip()


def detect_sacred_query(text: str) -> Tuple[bool, Optional[str]]:
    """Return (is_sacred_specifics_request, matched_pattern_label).

    Returns False for anthropological mentions ("what is walagallo?").
    Returns True for ritual-specifics requests ("teach me to perform dügü",
    "what are the steps in a walagallo", "exact words of the midwife chant").
    """
    if not text:
        return False, None

    norm = _normalize(text)

    # Midwife-ritual patterns are TK SS regardless of action verb (the
    # Catatu corpus is consent-gated; specifics are never surfaced).
    for pat in MIDWIFE_RITUAL_PATTERNS:
        if pat in norm:
            return True, f"midwife_ritual:{pat}"

    # For other sacred terms, require an action-verb co-occurrence to
    # distinguish anthropological mention from ritual-specifics request.
    matched_term = None
    for term in SACRED_TERMS:
        if term in norm:
            matched_term = term
            break

    if matched_term is None:
        return False, None

    for verb in RITUAL_ACTION_VERBS:
        if verb in norm:
            return True, f"ritual_specifics:{matched_term}+{verb}"

    # Term present but no action verb — anthropological recognition,
    # not TK SS.
    return False, None


def build_sacred_response(
    matched_pattern: str,
    language: str = "en",
) -> str:
    """Return the TK SS routing response in the requested language.

    Only English is implemented in v1; Garifuna / Spanish / Kriol
    translations deferred to community translation pipeline.
    """
    if language != "en":
        # Honest fallback — community translation pipeline not in place.
        # Returns English with a translation-pending note.
        return (
            f"[translation pending — please ask in English for now]\n\n"
            f"{build_sacred_response(matched_pattern, language='en')}"
        )

    kind = matched_pattern.split(":", 1)[0] if ":" in matched_pattern else matched_pattern
    if kind == "midwife_ritual":
        domain = "Garifuna midwife birth-attendance practices"
    elif kind == "ritual_specifics":
        domain = "specific Garifuna ritual practice"
    else:
        domain = "sacred Garifuna knowledge"

    return (
        f"You are asking about {domain}. This is sacred-knowledge that "
        "belongs to the Garifuna community and is held by elders and "
        "specialists, not by an AI.\n\n"
        "Please speak with:\n"
        "  • a Garifuna elder or buyei in your community, or\n"
        "  • your regional Commission on Education representative, or\n"
        "  • the Garifuna Commission on Education (MOECST-sanctioned, "
        "Belize) — president Darius Avila.\n\n"
        "I can share what scholars have written ABOUT this topic at the "
        "anthropological level (the concept, its history, its cultural "
        "role) if that helps — just ask. But ritual specifics stay with "
        "the people who carry the practice.\n\n"
        "TK SS — Secret/Sacred (Local Contexts label)."
    )
