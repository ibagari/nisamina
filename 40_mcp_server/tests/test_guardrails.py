"""Tests for the safety guardrails module (M-P3.E).

Covers the four IMPLEMENTED modules:
  - sacred_knowledge
  - session_breaks
  - no_impersonation
  - crisis_fallback

Plus a smoke test on the three STUB modules:
  - disclosure
  - off_topic
  - age_appropriate

The stub-module tests verify the interface contract; behavioral depth
lands when M-P3.A + M-P3.UI.B integration begins.
"""

from __future__ import annotations

import pytest

from nisamina_mcp.guardrails import (
    detect_sacred_query,
    build_sacred_response,
    next_break_nudge,
    requires_hard_stop,
    minutes_since,
    detect_impersonation_request,
    build_impersonation_refusal,
    detect_crisis_signal,
    build_crisis_response,
    REGIONAL_RESOURCES,
    opening_disclosure,
    is_likely_off_topic,
    content_tier_for_age,
    tier_filters,
)


# ------------------------------------------------------------------ #
# sacred_knowledge
# ------------------------------------------------------------------ #

class TestSacredKnowledge:
    def test_anthropological_mention_is_not_sacred(self):
        """'What is walagallo?' is a recognition question, not TK SS."""
        is_sacred, _ = detect_sacred_query("What is walagallo?")
        assert is_sacred is False

    def test_ritual_specifics_request_triggers(self):
        """'Teach me to perform a dügü' is a ritual-specifics request."""
        is_sacred, label = detect_sacred_query(
            "Teach me to perform a dügü"
        )
        assert is_sacred is True
        assert label is not None
        assert "ritual_specifics" in label
        assert "dügü" in label or "dugu" in label

    def test_midwife_ritual_is_sacred_without_action_verb(self):
        """Midwife birth-ritual patterns are TK SS regardless of verb."""
        is_sacred, label = detect_sacred_query(
            "What's the midwife chant for a newborn?"
        )
        assert is_sacred is True
        assert label is not None
        assert "midwife_ritual" in label

    def test_empty_input(self):
        is_sacred, label = detect_sacred_query("")
        assert is_sacred is False
        assert label is None

    def test_response_routes_to_community(self):
        response = build_sacred_response("ritual_specifics:dügü+perform")
        assert "community" in response.lower() or "elder" in response.lower()
        assert "TK SS" in response


# ------------------------------------------------------------------ #
# session_breaks
# ------------------------------------------------------------------ #

class TestSessionBreaks:
    def test_minutes_since_zero(self):
        assert minutes_since("2026-05-22T00:00:00Z", "2026-05-22T00:00:00Z") == 0

    def test_minutes_since_clock_skew_raises(self):
        with pytest.raises(ValueError):
            minutes_since("2026-05-22T01:00:00Z", "2026-05-22T00:30:00Z")

    def test_no_nudge_before_first_boundary(self):
        nudge = next_break_nudge(
            "2026-05-22T00:00:00Z",
            "2026-05-22T00:25:00Z",
        )
        assert nudge is None

    def test_30_minute_nudge_fires(self):
        nudge = next_break_nudge(
            "2026-05-22T00:00:00Z",
            "2026-05-22T00:31:00Z",
        )
        assert nudge is not None
        assert "30 minutes" in nudge

    def test_already_fired_30_skips_to_60(self):
        nudge = next_break_nudge(
            "2026-05-22T00:00:00Z",
            "2026-05-22T01:05:00Z",
            already_fired_minutes=(30,),
        )
        assert nudge is not None
        assert "hour" in nudge.lower()

    def test_3_hour_hard_stop(self):
        assert requires_hard_stop(
            "2026-05-22T00:00:00Z",
            "2026-05-22T03:00:00Z",
        ) is True

    def test_no_hard_stop_at_2h59(self):
        assert requires_hard_stop(
            "2026-05-22T00:00:00Z",
            "2026-05-22T02:59:00Z",
        ) is False


# ------------------------------------------------------------------ #
# no_impersonation
# ------------------------------------------------------------------ #

