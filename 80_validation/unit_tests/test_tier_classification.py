"""Unit tests for tier classification + public_release derivation logic.

The canonical tier rule (plan v1.1 §1.6, strict V_VAULT per F-017):
    - Tier 5: vault_attested == True (explicit per-row Sentences_VERIFIED 01.ods attestation)
    - Tier A: n_sources >= 4 (after JW/Magarada/Catatu stripping)
    - Tier B: n_sources >= 2
    - Tier C: n_sources == 1
    - Tier X: n_sources == 0 (all sources stripped) OR non_conformant
    - public_release = (tier in {5, A, B}) AND is_conformant AND n_sources >= 2

This file's classify() helper mirrors the build script's logic for unit-testing.
"""
import sys
from pathlib import Path
import pytest

# We define a local classify() to test the rule itself, decoupled from the build
# script's I/O. The build script must import + use this same logic.

APP = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(APP / "20_normalize"))
from cayetano_1992 import is_conformant


def classify(headword_normalized: str, sources: set, vault_attested: bool) -> tuple[str, bool, bool]:
    """Returns (tier, public_release, non_conformant).

    Mirrors build_foundry_v6.py's classification logic exactly.
    """
    n = len(sources)
    is_conf, _ = is_conformant(headword_normalized)
    non_conf = not is_conf

    if non_conf:
        tier = "X"
    elif vault_attested:
        tier = "5"
    elif n >= 4:
        tier = "A"
    elif n >= 2:
        tier = "B"
    elif n >= 1:
        tier = "C"
    else:
        tier = "X"

    public_release = (tier in ("5", "A", "B")) and is_conf and (n >= 2 or tier == "5")
    return tier, public_release, non_conf


class TestTier:
    def test_tier_5_requires_vault_AND_conformance(self):
        # Conformant + vault attested → Tier-5
        t, _, _ = classify("magarada", {"V_VAULT", "foundry_v5"}, vault_attested=True)
        assert t == "5"

    def test_tier_5_blocked_if_non_conformant(self):
        # Even with vault attestation, English/Spanish loan → Tier-X
        t, pub, nc = classify("give", {"V_VAULT", "lgd_living_dictionary"}, vault_attested=True)
        assert t == "X"
        assert pub is False
        assert nc is True

    def test_tier_A_4_plus_sources(self):
        t, pub, _ = classify("aayé", {"a", "b", "c", "d"}, vault_attested=False)
        assert t == "A"
        assert pub is True

    def test_tier_B_2_or_3_sources(self):
        t, pub, _ = classify("aban", {"a", "b"}, vault_attested=False)
        assert t == "B"
        assert pub is True

        t, pub, _ = classify("aban", {"a", "b", "c"}, vault_attested=False)
        assert t == "B"

    def test_tier_C_single_source(self):
        t, pub, _ = classify("aban", {"only_source"}, vault_attested=False)
        assert t == "C"
        assert pub is False  # Tier-C must triangulate first

    def test_tier_X_zero_sources(self):
        t, pub, _ = classify("aban", set(), vault_attested=False)
        assert t == "X"
        assert pub is False

    def test_tier_X_non_conformant(self):
        # Headword is "give" (English); even with many sources, must be Tier-X
        t, pub, nc = classify("give", {"a", "b", "c", "d", "e"}, vault_attested=False)
        assert t == "X"
        assert pub is False
        assert nc is True

    @pytest.mark.parametrize("headword,sources,vault,expected_tier,expected_public", [
        ("magarada", {"foundry_v5"}, False, "C", False),
        ("magarada", {"foundry_v5", "BSB"}, False, "B", True),
        ("magarada", {"foundry_v5", "BSB", "Hadel_1975"}, False, "B", True),
        ("magarada", {"foundry_v5", "BSB", "Hadel_1975", "Suazo"}, False, "A", True),
        ("magarada", {"foundry_v5", "V_VAULT"}, True, "5", True),
        ("give", {"foundry_v5", "BSB", "Hadel_1975", "Suazo"}, False, "X", False),
        ("vagina", {"foundry_v5", "BSB", "Hadel_1975", "Suazo"}, False, "X", False),
        ("dán (time; weather)", {"a", "b", "c"}, True, "X", False),  # extraction artifact
    ])
    def test_classification_truth_table(self, headword, sources, vault, expected_tier, expected_public):
        t, pub, _ = classify(headword, sources, vault)
        assert t == expected_tier, f"{headword!r} sources={len(sources)} vault={vault} → tier={t} expected={expected_tier}"
        assert pub == expected_public, f"{headword!r} → public_release={pub} expected={expected_public}"


class TestPublicReleaseDerivation:
    def test_public_release_requires_conformance(self):
        _, pub, _ = classify("give", {"foundry_v5", "BSB", "Hadel_1975", "Suazo"}, False)
        assert pub is False

    def test_public_release_requires_min_triangulation(self):
        # Single-source: public_release False even if conformant
        _, pub, _ = classify("magarada", {"foundry_v5"}, False)
        assert pub is False

    def test_public_release_for_tier_5_with_one_source_OK(self):
        # Tier-5 (V_VAULT) is supreme: a single V_VAULT source can grant public_release
        # because director-attestation is the highest evidence tier.
        _, pub, _ = classify("aayé", {"V_VAULT"}, True)
        assert pub is True
