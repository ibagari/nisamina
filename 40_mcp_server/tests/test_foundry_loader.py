"""Tests for nisamina_mcp.foundry_loader."""
from __future__ import annotations
import pytest

from nisamina_mcp.foundry_loader import FoundryIndex, load, FOUNDRY_PATH


def test_foundry_path_exists():
    assert FOUNDRY_PATH.exists(), f"foundry not at {FOUNDRY_PATH}"


def test_load_returns_index(foundry_index):
    assert isinstance(foundry_index, FoundryIndex)
    assert len(foundry_index) > 0


def test_public_release_filter(foundry_index):
    """Every loaded record must have public_release=True."""
    for r in foundry_index:
        assert r.get("public_release") is True


def test_expected_record_count(foundry_index):
    """V0.2 build manifest says 33,133 public-release records."""
    assert len(foundry_index) == 33133


def test_vault_attested_subset(foundry_index):
    """V_VAULT subset must match F-026 reconciliation (542 unique)."""
    vault = foundry_index.vault_attested()
    assert len(vault) == 542
    for r in vault:
        assert r.get("vault_attested") is True
        assert r.get("tier") == "5"


def test_exact_lookup_hit(foundry_index):
    out = foundry_index.lookup_exact("ababagüda")
    assert len(out) >= 1
    assert out[0]["headword_normalized"] == "ababagüda"


def test_exact_lookup_miss(foundry_index):
    assert foundry_index.lookup_exact("zzzqqqxxx_not_a_garifuna_word") == []


def test_exact_lookup_case_insensitive(foundry_index):
    a = foundry_index.lookup_exact("ababagüda")
    b = foundry_index.lookup_exact("ABABAGÜDA")
    assert len(a) == len(b)


def test_prefix_lookup_returns_results(foundry_index):
    out = foundry_index.lookup_prefix("maga", limit=10)
    assert len(out) >= 1
    for r in out:
        assert r["headword_normalized"].lower().startswith("maga")


def test_prefix_lookup_respects_limit(foundry_index):
    out = foundry_index.lookup_prefix("a", limit=5)
    assert len(out) <= 5


def test_fuzzy_lookup_finds_near_match(foundry_index):
    out = foundry_index.lookup_fuzzy("ababagda", limit=3, cutoff=0.7)
    # ababagüda is a close match
    assert any(r["headword_normalized"] == "ababagüda" for r in out)


def test_empty_query_returns_empty(foundry_index):
    assert foundry_index.lookup_exact("") == []
    assert foundry_index.lookup_prefix("") == []
    assert foundry_index.lookup_fuzzy("") == []


def test_load_from_missing_path_raises():
    with pytest.raises(FileNotFoundError):
        load("/nonexistent/path/to/foundry.jsonl")
