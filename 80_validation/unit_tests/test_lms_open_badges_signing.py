"""Tests for D-070 Ed25519 signing in open_badges.py.

PyNaCl is OPTIONAL — tests skip cleanly if not installed.
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.open_badges import (
    AchievementKind, CriteriaSpec, BadgeClass, IssuerProfile,
    RecipientIdentifier, BadgeIssuer, Ed25519Signer, verify_assertion,
)

# Skip the whole file if PyNaCl not installed
pytest.importorskip("nacl", reason="PyNaCl optional dep (per D-070)")


def _mk_issuer() -> IssuerProfile:
    return IssuerProfile(
        issuer_id="https://nisamina.ibagari.foundation",
        name="Ibagari Foundation",
        url="https://nisamina.ibagari.foundation",
    )


def _mk_lesson_badge() -> BadgeClass:
    return BadgeClass(
        badge_id="badge.lesson.greetings.day1",
        name="Day 1 — Greetings",
        description="Completed Day 1",
        achievement_kind=AchievementKind.LESSON_COMPLETION,
        criteria=CriteriaSpec(narrative="Completed all 4 units"),
        attribution_refs=("attr_055",),
        consent_ref="consent_011",
    )


def _mk_recipient() -> RecipientIdentifier:
    return RecipientIdentifier(
        identifier="learner_hash_abc",
        identifier_type="platform-id",
    )


def test_signer_generates_keypair():
    signer = Ed25519Signer.generate(
        verification_method_iri="did:example:nisamina#key-1",
    )
    pubkey = signer.public_key_b64()
    assert isinstance(pubkey, str)
    assert len(pubkey) > 30  # base64url-encoded 32 bytes


def test_signer_signs_and_verifies():
    signer = Ed25519Signer.generate(
        verification_method_iri="did:example:nisamina#key-1",
    )
    message = b"Hello, Garifuna learners!"
    sig_b64 = signer.sign_b64(message)
    pubkey = signer.public_key_b64()
    assert isinstance(sig_b64, str)
    # Verify via low-level: reconstruct via VerifyKey
    import base64
    from nacl.signing import VerifyKey
    vk = VerifyKey(base64.urlsafe_b64decode(pubkey + "==="))
    vk.verify(message, base64.urlsafe_b64decode(sig_b64 + "==="))


def test_badge_issuer_with_signer_produces_proof():
    signer = Ed25519Signer.generate(
        verification_method_iri="did:example:nisamina#key-1",
    )
    issuer = BadgeIssuer(_mk_issuer(), signer=signer)
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    jsonld = issuer.sign(assertion)
    assert "proof" in jsonld
    assert jsonld["proof"]["type"] == "DataIntegrityProof"
    assert jsonld["proof"]["cryptosuite"] == "eddsa-2022"
    assert "proofValue" in jsonld["proof"]


def test_unsigned_issuer_raises_on_sign():
    issuer = BadgeIssuer(_mk_issuer(), signer=None)
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    with pytest.raises(RuntimeError, match="no signer"):
        issuer.sign(assertion)


def test_verify_assertion_round_trip():
    signer = Ed25519Signer.generate(
        verification_method_iri="did:example:nisamina#key-1",
    )
    issuer = BadgeIssuer(_mk_issuer(), signer=signer)
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    jsonld_signed = issuer.sign(assertion)
    pubkey = signer.public_key_b64()
    assert verify_assertion(jsonld_signed, pubkey) is True


def test_verify_rejects_tampered_credential():
    signer = Ed25519Signer.generate(
        verification_method_iri="did:example:nisamina#key-1",
    )
    issuer = BadgeIssuer(_mk_issuer(), signer=signer)
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    jsonld_signed = issuer.sign(assertion)
    # Tamper with the envir field
    jsonld_signed["nisamina:envir"] = "honduras"
    pubkey = signer.public_key_b64()
    assert verify_assertion(jsonld_signed, pubkey) is False


def test_verify_rejects_missing_proof():
    pubkey = Ed25519Signer.generate(
        verification_method_iri="did:example:nisamina#key-1",
    ).public_key_b64()
    assert verify_assertion({"@context": ["x"]}, pubkey) is False


def test_signer_from_file(tmp_path):
    # Generate a key and save to file, then load
    import os
    from nacl.signing import SigningKey
    sk = SigningKey.generate()
    key_path = tmp_path / "test_signing_key.bin"
    key_path.write_bytes(bytes(sk))
    signer = Ed25519Signer.from_file(
        str(key_path),
        verification_method_iri="did:example:test#key-1",
    )
    sig = signer.sign_b64(b"test")
    assert isinstance(sig, str)


def test_signer_rejects_wrong_key_length(tmp_path):
    bad_key_path = tmp_path / "bad_key.bin"
    bad_key_path.write_bytes(b"too short")
    with pytest.raises(ValueError, match="32 bytes"):
        Ed25519Signer.from_file(str(bad_key_path), verification_method_iri="did:example:x")
