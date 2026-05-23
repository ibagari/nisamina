"""Tests for M-P3.LMS.A11Y — WCAG 2.2 AAA helpers."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.a11y import (
    ContrastLevel, BandwidthMode, WorkbookSection,
    contrast_ratio, classify_contrast, validate_touch_target,
    render_workbook_markdown, select_assets_for_mode,
    MIN_TOUCH_TARGET_PX,
)


# === Contrast computation ===


def test_contrast_ratio_white_on_black_is_21():
    # Maximum possible contrast: pure white on pure black = 21:1
    r = contrast_ratio((255, 255, 255), (0, 0, 0))
    assert 20.99 < r < 21.01


def test_contrast_ratio_symmetric():
    a = contrast_ratio((255, 255, 255), (0, 0, 0))
    b = contrast_ratio((0, 0, 0), (255, 255, 255))
    assert a == b


def test_classify_contrast_aaa_pass_normal_text():
    # ~14:1 — well over 7:1 AAA normal-text threshold
    level = classify_contrast((20, 20, 20), (245, 245, 245), is_large_text=False)
    assert level == ContrastLevel.AAA


def test_classify_contrast_aa_only_normal_text():
    # ~5:1 — passes AA (≥4.5) but not AAA (≥7)
    level = classify_contrast((100, 100, 100), (250, 250, 250), is_large_text=False)
    assert level == ContrastLevel.AA


def test_classify_contrast_fail():
    # Light gray on white — ~2:1; fails AA
    level = classify_contrast((200, 200, 200), (255, 255, 255), is_large_text=False)
    assert level == ContrastLevel.FAIL


def test_large_text_aaa_threshold_lower():
    # ~5:1 — fails AAA normal but passes AAA large (≥4.5)
    normal = classify_contrast((100, 100, 100), (250, 250, 250), is_large_text=False)
    large = classify_contrast((100, 100, 100), (250, 250, 250), is_large_text=True)
    assert normal == ContrastLevel.AA
    assert large == ContrastLevel.AAA


# === Touch target ===


def test_touch_target_exactly_44_passes():
    assert validate_touch_target(MIN_TOUCH_TARGET_PX, MIN_TOUCH_TARGET_PX) is True


def test_touch_target_below_44_fails():
    assert validate_touch_target(43, 44) is False
    assert validate_touch_target(44, 43) is False


def test_touch_target_above_44_passes():
    assert validate_touch_target(48, 48) is True


# === Print workbook ===


def test_workbook_contains_metadata():
    md = render_workbook_markdown(
        title="Day 1 — Greetings",
        envir="svg_yurumein",
        pathway="heritage",
        grade_band="03_Early_Elementary_Grades_1_to_2",
        sections=(
            WorkbookSection("Vocabulary", "buguya · nuani · seremein"),
            WorkbookSection("Practice", "Match each word to its English gloss."),
        ),
    )
    assert "# Day 1 — Greetings" in md
    assert "svg_yurumein" in md
    assert "Labayayahoun Ibagari" in md
    assert "Vocabulary" in md
    assert "Buguya nuani Wamaraga" in md


def test_workbook_with_custom_license():
    md = render_workbook_markdown(
        title="Custom",
        envir="garicomm",
        pathway="novice",
        grade_band="01_PreK_Ages_3_to_5",
        sections=(WorkbookSection("X", "Y"),),
        license_principle="Apache 2.0 + custom",
    )
    assert "Apache 2.0 + custom" in md


# === Bandwidth mode asset selection ===


def test_full_mode_returns_all_assets():
    assets = [
        {"kind": "video"}, {"kind": "audio"}, {"kind": "document"}, {"kind": "image"},
    ]
    assert len(select_assets_for_mode(assets, BandwidthMode.FULL)) == 4


def test_audio_only_mode_filters():
    assets = [
        {"kind": "video"}, {"kind": "audio"}, {"kind": "oral_history"}, {"kind": "image"},
    ]
    out = select_assets_for_mode(assets, BandwidthMode.AUDIO_ONLY)
    assert len(out) == 2
    assert all(a["kind"] in ("audio", "oral_history") for a in out)


def test_text_only_mode_filters():
    assets = [
        {"kind": "video"}, {"kind": "document"}, {"kind": "audio"},
    ]
    out = select_assets_for_mode(assets, BandwidthMode.TEXT_ONLY)
    assert len(out) == 1
    assert out[0]["kind"] == "document"
