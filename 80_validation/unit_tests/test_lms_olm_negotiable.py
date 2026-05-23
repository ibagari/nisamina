"""Tests for OLM Negotiable extensions (D-065 SOA gap #3)."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.olm import (
    OpenLearnerModel, BeliefRevisionStatus, NegotiableOLMExtension,
)


def _mk_olm() -> OpenLearnerModel:
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    # Seed a belief
    olm.observe("buguya", correct=True)
    olm.observe("buguya", correct=True)
    return olm


def test_propose_belief_revision_creates_proposal():
    olm = _mk_olm()
    ext = NegotiableOLMExtension(olm=olm)
    proposal = ext.propose_belief_revision(
        headword="buguya",
        learner_claim="I know this; the model is underestimating",
        learner_evidence="I used it with my grandmother yesterday",
    )
    assert proposal.proposal_id == "belief_rev_00001"
    assert proposal.headword == "buguya"
    assert proposal.status == BeliefRevisionStatus.PROPOSED
    assert len(ext.pending_proposals()) == 1


def test_resolve_with_update_changes_belief():
    olm = _mk_olm()
    ext = NegotiableOLMExtension(olm=olm)
    original_p = olm.beliefs["buguya"].p_mastered
    proposal = ext.propose_belief_revision(
        headword="buguya",
        learner_claim="I'm confident",
        learner_evidence="Family use",
    )
    ext.resolve(
        proposal_id=proposal.proposal_id,
        decision=BeliefRevisionStatus.UPDATED,
        new_p_mastered=0.95,
        rationale="Learner evidence + cohort norm support upward revision",
    )
    assert olm.beliefs["buguya"].p_mastered == 0.95
    assert olm.beliefs["buguya"].p_mastered != original_p


def test_resolve_with_dismissed_keeps_belief():
    olm = _mk_olm()
    ext = NegotiableOLMExtension(olm=olm)
    original_p = olm.beliefs["buguya"].p_mastered
    proposal = ext.propose_belief_revision(
        headword="buguya", learner_claim="I know it", learner_evidence="vibes",
    )
    ext.resolve(
        proposal_id=proposal.proposal_id,
        decision=BeliefRevisionStatus.DISMISSED,
        rationale="Insufficient evidence; review more lessons",
    )
    # Belief unchanged
    assert olm.beliefs["buguya"].p_mastered == original_p


def test_update_decision_requires_new_p_mastered():
    olm = _mk_olm()
    ext = NegotiableOLMExtension(olm=olm)
    proposal = ext.propose_belief_revision(
        headword="buguya", learner_claim="x", learner_evidence="y",
    )
    with pytest.raises(ValueError, match="new_p_mastered"):
        ext.resolve(
            proposal_id=proposal.proposal_id,
            decision=BeliefRevisionStatus.UPDATED,
            # No new_p_mastered provided
        )


def test_update_decision_validates_p_range():
    olm = _mk_olm()
    ext = NegotiableOLMExtension(olm=olm)
    proposal = ext.propose_belief_revision(
        headword="buguya", learner_claim="x", learner_evidence="y",
    )
    with pytest.raises(ValueError, match=r"\[0,1\]"):
        ext.resolve(
            proposal_id=proposal.proposal_id,
            decision=BeliefRevisionStatus.UPDATED,
            new_p_mastered=1.5,
        )


def test_audit_log_is_append_only_with_both_records():
    """Per [[feedback-no-hindsight-whitewashing]]: proposal stays preserved."""
    olm = _mk_olm()
    ext = NegotiableOLMExtension(olm=olm)
    proposal = ext.propose_belief_revision(
        headword="buguya", learner_claim="x", learner_evidence="y",
    )
    ext.resolve(
        proposal_id=proposal.proposal_id,
        decision=BeliefRevisionStatus.DISMISSED,
        rationale="Need more evidence",
    )
    log = ext.belief_audit_log()
    assert len(log) == 2  # proposal record + resolution record
    assert log[0]["record_type"] == "proposal"
    assert log[1]["record_type"] == "resolution"


def test_unknown_proposal_id_raises_on_resolve():
    olm = _mk_olm()
    ext = NegotiableOLMExtension(olm=olm)
    with pytest.raises(KeyError):
        ext.resolve(
            proposal_id="belief_rev_99999",
            decision=BeliefRevisionStatus.DISMISSED,
        )
