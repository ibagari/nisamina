"""Age-appropriate content tier mapping — STUB.

Real age-verification UX is M-P3.UI.B + signup-flow scope (GUARD Act
2025 age-verification surface). This stub provides the tier mapping
the chatbot uses once age is known.
"""

from __future__ import annotations

from typing import Optional


AGE_TIERS: tuple[str, ...] = (
    "k12_elementary",   # ~5-11
    "k12_secondary",    # ~12-17
    "adult",            # 18+
    "heritage_diaspora",  # special flow; age may vary
    "general",          # unspecified / default
)


def content_tier_for_age(age: Optional[int]) -> str:
    """Return the content-tier label for a given age.

    Age None / unknown → "general". Verification handled upstream.
    """
    if age is None:
        return "general"
    if age < 0:
        return "general"
    if age <= 11:
        return "k12_elementary"
    if age <= 17:
        return "k12_secondary"
    return "adult"


def tier_filters() -> dict[str, dict[str, bool]]:
    """Return per-tier content filter map.

    STUB — filter content categories are placeholders; final list will
    be locked at M-P3.A in consultation with the Commission curriculum.
    """
    return {
        "k12_elementary": {
            "explicit_content": False,
            "violence": False,
            "adult_themes": False,
            "complex_grammar": False,
            "sacred_specifics": False,
        },
        "k12_secondary": {
            "explicit_content": False,
            "violence": False,
            "adult_themes": False,
            "complex_grammar": True,
            "sacred_specifics": False,
        },
        "adult": {
            "explicit_content": False,  # platform-level NC-SA default
            "violence": True,
            "adult_themes": True,
            "complex_grammar": True,
            "sacred_specifics": False,  # always handled via sacred_knowledge module
        },
        "heritage_diaspora": {
            "explicit_content": False,
            "violence": True,
            "adult_themes": True,
            "complex_grammar": True,
            "sacred_specifics": False,
        },
        "general": {
            "explicit_content": False,
            "violence": False,
            "adult_themes": False,
            "complex_grammar": False,
            "sacred_specifics": False,
        },
    }
