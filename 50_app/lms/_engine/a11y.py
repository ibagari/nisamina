"""M-P3.LMS.A11Y — WCAG 2.2 AAA + low-bandwidth + print-export.

Per F-059 D-MAX-12 + WCAG 2.2 AAA + UNESCO Languages Matter 2025 + federal
April 24 2026 deadline (AA is floor; AAA is target where feasible).

This module provides PROGRAMMATIC accessibility helpers that the UI layer
(M-P3.UI.A Next.js scaffold + M-P3.UI.B routing + M-P3.UI.D chatbot embed)
consumes to enforce a11y at runtime. WCAG validators in JS-land (axe-core)
handle the DOM side; this module handles content-side preconditions.

Surface:
- contrast ratio computation (sRGB → WCAG)
- AAA contrast checker (≥7:1 normal text; ≥4.5:1 large text)
- AA contrast checker (≥4.5:1 / ≥3:1)
- touch target validator (≥44×44 px per WCAG 2.5.8 SC)
- print-export workbook (markdown + sanitized HTML; offline-only learners)
- low-bandwidth content selector (audio-only + text-only modes)
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence


class ContrastLevel(str, Enum):
    FAIL = "fail"
    AA = "aa"
    AAA = "aaa"


def _srgb_to_linear(channel: int) -> float:
    """sRGB 0..255 → linear 0..1 per WCAG relative luminance formula."""
    c = channel / 255.0
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG relative luminance of an sRGB color (0..1)."""
    r, g, b = rgb
    return 0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g) + 0.0722 * _srgb_to_linear(b)


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """WCAG contrast ratio between two sRGB colors. Always ≥1.0."""
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def classify_contrast(
    fg: tuple[int, int, int],
    bg: tuple[int, int, int],
    is_large_text: bool = False,
) -> ContrastLevel:
    """Return WCAG level for given color pair.

    Per WCAG 2.2 SC 1.4.6 (AAA):
      - Normal text: ≥7:1
      - Large text:  ≥4.5:1
    Per WCAG 2.2 SC 1.4.3 (AA):
      - Normal text: ≥4.5:1
      - Large text:  ≥3:1
    """
    r = contrast_ratio(fg, bg)
    aaa_threshold = 4.5 if is_large_text else 7.0
    aa_threshold = 3.0 if is_large_text else 4.5
    if r >= aaa_threshold:
        return ContrastLevel.AAA
    if r >= aa_threshold:
        return ContrastLevel.AA
    return ContrastLevel.FAIL


# Touch target — WCAG 2.5.8 (Level AA in 2.2; AAA = 44px + spacing)
MIN_TOUCH_TARGET_PX = 44


def validate_touch_target(width_px: int, height_px: int) -> bool:
    """WCAG 2.5.8 — touch target must be ≥44×44 px (with allowable exceptions
    that this helper does NOT enable; callers must opt-out explicitly)."""
    return width_px >= MIN_TOUCH_TARGET_PX and height_px >= MIN_TOUCH_TARGET_PX


# === Print-export workbook ==================================================


@dataclass(frozen=True)
class WorkbookSection:
    title: str
    body_markdown: str


def render_workbook_markdown(
    *,
    title: str,
    envir: str,
    pathway: str,
    grade_band: str,
    sections: Sequence[WorkbookSection],
    license_principle: str = "Labayayahoun Ibagari + CC-BY-NC-SA 4.0",
) -> str:
    """Render a printable workbook as Markdown.

    SVG-Yurumein remote-area pilot + diaspora offline-only learners (D-MAX-12)
    need a paper-printable form. Markdown converts cleanly to PDF via pandoc.
    """
    out = [f"# {title}\n", f"*Envir: {envir} · Pathway: {pathway} · Grade band: {grade_band}*\n"]
    out.append(f"*License: {license_principle}*\n\n---\n")
    for i, s in enumerate(sections, 1):
        out.append(f"## {i}. {s.title}\n\n{s.body_markdown}\n\n---\n")
    out.append("\n*Buguya nuani Wamaraga.*\n")
    return "".join(out)


# === Low-bandwidth content selector ========================================


class BandwidthMode(str, Enum):
    FULL = "full"                    # video + audio + image + text (no constraint)
    AUDIO_ONLY = "audio_only"        # audio + text fallback; no images/video
    TEXT_ONLY = "text_only"          # text + transcripts only
    PRINT = "print"                  # paper-only fallback (uses render_workbook_markdown)


def select_assets_for_mode(
    available_assets: Sequence[dict],
    mode: BandwidthMode,
) -> list[dict]:
    """Filter a list of asset dicts by their suitability for a bandwidth mode.

    `available_assets` are dicts with a "kind" key per MultimodalAsset.
    """
    if mode == BandwidthMode.FULL:
        return list(available_assets)
    if mode == BandwidthMode.AUDIO_ONLY:
        return [a for a in available_assets if a.get("kind") in ("audio", "oral_history")]
    if mode == BandwidthMode.TEXT_ONLY:
        # Only documents + items lacking heavyweight media
        return [a for a in available_assets if a.get("kind") in ("document",)]
    if mode == BandwidthMode.PRINT:
        # Print mode is a content-side concern; this returns text/document assets
        # for embedding into the printable workbook.
        return [a for a in available_assets if a.get("kind") in ("document",)]
    return []
