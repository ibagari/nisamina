"""M-P3.LMS.OLM — Open Learner Model with per-headword mastery beliefs.

Per F-056 LEARNER_MODEL + F-059 D-MAX-2 (mastery learning Bloom 2-sigma).
Mastery threshold: 0.85 (per Bloom standard cited in F-059 D-MAX-2).

Belief update uses Bayesian Knowledge Tracing (BKT) parameters per Corbett & Anderson 1995:
- P(L0)   = prior probability of mastery
- P(T)    = probability of learning given non-mastery
- P(G)    = probability of guess (correct without mastery)
- P(S)    = probability of slip (incorrect with mastery)

Scaffolded implementation; full BKT-LSTM hybrid is M-P3.LMS.LEARNER_MODEL per F-056.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


MASTERY_THRESHOLD = 0.85

# BKT defaults (Corbett & Anderson 1995 vocabulary-learning baseline)
DEFAULT_P_L0 = 0.20  # prior — 20% chance learner already mastered this headword
DEFAULT_P_T = 0.15   # transition — 15% chance of mastery per opportunity
DEFAULT_P_G = 0.20   # guess — 20% chance of correct without mastery
DEFAULT_P_S = 0.10   # slip — 10% chance of incorrect with mastery


@dataclass
class MasteryBelief:
    """Per-headword mastery state for a single learner."""
    learner_id: str
    headword_garifuna: str
    envir: str
    p_mastered: float = DEFAULT_P_L0
    p_transition: float = DEFAULT_P_T
    p_guess: float = DEFAULT_P_G
    p_slip: float = DEFAULT_P_S
    observation_count: int = 0
    correct_count: int = 0

    def update(self, correct: bool) -> None:
        """BKT one-step update given an observation."""
        if correct:
            # P(mastered | correct) = P(mastered) * (1-P(S)) / (P(mastered)*(1-P(S)) + (1-P(mastered))*P(G))
            num = self.p_mastered * (1 - self.p_slip)
            denom = num + (1 - self.p_mastered) * self.p_guess
            self.p_mastered = num / denom if denom > 0 else self.p_mastered
            self.correct_count += 1
        else:
            # P(mastered | incorrect) = P(mastered) * P(S) / (P(mastered)*P(S) + (1-P(mastered))*(1-P(G)))
            num = self.p_mastered * self.p_slip
            denom = num + (1 - self.p_mastered) * (1 - self.p_guess)
            self.p_mastered = num / denom if denom > 0 else self.p_mastered

        # Apply transition (learning given non-mastery)
        self.p_mastered = self.p_mastered + (1 - self.p_mastered) * self.p_transition
        self.observation_count += 1

    @property
    def is_mastered(self) -> bool:
        return self.p_mastered >= MASTERY_THRESHOLD

    @property
    def accuracy(self) -> float:
        return self.correct_count / self.observation_count if self.observation_count else 0.0


@dataclass
class OpenLearnerModel:
    """Aggregate model — collection of per-headword beliefs + cohort-level summary.

    Open-learner-model (OLM) per F-056: learner can view and contest their own model.
    `to_learner_view()` returns the view exposed to the learner UI; `to_caliper_summary()`
    returns the aggregate-only view exposed to teachers / Commission dashboard.
    """
    learner_id: str
    envir: str
    beliefs: dict[str, MasteryBelief] = field(default_factory=dict)

    def observe(self, headword_garifuna: str, correct: bool) -> MasteryBelief:
        belief = self.beliefs.get(headword_garifuna)
        if belief is None:
            belief = MasteryBelief(
                learner_id=self.learner_id,
                headword_garifuna=headword_garifuna,
                envir=self.envir,
            )
            self.beliefs[headword_garifuna] = belief
        belief.update(correct)
        return belief

    def mastered_count(self) -> int:
        return sum(1 for b in self.beliefs.values() if b.is_mastered)

    def mastery_rate(self) -> float:
        if not self.beliefs:
            return 0.0
        return self.mastered_count() / len(self.beliefs)

    def to_learner_view(self) -> dict:
        """View exposed to the learner UI — per F-056 OLM transparency principle."""
        return {
            "learner_id": self.learner_id,
            "envir": self.envir,
            "total_headwords_seen": len(self.beliefs),
            "mastered_count": self.mastered_count(),
            "mastery_rate": self.mastery_rate(),
            "per_headword": [
                {
                    "headword_garifuna": b.headword_garifuna,
                    "p_mastered": round(b.p_mastered, 3),
                    "is_mastered": b.is_mastered,
                    "observation_count": b.observation_count,
                }
                for b in self.beliefs.values()
            ],
        }

    def to_caliper_summary(self) -> dict:
        """Aggregate-only view exposed to teachers / Commission — no per-headword PII."""
        return {
            "envir": self.envir,
            "total_headwords_seen": len(self.beliefs),
            "mastered_count": self.mastered_count(),
            "mastery_rate": self.mastery_rate(),
        }
