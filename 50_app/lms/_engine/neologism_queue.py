"""M-P3.LMS.STEM_NEOLOGISM_QUEUE — Garifuna technical-register coining queue.

Per F-067 + F-066 + F-031 Commission institutional channel + F-055 axis #1.

When STEM lesson generation needs a Garifuna term that doesn't yet exist in
foundry V0.2 (e.g., "fraction", "variable", "algorithm"), engineer does NOT
invent the term. The need is queued for Commission elder-mentor + lexicographer
review. Until a canonical term lands, the lesson renders the English/Spanish
term with a `[needs Garifuna term]` flag visible in the learner UI.

Flow:
    1. Lesson generator detects missing term → queue_request(...)
    2. Queue persists to per-envir JSONL log (auditable)
    3. Commission/lexicographer review batches via M-P3.LMS.ELDER_LOOP
    4. Approved coining → appended to foundry V0.3 with attribution
    5. Lesson re-renders with canonical term

This is the substrate for F-031 Commission elder collaboration + per-language
sovereign neologism governance.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional
import json


class RequestStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_MORE_INFO = "needs_more_info"


@dataclass(frozen=True)
class NeologismRequest:
    """A single technical-register coining request."""
    request_id: str
    source_term: str                 # e.g., "fraction" (English) or "fracción" (Spanish)
    source_language: str             # "en" | "es"
    semantic_field: str              # "math" | "science" | "computing" | "linguistics" | ...
    grade_band: str                  # e.g., "04_Upper_Elementary_Grades_3_to_5"
    context_sentence: str            # the sentence in which the term appears
    cohort_ref: Optional[str]        # optional cohort_id that surfaced the need
    envir: str                       # which envir is requesting (one of 7)
    requested_at: str                # ISO 8601 UTC
    status: RequestStatus = RequestStatus.PENDING
    proposed_terms: tuple[str, ...] = ()  # optional engineer-side seed suggestions for elder review
    notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        d["proposed_terms"] = list(self.proposed_terms)
        return d


@dataclass(frozen=True)
class NeologismApproval:
    """Commission/lexicographer approval response for a request."""
    request_id: str
    approved_term_garifuna: str
    register_tier: str               # "informal" | "formal" | "academic" | "cultural_ceremonial"
    approving_authority: str         # e.g., "Commission elder panel" | "lexicographer:Avila" | ...
    approved_at: str                 # ISO 8601 UTC
    foundry_v03_pending_append: bool = True
    notes: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class NeologismQueue:
    """File-backed neologism queue. One JSONL per envir for sovereignty.

    Per F-055 axis #6: each envir's queue lives at its own path; no cross-envir
    leak. Diaspora envir queue is separate; STEM queue is separate; etc.
    """

    def __init__(self, queue_path: Path):
        self.queue_path = Path(queue_path)
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)

    def queue_request(
        self,
        *,
        source_term: str,
        source_language: str,
        semantic_field: str,
        grade_band: str,
        context_sentence: str,
        envir: str,
        cohort_ref: Optional[str] = None,
        proposed_terms: tuple[str, ...] = (),
        notes: str = "",
    ) -> NeologismRequest:
        request_id = self._next_request_id()
        req = NeologismRequest(
            request_id=request_id,
            source_term=source_term,
            source_language=source_language,
            semantic_field=semantic_field,
            grade_band=grade_band,
            context_sentence=context_sentence,
            envir=envir,
            cohort_ref=cohort_ref,
            requested_at=_now_iso(),
            proposed_terms=proposed_terms,
            notes=notes,
        )
        self._append(req.to_dict())
        return req

    def _next_request_id(self) -> str:
        # Sequential per-envir IDs; auditable; no random
        existing = self.list_requests()
        n = len(existing) + 1
        return f"neologism_{n:05d}"

    def _append(self, record: dict) -> None:
        with self.queue_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def list_requests(self) -> list[dict]:
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

    def pending(self) -> list[dict]:
        return [r for r in self.list_requests() if r.get("status") == RequestStatus.PENDING.value]

    def record_approval(self, approval: NeologismApproval) -> None:
        """Append an approval record. Per [[feedback-no-hindsight-whitewashing]],
        the original PENDING record stays; this is an append-only correction_ref."""
        ap_dict = asdict(approval)
        ap_dict["record_type"] = "approval"
        self._append(ap_dict)
