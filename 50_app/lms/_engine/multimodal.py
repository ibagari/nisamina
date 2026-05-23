"""M-P3.LMS.MULTIMODAL — Video + Oral-history + Image with consent surfacing.

Per F-059 D-MAX-6 + UNESCO Feb 2025 + UNESCO Dec 2025 Chile vitality study +
F-031 Commission elder-mentor recordings + F-055 axis #1 sovereign presentation.

Every multimodal asset MUST carry:
- consent_id    — pointer to 00_governance/consent_registry.jsonl
- attribution_id — pointer to 00_governance/attribution_register.jsonl

The cite_sources MCP tool surfaces these at every play / view / read event
(per F-058 attribution-chain invariant + per Labayayahoun Ibagari principle:
"matter belongs to the people; presentation belongs to Nisamina").

Scaffolded; concrete storage layer (S3 / Cloudflare R2 / HF Hub) lands in
M-P3.LMS.MULTIMODAL.STORAGE sub-manifest (depends on PL-D legal counsel
sign-off for per-asset license review per F-074 PHASE-LATER).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class AssetKind(str, Enum):
    VIDEO = "video"
    ORAL_HISTORY = "oral_history"        # e.g., elder-mentor recording per F-031
    IMAGE = "image"                       # e.g., textbook diagrams (F-040 substrate) or diaspora archive
    AUDIO = "audio"                       # supplementary; main TTS goes via tts_garifuna.py
    DOCUMENT = "document"                 # supplementary; main lesson_player handles text


class ConsentScope(str, Enum):
    """Per-asset scope per Labayayahoun Ibagari stewardship principle."""
    INTERNAL_PEDAGOGY = "internal_pedagogy"
    LMS_ENVIR_RESTRICTED = "lms_envir_restricted"
    CHATBOT_HERITAGE_MODE = "chatbot_heritage_mode"
    PUBLIC_REPUBLICATION = "public_republication"      # requires verbatim-publication license review
    SACRED_ELDER_GATED = "sacred_elder_gated"          # restricted; routes via M-P3.LMS.ELDER_LOOP


@dataclass(frozen=True)
class MultimodalAsset:
    """A single multimodal asset bundled with consent + attribution.

    Construction REQUIRES consent_id and attribution_id; raises ValueError
    if either is missing. This is the engine-level enforcement of the
    sovereign-presentation invariant.
    """
    asset_id: str                # e.g., "video.dugu_movement.elder_2026_05.001"
    kind: AssetKind
    title_en: str
    title_es: str
    title_cab: Optional[str]     # may be None if Garifuna title queued via neologism_queue
    consent_id: str              # required — points to consent_registry.jsonl
    attribution_id: str          # required — points to attribution_register.jsonl
    consent_scope: ConsentScope
    envir: str                   # belize | honduras | ... | stem_alternative | garicomm
    duration_seconds: Optional[float] = None  # for time-based media
    width_px: Optional[int] = None             # for image/video
    height_px: Optional[int] = None
    storage_path: Optional[str] = None         # opaque — resolved by storage backend
    cultural_anchors: tuple[str, ...] = ()
    dialect_tag: Optional[str] = None
    elder_signoff_required: bool = False        # True for ICH / sacred / ceremony content


def make_asset(
    asset_id: str,
    kind: AssetKind,
    title_en: str,
    title_es: str,
    consent_id: str,
    attribution_id: str,
    consent_scope: ConsentScope,
    envir: str,
    **kwargs,
) -> MultimodalAsset:
    """Constructor that enforces consent_id + attribution_id are non-empty.

    Use this instead of MultimodalAsset(...) directly — it surfaces missing
    governance refs as a clear error rather than letting silent missing values
    propagate.
    """
    if not consent_id:
        raise ValueError(
            f"asset {asset_id}: consent_id is required; refer to 00_governance/consent_registry.jsonl"
        )
    if not attribution_id:
        raise ValueError(
            f"asset {asset_id}: attribution_id is required; refer to 00_governance/attribution_register.jsonl"
        )
    if consent_scope == ConsentScope.SACRED_ELDER_GATED:
        kwargs.setdefault("elder_signoff_required", True)
    return MultimodalAsset(
        asset_id=asset_id,
        kind=kind,
        title_en=title_en,
        title_es=title_es,
        consent_id=consent_id,
        attribution_id=attribution_id,
        consent_scope=consent_scope,
        envir=envir,
        title_cab=kwargs.pop("title_cab", None),
        **kwargs,
    )


@dataclass
class AssetCatalog:
    """Per-envir asset catalog. Enforces envir isolation per F-055 axis #6.

    A catalog only holds assets matching its envir; cross-envir composition
    happens at orchestrator level via explicit cross-envir overlay (e.g.,
    garicomm canonical layer cross-references country envirs).
    """
    envir: str
    assets: dict[str, MultimodalAsset] = field(default_factory=dict)

    def add(self, asset: MultimodalAsset) -> None:
        if asset.envir != self.envir:
            raise ValueError(
                f"envir mismatch: catalog={self.envir}, asset.envir={asset.envir}"
            )
        if asset.asset_id in self.assets:
            raise ValueError(f"duplicate asset_id: {asset.asset_id}")
        self.assets[asset.asset_id] = asset

    def list_kind(self, kind: AssetKind) -> list[MultimodalAsset]:
        return [a for a in self.assets.values() if a.kind == kind]

    def sacred_gated(self) -> list[MultimodalAsset]:
        return [a for a in self.assets.values() if a.consent_scope == ConsentScope.SACRED_ELDER_GATED]

    def play_event_payload(self, asset_id: str) -> dict:
        """Returns the cite_sources-compatible payload for an asset play event.

        The chatbot orchestrator emits this on each play; Caliper event captures
        it as the object payload + attribution chain.
        """
        asset = self.assets.get(asset_id)
        if asset is None:
            raise KeyError(f"unknown asset_id: {asset_id}")
        return {
            "asset_id": asset.asset_id,
            "kind": asset.kind.value,
            "title": {"en": asset.title_en, "es": asset.title_es, "cab": asset.title_cab},
            "consent_ref": asset.consent_id,
            "attribution_ref": asset.attribution_id,
            "envir": asset.envir,
            "scope": asset.consent_scope.value,
            "elder_signoff_required": asset.elder_signoff_required,
        }
