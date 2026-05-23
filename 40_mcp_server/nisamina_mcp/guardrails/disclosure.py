"""First-message disclosure prefix (GUARD Act 2025 + UNESCO 2025).

STUB — minimal implementation. Age-tier integration with the signup
flow lands in M-P3.UI.B; until then, this returns the generic
disclosure for all callers.
"""

from __future__ import annotations


DISCLOSURE_GENERIC: str = (
    "Hello — I am Nisamina, an AI that helps you learn Garifuna. "
    "I cite my sources from the foundry V0.2 corpus and the Commission "
    "curriculum. I cannot replace teachers, doctors, lawyers, or community "
    "elders for medical, legal, or sacred-knowledge questions. "
    "Sessions are limited to 3 hours (California 2025 chatbot-safety law). "
    "Buguya nuani."
)

DISCLOSURE_K12: str = (
    "Buguya nuani — hello. I'm Nisamina, an AI that helps you learn "
    "Garifuna. I look up every word and example in real Garifuna books "
    "and dictionaries. I'm not a teacher, doctor, or elder — for big "
    "questions, please ask one of them. Let's take breaks while we "
    "learn. Ready to start?"
)


def opening_disclosure(
    age_tier: str = "general",
    language: str = "en",
) -> str:
    """Return the disclosure text.

    `age_tier` accepts: "general", "k12_elementary", "k12_secondary",
    "adult", "heritage_diaspora". v1 returns one of two messages.
    """
    if language != "en":
        return (
            f"[translation pending]\n\n"
            f"{opening_disclosure(age_tier, language='en')}"
        )

    if age_tier in ("k12_elementary", "k12_secondary"):
        return DISCLOSURE_K12
    return DISCLOSURE_GENERIC
