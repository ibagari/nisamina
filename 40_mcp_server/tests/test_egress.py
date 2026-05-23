"""Tests for nisamina_mcp.egress — the strip-linter response wrapper."""
from __future__ import annotations
import pytest

from nisamina_mcp.egress import (
    enforce_egress, StripLinterError, _coerce_to_records, _looks_like_foundry_record,
)


def test_good_record_passes(good_record):
    out = enforce_egress(good_record, context="t-good")
    assert out is good_record  # unchanged identity


def test_good_record_list_passes(good_record):
    out = enforce_egress([good_record, good_record], context="t-good-list")
    assert len(out) == 2


def test_jw_field_blocks(jw_leak_record):
    with pytest.raises(StripLinterError) as ei:
        enforce_egress(jw_leak_record, context="t-jw")
    assert "jw" in str(ei.value).lower()
    assert "t-jw" in str(ei.value)


def test_catatu_field_blocks(catatu_leak_record):
    with pytest.raises(StripLinterError):
        enforce_egress(catatu_leak_record, context="t-catatu")


def test_tier_c_blocks(tier_c_record):
    with pytest.raises(StripLinterError) as ei:
        enforce_egress(tier_c_record, context="t-tier-c")
    assert "tier_c" in str(ei.value).lower() or "tier-c" in str(ei.value).lower()


def test_mixed_list_blocks_on_first_violation(good_record, jw_leak_record):
    with pytest.raises(StripLinterError):
        enforce_egress([good_record, jw_leak_record], context="t-mixed")


def test_nested_leak_blocked(jw_leak_record):
    """A jw record nested inside a synthesized report must still be caught."""
    composed = {"tokens": [{"token": "give", "matched_records": [jw_leak_record]}]}
    with pytest.raises(StripLinterError):
        enforce_egress(composed, context="t-nested")


def test_deeply_nested_leak_blocked(jw_leak_record):
    composed = {"a": {"b": {"c": [{"d": jw_leak_record}]}}}
    with pytest.raises(StripLinterError):
        enforce_egress(composed, context="t-deep")


def test_synthesized_report_does_not_false_positive():
    """A cayetano_normalize-shape dict has no `headword`/`tier`/`public_release`
    combo so the linter should NOT fire on it."""
    report = {"input": "catei", "normalized": "katei", "is_changed": True,
              "changes": [], "is_conformant": True, "conformance_reasons": [],
              "syllables": ["ka", "tei"], "expected_stress_index": 0,
              "actual_stress_index": None, "is_irregular_stress": False}
    out = enforce_egress(report, context="t-synth")
    assert out["normalized"] == "katei"


def test_cite_sources_shape_does_not_false_positive():
    """cite_sources's response has `headword` + `sources` (list of dicts) but
    no `tier` / `public_release` so it must NOT be linted as a foundry record."""
    report = {"headword": "x", "normalized": "x", "found": True, "sources": [
        {"source_id": "src_a", "attributions": [{"id": "attr_001"}]},
    ]}
    out = enforce_egress(report, context="t-cite-shape")
    assert out["headword"] == "x"


def test_none_payload_passes():
    assert enforce_egress(None, context="t-none") is None


def test_empty_list_passes():
    assert enforce_egress([], context="t-empty") == []


def test_string_payload_passes():
    """Bare strings (e.g., from a prompt) have nothing to lint."""
    assert enforce_egress("a plain string", context="t-str") == "a plain string"


def test_looks_like_foundry_record_positive(good_record):
    assert _looks_like_foundry_record(good_record)


def test_looks_like_foundry_record_negative_synthesized():
    assert not _looks_like_foundry_record({"input": "x", "normalized": "x"})
    assert not _looks_like_foundry_record({"headword": "x", "sources": [{"a": 1}]})  # cite_sources shape
    assert not _looks_like_foundry_record({"headword": "x", "tier": "A"})  # missing public_release


def test_coerce_extracts_only_foundry_shaped(good_record, jw_leak_record):
    nested = {"reports": [{"normalized": "y"}, {"matched": [good_record, jw_leak_record]}]}
    extracted = _coerce_to_records(nested)
    assert good_record in extracted
    assert jw_leak_record in extracted
    assert len(extracted) == 2  # synthesized reports were NOT counted


def test_context_appears_in_error_message(jw_leak_record):
    with pytest.raises(StripLinterError) as ei:
        enforce_egress(jw_leak_record, context="my-unique-context-42")
    assert "my-unique-context-42" in str(ei.value)
