"""Tests for M-P3.LMS.CHARTS — Trilingual learning charts."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.charts import (
    Chart, ChartItem, ChartSubject, ChartTier, TrilingualGloss, ChartCatalog,
)
from lms._engine.chart_seed import (
    build_seed_catalog,
    ALPHABET_CHART, NUMBERS_1_10_CHART, BODY_PARTS_CHART, FAMILY_KINSHIP_CHART,
    GREETINGS_CHART, FOOD_CHART, CALENDAR_CULTURAL_CHART,
)


# === Schema basics ===

def test_trilingual_gloss_pending_neologism_flag():
    g_full = TrilingualGloss(cab="aban", en="one", es="uno")
    g_missing = TrilingualGloss(cab=None, en="brown", es="marrón", pending_neologism=True)
    assert g_full.pending_neologism is False
    assert g_missing.pending_neologism is True


def test_elder_gated_tier_sets_signoff():
    chart = Chart(
        chart_id="x", subject=ChartSubject.DANCE_MUSIC,
        title=TrilingualGloss("x", "x", "x"),
        tier=ChartTier.ELDER_GATED,
        grade_bands=("01_PreK_Ages_3_to_5",),
        items=(),
    )
    assert chart.elder_signoff_required is True


def test_public_tier_does_not_set_signoff():
    chart = Chart(
        chart_id="x2", subject=ChartSubject.NUMBERS,
        title=TrilingualGloss("x", "x", "x"),
        tier=ChartTier.PUBLIC,
        grade_bands=("01_PreK_Ages_3_to_5",),
        items=(),
    )
    assert chart.elder_signoff_required is False


def test_pending_count_aggregates():
    items = (
        ChartItem("c.1", TrilingualGloss("a", "a", "a")),
        ChartItem("c.2", TrilingualGloss(None, "b", "b", pending_neologism=True)),
        ChartItem("c.3", TrilingualGloss(None, "c", "c", pending_neologism=True)),
    )
    chart = Chart(
        chart_id="t", subject=ChartSubject.NUMBERS,
        title=TrilingualGloss("t", "t", "t"),
        tier=ChartTier.PUBLIC,
        grade_bands=("01_PreK_Ages_3_to_5",),
        items=items,
    )
    assert chart.pending_garifuna_count() == 2


# === Catalog ===

def test_catalog_add_and_dedup():
    catalog = ChartCatalog()
    chart = Chart(
        chart_id="cdup", subject=ChartSubject.COLORS,
        title=TrilingualGloss("c", "c", "c"), tier=ChartTier.PUBLIC,
        grade_bands=("01_PreK_Ages_3_to_5",), items=(),
    )
    catalog.add(chart)
    with pytest.raises(ValueError, match="duplicate"):
        catalog.add(chart)


def test_catalog_by_subject_numbers_has_at_least_one():
    catalog = build_seed_catalog()
    by_subj = catalog.by_subject(ChartSubject.NUMBERS)
    # 1-10 + 11-20 extension charts may both be present
    assert len(by_subj) >= 1
    chart_ids = {c.chart_id for c in by_subj}
    assert "chart.numbers.1_10" in chart_ids


def test_catalog_subjects_covered_includes_core_subjects():
    """Seeded catalog must cover at least the 12 high-priority core subjects."""
    catalog = build_seed_catalog()
    covered = catalog.subjects_covered()
    core_required = {
        ChartSubject.ALPHABET, ChartSubject.NUMBERS, ChartSubject.COLORS,
        ChartSubject.SHAPES, ChartSubject.BODY_PARTS, ChartSubject.FIVE_SENSES,
        ChartSubject.FAMILY_KINSHIP, ChartSubject.GREETINGS, ChartSubject.EMOTIONS,
        ChartSubject.FOOD, ChartSubject.DAYS, ChartSubject.CALENDAR_CULTURAL,
    }
    assert core_required.issubset(covered)


def test_catalog_has_full_or_near_full_subject_coverage():
    """Per F-076 + D-060 director-correction event #10: catalog should cover
    the full ChartSubject enum (all 28 subjects) at least at placeholder level."""
    catalog = build_seed_catalog()
    missing = catalog.subjects_missing()
    # After D-060 + D-059, every ChartSubject should have at least one chart
    # (DANCE_MUSIC is ELDER_GATED placeholder; specifics route to elder channel)
    assert len(missing) == 0, f"Expected full coverage; missing: {[m.value for m in missing]}"


def test_dance_music_is_elder_gated():
    """Per Labayayahoun Ibagari + F-031: ICH dance/music routes to Commission
    elder channel for any deeper-than-naming engagement."""
    catalog = build_seed_catalog()
    chart = next(iter(catalog.by_subject(ChartSubject.DANCE_MUSIC)), None)
    assert chart is not None
    assert chart.tier == ChartTier.ELDER_GATED
    assert chart.elder_signoff_required is True


def test_pronouns_chart_includes_buguya():
    """K-2 BICS grammar essential; 'buguya' appears in 'buguya nuani' too."""
    catalog = build_seed_catalog()
    chart = next(iter(catalog.by_subject(ChartSubject.PRONOUNS)), None)
    assert chart is not None
    items = {it.item_id: it for it in chart.items}
    p2 = items.get("pron.2sg")
    assert p2 is not None
    assert p2.gloss.cab == "buguya"


def test_catalog_coverage_report_structure():
    catalog = build_seed_catalog()
    r = catalog.coverage_report()
    # Per F-076 + D-060: must have at least 12 core subjects + ideally 100% per
    # director-correction event #10
    assert r["total_charts"] >= 12
    assert r["subjects_covered"] >= 12
    assert r["subjects_total_enum"] == len(list(ChartSubject))
    assert 0 < r["coverage_pct"] <= 100
    assert isinstance(r["subjects_missing"], list)
    assert r["pending_neologisms_total"] >= 0


# === Seed corpus content ===

def test_alphabet_uses_ngc_orthography():
    items = ALPHABET_CHART.items
    letters = [it.gloss.cab for it in items]
    # NGC orthography includes ü (high central vowel)
    assert "ü" in letters
    # NGC has no c/k/q/v/x/z
    assert "c" not in letters
    assert "k" not in letters
    assert "z" not in letters


def test_numbers_1_10_has_all_canonical_garifuna():
    # All 10 numbers should have canonical Garifuna terms (no neologism queue items)
    assert NUMBERS_1_10_CHART.pending_garifuna_count() == 0
    assert len(NUMBERS_1_10_CHART.items) == 10
    item_ids = [it.item_id for it in NUMBERS_1_10_CHART.items]
    assert item_ids == [f"num.{n}" for n in range(1, 11)]


def test_body_parts_carries_cultural_anchor():
    items = {it.item_id: it for it in BODY_PARTS_CHART.items}
    heart = items.get("body.heart")
    assert heart is not None
    assert heart.gloss.cab == "anigi"
    assert "identity" in (heart.cultural_anchor or "").lower()


def test_family_kinship_flags_patrilineal_aunt_uncle_as_pending():
    items = {it.item_id: it for it in FAMILY_KINSHIP_CHART.items}
    # Patrilineal aunt/uncle pending Commission elder-mentor review
    assert items["kin.aunt-patri"].gloss.pending_neologism is True
    assert items["kin.uncle-patri"].gloss.pending_neologism is True
    # Matrilineal aunt/uncle have canonical terms
    assert items["kin.aunt-matri"].gloss.pending_neologism is False


def test_greetings_includes_buguya_nuani():
    items = {it.item_id: it for it in GREETINGS_CHART.items}
    bn = items.get("greet.thanks-affectionate")
    assert bn is not None
    assert bn.gloss.cab == "buguya nuani"
    assert "wamaraga" in (bn.cultural_anchor or "").lower()


def test_food_includes_ereba_with_cultural_anchor():
    items = {it.item_id: it for it in FOOD_CHART.items}
    ereba = items.get("food.ereba")
    assert ereba is not None
    assert ereba.gloss.cab == "ereba"
    assert "cassava" in (ereba.cultural_anchor or "").lower()


def test_calendar_cultural_is_institutional_tier():
    assert CALENDAR_CULTURAL_CHART.tier == ChartTier.INSTITUTIONAL
    # Settlement Day + Yurumein dates present
    item_ids = [it.item_id for it in CALENDAR_CULTURAL_CHART.items]
    assert "cal.settlement_day" in item_ids
    assert "cal.yurumein" in item_ids
    assert "cal.chugu" in item_ids
    assert "cal.beluria" in item_ids
