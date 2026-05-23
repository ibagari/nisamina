"""M-P3.LMS.ELDER_LOOP — F-056 layer 6 Commission elder-review queue.

Per F-056 layer 6 + F-031 Commission institutional channel + Te Hiku Media
Kaitiakitanga License + KĀ'EO "humans ARE the loop, not a checkpoint" + the
F-076-AMENDMENT-2 ELDER_GATED tier discipline.

Builds on the generic `ReviewQueue[T]` (D-065) to handle Commission community-
elder review work specifically: dance/music content vetting, sacred-knowledge
routing, ICH ceremony naming, dialect-variant approval, neologism coining at
the elder-mentor level (vs lexicographer level).

Per Labayayahoun Ibagari + F-055 axis #1: matter belongs to the people;
presentation is mediated by Nisamina ONLY when elder authority approves.
Sacred/ELDER_GATED content NEVER auto-publishes; it routes through this queue.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    from .review_queue import ReviewQueue, ReviewStatus, ReviewDecision
except ImportError:
    from review_queue import ReviewQueue, ReviewStatus, ReviewDecision


class ElderReviewItemKind(str, Enum):
    NEOLOGISM = "neologism"                     # technical-register Garifuna coining
    SACRED_CONTENT = "sacred_content"           # dance/ceremony/ritual content
    DIALECT_VARIANT = "dialect_variant"         # per-envir lexicon variant
    CULTURAL_ANCHOR = "cultural_anchor"         # chart/lesson cultural anchor proposal
    CEREMONY_NAMING = "ceremony_naming"         # public-facing ceremony name + framing
    PRONUNCIATION = "pronunciation"             # elder-recorded reference pronunciation
    HISTORICAL_NARRATIVE = "historical_narrative"  # historical claim or narrative


@dataclass(frozen=True)
class ElderReviewItem:
    """A single item requiring Commission elder review.

    Per F-031: routes through Commission focal-point (Avila + elder panel).
    Per F-055 axis #6: per-envir; cross-envir items require explicit cross-
    envir authority (e.g., GariComm canonical reconciliation).
    """
    item_kind: ElderReviewItemKind
    title: str
    context_summary: str                        # what the proposal is about
    source_quote: Optional[str]                 # the actual content (if any)
    grade_band: Optional[str]                   # e.g., "03_Early_Elementary_Grades_1_to_2"
    cultural_protocol_flag: bool                # True if sacred-restricted scope
    submitter_role: str                         # "engineer" | "learner" | "teacher" | "curator"
    references: tuple[str, ...] = ()            # citations or related foundry refs


class ElderReviewQueue:
    """Specialized queue for Commission elder review work.

    Wraps `ReviewQueue[ElderReviewItem]` with:
    - Sacred-content immediate-flag (sacred items NEVER auto-resolve)
    - Multi-elder concurrence threshold (3-elder default for SACRED items)
    - F-031 Commission focal-point routing
    """

    SACRED_QUORUM_DEFAULT: int = 3              # 3-elder concurrence for SACRED items
    NEOLOGISM_QUORUM_DEFAULT: int = 2           # 2-authority concurrence (elder + lexicographer)

    def __init__(self, queue_path: Path, envir: str):
        self.queue = ReviewQueue[ElderReviewItem](
            queue_path=queue_path,
            proposal_type="elder_review",
            envir=envir,
            payload_serializer=lambda item: {
                "item_kind": item.item_kind.value,
                "title": item.title,
                "context_summary": item.context_summary,
                "source_quote": item.source_quote,
                "grade_band": item.grade_band,
                "cultural_protocol_flag": item.cultural_protocol_flag,
                "submitter_role": item.submitter_role,
                "references": list(item.references),
            },
        )
        self.envir = envir

    def submit_item(
        self,
        *,
        item: ElderReviewItem,
        submitter: str,
        notes: str = "",
    ):
        """Submit an item for elder review. Sacred items get auto-tagged with
        the appropriate quorum requirement."""
        if item.cultural_protocol_flag and item.item_kind not in (
            ElderReviewItemKind.SACRED_CONTENT,
            ElderReviewItemKind.CEREMONY_NAMING,
        ):
            # Sacred-flagged item MUST be SACRED_CONTENT or CEREMONY_NAMING kind
            raise ValueError(
                f"item_kind={item.item_kind.value} marked cultural_protocol_flag=True "
                f"but only SACRED_CONTENT/CEREMONY_NAMING tier accepts that flag"
            )
        return self.queue.submit(submitter=submitter, payload=item, notes=notes)

    def required_quorum(self, item: ElderReviewItem) -> int:
        """Quorum policy by item kind."""
        if item.cultural_protocol_flag or item.item_kind in (
            ElderReviewItemKind.SACRED_CONTENT,
            ElderReviewItemKind.CEREMONY_NAMING,
        ):
            return self.SACRED_QUORUM_DEFAULT
        if item.item_kind == ElderReviewItemKind.NEOLOGISM:
            return self.NEOLOGISM_QUORUM_DEFAULT
        return 1                                  # default: single elder concurrence

    def approvals_for(self, proposal_id: str) -> list[dict]:
        """All approval decisions referencing this proposal."""
        return [
            r
            for r in self.queue.list_records()
            if r.get("record_type") == "decision"
            and r.get("proposal_ref") == proposal_id
            and r.get("decision") == ReviewStatus.APPROVED.value
        ]

    def has_reached_quorum(self, proposal: dict, required: int) -> bool:
        """Check if quorum-many distinct authorities have approved."""
        approvals = self.approvals_for(proposal.get("proposal_id"))
        distinct_authorities = {a.get("approving_authority") for a in approvals}
        return len(distinct_authorities) >= required

    def add_concurrence(
        self,
        *,
        proposal_ref: str,
        approving_authority: str,
        rationale: str = "",
        derived_artifact_ref: Optional[str] = None,
    ) -> ReviewDecision:
        """Add one approval. Caller checks has_reached_quorum() separately."""
        return self.queue.approve(
            proposal_ref=proposal_ref,
            approving_authority=approving_authority,
            rationale=rationale,
            derived_artifact_ref=derived_artifact_ref,
        )

    def reject(
        self,
        *,
        proposal_ref: str,
        approving_authority: str,
        rationale: str,
    ) -> ReviewDecision:
        """Single-elder rejection blocks the proposal (rejection is not gated
        by quorum — any one elder's veto is honored per Kaitiakitanga + F-031
        Commission discretion)."""
        return self.queue.reject(
            proposal_ref=proposal_ref,
            approving_authority=approving_authority,
            rationale=rationale,
        )

    def pending(self) -> list[dict]:
        return self.queue.pending_proposals()

    def approved_with_quorum(self) -> list[dict]:
        """Approved proposals that have reached their required quorum."""
        out: list[dict] = []
        for r in self.queue.list_records():
            if r.get("record_type") != "proposal":
                continue
            # Reconstruct item-kind from payload
            payload = r.get("payload", {})
            kind_value = payload.get("item_kind", "")
            try:
                kind = ElderReviewItemKind(kind_value)
            except ValueError:
                continue
            # Build a minimal item to compute required quorum
            item = ElderReviewItem(
                item_kind=kind,
                title=payload.get("title", ""),
                context_summary=payload.get("context_summary", ""),
                source_quote=payload.get("source_quote"),
                grade_band=payload.get("grade_band"),
                cultural_protocol_flag=payload.get("cultural_protocol_flag", False),
                submitter_role=payload.get("submitter_role", ""),
                references=tuple(payload.get("references", ())),
            )
            required = self.required_quorum(item)
            if self.has_reached_quorum(r, required):
                out.append(r)
        return out
