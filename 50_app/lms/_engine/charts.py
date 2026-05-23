"""M-P3.LMS.CHARTS — Trilingual Garifuna learning charts.

Per F-076 + director directive 2026-05-23 "add missing charts per subject where needed".

A chart is a labeled visual reference (in the spirit of the 17 published English charts
in /Volumes/AI External/Nisamina_AI_Garifuna_Textbook_Library/Garifuna_Learning_Charts/)
rebuilt with TRILINGUAL labels (Garifuna + English + Spanish) and SCIENTIFIC integrity.

Each chart entry has:
  - canonical key (e.g., "anatomy.body.head")
  - trilingual gloss (cab + en + es; cab may have [needs Garifuna term] marker
    routed via neologism_queue per F-067 §3)
  - cultural anchor (Caribbean / Garifuna context where relevant)
  - dialect tag (when chart contains region-specific lexicon)
  - source citation (which dictionary / reference informed the cab term)

Per F-055 axis #1 sovereign presentation: source PRESENTATION matter is rebuilt
fresh (engineer-side, peer-reviewed-cited), not republished from copyrighted
reference charts. Per Labayayahoun Ibagari: matter belongs to the people;
presentation belongs to Nisamina.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ChartSubject(str, Enum):
    # Core early-learning subjects (typically present in pubished reference charts)
    ALPHABET = "alphabet"               # Garifuna NGC orthography
    NUMBERS = "numbers"                 # 1-10, 1-20, counting in Garifuna
    COLORS = "colors"
    SHAPES = "shapes"
    BODY_PARTS = "body_parts"           # anatomy (1 of 5 ref charts)
    FIVE_SENSES = "five_senses"
    SKELETAL = "skeletal"
    ORGANS = "organs"                   # respiratory / digestive / circulatory
    # Common life domains (often missing from generic English chart packs)
    FAMILY_KINSHIP = "family_kinship"   # Garifuna matrilineal terminology (rich domain)
    GREETINGS = "greetings"
    EMOTIONS = "emotions"
    FOOD = "food"                       # hudutu + sere + ereba + machuca + cassava + etc.
    ANIMALS = "animals"                 # Caribbean + diaspora common
    PLANTS = "plants"                   # cassava, plantain, breadfruit, etc.
    WEATHER = "weather"                 # Caribbean specifics (hurricane, tide)
    SKY = "sky"                         # sun + moon + stars
    DAYS = "days_of_week"
    MONTHS = "months"
    SEASONS = "seasons"
    VERBS_COMMON = "verbs_common"
    NOUNS_HOME = "nouns_home"           # household objects + dabuyaba
    NOUNS_KITCHEN = "nouns_kitchen"     # cooking tools + traditional cookware
    NOUNS_SEA = "nouns_sea"             # canoe, paddle, net, fish kinds
    PRONOUNS = "pronouns"
    ADJECTIVES_BASIC = "adjectives_basic"  # big/small/hot/cold/etc.
    # Garifuna cultural-heritage specific (Tier-5 V_VAULT + community-governed)
    DANCE_MUSIC = "dance_music"         # punta + paranda + chumba + hungahunga
    CALENDAR_CULTURAL = "calendar_cultural"  # Settlement Day, Yurumein April 14, Chugu, Beluria
    CLOTHING_TRADITIONAL = "clothing_traditional"
    # Process/cycle tier (per F-076-AMENDMENT-2 + NGSS K-12 6-cycle framework)
    PROCESS_CYCLES = "process_cycles"   # day/night, week, year, water, life, NGSS-6, Caribbean ecology, Garifuna cultural cycles


class ChartTier(str, Enum):
    """Per-chart cultural-protocol tier."""
    PUBLIC = "public"                       # general learning content; freely shareable
    INSTITUTIONAL = "institutional"         # for MOE/Commission distribution
    ELDER_GATED = "elder_gated"             # requires Commission elder sign-off before publication
    SACRED_RESTRICTED = "sacred_restricted" # never republished; routes to elder channel only


@dataclass(frozen=True)
class TrilingualGloss:
    """Three-language gloss of a single chart item.

    cab may be None if no canonical Garifuna term exists yet (routed via
    neologism_queue per F-067 §3). pending_neologism flag surfaces this in UI.
    """
    cab: Optional[str]                  # Garifuna (NGC orthography per Cayetano 1992)
    en: str                             # English
    es: str                             # Spanish
    pending_neologism: bool = False
    dialect_tag: Optional[str] = None   # cab_BLZ / cab_HND / cab_GUA / cab_NIC / cab_SVG


@dataclass(frozen=True)
class ChartItem:
    """A single labeled entry within a chart (e.g., one body part in an anatomy chart)."""
    item_id: str                        # e.g., "anatomy.head" — within-chart unique
    gloss: TrilingualGloss
    cultural_anchor: Optional[str] = None  # Caribbean / Garifuna context if relevant
    foundry_ref: Optional[str] = None   # headword_id in foundry V0.2 if canonical
    source_citation: Optional[str] = None  # e.g., "Cayetano 1992 NGC §body p.47"
    visual_hint: Optional[str] = None   # description for illustrator / accessibility alt-text


@dataclass(frozen=True)
class Chart:
    """A complete trilingual learning chart (typically 6-30 items)."""
    chart_id: str                       # e.g., "chart.body_parts.basic"
    subject: ChartSubject
    title: TrilingualGloss
    tier: ChartTier
    grade_bands: tuple[str, ...]        # which bands this chart serves
    items: tuple[ChartItem, ...]
    cultural_context_note: Optional[str] = None
    elder_signoff_required: bool = False  # set True for ELDER_GATED + SACRED_RESTRICTED tier

    def __post_init__(self):
        if self.tier in (ChartTier.ELDER_GATED, ChartTier.SACRED_RESTRICTED):
            object.__setattr__(self, "elder_signoff_required", True)

    def pending_garifuna_count(self) -> int:
        """How many items still need Garifuna canonical terms (neologism_queue)."""
        return sum(1 for item in self.items if item.gloss.pending_neologism)


@dataclass
class ChartCatalog:
    """In-memory chart catalog — covers all subjects + tracks coverage gaps."""
    charts: dict[str, Chart] = field(default_factory=dict)

    def add(self, chart: Chart) -> None:
        if chart.chart_id in self.charts:
            raise ValueError(f"duplicate chart_id: {chart.chart_id}")
        self.charts[chart.chart_id] = chart

    def by_subject(self, subject: ChartSubject) -> list[Chart]:
        return [c for c in self.charts.values() if c.subject == subject]

    def subjects_covered(self) -> set[ChartSubject]:
        return {c.subject for c in self.charts.values()}

    def subjects_missing(self) -> set[ChartSubject]:
        """All ChartSubject enum values NOT yet represented in the catalog."""
        return set(ChartSubject) - self.subjects_covered()

    def total_pending_neologisms(self) -> int:
        return sum(c.pending_garifuna_count() for c in self.charts.values())

    def coverage_report(self) -> dict:
        """High-level coverage view (for documentarian + Commission review)."""
        subjects_all = set(ChartSubject)
        covered = self.subjects_covered()
        missing = subjects_all - covered
        return {
            "total_charts": len(self.charts),
            "subjects_total_enum": len(subjects_all),
            "subjects_covered": len(covered),
            "subjects_missing": [s.value for s in sorted(missing, key=lambda x: x.value)],
            "coverage_pct": round(100 * len(covered) / len(subjects_all), 1),
            "pending_neologisms_total": self.total_pending_neologisms(),
        }
