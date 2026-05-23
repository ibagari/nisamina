"""Unit tests for 99_publish/strip_linter.py — the pre-publish artifact gate."""
import pytest
from strip_linter import lint_record, lint_artifact, block_if_violations, StripLinterError, Violation


def make_record(**overrides):
    base = {
        "headword": "magarada",
        "headword_normalized": "magarada",
        "sources": ["foundry_v5", "BSB", "Hadel_1975", "Suazo_Pildoritas"],
        "n_sources": 4,
        "tier": "A",
        "public_release": True,
        "vault_attested": False,
        "bsb_attested": True,
    }
    base.update(overrides)
    return base


class TestLintRule:
    def test_clean_record_passes(self):
        v = lint_record(make_record())
        assert v == []

    def test_jw_field_blocked(self):
        v = lint_record(make_record(jw_corroborated=True))
        assert any(viol.rule == "jw_field_present" for viol in v)

    def test_catatu_field_blocked(self):
        v = lint_record(make_record(catatu_corroborated=True))
        assert any(viol.rule == "catatu_field_present" for viol in v)

    def test_magarada_unverified_blocked(self):
        v = lint_record(make_record(magarada_unverified=True))
        assert any(viol.rule == "magarada_unverified_true" for viol in v)

    def test_tier_C_blocked(self):
        v = lint_record(make_record(tier="C", n_sources=1, sources=["foundry_v5"]))
        assert any(viol.rule == "tier_C_in_public" for viol in v)

    def test_tier_X_blocked(self):
        v = lint_record(make_record(tier="X", n_sources=0, sources=[], public_release=False))
        assert any(viol.rule == "tier_X_in_public" for viol in v)

    def test_public_release_false_blocked(self):
        v = lint_record(make_record(public_release=False))
        assert any(viol.rule == "public_release_false" for viol in v)

    def test_jw_source_in_attribution_blocked(self):
        v = lint_record(make_record(sources=["foundry_v5", "watch_tower_2013"]))
        assert any(viol.rule == "jw_source_in_public_attribution" for viol in v)

    def test_magarada_source_in_attribution_blocked(self):
        v = lint_record(make_record(sources=["foundry_v5", "magarada_stories"]))
        assert any(viol.rule == "magarada_source_in_public_attribution" for viol in v)

    def test_catatu_source_in_attribution_blocked(self):
        v = lint_record(make_record(sources=["foundry_v5", "catatu_midwife_5890"]))
        assert any(viol.rule == "catatu_source_in_public_attribution" for viol in v)

    def test_non_cayetano_conformant_blocked(self):
        v = lint_record(make_record(headword="give", headword_normalized="give"))
        assert any(viol.rule == "non_cayetano_conformant" for viol in v)

    def test_missing_required_fields_blocked(self):
        v = lint_record({"headword": "magarada"})
        assert any(viol.rule == "missing_required_fields" for viol in v)

    def test_magarada_songs_allowed(self):
        """Songs are consent_001 granted; not blocked at strip stage."""
        v = lint_record(make_record(sources=["foundry_v5", "Magarada_Garifuna_Songs_text_Images"]))
        # Songs may still trigger the substring match in is_magarada — verify the SONGS_ALLOWLIST in
        # magarada_preliminary_gate.py handles this. If linter still flags, document why.
        # Currently expected: songs do NOT trigger the gate.
        assert not any(viol.rule == "magarada_source_in_public_attribution" for viol in v)


class TestLintArtifact:
    def test_clean_artifact_returns_clean_true(self):
        r = lint_artifact([make_record(), make_record(headword="aban", headword_normalized="aban")])
        assert r["clean"] is True
        assert r["violations_total"] == 0

    def test_violations_aggregated_by_rule(self):
        r = lint_artifact([
            make_record(jw_corroborated=True),
            make_record(tier="C", n_sources=1, sources=["foundry_v5"]),
            make_record(headword="give", headword_normalized="give"),
        ])
        assert r["clean"] is False
        assert "jw_field_present" in r["violations_by_rule"]
        assert "tier_C_in_public" in r["violations_by_rule"]
        assert "non_cayetano_conformant" in r["violations_by_rule"]


class TestBlockIfViolations:
    def test_clean_passes_silently(self):
        block_if_violations([make_record()])  # should not raise

    def test_violation_raises(self):
        with pytest.raises(StripLinterError):
            block_if_violations([make_record(jw_corroborated=True)])
