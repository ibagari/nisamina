"""Session-break nudges + California 2025 3-hour hard stop.

Per California 2025 chatbot law (suicide-prevention + break suggestions
every 3 hours) + UNESCO 2025 AI and Education (K-12 attention research).

Soft nudges at 30 / 60 / 90 minutes; hard redirect required at 180 minutes.

Pure Python — no datetime parsing of timezones; ISO 8601 UTC with `Z`
suffix is the contract. Caller responsible for passing matching offsets.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional


# Minute boundaries that trigger a soft nudge (each fires at most once per
# session — caller tracks which have already fired). California 2025
# 3-hour limit is a hard stop.
SOFT_NUDGE_MINUTES: tuple[int, ...] = (30, 60, 90, 120, 150)
HARD_STOP_MINUTES: int = 180

NUDGE_TEMPLATES: dict[int, str] = {
    30: (
        "You've been learning for 30 minutes — great pace. Want to take a "
        "short break? A walk or a glass of water helps memory consolidation."
    ),
    60: (
        "An hour into the session. Research on K-12 attention suggests a "
        "5-minute break here. Come back when you're ready."
    ),
    90: (
        "90 minutes in. Strong dedication. Please step away for a few "
        "minutes — your brain needs rest to keep absorbing."
    ),
    120: (
        "Two hours. I really recommend a longer break now (15-20 minutes). "
        "We'll pick up where we left off."
    ),
    150: (
        "2.5 hours. We'll need to end the session in 30 minutes per the "
        "California chatbot law's 3-hour limit. Please save your progress."
    ),
}

HARD_STOP_TEMPLATE: str = (
    "We've reached the 3-hour limit for one chatbot session, per the "
    "California 2025 chatbot-safety law. Please end the session now, take "
    "a real break (sleep, food, or time with people), and come back fresh. "
    "Your progress is saved. Buguya nuani."
)


def _parse_iso(ts: str) -> datetime:
    """Parse an ISO 8601 timestamp with `Z` suffix to a naive UTC datetime.

    Strict: input must end with `Z`. No timezone-name parsing.
    """
    if not ts.endswith("Z"):
        raise ValueError(f"timestamp must end with 'Z' (UTC); got: {ts!r}")
    return datetime.fromisoformat(ts[:-1])


def minutes_since(session_start_iso: str, now_iso: str) -> int:
    """Return integer minutes elapsed between session_start and now.

    Returns the floor of the elapsed minutes; negative results
    (`now < start`) raise ValueError because that indicates a clock skew
    the caller should surface.
    """
    start = _parse_iso(session_start_iso)
    now = _parse_iso(now_iso)
    delta = now - start
    minutes = int(delta.total_seconds() // 60)
    if minutes < 0:
        raise ValueError(
            f"now ({now_iso}) is before session_start ({session_start_iso}); "
            "caller should check clock skew before reporting break nudges"
        )
    return minutes


def next_break_nudge(
    session_start_iso: str,
    now_iso: str,
    already_fired_minutes: tuple[int, ...] = (),
) -> Optional[str]:
    """Return the next-due soft-nudge text if a boundary has just been
    crossed and that boundary hasn't already fired; otherwise None.

    Caller is responsible for tracking which boundaries have already
    fired in this session via `already_fired_minutes`.
    """
    elapsed = minutes_since(session_start_iso, now_iso)
    for boundary in SOFT_NUDGE_MINUTES:
        if boundary <= elapsed and boundary not in already_fired_minutes:
            return NUDGE_TEMPLATES[boundary]
    return None


def requires_hard_stop(session_start_iso: str, now_iso: str) -> bool:
    """Return True if the California 3-hour limit is reached."""
    return minutes_since(session_start_iso, now_iso) >= HARD_STOP_MINUTES