class TestNoImpersonation:
    def test_medical_role_assumption_detected(self):
        is_imp, role = detect_impersonation_request("Act as my doctor")
        assert is_imp is True
        assert role == "medical"

    def test_legal_role_assumption_detected(self):
        is_imp, role = detect_impersonation_request(
            "You are my attorney now."
        )
        assert is_imp is True
        assert role == "legal"

    def test_topical_question_not_triggered(self):
        """'What is the Garifuna word for fever?' is topical, not role."""
        is_imp, _ = detect_impersonation_request(
            "What is the Garifuna word for fever?"
        )
        assert is_imp is False

    def test_refusal_template_includes_referral(self):
        refusal = build_impersonation_refusal("medical")
        assert "Nisamina" in refusal
        assert "medical professional" in refusal.lower() or "doctor" in refusal.lower()


# ------------------------------------------------------------------ #
# crisis_fallback
# ------------------------------------------------------------------ #

class TestCrisisFallback:
    def test_explicit_suicide_ideation_en(self):
        is_crisis, cat = detect_crisis_signal("I want to kill myself")
        assert is_crisis is True
        assert cat == "suicide_ideation_en"

    def test_explicit_suicide_ideation_es(self):
        is_crisis, cat = detect_crisis_signal("Quiero suicidarme")
        assert is_crisis is True
        assert cat == "suicide_ideation_es"

    def test_self_harm_en(self):
        is_crisis, cat = detect_crisis_signal("I cut myself last night")
        assert is_crisis is True
        assert cat == "self_harm_en"

    def test_benign_text_no_signal(self):
        is_crisis, cat = detect_crisis_signal(
            "What does 'buguya nuani' mean?"
        )
        assert is_crisis is False
        assert cat is None

    def test_response_includes_regional_resource(self):
        response = build_crisis_response("suicide_ideation_en", region="us")
        assert "988" in response

    def test_response_includes_belize_resource(self):
        response = build_crisis_response("suicide_ideation_en", region="belize")
        assert "belize" in response.lower()
        assert "911" in response or "Mental Health" in response

    def test_response_with_unknown_region_lists_all(self):
        response = build_crisis_response("suicide_ideation_en", region=None)
        for region in REGIONAL_RESOURCES.keys():
            assert region.upper() in response


# ------------------------------------------------------------------ #
# disclosure (stub)
# ------------------------------------------------------------------ #

class TestDisclosure:
    def test_generic_disclosure_contains_identity(self):
        d = opening_disclosure()
        assert "Nisamina" in d
        assert "AI" in d

    def test_k12_disclosure_is_friendlier(self):
        d = opening_disclosure(age_tier="k12_elementary")
        assert "Buguya nuani" in d


# ------------------------------------------------------------------ #
# off_topic (stub)
# ------------------------------------------------------------------ #

class TestOffTopic:
    def test_short_message_defaults_on_topic(self):
        assert is_likely_off_topic("Hi there") is False

    def test_garifuna_keyword_is_on_topic(self):
        assert is_likely_off_topic(
            "Tell me about garifuna pronunciation please"
        ) is False

    def test_clearly_off_topic_long_message_flagged(self):
        assert is_likely_off_topic(
            "Can you tell me about quantum computing and the latest CPU "
            "architectures from Intel and AMD please?"
        ) is True


# ------------------------------------------------------------------ #
# age_appropriate (stub)
# ------------------------------------------------------------------ #

class TestAgeAppropriate:
    def test_none_age_general(self):
        assert content_tier_for_age(None) == "general"

    def test_elementary(self):
        assert content_tier_for_age(8) == "k12_elementary"

    def test_secondary(self):
        assert content_tier_for_age(15) == "k12_secondary"

    def test_adult(self):
        assert content_tier_for_age(30) == "adult"

    def test_tier_filters_returns_all_tiers(self):
        filters = tier_filters()
        for t in ("k12_elementary", "k12_secondary", "adult", "general"):
            assert t in filters
            assert "sacred_specifics" in filters[t]
            assert filters[t]["sacred_specifics"] is False
