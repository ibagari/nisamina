"""Shared fixtures for the nisamina-mcp test suite."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

# Ensure the nisamina_mcp package is importable when running pytest from
# 40_mcp_server/ (where pyproject.toml lives) or from the repo root.
_HERE = Path(__file__).resolve().parent
_PKG_ROOT = _HERE.parent
sys.path.insert(0, str(_PKG_ROOT))

from nisamina_mcp.foundry_loader import load as _load  # noqa: E402


@pytest.fixture(scope="session")
def foundry_index():
    """Load the foundry once per test session (it's 33k records)."""
    return _load()


@pytest.fixture()
def good_record() -> dict:
    return {
        "headword": "magarada",
        "headword_normalized": "magarada",
        "sources": ["foundry_v5", "BSB", "Hadel_1975", "Suazo_Pildoritas"],
        "n_sources": 4,
        "tier": "A",
        "public_release": True,
        "vault_attested": False,
    }


@pytest.fixture()
def jw_leak_record() -> dict:
    return {
        "headword": "give",
        "headword_normalized": "give",
        "sources": ["foundry_v5", "watch_tower_2013"],
        "n_sources": 2,
        "tier": "B",
        "public_release": True,
        "jw_corroborated": True,
    }


@pytest.fixture()
def catatu_leak_record() -> dict:
    return {
        "headword": "babugu",
        "headword_normalized": "babugu",
        "sources": ["foundry_v5", "catatu_midwife_recording"],
        "n_sources": 2,
        "tier": "B",
        "public_release": True,
        "catatu_corroborated": True,
    }


@pytest.fixture()
def tier_c_record() -> dict:
    return {
        "headword": "amülei",
        "headword_normalized": "amülei",
        "sources": ["foundry_v5"],
        "n_sources": 1,
        "tier": "C",
        "public_release": True,
    }
