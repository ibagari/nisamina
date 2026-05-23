"""Tests for M-P3.LMS.MULTIMODAL — Video + Oral-history + Image with consent."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.multimodal import (
    AssetKind, ConsentScope, MultimodalAsset, AssetCatalog, make_asset,
)


def _mk_asset(envir: str = "belize") -> MultimodalAsset:
    return make_asset(
        asset_id="oh.dugu_elder_2026.001",
        kind=AssetKind.ORAL_HISTORY,
        title_en="Dügü ceremony — elder recollection",
        title_es="Ceremonia Dügü — recuerdo de un anciano",
        consent_id="consent_011",
        attribution_id="attr_055",
        consent_scope=ConsentScope.SACRED_ELDER_GATED,
        envir=envir,
        duration_seconds=420.5,
        cultural_anchors=("dugu_ceremony", "ancestor_veneration"),
        dialect_tag="cab_BLZ",
    )


def test_make_asset_requires_consent_id():
    with pytest.raises(ValueError, match="consent_id is required"):
        make_asset(
            asset_id="x", kind=AssetKind.IMAGE,
            title_en="t", title_es="t",
            consent_id="",  # missing
            attribution_id="attr_001",
            consent_scope=ConsentScope.INTERNAL_PEDAGOGY,
            envir="belize",
        )


def test_make_asset_requires_attribution_id():
    with pytest.raises(ValueError, match="attribution_id is required"):
        make_asset(
            asset_id="x", kind=AssetKind.IMAGE,
            title_en="t", title_es="t",
            consent_id="consent_011",
            attribution_id="",
            consent_scope=ConsentScope.INTERNAL_PEDAGOGY,
            envir="belize",
        )


def test_sacred_scope_sets_elder_signoff_required():
    asset = _mk_asset()
    assert asset.consent_scope == ConsentScope.SACRED_ELDER_GATED
    assert asset.elder_signoff_required is True


def test_catalog_enforces_envir():
    catalog = AssetCatalog(envir="belize")
    asset = _mk_asset(envir="belize")
    catalog.add(asset)
    assert len(catalog.assets) == 1


def test_catalog_rejects_foreign_envir():
    catalog = AssetCatalog(envir="belize")
    asset = _mk_asset(envir="honduras")
    with pytest.raises(ValueError, match="envir mismatch"):
        catalog.add(asset)


def test_catalog_rejects_duplicate_id():
    catalog = AssetCatalog(envir="belize")
    catalog.add(_mk_asset())
    with pytest.raises(ValueError, match="duplicate"):
        catalog.add(_mk_asset())


def test_list_kind_filters():
    catalog = AssetCatalog(envir="belize")
    catalog.add(_mk_asset())
    catalog.add(make_asset(
        asset_id="img.dugu_mask.001", kind=AssetKind.IMAGE,
        title_en="Dügü mask", title_es="Máscara Dügü",
        consent_id="consent_011", attribution_id="attr_055",
        consent_scope=ConsentScope.INTERNAL_PEDAGOGY, envir="belize",
    ))
    assert len(catalog.list_kind(AssetKind.ORAL_HISTORY)) == 1
    assert len(catalog.list_kind(AssetKind.IMAGE)) == 1
    assert len(catalog.list_kind(AssetKind.VIDEO)) == 0


def test_sacred_gated_filter():
    catalog = AssetCatalog(envir="belize")
    catalog.add(_mk_asset())
    sacred = catalog.sacred_gated()
    assert len(sacred) == 1
    assert sacred[0].consent_scope == ConsentScope.SACRED_ELDER_GATED


def test_play_event_payload_contains_attribution_chain():
    catalog = AssetCatalog(envir="belize")
    asset = _mk_asset()
    catalog.add(asset)
    payload = catalog.play_event_payload(asset.asset_id)
    assert payload["consent_ref"] == "consent_011"
    assert payload["attribution_ref"] == "attr_055"
    assert payload["envir"] == "belize"
    assert payload["scope"] == "sacred_elder_gated"
    assert payload["elder_signoff_required"] is True


def test_play_event_payload_unknown_id_raises():
    catalog = AssetCatalog(envir="belize")
    with pytest.raises(KeyError):
        catalog.play_event_payload("nonexistent")
