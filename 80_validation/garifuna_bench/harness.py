"""GarifunaBench top-level harness.

Loads held-out items, dispatches to task-specific scorers, refuses to
emit authoritative scores on items still carrying the
`engineer-scaffold-only-NOT-AUTHORITATIVE` marker (plan v1 §6 rule 2).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


ENGINEER_SCAFFOLD_MARKER: str = "engineer-scaffold-only-NOT-AUTHORITATIVE"


class NotAuthoritativeError(Exception):
    """Raised when a caller asks for an authoritative bench score on
    fixture items that haven't been graded by director / commission /
    community."""


@dataclass
class BenchItem:
    id: str
    task: str
    input: str
    expected: str
    source_ids: list[str]
    headword: Optional[str] = None
    tier: Optional[int] = None
    graded_by: str = ENGINEER_SCAFFOLD_MARKER
    notes: str = ""

    @property
    def is_authoritative(self) -> bool:
        gb = (self.graded_by or "").strip()
        return bool(gb) and gb != ENGINEER_SCAFFOLD_MARKER


@dataclass
class TaskReport:
    task: str
    n_items: int
    n_authoritative: int
    sanity_only: bool
    per_item: list[dict] = field(default_factory=list)
    aggregate_score: Optional[float] = None
    notes: str = ""


def load_fixture(path: str | Path) -> list[BenchItem]:
    """Load a JSONL fixture into BenchItem objects."""
    items: list[BenchItem] = []
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue
            raw = json.loads(line)
            items.append(BenchItem(
                id=raw["id"],
                task=raw["task"],
                input=raw["input"],
                expected=raw["expected"],
                source_ids=list(raw.get("source_ids", [])),
                headword=raw.get("headword"),
                tier=raw.get("tier"),
                graded_by=raw.get("graded_by", ENGINEER_SCAFFOLD_MARKER),
                notes=raw.get("notes", ""),
            ))
    return items


class BenchHarness:
    """Top-level orchestrator. Holds a fixture + a chatbot callable.

    `chatbot_callable` signature: (item: BenchItem) -> str.
    At M-P3.A, this is wired to the real Gemma 4 E4B brain over MCP.
    """

    def __init__(
        self,
        items: list[BenchItem],
        chatbot_callable: Callable[[BenchItem], str],
    ) -> None:
        self.items = items
        self.chatbot = chatbot_callable

    @property
    def is_authoritative(self) -> bool:
        return all(i.is_authoritative for i in self.items) and bool(self.items)

    def filter_by_task(self, task: str) -> list[BenchItem]:
        return [i for i in self.items if i.task == task]

    def _score_item(self, item: BenchItem, response: str) -> dict:
        from .tasks import (
            mt_en_to_cab,
            mt_cab_to_en,
            vocab_recall,
            conversation_quality,
            pronunciation_grading,
        )

        scorers = {
            "mt_en_to_cab": mt_en_to_cab.score,
            "mt_cab_to_en": mt_cab_to_en.score,
            "vocab_recall": vocab_recall.score,
            "conversation_quality": conversation_quality.score,
            "pronunciation_grading": pronunciation_grading.score,
        }
        scorer = scorers.get(item.task)
        if scorer is None:
            return {"id": item.id, "error": f"unknown task: {item.task}"}
        try:
            score = scorer(item.input, item.expected, response)
        except NotImplementedError as e:
            return {"id": item.id, "skipped": str(e)}
        return {
            "id": item.id,
            "task": item.task,
            "score": score,
            "graded_by": item.graded_by,
            "response": response,
        }

    def sanity_check(self, task: str) -> TaskReport:
        """Run task on all items (authoritative or not), return report
        marked `sanity_only`. Safe to call on engineer-scaffold-only
        fixtures."""
        relevant = self.filter_by_task(task)
        per_item = []
        for item in relevant:
            response = self.chatbot(item)
            per_item.append(self._score_item(item, response))

        n_auth = sum(1 for i in relevant if i.is_authoritative)
        return TaskReport(
            task=task,
            n_items=len(relevant),
            n_authoritative=n_auth,
            sanity_only=True,
            per_item=per_item,
            aggregate_score=None,  # no aggregate in sanity mode
            notes=(
                "SANITY CHECK ONLY — items may include "
                f"{ENGINEER_SCAFFOLD_MARKER} marked entries; not a "
                "publishable bench result."
            ),
        )

    def run_task(self, task: str) -> TaskReport:
        """Authoritative scoring — requires every relevant item to
        be graded. Raises NotAuthoritativeError otherwise."""
        relevant = self.filter_by_task(task)
        if not relevant:
            raise ValueError(f"no items match task '{task}'")

        un_authoritative = [i.id for i in relevant if not i.is_authoritative]
        if un_authoritative:
            raise NotAuthoritativeError(
                f"task '{task}' has {len(un_authoritative)} items still "
                f"marked {ENGINEER_SCAFFOLD_MARKER!r}: {un_authoritative[:5]}"
                f"{'...' if len(un_authoritative) > 5 else ''}. "
                f"Per plan v1 §6 rule 2 (never self-graded), all items "
                f"must carry a graded_by string from director / commission "
                f"/ community before authoritative scoring."
            )

        per_item = []
        scores: list[float] = []
        for item in relevant:
            response = self.chatbot(item)
            row = self._score_item(item, response)
            per_item.append(row)
            if isinstance(row.get("score"), (int, float)):
                scores.append(float(row["score"]))

        aggregate = sum(scores) / len(scores) if scores else None
        return TaskReport(
            task=task,
            n_items=len(relevant),
            n_authoritative=len(relevant),
            sanity_only=False,
            per_item=per_item,
            aggregate_score=aggregate,
            notes="",
        )
