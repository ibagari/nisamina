"""Tests for M-P3.LMS.OLM Open Learner Model with BKT mastery beliefs."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.olm import (
    MasteryBelief, OpenLearnerModel, MASTERY_THRESHOLD,
)


def test_initial_belief_below_threshold():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    b = olm.observe("buguya", correct=False)
    assert b.p_mastered < MASTERY_THRESHOLD
    assert not b.is_mastered


def test_correct_observations_raise_belief():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    p0 = olm.observe("buguya", correct=True).p_mastered
    for _ in range(5):
        olm.observe("buguya", correct=True)
    p_after = olm.beliefs["buguya"].p_mastered
    assert p_after > p0


def test_eventual_mastery_after_streak_of_correct():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    for _ in range(15):
        olm.observe("buguya", correct=True)
    assert olm.beliefs["buguya"].is_mastered


def test_incorrect_observation_does_not_overshoot():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    olm.observe("buguya", correct=False)
    b = olm.beliefs["buguya"]
    # p_mastered should never drop below 0 or exceed 1
    assert 0.0 <= b.p_mastered <= 1.0


def test_per_headword_independence():
    olm = OpenLearnerModel(learner_id="L1", envir="belize")
    for _ in range(15):
        olm.observe("buguya", correct=True)
    olm.observe("nuani", correct=False)
    assert olm.beliefs["buguya"].is_mastered
    assert not olm.beliefs["nuani"].is_mastered


def test_mastery_rate_aggregation():
    olm = OpenLearnerModel(learner_id="L1", envir="honduras")
    for word in ("a", "b", "c", "d"):
        for _ in range(15):
            olm.observe(word, correct=True)
    for word in ("e", "f"):
        olm.observe(word, correct=False)
    # 4 of 6 mastered = 0.667
    assert olm.mastered_count() == 4
    assert 0.6 < olm.mastery_rate() < 0.7


def test_learner_view_includes_per_headword():
    olm = OpenLearnerModel(learner_id="L1", envir="guatemala")
    olm.observe("buguya", correct=True)
    v = olm.to_learner_view()
    assert v["learner_id"] == "L1"
    assert v["envir"] == "guatemala"
    assert any(h["headword_garifuna"] == "buguya" for h in v["per_headword"])


def test_caliper_summary_excludes_per_headword_pii():
    olm = OpenLearnerModel(learner_id="L1", envir="svg_yurumein")
    olm.observe("buguya", correct=True)
    olm.observe("nuani", correct=False)
    s = olm.to_caliper_summary()
    # Should NOT contain per_headword detail (aggregate only)
    assert "per_headword" not in s
    assert "learner_id" not in s
    assert s["envir"] == "svg_yurumein"
    assert s["total_headwords_seen"] == 2
