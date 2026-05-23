"""M-P3.LMS.BLOCKS — LessonBlock ABC + plugin contract.

Per D-065 self-evolution gap #4 + research-brief §2 (Open edX XBlock pattern;
Python class with a small handler protocol; version-pinnable; self-contained).

A LessonBlock is the smallest deployable learning unit a community contributor
can ship without engineer code edits. Examples:
- a VocabFlashcardBlock implementing GameKind.VOCAB_MATCH
- a CulturalAnchorBlock surfacing a chart item + audio
- a DialecticTutorBlock wiring SocraticTutor + a specific concept

Per Open edX XBlock convention (which the 2025 self-evolution research found
SOA): each block declares an id + version + handlers; loader instantiates
versioned blocks dynamically; lesson_player composes them into Lessons.

Per F-055 axis #1 sovereign-presentation: every block has a `provenance()`
method returning attribution + consent refs. cite_sources MCP surface consumes.
Per F-031 + Kaitiakitanga: community-contributed blocks route via ReviewQueue
before registration; once registered, runtime registry treats them as
first-class.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class BlockRenderContext:
    """Inputs passed to a block's render() method at runtime."""
    learner_id: str
    envir: str
    pathway: str                                # "heritage" | "novice" | "l1_maintainer"
    primary_modality: str                       # "audio" | "visual" | "text" | "interactive"
    grade_band: Optional[str] = None
    cohort_ref: Optional[str] = None
    bandwidth_mode: str = "full"                # "full" | "audio_only" | "text_only" | "print"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderedBlock:
    """What a block emits for the UI layer to consume."""
    block_id: str
    block_version: str
    rendered_prompt: str
    rendered_audio_ref: Optional[str] = None
    rendered_visual_ref: Optional[str] = None
    expected_response_kind: str = "free_text"   # "free_text" | "multiple_choice" | "audio"
    options: tuple[str, ...] = ()               # for multiple_choice
    cite_sources_payload: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Score:
    """Result of a block scoring a learner response."""
    correct: bool
    raw_score: float                            # [0.0, 1.0]
    partial_credit: float = 0.0
    feedback_text: str = ""
    feedback_modality: str = "text"
    affect_signal_correct_streak_delta: int = 0  # for affect_gentle integration


@dataclass(frozen=True)
class ProvenanceRef:
    """Attribution + consent + source citations per F-055 axis #1."""
    attribution_refs: tuple[str, ...]
    consent_ref: Optional[str]
    source_citations: tuple[str, ...]
    license: str = "CC-BY-NC-SA-4.0"
    contributor: Optional[str] = None


# === The LessonBlock ABC ===================================================


