"""M-P3.LMS.REVIEW_QUEUE — Universal review queue (generic over T).

Per D-065 self-evolution gap #1 + research-brief §2 (Kaitiakitanga / FirstVoices /
Te Hiku Media community-CMS pattern).

Extracts the queue/approval mechanics from `neologism_queue.py` into a generic
`ReviewQueue[T]` reusable for:
  - neologisms (existing — preserved as specialization)
  - chart proposals (cultural-context anchor additions)
  - dialect-variant proposals (per-envir lexicon variants)
  - sentence-correction proposals (learner-submitted)
  - pronunciation recordings (Forvo-style; community-recorded)
  - mastery-threshold proposals (population calibrator → Commission sign-off)

Append-only JSONL per F-046 + [[feedback-no-hindsight-whitewashing]]:
- Original PENDING record preserved alongside approval/rejection.
- Approval records reference the request via `request_ref`.
- Each authority record names the approving authority per F-031 + Kaitiakitanga.

Per F-055 axis #6: queues are per-envir; cross-envir review requires explicit
Commission-cross-envir authority.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generic, Optional, TypeVar
import json


T = TypeVar("T")


class ReviewStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_MORE_INFO = "needs_more_info"
    SUPERSEDED = "superseded"            # for replacement proposals


@dataclass(frozen=True)
class ReviewProposal(Generic[T]):
    """A proposed change of type T."""
    proposal_id: str
    proposal_type: str                    # "neologism" | "chart" | "dialect_variant" | ...
    envir: str
    submitter: str                        # who proposed it (learner_id / curator / elder)
    payload: T                            # the proposed change (T-specific)
    submitted_at: str                     # ISO 8601 UTC
    status: ReviewStatus = ReviewStatus.PENDING
    notes: str = ""


@dataclass(frozen=True)
class ReviewDecision:
    """An authority decision on a proposal."""
    proposal_ref: str                     # proposal_id of the request
    decision: ReviewStatus                # APPROVED | REJECTED | NEEDS_MORE_INFO
    approving_authority: str              # "Commission elder panel" | "lexicographer:Avila" | etc.
    decided_at: str                       # ISO 8601 UTC
    rationale: str = ""
    derived_artifact_ref: Optional[str] = None  # if APPROVED + something downstream was created


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class ReviewQueue(Generic[T]):
    """Append-only JSONL queue per-envir; supports any T payload.

    Serializes T via the caller-provided `payload_serializer` (defaults to asdict
    for dataclasses; pass a custom callable for other shapes).
    """

    def __init__(
        self,
        queue_path: Path,
        proposal_type: str,
        envir: str,
        payload_serializer: Optional[Callable[[T], dict]] = None,
        payload_deserializer: Optional[Callable[[dict], T]] = None,
    ):
        self.queue_path = Path(queue_path)
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.proposal_type = proposal_type
        self.envir = envir
        self._serialize = payload_serializer or (lambda x: asdict(x) if hasattr(x, "__dataclass_fields__") else dict(x))
        self._deserialize = payload_deserializer  # may be None; caller does conversion if needed

    # === Submission ========================================================

    def submit(
        self,
        *,
        submitter: str,
        payload: T,
        notes: str = "",
    ) -> ReviewProposal[T]:
        proposal_id = self._next_proposal_id()
        proposal = ReviewProposal(
            proposal_id=proposal_id,
            proposal_type=self.proposal_type,
            envir=self.envir,
            submitter=submitter,
            payload=payload,
            submitted_at=_now_iso(),
            notes=notes,
        )
        self._append({
            "record_type": "proposal",
            "proposal_id": proposal.proposal_id,
            "proposal_type": proposal.proposal_type,
            "envir": proposal.envir,
            "submitter": proposal.submitter,
            "payload": self._serialize(payload),
            "submitted_at": proposal.submitted_at,
            "status": proposal.status.value,
            "notes": proposal.notes,
        })
        return proposal

    # === Decision ==========================================================

    def record_decision(self, decision: ReviewDecision) -> None:
        """Append a decision record; the original proposal stays untouched
        (no hindsight whitewashing)."""
        self._append({
            "record_type": "decision",
            "proposal_ref": decision.proposal_ref,
            "decision": decision.decision.value,
            "approving_authority": decision.approving_authority,
            "decided_at": decision.decided_at,
            "rationale": decision.rationale,
            "derived_artifact_ref": decision.derived_artifact_ref,
        })

    def approve(
        self,
        *,
        proposal_ref: str,
        approving_authority: str,
        rationale: str = "",
        derived_artifact_ref: Optional[str] = None,
    ) -> ReviewDecision:
        d = ReviewDecision(
            proposal_ref=proposal_ref,
            decision=ReviewStatus.APPROVED,
            approving_authority=approving_authority,
            decided_at=_now_iso(),
            rationale=rationale,
            derived_artifact_ref=derived_artifact_ref,
        )
        self.record_decision(d)
        return d

    def reject(
        self,
        *,
        proposal_ref: str,
        approving_authority: str,
        rationale: str,
    ) -> ReviewDecision:
        d = ReviewDecision(
            proposal_ref=proposal_ref,
            decision=ReviewStatus.REJECTED,
            approving_authority=approving_authority,
            decided_at=_now_iso(),
            rationale=rationale,
        )
        self.record_decision(d)
        return d

    # === Queries ===========================================================

    def list_records(self) -> list[dict]:
        if not self.queue_path.exists():
            return []
        out: list[dict] = []
        for line in self.queue_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def pending_proposals(self) -> list[dict]:
        # A proposal is "pending" if no APPROVED/REJECTED decision references it.
        records = self.list_records()
        decided: set[str] = set()
        for r in records:
            if r.get("record_type") == "decision":
                if r.get("decision") in (ReviewStatus.APPROVED.value, ReviewStatus.REJECTED.value):
                    decided.add(r.get("proposal_ref"))
        return [
            r for r in records
            if r.get("record_type") == "proposal" and r.get("proposal_id") not in decided
        ]

    def approved_proposals(self) -> list[dict]:
        records = self.list_records()
        approved_refs: set[str] = {
            r.get("proposal_ref")
            for r in records
            if r.get("record_type") == "decision"
            and r.get("decision") == ReviewStatus.APPROVED.value
        }
        return [r for r in records if r.get("record_type") == "proposal" and r.get("proposal_id") in approved_refs]

    # === Private ===========================================================

    def _next_proposal_id(self) -> str:
        # Sequential per-queue; auditable; deterministic
        existing = [r for r in self.list_records() if r.get("record_type") == "proposal"]
        n = len(existing) + 1
        return f"{self.proposal_type}_{n:05d}"

    def _append(self, record: dict) -> None:
        with self.queue_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
