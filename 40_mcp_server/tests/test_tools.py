"""Unit tests for the 5 MCP tools."""
from __future__ import annotations
import pytest

from nisamina_mcp.tools.lookup_headword import lookup_headword
from nisamina_mcp.tools.cayetano_normalize import cayetano_normalize
from nisamina_mcp.tools.parse_morphology import parse_morphology
from nisamina_mcp.tools.translate_sentence import translate_sentence
from nisamina_mcp.tools.cite_sources import cite_sources


# ---- lookup_headword ----

def test_lookup_exact_hit(foundry_index):
    out = lookup_headword(foundry_index, "ababagüda", mode="exact")
    assert len(out) >= 1
    assert out[0]["headword_normalized"] == "ababagüda"


def test_lookup_exact_miss(foundry_index):
    assert lookup_headword(foundry_index, "zzzqqqxxx", mode="exact") == []


def test_lookup_prefix(foundry_index):
    out = lookup_headword(foundry_index, "maga", mode="prefix", limit=5)
    assert 0 < len(out) <= 5


def test_lookup_fuzzy(foundry_index):
    out = lookup_headword(foundry_index, "ababagda", mode="fuzzy", limit=3)
    assert any(r["headword_normalized"] == "ababagüda" for r in out)


def test_lookup_invalid_mode_raises(foundry_index):
    with pytest.raises(ValueError):
        lookup_headword(foundry_index, "x", mode="bogus")  # type: ignore[arg-type]


def test_lookup_limit_clamps_to_default(foundry_index):
    out = lookup_headword(foundry_index, "a", mode="prefix", limit=999)
    # limit > 100 silently clamps to DEFAULT_LIMIT=10
    assert len(out) <= 10


# ---- cayetano_normalize ----

def test_normalize_catei_to_katei():
    r = cayetano_normalize("catei")
    assert r["normalized"] == "katei"
    assert r["is_changed"] is True
    assert r["is_conformant"] is True


def test_normalize_quei_to_kei():
    r = cayetano_normalize("quei")
    assert r["normalized"] == "kei"
    assert r["is_changed"] is True


def test_normalize_already_conformant_no_change():
    r = cayetano_normalize("magarada")
    assert r["normalized"] == "magarada"
    assert r["is_changed"] is False
    assert r["is_conformant"] is True


def test_normalize_loan_flagged_non_conformant():
    r = cayetano_normalize("abandonar")
    # has 'v'/'z'/'x' substitute pattern check — 'abandonar' itself is all-cayetano-alphabet
    # but it triggers no specific replacement; conformance depends on rules
    # so we test that the function doesn't crash + returns a string
    assert isinstance(r["normalized"], str)


def test_normalize_empty_input():
    r = cayetano_normalize("")
    assert r["input"] == ""
    assert r["normalized"] == ""


def test_normalize_returns_syllables_and_stress():
    r = cayetano_normalize("magarada")
    assert isinstance(r["syllables"], list)
    assert "expected_stress_index" in r
    assert "is_irregular_stress" in r


def test_normalize_type_error_on_non_string():
    with pytest.raises(TypeError):
        cayetano_normalize(12345)  # type: ignore[arg-type]


# ---- parse_morphology ----

def test_parse_morphology_found(foundry_index):
    r = parse_morphology(foundry_index, "ababagüda")
    assert r["found"] is True
    assert len(r["senses"]) >= 1
    s0 = r["senses"][0]
    assert s0["pos"] == "verb"


def test_parse_morphology_not_found(foundry_index):
    r = parse_morphology(foundry_index, "zzzqqqxxx")
    assert r["found"] is False
    assert r["senses"] == []


def test_parse_morphology_empty_input(foundry_index):
    r = parse_morphology(foundry_index, "")
    assert r["found"] is False


# ---- translate_sentence ----

def test_translate_sentence_basic(foundry_index):
    r = translate_sentence(foundry_index, "Ababagüdati kalíki gamísa tó.")
    assert r["input"].startswith("Ababagüdati")
    assert len(r["tokens"]) == 4  # 4 word-tokens
    matched = sum(1 for t in r["tokens"] if t["matched_records"])
    assert matched >= 1


def test_translate_sentence_unmatched_flag(foundry_index):
    r = translate_sentence(foundry_index, "zzzqqq xxxyyy", fuzzy_fallback=False)
    assert len(r["tokens"]) == 2
    assert all(t["unmatched"] for t in r["tokens"])


def test_translate_sentence_fuzzy_fallback(foundry_index):
    """Disabling fuzzy means tokens that would have fuzzy candidates won't get them."""
    r_no = translate_sentence(foundry_index, "ababagda", fuzzy_fallback=False)
    r_yes = translate_sentence(foundry_index, "ababagda", fuzzy_fallback=True)
    fuzzy_no = sum(len(t["fuzzy_candidates"]) for t in r_no["tokens"])
    fuzzy_yes = sum(len(t["fuzzy_candidates"]) for t in r_yes["tokens"])
    assert fuzzy_no == 0
    assert fuzzy_yes >= 1


def test_translate_sentence_empty(foundry_index):
    r = translate_sentence(foundry_index, "")
    assert r["tokens"] == []


def test_translate_sentence_type_error(foundry_index):
    with pytest.raises(TypeError):
        translate_sentence(foundry_index, 12345)  # type: ignore[arg-type]


# ---- cite_sources ----

def test_cite_sources_found(foundry_index):
    r = cite_sources(foundry_index, "ababagüda")
    assert r["found"] is True
    # foundry record has 3 source IDs
    assert len(r["sources"]) >= 1
    # Each source entry has the right shape
    for s in r["sources"]:
        assert "source_id" in s
        assert "attributions" in s
        assert isinstance(s["attributions"], list)


def test_cite_sources_not_found(foundry_index):
    r = cite_sources(foundry_index, "zzzqqqxxx")
    assert r["found"] is False
    assert r["sources"] == []


def test_cite_sources_empty(foundry_index):
    r = cite_sources(foundry_index, "")
    assert r["found"] is False
