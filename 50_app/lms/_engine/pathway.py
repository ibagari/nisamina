"""M-P3.LMS.PATHWAY — Heritage / Novice / L1-maintainer pathway differentiation.

Per F-059 D-MAX-5 + Carreira & Kagan (2018) heritage-language pedagogy + Polinsky & Kagan
heritage continuum + Form-Focused Instruction in HL Classroom (Frontiers 2020).

Three pathways share common content but differ in:
- scaffolding_intensity (how much support / explicit instruction)
- register_focus (informal / formal / academic / cultural-ceremonial)
- assessment_threshold (mastery bar; HL learners have asymmetric receptive vs productive)
- form_focused_intensity (Frontiers 2020 — HL speakers need form-focused intervention
  for less-perceptible distinctions; L2 learners benefit from broader form exposure)

Identity-relevant content surfacing (per HL pedagogy literature) is higher for heritage learners.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Optional

try:
    from .lesson_player import Lesson, Unit, Step, StepKind
except ImportError:
    from lesson_player import Lesson, Unit, Step, StepKind


class PathwayKind(str, Enum):
    HERITAGE = "heritage"
    NOVICE = "novice"
    L1_MAINTAINER = "l1_maintainer"


class RegisterTier(str, Enum):
    """Linguistic register focus per pathway."""
    INFORMAL = "informal"           # everyday speech; family + community
    FORMAL = "formal"               # ceremonial + literary; gain-the-form scaffolding
    ACADEMIC = "academic"           # literacy + academic discourse
    CULTURAL_CEREMONIAL = "cultural_ceremonial"  # ICH + ritual + elder speech


@dataclass(frozen=True)
class LearnerProfile:
    """Inputs to PathwayResolver — what we know about the learner."""
    has_heritage_speaker_family: bool = False
    self_reported_proficiency: float = 0.0  # [0, 1]; per Polinsky-Kagan continuum
    primary_language: Optional[str] = None  # "garifuna" | "english" | "spanish" | "kr" | ...
    location: Optional[str] = None
    age_group: Optional[str] = None  # "child" | "youth" | "adult" | "elder"


@dataclass(frozen=True)
class PathwaySpec:
    """Configuration for a learner pathway."""
    kind: PathwayKind
    scaffolding_intensity: float    # [0, 1]; how much explicit support
    register_focus: RegisterTier
    assessment_threshold: float     # [0, 1]; mastery bar
    form_focused_intensity: float   # [0, 1]; Frontiers 2020
    identity_relevance_weight: float  # [0, 1]; surface cultural/identity content
    starts_with_reception: bool     # HL learners often have receptive > productive


# === Three canonical pathways ===
# Calibrated from peer-reviewed sources cited in F-059 D-MAX-5.

HERITAGE_PATHWAY = PathwaySpec(
    kind=PathwayKind.HERITAGE,
    scaffolding_intensity=0.6,        # moderate — leverage existing receptive knowledge
    register_focus=RegisterTier.CULTURAL_CEREMONIAL,
    assessment_threshold=0.80,        # slightly below novice — HL learners have asymmetric gaps
    form_focused_intensity=0.85,      # high — Form-Focused Instruction Frontiers 2020
    identity_relevance_weight=0.95,   # high — identity/connection is central HL motivation
    starts_with_reception=True,       # HL learners typically have receptive > productive
)

NOVICE_PATHWAY = PathwaySpec(
    kind=PathwayKind.NOVICE,
    scaffolding_intensity=0.9,        # high — no prior exposure
    register_focus=RegisterTier.INFORMAL,
    assessment_threshold=0.85,        # standard mastery bar
    form_focused_intensity=0.50,      # medium — broader form exposure for L2
    identity_relevance_weight=0.45,   # moderate — cultural curiosity but not identity
    starts_with_reception=False,      # parallel reception + production from day one
)

L1_MAINTAINER_PATHWAY = PathwaySpec(
    kind=PathwayKind.L1_MAINTAINER,
    scaffolding_intensity=0.3,        # low — fluent learners; literacy-focus, not basics
    register_focus=RegisterTier.ACADEMIC,
    assessment_threshold=0.90,        # high — fluent speakers should approach native-like literacy
    form_focused_intensity=0.40,      # medium-low — written form focus rather than oral form
    identity_relevance_weight=0.75,   # high — cultural pride + intergenerational transmission
    starts_with_reception=False,      # productive parity expected
)


_PATHWAY_BY_KIND = {
    PathwayKind.HERITAGE: HERITAGE_PATHWAY,
    PathwayKind.NOVICE: NOVICE_PATHWAY,
    PathwayKind.L1_MAINTAINER: L1_MAINTAINER_PATHWAY,
}


def pathway_for(kind: PathwayKind) -> PathwaySpec:
    return _PATHWAY_BY_KIND[kind]


class PathwayResolver:
    """Map LearnerProfile → recommended PathwayKind.

    Heuristics from Polinsky & Kagan heritage continuum + standard HL classroom intake.
    """

    def resolve(self, profile: LearnerProfile) -> PathwayKind:
        # L1-maintainer: native speaker (high self-reported proficiency + heritage family + Garifuna primary)
        if (profile.self_reported_proficiency >= 0.7
                and profile.has_heritage_speaker_family
                and profile.primary_language == "garifuna"):
            return PathwayKind.L1_MAINTAINER
        # Heritage: family connection but lower active proficiency (diaspora kids; receptive only)
        if profile.has_heritage_speaker_family and profile.self_reported_proficiency < 0.7:
            return PathwayKind.HERITAGE
        # Novice: no family connection (educators + allies + curious learners)
        return PathwayKind.NOVICE


class PathwayAdapter:
    """Adapts a base Lesson to a pathway-specific variant.

    Adaptation rules (informed by HL literature):
    - Heritage pathway: re-weight steps toward form-focused practice (Frontiers 2020);
      add identity-anchor INSTRUCTION steps at start.
    - Novice pathway: add EXAMPLE steps before each CHECK_FOR_UNDERSTANDING; full
      explicit scaffolding.
    - L1_maintainer pathway: reduce INSTRUCTION steps; emphasize PRACTICE + REFLECTION.
    """

    def adapt(self, base_lesson: Lesson, pathway_kind: PathwayKind) -> Lesson:
        spec = pathway_for(pathway_kind)
        new_units: list[Unit] = []
        for unit in base_lesson.units:
            new_steps = self._adapt_steps(unit.steps, spec)
            new_units.append(replace(unit, steps=tuple(new_steps)))
        return replace(base_lesson, pathway=spec.kind.value, units=tuple(new_units))

    def _adapt_steps(self, steps: tuple[Step, ...], spec: PathwaySpec) -> list[Step]:
        if spec.kind == PathwayKind.HERITAGE:
            return self._heritage_adapt(steps, spec)
        if spec.kind == PathwayKind.NOVICE:
            return self._novice_adapt(steps, spec)
        return self._l1_maintainer_adapt(steps, spec)

    def _heritage_adapt(self, steps: tuple[Step, ...], spec: PathwaySpec) -> list[Step]:
        out: list[Step] = []
        # Prepend an identity-anchor instruction (cultural-protocol step)
        if steps:
            anchor = Step(
                step_id=f"hr.anchor.{steps[0].step_id}",
                kind=StepKind.INSTRUCTION,
                headword_garifuna=steps[0].headword_garifuna,
                prompt_text=f"Heritage anchor: connect '{steps[0].headword_garifuna}' to your family or community.",
            )
            out.append(anchor)
        # Boost form-focused practice: duplicate PRACTICE steps once
        for s in steps:
            out.append(s)
            if s.kind == StepKind.PRACTICE:
                out.append(replace(s, step_id=f"hr.ff.{s.step_id}"))
        return out

    def _novice_adapt(self, steps: tuple[Step, ...], spec: PathwaySpec) -> list[Step]:
        out: list[Step] = []
        for s in steps:
            # Insert an EXAMPLE step before each CHECK_FOR_UNDERSTANDING
            if s.kind == StepKind.CHECK_FOR_UNDERSTANDING:
                ex = Step(
                    step_id=f"nv.ex.{s.step_id}",
                    kind=StepKind.EXAMPLE,
                    headword_garifuna=s.headword_garifuna,
                    prompt_text=f"Example: {s.headword_garifuna} (study this before answering).",
                )
                out.append(ex)
            out.append(s)
        return out

    def _l1_maintainer_adapt(self, steps: tuple[Step, ...], spec: PathwaySpec) -> list[Step]:
        out: list[Step] = []
        for s in steps:
            # Skip basic INSTRUCTION steps (fluent speakers don't need them);
            # keep EXAMPLE/CHECK/PRACTICE/REFLECTION which test literacy + register.
            if s.kind == StepKind.INSTRUCTION:
                continue
            out.append(s)
        # If we cut everything, retain at least the original sequence
        return out if out else list(steps)
