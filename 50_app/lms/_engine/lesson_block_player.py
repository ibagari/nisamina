"""M-P3.LMS.LESSON_BLOCK_PLAYER — Compose LessonBlock plugins into a player.

Per D-067 + D-065 self-evolution gap #4 + D-066 LessonBlock substrate.

Bridges:
- LessonBlock plugin contract (blocks.py)
- BlockRegistry version-pinning
- lesson_player state machine (LessonState)
- Pathway / cognitive-load awareness from TutorState

A LessonBlockPlayer assembles a sequence of (block_id, block_version) into a
linear playable session, exposing render() per turn and score() upon response.
Community-contributed blocks plug in via the registry — no engineer code edit.

Per F-055 axis #1 sovereign-presentation: every block's render() emits a
cite_sources_payload; the player aggregates these into the session-level
audit chain. F-031 Commission elder review remains the gate for any block
new to the registry (via ReviewQueue + ElderReviewQueue).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

try:
    from .blocks import (
        BlockRegistry, LessonBlock, BlockRenderContext, RenderedBlock, Score,
    )
except ImportError:
    from blocks import (
        BlockRegistry, LessonBlock, BlockRenderContext, RenderedBlock, Score,
    )


class BlockPlayerState(str, Enum):
    PENDING = "pending"
    PLAYING = "playing"
    COMPLETED = "completed"


@dataclass(frozen=True)
class BlockReference:
    """A reference to a specific block + version in a lesson sequence."""
    block_id: str
    block_version: str
    init_kwargs: dict = field(default_factory=dict)


@dataclass
class BlockPlayerSession:
    """Per-learner per-lesson state for the LessonBlockPlayer."""
    session_id: str
    learner_id: str
    envir: str
    pathway: str
    block_sequence: tuple[BlockReference, ...]
    state: BlockPlayerState = BlockPlayerState.PENDING
    current_index: int = 0
    score_total: float = 0.0
    correct_count: int = 0
    incorrect_count: int = 0
    cite_sources_audit: list[dict] = field(default_factory=list)


class LessonBlockPlayer:
    """Plays a sequence of LessonBlock plugins as a linear lesson.

    Composition: caller provides a BlockRegistry pre-populated with the blocks
    needed by the lesson; player resolves each BlockReference at runtime,
    instantiates the block with init_kwargs, calls render() / score() in turn.
    """

    def __init__(self, registry: BlockRegistry):
        self.registry = registry

    def start(self, session: BlockPlayerSession) -> RenderedBlock:
        if session.state != BlockPlayerState.PENDING:
            raise ValueError(f"session not in PENDING state: {session.state}")
        if not session.block_sequence:
            raise ValueError("session has empty block_sequence")
        session.state = BlockPlayerState.PLAYING
        return self._render_current(session)

    def current_block(self, session: BlockPlayerSession) -> Optional[LessonBlock]:
        if session.current_index >= len(session.block_sequence):
            return None
        ref = session.block_sequence[session.current_index]
        block_cls = self.registry.get(ref.block_id, ref.block_version)
        return block_cls(**ref.init_kwargs)

    def submit(
        self,
        session: BlockPlayerSession,
        response: str,
        primary_modality: str = "text",
        bandwidth_mode: str = "full",
        ui_lang: str = "en",
    ) -> tuple[Score, Optional[RenderedBlock]]:
        """Submit a learner response on the current block; return Score + next render.

        Returns (Score, next_rendered_block_or_None). If next is None, session is COMPLETED.
        """
        if session.state != BlockPlayerState.PLAYING:
            raise ValueError(f"session not PLAYING: {session.state}")

        block = self.current_block(session)
        if block is None:
            raise RuntimeError("no current block to submit against")

        ctx = self._make_ctx(session, primary_modality, bandwidth_mode, ui_lang)
        score = block.score(response, ctx=ctx)

        # Update aggregate state
        session.score_total += score.raw_score
        if score.correct:
            session.correct_count += 1
        else:
            session.incorrect_count += 1

        # Capture provenance + cite_sources payload for audit
        prov = block.provenance()
        session.cite_sources_audit.append({
            "block_id": block.block_id,
            "block_version": block.block_version,
            "block_kind": block.block_kind,
            "attribution_refs": list(prov.attribution_refs),
            "consent_ref": prov.consent_ref,
            "license": prov.license,
            "source_citations": list(prov.source_citations),
            "score_raw": score.raw_score,
            "correct": score.correct,
        })

        # Advance
        session.current_index += 1
        if session.current_index >= len(session.block_sequence):
            session.state = BlockPlayerState.COMPLETED
            return score, None
        return score, self._render_current(session, primary_modality, bandwidth_mode, ui_lang)

    def _render_current(
        self,
        session: BlockPlayerSession,
        primary_modality: str = "text",
        bandwidth_mode: str = "full",
        ui_lang: str = "en",
    ) -> RenderedBlock:
        block = self.current_block(session)
        if block is None:
            raise RuntimeError("no current block to render")
        ctx = self._make_ctx(session, primary_modality, bandwidth_mode, ui_lang)
        return block.render(ctx)

    def _make_ctx(
        self,
        session: BlockPlayerSession,
        primary_modality: str,
        bandwidth_mode: str,
        ui_lang: str,
    ) -> BlockRenderContext:
        return BlockRenderContext(
            learner_id=session.learner_id,
            envir=session.envir,
            pathway=session.pathway,
            primary_modality=primary_modality,
            bandwidth_mode=bandwidth_mode,
            extra={"ui_lang": ui_lang},
        )

    def aggregate_score(self, session: BlockPlayerSession) -> float:
        """Total accumulated raw_score (max = len(block_sequence))."""
        return session.score_total

    def accuracy(self, session: BlockPlayerSession) -> float:
        total = session.correct_count + session.incorrect_count
        return session.correct_count / total if total else 0.0
