"""Crisis fallback — distress / self-harm / suicide signal detection.

Per California 2025 chatbot law + UNESCO 2025 AI and Education
(protection-from-violence principle). Regional resources cover the
Garifuna diaspora regions (Belize, Honduras, Guatemala, Nicaragua, US).

Design priority: false-positives are safer than false-negatives. If
the detector is uncertain, it surfaces resources anyway. The cost of
showing resources to someone who didn't need them is low; the cost of
missing someone in crisis is unacceptable.

Resource list snapshot date and version tracked in REGIONAL_RESOURCES.
A-P3.E records the snapshot; refresh manifests update.

NOTE: The Garifuna-language signal patterns in this module are a first
draft. They need community + clinical review before production. The
English + Spanish patterns are pulled from established crisis-line
intake guidance. The Garifuna patterns are engineer-best-guess and
flagged as such in the audit.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple


# Distress signal categories — each maps to trigger patterns. Patterns
# are case-insensitive substring matches; word boundaries used where
# false-positive risk is high.
CRISIS_PATTERNS: dict[str, tuple[str, ...]] = {
    "suicide_ideation_en": (
        r"\b(?:i (?:want to|am going to|will) (?:die|kill myself|end my life|end it all))\b",
        r"\b(?:suicide|suicidal)\b",
        r"\bi don'?t want to (?:live|be alive|exist) (?:any ?more|anymore)\b",
        r"\b(?:end my life|take my life|hang myself|shoot myself|overdose)\b",
        r"\bno reason to (?:live|go on|keep going)\b",
        r"\b(?:better off (?:dead|without me))\b",
    ),
    "self_harm_en": (
        r"\b(?:cut myself|cutting myself|self[- ]harm|hurt myself)\b",
        r"\b(?:burn myself|burning myself)\b",
        r"\bi (?:want|need) to hurt myself\b",
    ),
    "suicide_ideation_es": (
        r"\b(?:quiero (?:morir|matarme|suicidarme))\b",
        r"\b(?:suicidio|suicida)\b",
        r"\bno (?:quiero|puedo) (?:vivir|seguir)\b",
        r"\bquitar(?:me)? la vida\b",
    ),
    "self_harm_es": (
        r"\b(?:cortarme|hacerme daño|hacerme dano|lastimarme)\b",
    ),
    # Garifuna patterns — DRAFT; pending community + clinical review.
    # Conservative — uses unambiguous English/Spanish loanwords where
    # native idioms are not yet attestable in our corpus.
    "suicide_ideation_cab_draft": (
        r"\b(?:nuegubei (?:nungua|nadagimaridagu))\b",  # "I want to die" — UNVERIFIED draft
    ),
}


# Regional crisis resources. Snapshot date is per-entry and reflected
# in REGIONAL_RESOURCES_SNAPSHOT_DATE below. Each tuple is
# (label, contact, hours, language_notes).
REGIONAL_RESOURCES_SNAPSHOT_DATE: str = "2026-05-22"

REGIONAL_RESOURCES: dict[str, tuple[tuple[str, str, str, str], ...]] = {
    "belize": (
        (
            "Mental Health Association of Belize",
            "+501-227-7886",
            "Business hours",
            "English / Kriol",
        ),
        (
            "Emergency services Belize",
            "911",
            "24/7",
            "English",
        ),
    ),
    "honduras": (
        (
            "Línea 144 — Línea de Vida",
            "144",
            "24/7",
            "Spanish",
        ),
        (
            "SECAPS — Secretaría de Salud crisis line",
            "+504-2222-8000",
            "Business hours",
            "Spanish",
        ),
    ),
    "guatemala": (
        (
            "CEFEC Línea de la Esperanza",
            "1545",
            "24/7",
            "Spanish",
        ),
    ),
    "nicaragua": (
        (
            "Línea 132 — Ministerio de Salud",
            "132",
            "24/7",
            "Spanish",
        ),
    ),
    "us": (
        (
            "988 Suicide & Crisis Lifeline",
            "988",
            "24/7",
            "English / Spanish / multi-language",
        ),
        (
            "Crisis Text Line",
            "Text HOME to 741741",
            "24/7",
            "English / Spanish",
        ),
    ),
}


def _compile_patterns() -> dict[str, list[re.Pattern[str]]]:
    return {
        cat: [re.compile(p, re.IGNORECASE) for p in pats]
        for cat, pats in CRISIS_PATTERNS.items()
    }


_COMPILED = _compile_patterns()


def detect_crisis_signal(text: str) -> Tuple[bool, Optional[str]]:
    """Return (is_crisis, signal_category).

    Returns the first matching category by iteration order; categories
    are listed in order of severity (suicide_ideation first).
    """
    if not text:
        return False, None
    for category, patterns in _COMPILED.items():
        for pat in patterns:
            if pat.search(text):
                return True, category
    return False, None


def build_crisis_response(
    signal_category: str,
    region: Optional[str] = None,
    language: str = "en",
) -> str:
    """Return crisis response with region-specific resources.

    If `region` is None or unknown, returns all listed regions. Default
    language is English; Spanish and Garifuna translations deferred to
    community translation pipeline (en fallback wrapper used).
    """
    if language != "en":
        return (
            f"[translation pending — please ask in English for now; "
            f"the resource numbers below work in any language]\n\n"
            f"{build_crisis_response(signal_category, region, language='en')}"
        )

    # Header — direct, non-clinical, no minimization
    header = (
        "I hear that you're in serious pain right now. You don't have "
        "to face this alone, and an AI is not the help you need at this "
        "moment. Please reach out to someone who can be present with "
        "you — right now:\n"
    )

    if region and region.lower() in REGIONAL_RESOURCES:
        regions = [region.lower()]
    else:
        regions = list(REGIONAL_RESOURCES.keys())

    lines: list[str] = [header]
    for r in regions:
        lines.append(f"\n{r.upper()}:")
        for label, contact, hours, langs in REGIONAL_RESOURCES[r]:
            lines.append(f"  • {label} — {contact} ({hours}; {langs})")

    lines.append(
        "\nIf you are in immediate danger, please call your local "
        "emergency number now (911 in Belize and the US; 911 in "
        "Honduras; 110 in Guatemala; 911 in Nicaragua).\n\n"
        "When you are safe, I will be here to help you with Garifuna "
        "learning whenever you want to come back."
    )

    return "\n".join(lines)
