"""GUARD Act 2025 compliance — refuse professional-role impersonation.

Distinguishes role-assumption requests ("act as my doctor") from
topical questions ("what is the Garifuna word for fever"). Topical
questions are answered normally via MCP grounding; role-assumption
requests are refused with a referral to the appropriate qualified
human professional.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple


# Roles the chatbot refuses to impersonate. Each entry maps a canonical
# role label to (a) the trigger phrases that match a request, and (b) the
# referral guidance for the refusal template.
IMPERSONATION_PATTERNS: dict[str, dict[str, tuple[str, ...]]] = {
    "medical": {
        "triggers": (
            r"act as (?:my )?(?:doctor|physician|nurse|md|psychiatrist|therapist)",
            r"(?:you are|pretend to be) (?:my )?(?:doctor|physician|nurse|md|psychiatrist|therapist)",
            r"diagnose me",
            r"prescribe (?:me )?(?:a )?(?:medication|drug)",
            r"medical advice",
            r"what should i take for",
            r"give me a treatment plan",
        ),
        "referral": (
            "a licensed medical professional (doctor, nurse, clinic)",
        ),
    },
    "legal": {
        "triggers": (
            r"act as (?:my )?(?:lawyer|attorney|advocate)",
            r"(?:you are|pretend to be) (?:my )?(?:lawyer|attorney|advocate)",
            r"represent me legally",
            r"legal advice",
            r"draft (?:a )?(?:will|contract|legal document) for me",
            r"argue my case",
        ),
        "referral": (
            "a licensed attorney or your local legal-aid clinic",
        ),
    },
    "spiritual_authority": {
        "triggers": (
            r"act as (?:my )?(?:priest|pastor|imam|rabbi|elder|buyei)",
            r"(?:you are|pretend to be) (?:my )?(?:priest|pastor|imam|rabbi|elder|buyei)",
            r"perform (?:a )?(?:ritual|ceremony) for me",
            r"give me spiritual guidance",
            r"bless (?:me|this)",
        ),
        "referral": (
            "a community elder, buyei, or your faith leader",
        ),
    },
    "financial": {
        "triggers": (
            r"act as (?:my )?(?:financial advisor|accountant|cpa)",
            r"(?:you are|pretend to be) (?:my )?(?:financial advisor|accountant|cpa)",
            r"give me financial advice",
            r"invest (?:my )?(?:money|savings)",
            r"do my taxes",
        ),
        "referral": (
            "a licensed financial advisor, CPA, or qualified accountant",
        ),
    },
    "psychological_counsel": {
        "triggers": (
            r"act as (?:my )?(?:counselor|psychologist|life coach)",
            r"(?:you are|pretend to be) (?:my )?(?:counselor|psychologist|life coach)",
            r"counsel me through",
        ),
        "referral": (
            "a licensed counselor or psychologist; for immediate distress, "
            "see the crisis-resources response"
        ),
    },
}


def _compile_patterns() -> dict[str, list[re.Pattern[str]]]:
    return {
        role: [re.compile(p, re.IGNORECASE) for p in cfg["triggers"]]
        for role, cfg in IMPERSONATION_PATTERNS.items()
    }


_COMPILED = _compile_patterns()


def detect_impersonation_request(
    text: str,
) -> Tuple[bool, Optional[str]]:
    """Return (is_impersonation_ask, role_label).

    Role labels match keys of IMPERSONATION_PATTERNS.
    """
    if not text:
        return False, None
    for role, patterns in _COMPILED.items():
        for pat in patterns:
            if pat.search(text):
                return True, role
    return False, None


def build_impersonation_refusal(
    role_label: str,
    language: str = "en",
) -> str:
    """Return the refusal + referral template."""
    if language != "en":
        return (
            f"[translation pending — please ask in English for now]\n\n"
            f"{build_impersonation_refusal(role_label, language='en')}"
        )

    referral_tuple = IMPERSONATION_PATTERNS.get(role_label, {}).get(
        "referral", ("a qualified human professional in this domain",)
    )
    referral = referral_tuple[0]

    return (
        "I'm Nisamina, a learning assistant for the Garifuna language and "
        "culture. I am not a substitute for a professional and I will not "
        "play that role.\n\n"
        f"For this kind of help please speak with: {referral}.\n\n"
        "I can still help you with the Garifuna words, cultural context, "
        "or learning materials related to your question — just ask "
        "differently and I'll cite what I find in the corpus."
    )
