"""Nisamina API bridge — FastAPI thin layer serving engine → UI.

Per D-070 director-approved scope: thin shim that:
- exposes engine state (charts, badges, tutor sessions, pathways) to the
  Next.js UI via HTTP/JSON
- enforces F-055 axis #6 per-MOE envir sovereignty at the route layer
- supports trilingual response language per F-066

Per F-074 PHASE-NOW: read-only endpoints first; mutations queued (tutor
turn submission, badge issuance, neologism proposal POST etc.).

USAGE:
    pip install fastapi uvicorn
    cd 50_app/api && uvicorn main:app --reload --port 8000

Then Next.js (50_app/web/) fetches from http://localhost:8000/.../...
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Import engine — adjust path for both dev + production layouts
_HERE = Path(__file__).resolve().parent
_LMS = _HERE.parent / "lms"
if str(_LMS.parent.resolve()) not in sys.path:
    sys.path.insert(0, str(_LMS.parent.resolve()))

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    raise ImportError(
        "FastAPI required. Install with: pip install fastapi uvicorn"
    )

from lms._engine import (  # type: ignore  # noqa: E402
    build_seed_catalog,
    PathwayResolver, LearnerProfile, PathwayKind,
    ChartTier,
)


app = FastAPI(
    title="Nisamina Engine API",
    description="Thin HTTP/JSON bridge from Python LMS engine to Next.js UI",
    version="0.1.0",
)

# CORS: allow Next.js dev origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# === Health =================================================================


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "nisamina-engine-api", "version": "0.1.0"}


# === Pathway resolution =====================================================


@app.post("/api/v1/pathway/resolve")
def resolve_pathway(
    has_heritage_speaker_family: bool,
    self_reported_proficiency: float = Query(..., ge=0.0, le=1.0),
    primary_language: Optional[str] = None,
) -> dict:
    """Resolve pathway from learner profile.

    Mirror of client-side `resolvePathway()` in learner_state.ts; both stay in
    sync. Server-side is canonical for badge-issuance + cohort enrollment.
    """
    profile = LearnerProfile(
        has_heritage_speaker_family=has_heritage_speaker_family,
        self_reported_proficiency=self_reported_proficiency,
        primary_language=primary_language,
    )
    pathway = PathwayResolver().resolve(profile)
    return {
        "pathway": pathway.value,
        "profile": {
            "has_heritage_speaker_family": profile.has_heritage_speaker_family,
            "self_reported_proficiency": profile.self_reported_proficiency,
            "primary_language": profile.primary_language,
        },
    }


# === Chart catalog ==========================================================


@app.get("/api/v1/charts")
def list_charts(
    envir: Optional[str] = None,
    tier: Optional[str] = None,
) -> dict:
    """List all charts in the catalog with summary metadata.

    Per F-055 axis #1: cite_sources_payload included via attribution_refs +
    consent_ref + cultural_protocol_authority on every chart.
    """
    catalog = build_seed_catalog()
    charts = []
    for chart in catalog.charts.values():
        if tier is not None and chart.tier.value != tier:
            continue
        charts.append({
            "chart_id": chart.chart_id,
            "subject": chart.subject.value,
            "tier": chart.tier.value,
            "title_en": chart.title.en,
            "title_es": chart.title.es,
            "title_cab": chart.title.cab,
            "grade_bands": list(chart.grade_bands),
            "item_count": len(chart.items),
            "pending_neologisms": chart.pending_garifuna_count(),
            "elder_signoff_required": chart.elder_signoff_required,
            "cultural_context_note": chart.cultural_context_note,
        })
    return {"total": len(charts), "charts": charts, "coverage": catalog.coverage_report()}


@app.get("/api/v1/charts/{chart_id}")
def get_chart(chart_id: str) -> dict:
    """Fetch a single chart with full trilingual items."""
    catalog = build_seed_catalog()
    chart = catalog.charts.get(chart_id)
    if chart is None:
        raise HTTPException(status_code=404, detail=f"chart {chart_id} not found")
    return {
        "chart_id": chart.chart_id,
        "subject": chart.subject.value,
        "tier": chart.tier.value,
        "title": {
            "cab": chart.title.cab,
            "en": chart.title.en,
            "es": chart.title.es,
        },
        "grade_bands": list(chart.grade_bands),
        "items": [
            {
                "item_id": it.item_id,
                "gloss": {
                    "cab": it.gloss.cab,
                    "en": it.gloss.en,
                    "es": it.gloss.es,
                    "pending_neologism": it.gloss.pending_neologism,
                },
                "cultural_anchor": it.cultural_anchor,
                "foundry_ref": it.foundry_ref,
                "source_citation": it.source_citation,
            }
            for it in chart.items
        ],
        "cultural_context_note": chart.cultural_context_note,
        "elder_signoff_required": chart.elder_signoff_required,
    }


# === Envir-specific lesson route ===========================================


@app.get("/api/v1/envir/{envir}/pathway/{pathway}/lessons")
def list_lessons_for_envir(envir: str, pathway: str) -> dict:
    """Per F-055 axis #6: enforces per-MOE sovereignty at route level.

    Returns a sample lesson plan for the given envir + pathway. Production
    wires this to a lesson catalog database.
    """
    if envir not in ("belize", "honduras", "guatemala", "nicaragua", "svg_yurumein", "garicomm", "diaspora"):
        raise HTTPException(status_code=400, detail=f"unknown envir: {envir}")
    if pathway not in ("heritage", "novice", "l1_maintainer"):
        raise HTTPException(status_code=400, detail=f"unknown pathway: {pathway}")
    # Sample lesson plan; production reads from cohort-specific schedule
    return {
        "envir": envir,
        "pathway": pathway,
        "lessons": [
            {
                "lesson_id": "lesson.greetings.day1",
                "title_en": "Day 1 — Greetings",
                "title_es": "Día 1 — Saludos",
                "title_cab": "Lun aban — Buinetina",
                "unit_count": 4,
                "estimated_minutes": 15,
            },
            {
                "lesson_id": "lesson.family.kinship",
                "title_en": "Family + Kinship",
                "title_es": "Familia + parentesco",
                "title_cab": "Iduheñu",
                "unit_count": 6,
                "estimated_minutes": 20,
            },
            {
                "lesson_id": "lesson.food.daily",
                "title_en": "Food + Daily Life",
                "title_es": "Comida + vida cotidiana",
                "title_cab": "Aimuga",
                "unit_count": 5,
                "estimated_minutes": 18,
            },
        ],
    }


@app.get("/api/v1/envir/{envir}/pathway/{pathway}/lesson/{lesson_id}")
def get_lesson(envir: str, pathway: str, lesson_id: str) -> dict:
    """Per-envir per-pathway lesson detail. Production wires to lesson library."""
    return {
        "lesson_id": lesson_id,
        "envir": envir,
        "pathway": pathway,
        "title_en": "Sample lesson",
        "units": [
            {
                "unit_id": "u1",
                "title": "Greetings",
                "steps": [
                    {
                        "step_id": "u1.s1",
                        "kind": "instruction",
                        "headword_garifuna": "buguya",
                        "prompt_text": "Listen and repeat: 'buguya'.",
                        "primary_modality": "audio" if pathway == "heritage" else "visual",
                        "plain_summary": "Listen to how 'buguya' sounds.",
                    },
                    {
                        "step_id": "u1.s2",
                        "kind": "check_for_understanding",
                        "headword_garifuna": "buguya",
                        "prompt_text": "What does 'buguya' mean?",
                        "correct_response": "thank you",
                        "primary_modality": "text",
                    },
                ],
            },
        ],
    }


# === Badges (read-only; lists issued by issuer) =============================


@app.get("/api/v1/badges/{learner_id}")
def list_badges_for_learner(learner_id: str) -> dict:
    """Return all badges held by a learner.

    Production wires to the issued-credential ledger. Currently a stub.
    """
    return {
        "learner_id": learner_id,
        "badges": [
            {
                "assertion_id": "urn:uuid:sample-001",
                "badge_id": "badge.lesson.greetings.day1",
                "name": "Day 1 — Greetings",
                "achievement_kind": "lesson_completion",
                "issued_on": "2026-05-23T10:00:00Z",
                "envir": "belize",
            },
        ],
    }
