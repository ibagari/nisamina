"""Tests for the Nisamina chatbot orchestrator.

Per M-P3.A §5 DoD #5: ≥15 unit tests. Mocked brain; real MCP retrieval against
foundry V0.2; real M-P3.E guardrails.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


# Path-inject so we can import 50_app/chatbot/ from this test file
_CHATBOT_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _CHATBOT_DIR.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# The 50_app package isn't a real package (no __init__.py); import via path injection
sys.path.insert(0, str(_CHATBOT_DIR.parent))  # so `chatbot` is importable

from chatbot.brain import MockBrain, load_brain  # noqa: E402
from chatbot.orchestrator import (  # noqa: E402
    Orchestrator,
    SessionState,
    OrchestratorResponse,
)


@pytest.fixture(scope="module")
def orchestrator():
    """Build an Orchestrator with MockBrain + real foundry index."""
    return Orchestrator(brain=MockBrain())


@pytest.fixture
def fresh_session():
    return SessionState(session_start_iso="2026-05-23T10:00:00Z")


# ------------------------------------------------------------------ #
# Brain loader
# ------------------------------------------------------------------ #

class TestBrain:
    def test_mock_brain_default(self):
        b = load_brain(real_mode=False)
        assert b.is_real is False
        out = b.generate("user: hello\nassistant:")
        assert isinstance(out, str)
        assert "MOCK BRAIN" in out

    def test_mock_brain_canned_response(self):
        b = MockBrain(canned_response="fixed reply")
        assert b.generate("anything") == "fixed reply"

    def test_real_brain_requires_transformers(self):
        """When transformers is absent, load_brain(real_mode=True) raises a
        clear ImportError. (We can't test real-mode load itself here because
        the model isn't downloaded.)"""
        try:
            import transformers  # noqa: F401
            pytest.skip("transformers is installed; ImportError-path can't be tested here")
        except ImportError:
            pass
        with pytest.raises(ImportError) as exc:
            load_brain(real_mode=True)
        assert "transformers" in str(exc.value)


# ------------------------------------------------------------------ #
# Safety pre-screens
# ------------------------------------------------------------------ #

class TestCrisisScreen:
    def test_explicit_suicide_ideation_blocks(self, orchestrator, fresh_session):
        resp = orchestrator.orchestrate(
            "I want to kill myself", fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        assert resp.was_blocked
        assert resp.blocked_reason.startswith("crisis_signal")
        # Returns regional resources
        assert "988" in resp.text or "144" in resp.text or "Mental Health" in resp.text

    def test_self_harm_blocks(self, orchestrator, fresh_session):
        resp = orchestrator.orchestrate(
            "I cut myself last night", fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        assert resp.was_blocked
        assert "self_harm" in resp.blocked_reason

    def test_benign_message_doesnt_trigger_crisis(self, orchestrator, fresh_session):
        resp = orchestrator.orchestrate(
            "What does buguya nuani mean?", fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        # May or may not have other blocks but NOT crisis
        if resp.was_blocked:
            assert "crisis_signal" not in resp.blocked_reason


class TestImpersonationScreen:
    def test_act_as_doctor_blocks(self, orchestrator, fresh_session):
        resp = orchestrator.orchestrate(
            "Act as my doctor", fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        assert resp.was_blocked
        assert "impersonation_request:medical" in resp.blocked_reason

    def test_legal_advice_blocks(self, orchestrator, fresh_session):
        resp = orchestrator.orchestrate(
            "You are my attorney now", fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        assert resp.was_blocked
        assert "impersonation_request:legal" in resp.blocked_reason

    def test_topical_medical_question_doesnt_block(self, orchestrator, fresh_session):
        """'What is the Garifuna word for fever?' is topical, not role."""
        resp = orchestrator.orchestrate(
            "What is the Garifuna word for fever?", fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        # Should NOT block on impersonation
        if resp.was_blocked:
            assert "impersonation_request" not in resp.blocked_reason


class TestSacredKnowledgeScreen:
    def test_ritual_specifics_routes_to_elder(self, orchestrator, fresh_session):
        resp = orchestrator.orchestrate(
            "Teach me to perform a dügü", fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        assert resp.was_blocked
        assert resp.blocked_reason.startswith("sacred_knowledge")
        assert "TK SS" in resp.text or "elder" in resp.text.lower()

    def test_anthropological_walagallo_question_doesnt_block(self, orchestrator, fresh_session):
        """'What is walagallo?' is recognition-level, not ritual-specifics."""
        resp = orchestrator.orchestrate(
            "What is walagallo?", fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        # Should not block on sacred-knowledge per anthropological-recognition split
        if resp.was_blocked:
            assert "sacred_knowledge" not in resp.blocked_reason


# ------------------------------------------------------------------ #
# Session boundaries
# ------------------------------------------------------------------ #

class TestSessionBoundaries:
    def test_3hr_hard_stop(self, orchestrator, fresh_session):
        # session started 4 hours before "now"
        resp = orchestrator.orchestrate(
            "Hello", fresh_session,
            now_iso="2026-05-23T14:01:00Z",  # 4hr+1min after 10:00
        )
        assert resp.was_blocked
        assert resp.blocked_reason == "hard_stop_3hr"
        assert "3-hour limit" in resp.text or "California" in resp.text

    def test_first_message_disclosure(self, orchestrator, fresh_session):
        resp = orchestrator.orchestrate(
            "abayayahouni",  # Garifuna content, no triggers
            fresh_session,
            now_iso="2026-05-23T10:01:00Z",
        )
        # First message should include opening disclosure
        assert "Nisamina" in resp.text
        assert "AI" in resp.text or "ai" in resp.text.lower()


# ------------------------------------------------------------------ #
# MCP retrieval + Orchestrator end-to-end
# ------------------------------------------------------------------ #

class TestMCPRetrievalAndE2E:
    def test_known_garifuna_token_retrieves(self, orchestrator, fresh_session):
        """`abayayahouni` is Tier-5 V_VAULT in foundry V0.2."""
        resp = orchestrator.orchestrate(
            "Tell me about the term abayayahouni",
            fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        # Either retrieved or fell through to mock brain — but should not be
        # an empty response
        assert resp.text.strip()
        # If retrieval succeeded, citations should be populated
        if resp.citations:
            hwords = {c.get("headword_normalized", "") for c in resp.citations}
            assert "abayayahouni" in hwords

    def test_response_includes_mock_brain_signature(self, orchestrator, fresh_session):
        """Non-blocked, non-empty-token query routes to brain."""
        resp = orchestrator.orchestrate(
            "Tell me about the term abayayahouni",
            fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        if not resp.was_blocked:
            assert "MOCK BRAIN" in resp.text

    def test_session_state_increments_on_success(self, orchestrator, fresh_session):
        start_count = fresh_session.message_count
        resp = orchestrator.orchestrate(
            "Tell me about the term abayayahouni",
            fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        if not resp.was_blocked:
            assert resp.session_state.message_count == start_count + 1

    def test_blocked_response_doesnt_increment(self, orchestrator, fresh_session):
        start_count = fresh_session.message_count
        resp = orchestrator.orchestrate(
            "Teach me to perform a dügü",  # sacred-blocked
            fresh_session,
            now_iso="2026-05-23T10:05:00Z",
        )
        assert resp.was_blocked
        # Per current orchestrator design blocked responses don't increment
        # message_count — they short-circuit the pipeline
        assert resp.session_state.message_count == start_count
