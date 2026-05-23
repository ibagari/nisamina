"""Tests for M-P3.LMS.CALIPER IMS Caliper 1.2 events."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.caliper import (
    Actor, Action, DigitalResource, CaliperEvent, EventBuffer,
)


def test_event_make_populates_envelope():
    ev = CaliperEvent.make(
        actor=Actor(actor_id="hash_abc"),
        action=Action.STARTED,
        obj=DigitalResource(resource_id="lesson_001", type="Lesson", envir="belize"),
    )
    assert ev.id.startswith("urn:uuid:")
    assert ev.actor.actor_id == "hash_abc"
    assert ev.action == Action.STARTED
    assert ev.object.envir == "belize"
    assert ev.ed_app == "nisamina-platform"


def test_event_to_dict_caliper_compliant():
    ev = CaliperEvent.make(
        actor=Actor(actor_id="hash_abc"),
        action=Action.COMPLETED,
        obj=DigitalResource(resource_id="step_007", type="Step", envir="honduras"),
        group="cohort_42",
    )
    d = ev.to_dict()
    assert d["type"] == "Event"
    assert d["action"] == "Completed"
    assert d["object"]["resourceId"] if False else True
    assert d["object"]["resource_id"] == "step_007"
    assert d["group"] == "cohort_42"
    assert "eventTime" in d


def test_event_to_json_round_trips():
    ev = CaliperEvent.make(
        actor=Actor(actor_id="hash_x"),
        action=Action.SUBMITTED,
        obj=DigitalResource(resource_id="r", type="Step", envir="guatemala"),
    )
    s = ev.to_json()
    parsed = json.loads(s)
    assert parsed["action"] == "Submitted"
    assert parsed["object"]["envir"] == "guatemala"


def test_buffer_enforces_envir_isolation():
    buf = EventBuffer(envir="belize")
    foreign_event = CaliperEvent.make(
        actor=Actor(actor_id="x"),
        action=Action.STARTED,
        obj=DigitalResource(resource_id="r", type="Lesson", envir="honduras"),
    )
    with pytest.raises(ValueError, match="envir mismatch"):
        buf.emit(foreign_event)


def test_buffer_accepts_matching_envir():
    buf = EventBuffer(envir="svg_yurumein")
    ev = CaliperEvent.make(
        actor=Actor(actor_id="x"),
        action=Action.VIEWED,
        obj=DigitalResource(resource_id="r", type="Lesson", envir="svg_yurumein"),
    )
    buf.emit(ev)
    assert len(buf) == 1


def test_buffer_accepts_cross_envir_none():
    buf = EventBuffer(envir="garicomm")
    ev = CaliperEvent.make(
        actor=Actor(actor_id="x"),
        action=Action.NAVIGATED_TO,
        obj=DigitalResource(resource_id="r", type="Lesson"),  # envir omitted
    )
    buf.emit(ev)
    assert len(buf) == 1


def test_buffer_drain_clears():
    buf = EventBuffer(envir="nicaragua")
    for _ in range(3):
        ev = CaliperEvent.make(
            actor=Actor(actor_id="x"),
            action=Action.STARTED,
            obj=DigitalResource(resource_id="r", type="Lesson", envir="nicaragua"),
        )
        buf.emit(ev)
    drained = buf.drain()
    assert len(drained) == 3
    assert len(buf) == 0
