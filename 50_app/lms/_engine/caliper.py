"""M-P3.LMS.CALIPER — IMS Caliper Analytics 1.2 event emission.

Per F-056 + F-059 D-MAX-11. Emits structured events for cohort-level analytics
without storing per-learner PII beyond actor_id (which is an opaque hash).

Compliant with IMS Caliper 1.2 envelope:
- Event has: id, type, actor, action, object, eventTime, edApp, group.
- Per-MOE sovereignty (F-055 axis #6) — each envir's events stay in envir.

Scaffolded buffer enqueues events; flush is the responsibility of the envir's
data-residency-conformant ingest pipeline (M-P3.LMS.DASHBOARD per D-MAX-11).
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional
import json
import uuid


class Action(str, Enum):
    # Caliper 1.2 Action verbs (subset used at scaffold; full set in spec)
    STARTED = "Started"
    PAUSED = "Paused"
    RESUMED = "Resumed"
    COMPLETED = "Completed"
    SUBMITTED = "Submitted"
    GRADED = "Graded"
    VIEWED = "Viewed"
    NAVIGATED_TO = "NavigatedTo"
    REVIEWED = "Reviewed"


@dataclass(frozen=True)
class Actor:
    """Anonymous learner reference; actor_id is an opaque hash, not PII."""
    actor_id: str
    type: str = "Person"


@dataclass(frozen=True)
class DigitalResource:
    """Caliper DigitalResource — lesson, unit, step, card, assessment, etc."""
    resource_id: str
    type: str
    name: Optional[str] = None
    envir: Optional[str] = None  # belize | honduras | ... | svg_yurumein | garicomm


@dataclass(frozen=True)
class CaliperEvent:
    """Caliper 1.2 envelope (subset)."""
    id: str
    type: str
    actor: Actor
    action: Action
    object: DigitalResource
    event_time: str  # ISO8601
    ed_app: str = "nisamina-platform"
    group: Optional[str] = None  # cohort_id

    @classmethod
    def make(
        cls,
        actor: Actor,
        action: Action,
        obj: DigitalResource,
        event_type: str = "Event",
        group: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> "CaliperEvent":
        now = now or datetime.utcnow()
        return cls(
            id=f"urn:uuid:{uuid.uuid4()}",
            type=event_type,
            actor=actor,
            action=action,
            object=obj,
            event_time=now.isoformat() + "Z",
            group=group,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "actor": asdict(self.actor),
            "action": self.action.value,
            "object": {k: v for k, v in asdict(self.object).items() if v is not None},
            "eventTime": self.event_time,
            "edApp": self.ed_app,
            **({"group": self.group} if self.group else {}),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class EventBuffer:
    """In-memory buffer; flush is envir-conformant per F-055 axis #6 data sovereignty."""

    def __init__(self, envir: str):
        self.envir = envir
        self._events: list[CaliperEvent] = []

    def emit(self, event: CaliperEvent) -> None:
        # Enforce envir isolation: object's envir must match buffer's envir (or be None for cross-envir)
        if event.object.envir is not None and event.object.envir != self.envir:
            raise ValueError(
                f"envir mismatch: buffer={self.envir}, event.object.envir={event.object.envir}"
            )
        self._events.append(event)

    def drain(self) -> list[CaliperEvent]:
        out = list(self._events)
        self._events.clear()
        return out

    def __len__(self) -> int:
        return len(self._events)
