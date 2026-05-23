"""Tests for M-P3.LMS.ELDER_LOOP — Commission elder review queue."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.elder_loop import (
    ElderReviewItem, ElderReviewItemKind, ElderReviewQueue,
)


def _mk_queue(tmp_path: Path) -> ElderReviewQueue:
    return ElderReviewQueue(queue_path=tmp_path / "elder.jsonl", envir="belize")


def _mk_neologism_item() -> ElderReviewItem:
    return ElderReviewItem(
        item_kind=ElderReviewItemKind.NEOLOGISM,
        title="Garifuna technical term for 'fraction'",
        context_summary="STEM math curriculum K-12 needs technical-register term",
        source_quote="The fraction 1/2 represents half",
        grade_band="04_Upper_Elementary_Grades_3_to_5",
        cultural_protocol_flag=False,
        submitter_role="engineer",
        references=("Cayetano 1992", "Suazo HND"),
    )


def _mk_sacred_item() -> ElderReviewItem:
    return ElderReviewItem(
        item_kind=ElderReviewItemKind.SACRED_CONTENT,
        title="Dügü ceremony movement description",
        context_summary="Heritage pathway G6-9 chart wants ceremonial movement names",
        source_quote=None,
        grade_band="05_Lower_Secondary_Grades_6_to_9",
        cultural_protocol_flag=True,
        submitter_role="curator",
    )


def test_submit_basic(tmp_path):
    q = _mk_queue(tmp_path)
    p = q.submit_item(item=_mk_neologism_item(), submitter="engineer:x")
    assert p.proposal_id == "elder_review_00001"
    assert len(q.pending()) == 1


def test_quorum_neologism():
    q = ElderReviewQueue(queue_path=Path("/tmp/test_q.jsonl"), envir="belize")
    item = _mk_neologism_item()
    assert q.required_quorum(item) == 2  # lexicographer + elder


def test_quorum_sacred():
    q = ElderReviewQueue(queue_path=Path("/tmp/test_q.jsonl"), envir="belize")
    item = _mk_sacred_item()
    assert q.required_quorum(item) == 3  # 3-elder concurrence


def test_sacred_flag_validation(tmp_path):
    q = _mk_queue(tmp_path)
    # Setting cultural_protocol_flag=True on non-SACRED kind should raise
    bad = ElderReviewItem(
        item_kind=ElderReviewItemKind.NEOLOGISM,
        title="x", context_summary="x", source_quote=None, grade_band=None,
        cultural_protocol_flag=True,  # mismatched
        submitter_role="x",
    )
    with pytest.raises(ValueError, match="cultural_protocol_flag"):
        q.submit_item(item=bad, submitter="x")


def test_single_concurrence_not_enough_for_sacred(tmp_path):
    q = _mk_queue(tmp_path)
    p = q.submit_item(item=_mk_sacred_item(), submitter="curator")
    q.add_concurrence(proposal_ref=p.proposal_id, approving_authority="elder:1")
    approved = q.approved_with_quorum()
    # Need 3-elder concurrence; only 1 so far
    assert len(approved) == 0


def test_quorum_reached_after_three_distinct_elders(tmp_path):
    q = _mk_queue(tmp_path)
    p = q.submit_item(item=_mk_sacred_item(), submitter="curator")
    q.add_concurrence(proposal_ref=p.proposal_id, approving_authority="elder:1")
    q.add_concurrence(proposal_ref=p.proposal_id, approving_authority="elder:2")
    q.add_concurrence(proposal_ref=p.proposal_id, approving_authority="elder:3")
    approved = q.approved_with_quorum()
    assert len(approved) == 1


def test_duplicate_concurrence_does_not_count(tmp_path):
    q = _mk_queue(tmp_path)
    p = q.submit_item(item=_mk_sacred_item(), submitter="curator")
    # Same elder approves 3 times — quorum requires 3 DISTINCT authorities
    for _ in range(3):
        q.add_concurrence(proposal_ref=p.proposal_id, approving_authority="elder:1")
    approved = q.approved_with_quorum()
    assert len(approved) == 0


def test_single_reject_blocks_proposal(tmp_path):
    q = _mk_queue(tmp_path)
    p = q.submit_item(item=_mk_sacred_item(), submitter="curator")
    q.reject(
        proposal_ref=p.proposal_id,
        approving_authority="elder:1",
        rationale="content contradicts traditional protocol",
    )
    # Proposal is no longer pending (resolved by rejection)
    assert len(q.pending()) == 0
    # And not approved
    assert len(q.approved_with_quorum()) == 0
