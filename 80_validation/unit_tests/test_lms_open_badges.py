"""Tests for M-P3.LMS.OPEN_BADGES — Open Badges 3.0 JSON-LD emitter."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "50_app"))
from lms._engine.open_badges import (
    AchievementKind, CriteriaSpec, BadgeClass, IssuerProfile,
    RecipientIdentifier, AssertionCredential, BadgeIssuer, assertion_to_jsonld,
    OPEN_BADGES_3_CONTEXT,
)


def _mk_issuer() -> IssuerProfile:
    return IssuerProfile(
        issuer_id="https://nisamina.ibagari.foundation",
        name="Ibagari Foundation",
        url="https://nisamina.ibagari.foundation",
        email="garifunalearningacademy@gmail.com",
    )


def _mk_lesson_badge() -> BadgeClass:
    return BadgeClass(
        badge_id="badge.lesson.greetings.day1",
        name="Day 1 — Greetings",
        description="Completed the Day 1 Greetings lesson",
        achievement_kind=AchievementKind.LESSON_COMPLETION,
        criteria=CriteriaSpec(narrative="Completed all 4 units of Day 1 Greetings with ≥85% accuracy"),
        attribution_refs=("attr_055",),
        consent_ref="consent_011",
    )


def _mk_cultural_badge() -> BadgeClass:
    return BadgeClass(
        badge_id="badge.cultural.beluria_acknowledgment",
        name="Beluria — 9-night wake acknowledgment",
        description="Learner has completed the Beluria cultural-protocol introduction",
        achievement_kind=AchievementKind.CULTURAL_PROTOCOL_ACK,
        criteria=CriteriaSpec(narrative="Learner read + acknowledged the Beluria cultural-protocol notice"),
        attribution_refs=("attr_055",),
        consent_ref="consent_011",
        cultural_protocol_authority="Commission elder panel — Garifuna ICH affairs",
    )


def _mk_recipient() -> RecipientIdentifier:
    return RecipientIdentifier(
        identifier="learner_hash_abc123",
        identifier_type="platform-id",
    )


# === BadgeIssuer ===


def test_issue_lesson_completion_badge():
    issuer = BadgeIssuer(_mk_issuer())
    badge = _mk_lesson_badge()
    assertion = issuer.issue(
        badge_class=badge,
        recipient=_mk_recipient(),
        envir="belize",
        evidence_narrative="Learner completed Day 1 with 90% accuracy across 4 units",
    )
    assert assertion.assertion_id.startswith("urn:uuid:")
    assert assertion.envir == "belize"
    assert len(issuer.issued()) == 1


def test_cultural_badge_requires_authority():
    issuer = BadgeIssuer(_mk_issuer())
    bad_badge = BadgeClass(
        badge_id="badge.cultural.x", name="x", description="x",
        achievement_kind=AchievementKind.CULTURAL_PROTOCOL_ACK,
        criteria=CriteriaSpec(narrative="x"),
        cultural_protocol_authority=None,  # missing!
    )
    with pytest.raises(ValueError, match="cultural_protocol_authority"):
        issuer.issue(badge_class=bad_badge, recipient=_mk_recipient(), envir="belize")


def test_cultural_badge_with_authority_succeeds():
    issuer = BadgeIssuer(_mk_issuer())
    assertion = issuer.issue(
        badge_class=_mk_cultural_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    assert assertion.badge_class.cultural_protocol_authority is not None


def test_revoke_appends_revoked_copy_not_mutates():
    """Per [[feedback-no-hindsight-whitewashing]]: original assertion preserved."""
    issuer = BadgeIssuer(_mk_issuer())
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    success = issuer.revoke(assertion.assertion_id)
    assert success is True
    issued = issuer.issued()
    # Original (revoked=False) AND revoked copy both present
    assert len(issued) == 2
    assert any(not a.revoked for a in issued)
    assert any(a.revoked for a in issued)


def test_revoke_unknown_returns_false():
    issuer = BadgeIssuer(_mk_issuer())
    assert issuer.revoke("urn:uuid:nonexistent") is False


# === JSON-LD output ===


def test_jsonld_includes_open_badges_3_context():
    issuer = BadgeIssuer(_mk_issuer())
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    jsonld = assertion_to_jsonld(assertion)
    assert "@context" in jsonld
    assert jsonld["@context"] == OPEN_BADGES_3_CONTEXT


def test_jsonld_has_verifiable_credential_type():
    issuer = BadgeIssuer(_mk_issuer())
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    jsonld = assertion_to_jsonld(assertion)
    assert "VerifiableCredential" in jsonld["type"]
    assert "OpenBadgeCredential" in jsonld["type"]


def test_jsonld_carries_attribution_refs():
    issuer = BadgeIssuer(_mk_issuer())
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    jsonld = assertion_to_jsonld(assertion)
    assert jsonld.get("nisamina:attributionRefs") == ["attr_055"]
    assert jsonld.get("nisamina:consentRef") == "consent_011"


def test_jsonld_includes_achievement_in_credentialSubject():
    issuer = BadgeIssuer(_mk_issuer())
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="belize",
    )
    jsonld = assertion_to_jsonld(assertion)
    achievement = jsonld["credentialSubject"]["achievement"]
    assert achievement["name"] == "Day 1 — Greetings"
    assert achievement["achievementType"] == "lesson_completion"


def test_jsonld_envir_extension():
    """Per F-055 axis #6: badges carry envir tag for per-MOE routing."""
    issuer = BadgeIssuer(_mk_issuer())
    assertion = issuer.issue(
        badge_class=_mk_lesson_badge(),
        recipient=_mk_recipient(),
        envir="svg_yurumein",
    )
    jsonld = assertion_to_jsonld(assertion)
    assert jsonld["nisamina:envir"] == "svg_yurumein"
