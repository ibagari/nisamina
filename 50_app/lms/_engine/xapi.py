"""M-P3.LMS.XAPI — xAPI statement emission alongside Caliper events.

Per D-065 SOA gap #2 + research-brief §1 (1EdTech ADL co-canonical convergence
2025; Open edX Aspects ADR 0002 standardized on xAPI for default data transfer).

Mirrors every CaliperEvent to a structured xAPI statement (Experience API per
ADL specification — Actor-Verb-Object-Result form; cmi5 profile compatible).
This unlocks federation to MOE-side Learning Record Stores that expect xAPI.

Per F-055 axis #6: statements include the envir tag; downstream LRS endpoints
route to per-envir storage. Per Labayayahoun Ibagari: sacred-knowledge routing
events are surfaced but underlying prompt content is not persisted (privacy).

Reference: https://github.com/adlnet/xAPI-Spec
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

try:
    from .caliper import CaliperEvent, Action
except ImportError:
    from caliper import CaliperEvent, Action


# Canonical xAPI verbs per Tin Can Registry + ADL Vocabulary
_CALIPER_TO_XAPI_VERB: dict[str, dict[str, str]] = {
    "Started": {
        "id": "http://adlnet.gov/expapi/verbs/initialized",
        "display": "initialized",
    },
    "Paused": {
        "id": "https://w3id.org/xapi/adl/verbs/suspended",
        "display": "suspended",
    },
    "Resumed": {
        "id": "https://w3id.org/xapi/adl/verbs/resumed",
        "display": "resumed",
    },
    "Completed": {
        "id": "http://adlnet.gov/expapi/verbs/completed",
        "display": "completed",
    },
    "Submitted": {
        "id": "https://w3id.org/xapi/dod-isd/verbs/submitted",
        "display": "submitted",
    },
    "Graded": {
        "id": "http://adlnet.gov/expapi/verbs/scored",
        "display": "scored",
    },
    "Viewed": {
        "id": "http://id.tincanapi.com/verb/viewed",
        "display": "viewed",
    },
    "NavigatedTo": {
        "id": "http://adlnet.gov/expapi/verbs/launched",
        "display": "launched",
    },
    "Reviewed": {
        "id": "http://id.tincanapi.com/verb/reviewed",
        "display": "reviewed",
    },
}


@dataclass(frozen=True)
class XAPIStatement:
    """xAPI Actor-Verb-Object statement (subset; cmi5-compatible)."""
    id: str
    actor: dict
    verb: dict
    object: dict
    timestamp: str
    context: dict = field(default_factory=dict)
    result: Optional[dict] = None

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "actor": self.actor,
            "verb": self.verb,
            "object": self.object,
            "timestamp": self.timestamp,
            "context": self.context,
        }
        if self.result is not None:
            d["result"] = self.result
        return d


def caliper_to_xapi(event: CaliperEvent) -> XAPIStatement:
    """Convert a CaliperEvent to an equivalent xAPI statement.

    Per ADL/1EdTech 2025 convergence pattern: dual-emit Caliper for cohort
    dashboards + xAPI for portable learner-owned Learning Record Stores.
    """
    verb = _CALIPER_TO_XAPI_VERB.get(event.action.value)
    if verb is None:
        # Fallback to a generic interacted verb
        verb = {
            "id": "http://adlnet.gov/expapi/verbs/interacted",
            "display": "interacted",
        }

    actor_obj = {
        "objectType": event.actor.type,
        "account": {
            "homePage": f"https://nisamina.ibagari.foundation/envir/{event.object.envir or 'default'}",
            "name": event.actor.actor_id,
        },
    }
    object_obj = {
        "objectType": "Activity",
        "id": f"https://nisamina.ibagari.foundation/{event.object.type.lower()}/{event.object.resource_id}",
        "definition": {
            "type": f"http://nisamina.ibagari.foundation/activity-types/{event.object.type.lower()}",
            "name": {"en-US": event.object.name or event.object.resource_id},
        },
    }
    if event.object.envir:
        object_obj["definition"]["extensions"] = {
            "http://nisamina.ibagari.foundation/extensions/envir": event.object.envir,
        }
    context_obj: dict = {
        "platform": event.ed_app,
    }
    if event.group:
        context_obj["registration"] = event.group  # cmi5 cohort registration tag

    return XAPIStatement(
        id=str(uuid.uuid4()),
        actor=actor_obj,
        verb={"id": verb["id"], "display": {"en-US": verb["display"]}},
        object=object_obj,
        timestamp=event.event_time,
        context=context_obj,
    )


class XAPIEmitter:
    """In-memory buffer of xAPI statements; flush is per-envir LRS responsibility.

    Mirrors EventBuffer's envir-isolation enforcement.
    """

    def __init__(self, envir: str):
        self.envir = envir
        self._statements: list[XAPIStatement] = []

    def emit_from_caliper(self, event: CaliperEvent) -> XAPIStatement:
        """Convert + buffer a Caliper event as an xAPI statement."""
        if event.object.envir is not None and event.object.envir != self.envir:
            raise ValueError(
                f"envir mismatch: emitter={self.envir}, event.object.envir={event.object.envir}"
            )
        statement = caliper_to_xapi(event)
        self._statements.append(statement)
        return statement

    def drain(self) -> list[XAPIStatement]:
        out = list(self._statements)
        self._statements.clear()
        return out

    def __len__(self) -> int:
        return len(self._statements)
