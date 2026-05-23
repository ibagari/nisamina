"""Tests for M-P3.LMS.TUTOR_VERIFIER — non-LLM deterministic verifier agent."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.tutor_verifier import (
    VerifierStatus, VerifierIssue, VerifierResult,
    OrthographyVerifier, FoundryExistenceVerifier, DialectTagVerifier, CompositeVerifier,
)


# === Orthography verifier ===


def test_orthography_accepts_valid_ngc_token():
    v = OrthographyVerifier()
    result = v.verify(
        candidate_text="The Garifuna word for thank you is buguya.",
        context={"cab_tokens": ["buguya"]},
    )
    assert result.passed
    assert result.issues == ()


def test_orthography_flags_c_in_garifuna_token():
    """NGC orthography forbids c/k/q/v/x/z."""
    v = OrthographyVerifier()
    result = v.verify(
        candidate_text="Word: cariba.",
        context={"cab_tokens": ["cariba"]},
    )
    assert result.status == VerifierStatus.FAIL
    assert any("not in NGC orthography" in i.rationale for i in result.issues)


def test_orthography_accepts_u_with_diaeresis():
    v = OrthographyVerifier()
    result = v.verify(
        candidate_text="agüriahati — the one who nurtures",
        context={"cab_tokens": ["agüriahati"]},
    )
    assert result.passed


def test_orthography_ignores_non_cab_text():
    """The verifier only checks tokens flagged as Garifuna."""
    v = OrthographyVerifier()
    # English text containing c/k/v — but no cab_tokens supplied
    result = v.verify(
        candidate_text="The English word 'covenant' has c and v.",
        context={"cab_tokens": []},
    )
    assert result.passed


# === Foundry existence verifier ===


def test_foundry_existence_passes_known_headwords():
    v = FoundryExistenceVerifier(known_headwords={"buguya", "nuani", "ereba"})
    result = v.verify(
        candidate_text="buguya nuani",
        context={"cab_tokens": ["buguya", "nuani"]},
    )
    assert result.passed


def test_foundry_existence_rejects_hallucinated_headwords():
    """The brain MUST NOT invent Garifuna terms."""
    v = FoundryExistenceVerifier(known_headwords={"buguya", "nuani"})
    result = v.verify(
        candidate_text="invented_term",
        context={"cab_tokens": ["invented_term"]},
    )
    assert result.status == VerifierStatus.FAIL
    assert "neologism_queue" in result.issues[0].rationale


def test_foundry_existence_case_insensitive():
    v = FoundryExistenceVerifier(known_headwords={"buguya"})
    result = v.verify(
        candidate_text="Buguya",
        context={"cab_tokens": ["Buguya"]},
    )
    assert result.passed


# === Dialect tag verifier ===


def test_dialect_tag_passes_when_matching_envir():
    v = DialectTagVerifier(headword_to_dialect={"buguya": "cab_BLZ"})
    result = v.verify(
        candidate_text="buguya",
        context={"cab_tokens": ["buguya"], "learner_envir": "belize"},
    )
    assert result.passed


def test_dialect_tag_warns_on_envir_mismatch():
    """Belize learner getting a Honduras-specific variant → warning."""
    v = DialectTagVerifier(headword_to_dialect={"hnd_specific": "cab_HND"})
    result = v.verify(
        candidate_text="hnd_specific",
        context={"cab_tokens": ["hnd_specific"], "learner_envir": "belize"},
    )
    assert result.status == VerifierStatus.WARNING


def test_dialect_tag_garicomm_envir_accepts_any():
    """GariComm envir is canonical pan-Garifuna; any dialect OK."""
    v = DialectTagVerifier(headword_to_dialect={"buguya": "cab_BLZ"})
    result = v.verify(
        candidate_text="buguya",
        context={"cab_tokens": ["buguya"], "learner_envir": "garicomm"},
    )
    assert result.passed


def test_dialect_tag_skips_unknown_tokens():
    """Tokens not in headword_to_dialect map are passed through silently."""
    v = DialectTagVerifier(headword_to_dialect={})
    result = v.verify(
        candidate_text="unknown_token",
        context={"cab_tokens": ["unknown_token"], "learner_envir": "belize"},
    )
    assert result.passed


# === Composite verifier ===


def test_composite_fail_when_any_child_fails():
    foundry = FoundryExistenceVerifier(known_headwords={"buguya"})
    ortho = OrthographyVerifier()
    composite = CompositeVerifier([foundry, ortho])
    # Foundry will fail; orthography will pass
    result = composite.verify(
        candidate_text="invented_term",
        context={"cab_tokens": ["invented_term"]},
    )
    assert result.status == VerifierStatus.FAIL


def test_composite_warning_when_only_warnings():
    dialect = DialectTagVerifier(headword_to_dialect={"hnd_specific": "cab_HND"})
    foundry = FoundryExistenceVerifier(known_headwords={"hnd_specific"})
    composite = CompositeVerifier([foundry, dialect])
    # Foundry passes; dialect warns (Belize learner getting HND variant)
    result = composite.verify(
        candidate_text="hnd_specific",
        context={"cab_tokens": ["hnd_specific"], "learner_envir": "belize"},
    )
    assert result.status == VerifierStatus.WARNING


def test_composite_passes_when_all_children_pass():
    ortho = OrthographyVerifier()
    foundry = FoundryExistenceVerifier(known_headwords={"buguya"})
    dialect = DialectTagVerifier(headword_to_dialect={"buguya": "cab_BLZ"})
    composite = CompositeVerifier([ortho, foundry, dialect])
    result = composite.verify(
        candidate_text="buguya",
        context={"cab_tokens": ["buguya"], "learner_envir": "belize"},
    )
    assert result.passed
