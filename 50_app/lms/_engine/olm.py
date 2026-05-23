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


# ============================================================================
# Negotiable OLM extensions (D-065 SOA gap #3)
# ============================================================================
# Per Bull & Kay 2020 + Dimitrova STyLE-OLM + Jivet et al. 2020 systematic review.
# Inspectable → Negotiable: learner can challenge the model's belief and the
# system enters a structured debate before updating.
#
# Per [[feedback-no-hindsight-whitewashing]]: belief_audit_log is append-only;
# original beliefs are preserved with timestamps; corrections add new records
# referencing the prior via correction_ref.


import json  # noqa: E402 — module-level fine for stdlib
from datetime import datetime, timezone  # noqa: E402
from enum import Enum  # noqa: E402


class BeliefRevisionStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED_BY_LEARNER = "accepted_by_learner"   # learner accepts the system's current belief
    UPDATE_REQUESTED = "update_requested"          # learner contests; requests update
    UPDATED = "updated"                            # system applied an update
    DISMISSED = "dismissed"                        # system dismissed the contest with rationale


@dataclass(frozen=True)
class BeliefRevisionProposal:
    """Learner-initiated challenge to the system's belief about a headword."""
    proposal_id: str
    learner_id: str
    headword: str
    system_p_mastered: float
    learner_claim: str                             # e.g., "I know this; the model is wrong"
    learner_evidence: str                          # e.g., "I used this word with my grandmother yesterday"
    proposed_at: str                               # ISO 8601 UTC
    status: BeliefRevisionStatus = BeliefRevisionStatus.PROPOSED


@dataclass(frozen=True)
class BeliefRevisionResolution:
    """System decision on a learner challenge."""
    proposal_ref: str
    decision: BeliefRevisionStatus                 # UPDATED | DISMISSED
    new_p_mastered: Optional[float]                # if UPDATED
    rationale: str
    decided_at: str                                # ISO 8601 UTC


def _now_iso_olm() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class NegotiableOLMExtension:
    """Mix-in-style extension that adds Negotiable OLM behavior to an OpenLearnerModel.

    Used by composition (not inheritance) to keep OpenLearnerModel's data class
    semantics clean. The extension persists a separate belief_audit_log JSONL
    next to the OLM (append-only) and exposes propose/resolve methods.
    """

    def __init__(self, olm: "OpenLearnerModel"):
        self.olm = olm
        self._audit_log: list[dict] = []           # in-memory; production persists to JSONL
        self._proposals: dict[str, BeliefRevisionProposal] = {}
        self._next_id = 1

    def propose_belief_revision(
        self,
        *,
        headword: str,
        learner_claim: str,
        learner_evidence: str,
    ) -> BeliefRevisionProposal:
        belief = self.olm.beliefs.get(headword)
        system_p = belief.p_mastered if belief else 0.0
        proposal_id = f"belief_rev_{self._next_id:05d}"
        self._next_id += 1
        proposal = BeliefRevisionProposal(
            proposal_id=proposal_id,
            learner_id=self.olm.learner_id,
            headword=headword,
            system_p_mastered=system_p,
            learner_claim=learner_claim,
            learner_evidence=learner_evidence,
            proposed_at=_now_iso_olm(),
        )
        self._proposals[proposal_id] = proposal
        self._audit_log.append({
            "record_type": "proposal",
            "proposal_id": proposal_id,
            "learner_id": self.olm.learner_id,
            "envir": self.olm.envir,
            "headword": headword,
            "system_p_mastered_at_proposal": system_p,
            "learner_claim": learner_claim,
            "learner_evidence": learner_evidence,
            "proposed_at": proposal.proposed_at,
        })
        return proposal

    def resolve(
        self,
        *,
        proposal_id: str,
        decision: BeliefRevisionStatus,
        new_p_mastered: Optional[float] = None,
        rationale: str = "",
    ) -> BeliefRevisionResolution:
        if proposal_id not in self._proposals:
            raise KeyError(f"unknown proposal_id: {proposal_id}")
        if decision == BeliefRevisionStatus.UPDATED:
            if new_p_mastered is None:
                raise ValueError("UPDATED decision requires new_p_mastered")
            if not (0.0 <= new_p_mastered <= 1.0):
                raise ValueError(f"new_p_mastered must be in [0,1]; got {new_p_mastered}")
            # Apply update — but preserve the original belief in audit log
            proposal = self._proposals[proposal_id]
            belief = self.olm.beliefs.get(proposal.headword)
            if belief is not None:
                # Mutate p_mastered via object.__setattr__ since MasteryBelief is a regular dataclass
                belief.p_mastered = new_p_mastered  # noqa: E501 — direct mutation OK on non-frozen dataclass
        resolution = BeliefRevisionResolution(
            proposal_ref=proposal_id,
            decision=decision,
            new_p_mastered=new_p_mastered,
            rationale=rationale,
            decided_at=_now_iso_olm(),
        )
        self._audit_log.append({
            "record_type": "resolution",
            "proposal_ref": proposal_id,
            "decision": decision.value,
            "new_p_mastered": new_p_mastered,
            "rationale": rationale,
            "decided_at": resolution.decided_at,
        })
        return resolution

    def belief_audit_log(self) -> list[dict]:
        """Append-only record of belief proposals + resolutions."""
        return list(self._audit_log)

    def pending_proposals(self) -> list[BeliefRevisionProposal]:
        # A proposal is pending if no resolution record references it
        resolved_refs = {
            r.get("proposal_ref")
            for r in self._audit_log
            if r.get("record_type") == "resolution"
        }
        return [p for p in self._proposals.values() if p.proposal_id not in resolved_refs]