class LessonBlock(ABC):
    """Abstract base class for community-contributable learning units.

    Per Open edX XBlock convention. Instances are immutable runtime objects;
    state lives in the learner's session, not on the block itself.

    Required class attributes:
    - block_id: unique identifier (e.g., "vocab.greetings.buguya")
    - block_version: semver string (e.g., "0.1.0")
    - block_kind: high-level category (e.g., "vocab_flashcard", "chart_view",
                  "socratic_turn", "multimodal_view", "cultural_anchor")

    Required methods:
    - render(ctx) -> RenderedBlock: produces UI-ready output
    - score(response) -> Score: scores a learner response
    - provenance() -> ProvenanceRef: attribution chain
    """

    block_id: str = ""
    block_version: str = "0.0.0"
    block_kind: str = ""

    @abstractmethod
    def render(self, ctx: BlockRenderContext) -> RenderedBlock:
        """Produce a renderable block for the given context."""

    @abstractmethod
    def score(self, response: str, ctx: Optional[BlockRenderContext] = None) -> Score:
        """Score a learner response. ctx may inform per-pathway grading."""

    @abstractmethod
    def provenance(self) -> ProvenanceRef:
        """Return attribution chain. Required for cite_sources MCP surface."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Enforce that concrete subclasses set block_id + block_version + block_kind.
        # __abstractmethods__ may not exist yet when __init_subclass__ fires;
        # use getattr with default frozenset() to detect concrete status safely.
        abstract = getattr(cls, "__abstractmethods__", frozenset())
        if not abstract:  # concrete only
            if not cls.block_id:
                raise ValueError(f"{cls.__name__} must set block_id class attribute")
            if not cls.block_version or cls.block_version == "0.0.0":
                raise ValueError(f"{cls.__name__} must set block_version class attribute")
            if not cls.block_kind:
                raise ValueError(f"{cls.__name__} must set block_kind class attribute")


# === Block registry ========================================================


class BlockRegistry:
    """Versioned registry of available LessonBlock classes.

    Community contributors register their blocks via `register()`. Loader
    instantiates by (block_id, block_version). Multiple versions can coexist;
    lesson_player pins versions per cohort to keep deployments reproducible.
    """

    def __init__(self):
        # {(block_id, block_version): LessonBlock-subclass}
        self._registry: dict[tuple[str, str], type[LessonBlock]] = {}

    def register(self, block_cls: type[LessonBlock]) -> None:
        if not issubclass(block_cls, LessonBlock):
            raise TypeError(f"{block_cls.__name__} must subclass LessonBlock")
        key = (block_cls.block_id, block_cls.block_version)
        if key in self._registry:
            raise ValueError(
                f"block already registered: {block_cls.block_id} v{block_cls.block_version}"
            )
        self._registry[key] = block_cls

    def get(self, block_id: str, block_version: str) -> type[LessonBlock]:
        key = (block_id, block_version)
        if key not in self._registry:
            raise KeyError(f"unknown block: {block_id} v{block_version}")
        return self._registry[key]

    def latest_version_of(self, block_id: str) -> Optional[type[LessonBlock]]:
        """Return the highest-version registered class for a block_id, or None."""
        candidates = [(v, cls) for (bid, v), cls in self._registry.items() if bid == block_id]
        if not candidates:
            return None
        # Lexical sort of semver-like strings is wrong for >9; use tuple parse
        def _parse(v: str) -> tuple:
            try:
                return tuple(int(x) for x in v.split("."))
            except ValueError:
                return (0, 0, 0)
        candidates.sort(key=lambda c: _parse(c[0]), reverse=True)
        return candidates[0][1]

    def list_block_ids(self) -> list[str]:
        return sorted({bid for bid, _ in self._registry.keys()})

    def list_versions_of(self, block_id: str) -> list[str]:
        return sorted({v for bid, v in self._registry.keys() if bid == block_id})

    def __len__(self) -> int:
        return len(self._registry)


# === A simple reference implementation =====================================


class VocabFlashcardBlock(LessonBlock):
    """Reference LessonBlock implementation for a vocab-match flashcard.

    Demonstrates the contract: a concrete subclass with class attributes set +
    the 3 required methods implemented. Community contributors model new
    blocks on this pattern.
    """
    block_id = "vocab.flashcard.reference"
    block_version = "0.1.0"
    block_kind = "vocab_flashcard"

    def __init__(
        self,
        headword_garifuna: str,
        gloss_en: str,
        gloss_es: str,
        distractors: tuple[str, ...],
        attribution_refs: tuple[str, ...],
        consent_ref: Optional[str],
        source_citations: tuple[str, ...] = (),
    ):
        self.headword_garifuna = headword_garifuna
        self.gloss_en = gloss_en
        self.gloss_es = gloss_es
        self.distractors = distractors
        self.attribution_refs = attribution_refs
        self.consent_ref = consent_ref
        self.source_citations = source_citations

    def render(self, ctx: BlockRenderContext) -> RenderedBlock:
        # Per-pathway gloss preference: HERITAGE prefers anchor-style; NOVICE
        # explicit translation; L1_MAINTAINER abstract definition.
        if ctx.pathway == "heritage":
            prompt = f"When have you heard '{self.headword_garifuna}' in your community?"
        elif ctx.pathway == "novice":
            prompt = f"'{self.headword_garifuna}' means: choose the best match."
        else:  # l1_maintainer
            prompt = f"Define '{self.headword_garifuna}' in academic register."

        # Correct gloss per UI language
        target_gloss = self.gloss_en if ctx.extra.get("ui_lang") != "es" else self.gloss_es

        return RenderedBlock(
            block_id=self.block_id,
            block_version=self.block_version,
            rendered_prompt=prompt,
            expected_response_kind="multiple_choice",
            options=tuple([target_gloss, *self.distractors]),
            cite_sources_payload=self.provenance().__dict__,
        )

    def score(self, response: str, ctx: Optional[BlockRenderContext] = None) -> Score:
        target_gloss = self.gloss_en if (ctx and ctx.extra.get("ui_lang") == "es") else None
        accepted = {self.gloss_en.lower().strip(), self.gloss_es.lower().strip()}
        is_correct = response.lower().strip() in accepted
        return Score(
            correct=is_correct,
            raw_score=1.0 if is_correct else 0.0,
            feedback_text="Correct!" if is_correct else f"The answer is: {self.gloss_en}",
            affect_signal_correct_streak_delta=1 if is_correct else 0,
        )

    def provenance(self) -> ProvenanceRef:
        return ProvenanceRef(
            attribution_refs=self.attribution_refs,
            consent_ref=self.consent_ref,
            source_citations=self.source_citations,
        )
