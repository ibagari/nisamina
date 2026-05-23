"""Tests for M-P3.LMS.REVIEW_QUEUE — universal review queue."""
from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.review_queue import (
    ReviewQueue, ReviewProposal, ReviewDecision, ReviewStatus,
)


@dataclass(frozen=True)
class _ChartProposalPayload:
    chart_id: str
    new_anchor: str


def _mk_queue(tmp_path: Path) -> ReviewQueue:
    return ReviewQueue[_ChartProposalPayload](
        queue_path=tmp_path / "chart_review.jsonl",
        proposal_type="chart_proposal",
        envir="belize",
    )


def test_submit_creates_pending_proposal(tmp_path):
    q = _mk_queue(tmp_path)
    proposal = q.submit(
        submitter="curator:dgonzalez",
        payload=_ChartProposalPayload("chart.calendar.garifuna_observances", "Chugu lunar cycle"),
    )
    assert proposal.proposal_id == "chart_proposal_00001"
    assert proposal.status == ReviewStatus.PENDING
    assert len(q.pending_proposals()) == 1


def test_approve_moves_proposal_to_approved(tmp_path):
    q = _mk_queue(tmp_path)
    p = q.submit(
        submitter="learner:L1",
        payload=_ChartProposalPayload("chart.colors.basic", "Caribbean turquoise"),
    )
    q.approve(
        proposal_ref=p.proposal_id,
        approving_authority="Commission elder panel",
        rationale="Aligns with Cayetano 1992 §colors",
    )
    assert len(q.pending_proposals()) == 0
    approved = q.approved_proposals()
    assert len(approved) == 1
    assert approved[0]["proposal_id"] == p.proposal_id


def test_reject_does_not_appear_in_approved(tmp_path):
    q = _mk_queue(tmp_path)
    p = q.submit(
        submitter="curator:x",
        payload=_ChartProposalPayload("chart.invalid", "made up"),
    )
    q.reject(
        proposal_ref=p.proposal_id,
        approving_authority="Commission elder",
        rationale="No source citation",
    )
    assert len(q.pending_proposals()) == 0
    assert len(q.approved_proposals()) == 0


def test_persistence_across_instances(tmp_path):
    path = tmp_path / "q.jsonl"
    q1 = ReviewQueue[_ChartProposalPayload](
        queue_path=path, proposal_type="chart", envir="belize",
    )
    q1.submit(submitter="x", payload=_ChartProposalPayload("c", "a"))
    q2 = ReviewQueue[_ChartProposalPayload](
        queue_path=path, proposal_type="chart", envir="belize",
    )
    assert len(q2.list_records()) == 1


def test_decision_records_appended_not_overwriting(tmp_path):
    """Per [[feedback-no-hindsight-whitewashing]]: original proposal preserved."""
    q = _mk_queue(tmp_path)
    p = q.submit(submitter="x", payload=_ChartProposalPayload("c", "a"))
    q.approve(proposal_ref=p.proposal_id, approving_authority="elder")
    records = q.list_records()
    assert len(records) == 2  # proposal + decision (both present)
    assert records[0]["record_type"] == "proposal"
    assert records[1]["record_type"] == "decision"


def test_sequential_ids(tmp_path):
    q = _mk_queue(tmp_path)
    p1 = q.submit(submitter="x", payload=_ChartProposalPayload("c1", "a1"))
    p2 = q.submit(submitter="x", payload=_ChartProposalPayload("c2", "a2"))
    p3 = q.submit(submitter="x", payload=_ChartProposalPayload("c3", "a3"))
    assert p1.proposal_id == "chart_proposal_00001"
    assert p2.proposal_id == "chart_proposal_00002"
    assert p3.proposal_id == "chart_proposal_00003"
