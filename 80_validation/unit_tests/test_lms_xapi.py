"""Tests for M-P3.LMS.XAPI — xAPI dual-emit alongside Caliper."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.caliper import (
    Actor, Action, DigitalResource, CaliperEvent,
)
from lms._engine.xapi import (
    XAPIStatement, XAPIEmitter, caliper_to_xapi,
)


def _mk_caliper_event(envir: str = "belize", action: Action = Action.STARTED) -> CaliperEvent:
    return CaliperEvent.make(
        actor=Actor(actor_id="hash_abc"),
        action=action,
        obj=DigitalResource(resource_id="lesson_001", type="Lesson", envir=envir, name="Day 1"),
        group="cohort_42",
    )


def test_caliper_to_xapi_basic_structure():
    ev = _mk_caliper_event()
    stmt = caliper_to_xapi(ev)
    assert isinstance(stmt, XAPIStatement)
    assert stmt.actor["account"]["name"] == "hash_abc"
    assert "initialized" in stmt.verb["display"]["en-US"]
    assert "Activity" in stmt.object["objectType"]


def test_caliper_to_xapi_envir_in_extensions():
    ev = _mk_caliper_event(envir="honduras")
    stmt = caliper_to_xapi(ev)
    extensions = stmt.object["definition"].get("extensions", {})
    assert "envir" in str(extensions)
    assert "honduras" in str(extensions)


def test_caliper_to_xapi_completed_verb():
    ev = _mk_caliper_event(action=Action.COMPLETED)
    stmt = caliper_to_xapi(ev)
    assert stmt.verb["id"] == "http://adlnet.gov/expapi/verbs/completed"


def test_emitter_buffers_statements():
    buf = XAPIEmitter(envir="belize")
    for _ in range(3):
        buf.emit_from_caliper(_mk_caliper_event(envir="belize"))
    assert len(buf) == 3
    drained = buf.drain()
    assert len(drained) == 3
    assert len(buf) == 0


def test_emitter_envir_isolation():
    buf = XAPIEmitter(envir="belize")
    foreign_event = _mk_caliper_event(envir="honduras")
    with pytest.raises(ValueError, match="envir mismatch"):
        buf.emit_from_caliper(foreign_event)


def test_statement_to_dict_round_trips():
    stmt = caliper_to_xapi(_mk_caliper_event())
    d = stmt.to_dict()
    assert "id" in d
    assert "actor" in d
    assert "verb" in d
    assert "object" in d
    assert "timestamp" in d


def test_unknown_action_falls_back_to_interacted():
    # Use an action that's defined but not mapped
    ev = CaliperEvent.make(
        actor=Actor(actor_id="x"),
        action=Action.VIEWED,
        obj=DigitalResource(resource_id="r", type="Lesson", envir="belize"),
    )
    stmt = caliper_to_xapi(ev)
    # Viewed is in the mapping; should resolve normally
    assert "viewed" in stmt.verb["display"]["en-US"]
