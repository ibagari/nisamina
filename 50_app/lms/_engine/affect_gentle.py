"""M-P3.LMS.AFFECT_GENTLE — F-056 layer 5 engagement signals (privacy-respecting).

Per F-056 layer 5 + F-059 D-MAX-AFFECT_GENTLE + SDT 2024-2025 + Hamari 2014.

PRIVACY-RESPECTING engagement signals:
- NO camera or microphone biometrics
- NO eye-tracking
- NO physiological signals
- NO biometric data of any kind

Behavioral signals only (per Hamari 2014 gamification meta + SDT motivation):
- session length (capped + bucketed; opt-in)
- pause patterns (between-turn latency; opt-in)
- retry behavior (correct/incorrect cadence)
- session-of-day distribution (morning/afternoon/evening; opt-in)

Per Indigenous gamification ethics (Miner 2022 + UX Mag 2026): NO streak
pressure / leaderboards. Output is **gentle nudges**, not pressure:
- "You've been at it 45 min — want a 5-min break?" (per California 3-hour law)
- "You're solid on greetings — try a new domain?" (positive surfacing)
- "You haven't visited in 4 days — your community misses you" (gentle return)

Opt-in default per Labayayahoun Ibagari sovereign stewardship.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional


class EngagementSignal(str, Enum):
    SESSION_LENGTH = "session_length"
    PAUSE_PATTERN = "pause_pattern"
    RETRY_BEHAVIOR = "retry_behavior"
    SESSION_TIME_OF_DAY = "session_time_of_day"
    RETURN_GAP = "return_gap"


class NudgeKind(str, Enum):
    BREAK = "break"                          # "Want a 5-min break?"
    POSITIVE_SURFACING = "positive_surfacing"  # "Solid on X; try Y?"
    GENTLE_RETURN = "gentle_return"          # "Your community misses you"
    HARD_STOP = "hard_stop"                  # California 3-hour cap; non-optional
    PACE_DOWN = "pace_down"                  # if retry behavior shows frustration


@dataclass(frozen=True)
class Nudge:
    """A gentle nudge to surface in the UI."""
    nudge_kind: NudgeKind
    message_en: str
    message_es: str
    message_cab: Optional[str]
    is_blocking: bool                        # only HARD_STOP is True
    severity: str = "info"                   # "info" | "warning" | "block"


# === Defaults ===============================================================

DEFAULT_SOFT_NUDGE_MINUTES: int = 45        # break suggestion after 45 min
DEFAULT_HARD_STOP_MINUTES: int = 180         # California 3-hour cap
DEFAULT_GENTLE_RETURN_DAYS: int = 4          # 4+ days absent triggers return nudge
DEFAULT_FRUSTRATION_WINDOW_INCORRECT: int = 5  # 5+ consecutive incorrect → pace-down


# === State ==================================================================


@dataclass
class AffectState:
    """Per-learner per-session affect state. All fields opt-in collected.

    Persistence: stored in per-envir database row; never aggregated cross-envir
    without explicit Commission-cross-envir authority per F-055 axis #6.
    """
    learner_id: str
    envir: str
    session_start: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    last_session_end: Optional[datetime] = None
    consecutive_incorrect: int = 0
    consecutive_correct: int = 0
    opt_in_engagement_signals: bool = False  # default OFF
    nudges_seen_this_session: list[NudgeKind] = field(default_factory=list)


# === Nudge generator ========================================================


class GentleNudgeGenerator:
    """Generates gentle nudges from AffectState.

    Per SDT (self-determination theory): autonomy + competence + relatedness.
    All nudges support autonomy (the learner chooses); never coerce.
    """

    def __init__(
        self,
        soft_nudge_minutes: int = DEFAULT_SOFT_NUDGE_MINUTES,
        hard_stop_minutes: int = DEFAULT_HARD_STOP_MINUTES,
        gentle_return_days: int = DEFAULT_GENTLE_RETURN_DAYS,
        frustration_window: int = DEFAULT_FRUSTRATION_WINDOW_INCORRECT,
    ):
        self.soft_nudge_minutes = soft_nudge_minutes
        self.hard_stop_minutes = hard_stop_minutes
        self.gentle_return_days = gentle_return_days
        self.frustration_window = frustration_window

    def maybe_nudge(self, state: AffectState, now: Optional[datetime] = None) -> Optional[Nudge]:
        """Produce a nudge if state warrants; None otherwise.

        Priority order (highest first):
        1. HARD_STOP (always; non-optional; California law)
        2. PACE_DOWN (frustration safety)
        3. BREAK (soft nudge; if opt-in)
        4. GENTLE_RETURN (cross-session; if opt-in)
        5. POSITIVE_SURFACING (if opt-in + consecutive_correct)
        """
        now = now or datetime.now(timezone.utc)

        # 1. HARD_STOP — always enforced regardless of opt-in
        if state.session_start is not None:
            elapsed_min = (now - state.session_start).total_seconds() / 60.0
            if elapsed_min >= self.hard_stop_minutes:
                if NudgeKind.HARD_STOP not in state.nudges_seen_this_session:
                    return Nudge(
                        nudge_kind=NudgeKind.HARD_STOP,
                        message_en=(
                            "You've been learning for 3 hours. Per California law + your wellbeing, "
                            "we're pausing the session. Take a real break — your progress is saved."
                        ),
                        message_es=(
                            "Has estado aprendiendo durante 3 horas. Por ley de California y por tu "
                            "bienestar, pausamos la sesión. Toma un descanso real — tu progreso está guardado."
                        ),
                        message_cab=None,  # Garifuna translation pending Commission
                        is_blocking=True,
                        severity="block",
                    )

        # 2. PACE_DOWN — frustration safety (always, even without opt-in)
        if state.consecutive_incorrect >= self.frustration_window:
            if NudgeKind.PACE_DOWN not in state.nudges_seen_this_session:
                return Nudge(
                    nudge_kind=NudgeKind.PACE_DOWN,
                    message_en=(
                        "This material is challenging — let's slow down. "
                        "Would you like to review the basics, or try something different?"
                    ),
                    message_es=(
                        "Este material es desafiante — vamos a ir más despacio. "
                        "¿Quieres repasar lo básico, o probar algo diferente?"
                    ),
                    message_cab=None,
                    is_blocking=False,
                    severity="warning",
                )

        # Below here: opt-in required
        if not state.opt_in_engagement_signals:
            return None

        # 3. BREAK — soft break nudge
        if state.session_start is not None:
            elapsed_min = (now - state.session_start).total_seconds() / 60.0
            if elapsed_min >= self.soft_nudge_minutes:
                if NudgeKind.BREAK not in state.nudges_seen_this_session:
                    return Nudge(
                        nudge_kind=NudgeKind.BREAK,
                        message_en="You've been going for 45 minutes — want a 5-minute break?",
                        message_es="Llevas 45 minutos — ¿quieres un descanso de 5 minutos?",
                        message_cab=None,
                        is_blocking=False,
                        severity="info",
                    )

        # 4. GENTLE_RETURN — cross-session
        if state.last_session_end is not None:
            gap_days = (now - state.last_session_end).days
            if gap_days >= self.gentle_return_days:
                if NudgeKind.GENTLE_RETURN not in state.nudges_seen_this_session:
                    return Nudge(
                        nudge_kind=NudgeKind.GENTLE_RETURN,
                        message_en=f"It's been {gap_days} days. Your learning community is here when you're ready.",
                        message_es=f"Han pasado {gap_days} días. Tu comunidad de aprendizaje está aquí cuando estés listo/a.",
                        message_cab=None,
                        is_blocking=False,
                        severity="info",
                    )

        # 5. POSITIVE_SURFACING
        if state.consecutive_correct >= 10:
            if NudgeKind.POSITIVE_SURFACING not in state.nudges_seen_this_session:
                return Nudge(
                    nudge_kind=NudgeKind.POSITIVE_SURFACING,
                    message_en="You're on a roll. Want to try a new domain — or go deeper in this one?",
                    message_es="Vas muy bien. ¿Quieres probar un nuevo dominio — o profundizar más en este?",
                    message_cab=None,
                    is_blocking=False,
                    severity="info",
                )

        return None
