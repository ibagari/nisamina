"""M-P3.LMS.STEM_LESSON_GEN — Trilingual STEM lesson generator.

Per F-067 §4 PART 4 + F-066 trilingual + F-065-AMENDMENT 5-pillar framework.

Produces lesson JSON in the schema documented in GARIFUNA_OVERLAY_PROTOCOL.md:
    {
      "lesson_id": "stem.<subject>.<band>.<concept>",
      "subject": "Math" | "Science" | "Computing",
      "grade_band": "04_Upper_Elementary_Grades_3_to_5",
      "concept": "...",
      "source_refs": [...],
      "consent_ref": "consent_012",
      "attribution_refs": [...],
      "trilingual": {
        "cab": {...},  # Garifuna
        "en":  {...},  # English
        "es":  {...}   # Spanish
      },
      "cultural_anchors": [...],
      "pathway_variants": {
        "heritage": {...},
        "novice": {...},
        "l1_maintainer": {...}
      }
    }

Generator flow:
    1. Take source concept + grade band + subject + cultural anchor
    2. Build English + Spanish base content (source-language-faithful)
    3. For Garifuna track: look up terms in foundry; queue missing terms via
       NeologismQueue per F-067 §3 (engineer never invents technical Garifuna)
    4. Apply pathway differentiation per F-059 D-MAX-5
    5. Emit lesson JSON
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from .neologism_queue import NeologismQueue
    from .pathway import PathwayKind, pathway_for
except ImportError:
    from neologism_queue import NeologismQueue
    from pathway import PathwayKind, pathway_for


@dataclass(frozen=True)
class SourceRef:
    corpus: str         # e.g., "Singapore_Math_4A"
    page: str           # e.g., "47-52"
    publisher: str      # e.g., "Singapore Math Inc."


@dataclass(frozen=True)
class ConceptSpec:
    """Input spec for one lesson."""
    subject: str                     # "Math" | "Science" | "Computing"
    grade_band: str                  # e.g., "04_Upper_Elementary_Grades_3_to_5"
    concept_slug: str                # e.g., "bar_modeling.fractions_intro"
    concept_title_en: str
    concept_title_es: str
    source_refs: tuple[SourceRef, ...]
    cultural_anchors: tuple[str, ...]   # Caribbean / Garifuna ecological-cultural hooks
    technical_terms: tuple[str, ...]    # source-language terms that need Garifuna coining
    objectives_en: tuple[str, ...]
    objectives_es: tuple[str, ...]


class LessonGenerator:
    """Trilingual lesson JSON generator.

    Per F-067 + F-066: Garifuna technical-register terms are NOT engineer-invented.
    Missing terms are queued via NeologismQueue; lesson renders English/Spanish
    fallback with `[needs Garifuna term]` flag.
    """

    def __init__(
        self,
        foundry_terms: dict[str, str],
        neologism_queue: NeologismQueue,
        envir: str = "stem_alternative",
    ):
        """
        Args:
            foundry_terms: dict mapping {source_language_term: garifuna_term}
                          loaded from foundry V0.2 + later V0.3 coinings
            neologism_queue: queue for missing terms (Commission elder review)
            envir: source envir id (controls per-envir sovereignty)
        """
        self.foundry_terms = foundry_terms
        self.queue = neologism_queue
        self.envir = envir

    def garifuna_for(
        self,
        source_term: str,
        source_language: str,
        semantic_field: str,
        grade_band: str,
        context_sentence: str,
    ) -> tuple[Optional[str], bool]:
        """Look up the Garifuna term; if missing, queue it.

        Returns:
            (garifuna_term, is_canonical):
                - if canonical: (term, True)
                - if missing: (None, False) and request queued
        """
        canonical = self.foundry_terms.get(source_term)
        if canonical:
            return canonical, True
        # Missing — queue for Commission/lexicographer review
        self.queue.queue_request(
            source_term=source_term,
            source_language=source_language,
            semantic_field=semantic_field,
            grade_band=grade_band,
            context_sentence=context_sentence,
            envir=self.envir,
        )
        return None, False

    def render_garifuna_text(
        self,
        source_text: str,
        source_language: str,
        semantic_field: str,
        grade_band: str,
        technical_terms: tuple[str, ...],
    ) -> tuple[str, list[str]]:
        """Render Garifuna track for a piece of text.

        Looks up each technical term in foundry; substitutes if found;
        otherwise marks `[needs Garifuna term]` + queues for review.

        Returns:
            (rendered_text_with_garifuna_where_available, pending_terms_list)
        """
        out = source_text
        pending: list[str] = []
        for term in technical_terms:
            gari, ok = self.garifuna_for(
                source_term=term,
                source_language=source_language,
                semantic_field=semantic_field,
                grade_band=grade_band,
                context_sentence=source_text,
            )
            if ok and gari:
                out = out.replace(term, gari)
            else:
                out = out.replace(term, f"{term} [needs Garifuna term]")
                pending.append(term)
        return out, pending

    def generate_lesson(self, spec: ConceptSpec) -> dict:
        """Produce a lesson JSON dict from a ConceptSpec."""
        lesson_id = f"stem.{spec.subject.lower()}.{spec.grade_band}.{spec.concept_slug}"
        semantic_field = spec.subject.lower()

        # Garifuna track — substitute or queue per term
        gari_text, pending = self.render_garifuna_text(
            source_text=spec.concept_title_en,
            source_language="en",
            semantic_field=semantic_field,
            grade_band=spec.grade_band,
            technical_terms=spec.technical_terms,
        )
        # Garifuna objectives — same scaffold
        gari_objs: list[str] = []
        for obj in spec.objectives_en:
            rendered, _ = self.render_garifuna_text(
                source_text=obj,
                source_language="en",
                semantic_field=semantic_field,
                grade_band=spec.grade_band,
                technical_terms=spec.technical_terms,
            )
            gari_objs.append(rendered)

        return {
            "lesson_id": lesson_id,
            "subject": spec.subject,
            "grade_band": spec.grade_band,
            "concept": spec.concept_slug,
            "source_refs": [
                {"corpus": r.corpus, "page": r.page, "publisher": r.publisher}
                for r in spec.source_refs
            ],
            "consent_ref": "consent_012",
            "attribution_refs": [],  # per-publisher attribution rows queued M-P3.LMS.STEM_ATTRIBUTION
            "trilingual": {
                "cab": {
                    "title": gari_text,
                    "objectives": gari_objs,
                    "pending_neologisms": pending,
                },
                "en": {
                    "title": spec.concept_title_en,
                    "objectives": list(spec.objectives_en),
                },
                "es": {
                    "title": spec.concept_title_es,
                    "objectives": list(spec.objectives_es),
                },
            },
            "cultural_anchors": list(spec.cultural_anchors),
            "pathway_variants": self._pathway_variants(spec),
        }

    def _pathway_variants(self, spec: ConceptSpec) -> dict:
        """Generate pathway-specific scaffolding hooks per F-059 D-MAX-5."""
        heritage_spec = pathway_for(PathwayKind.HERITAGE)
        novice_spec = pathway_for(PathwayKind.NOVICE)
        l1_spec = pathway_for(PathwayKind.L1_MAINTAINER)
        return {
            "heritage": {
                "identity_anchor_required": True,
                "form_focused_intensity": heritage_spec.form_focused_intensity,
                "register_focus": heritage_spec.register_focus.value,
                "starts_with_reception": heritage_spec.starts_with_reception,
            },
            "novice": {
                "scaffolding_intensity": novice_spec.scaffolding_intensity,
                "explicit_examples_prepended": True,
                "register_focus": novice_spec.register_focus.value,
            },
            "l1_maintainer": {
                "skip_basic_instructions": True,
                "academic_register_emphasized": True,
                "assessment_threshold": l1_spec.assessment_threshold,
            },
        }
