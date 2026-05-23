"""Chatbot orchestrator — wires brain + system prompt + guardrails + MCP + bench.

Per M-P3.A §4 ten-step pipeline:
1. safety pre-screen (crisis > impersonation > sacred > off-topic)
2. first-message disclosure
3. session-break nudge
4. hard-stop at 3 hours
5. MCP retrieval (foundry context)
6. augmented prompt
7. brain generation
8. hallucination post-screen
9. egress wrapper
10. return

All pure-Python; brain is injected (mock for tests; real for HF Space).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


# Resolve MCP path for both layouts:
#   - Local dev: orchestrator.py at nisamina-app/50_app/chatbot/ — MCP at parents[2]/40_mcp_server
#   - HF Space:  orchestrator.py at /app/ alongside nisamina_mcp/ — same dir
_HERE = Path(__file__).resolve().parent
if (_HERE / "nisamina_mcp").exists():
    _REPO_ROOT = _HERE
    _MCP_PATH = _HERE
else:
    _REPO_ROOT = _HERE.parents[1]  # 50_app/.. = repo root
    _MCP_PATH = _REPO_ROOT / "40_mcp_server"
if str(_MCP_PATH) not in sys.path:
    sys.path.insert(0, str(_MCP_PATH))

from nisamina_mcp.foundry_loader import load, FoundryIndex  # noqa: E402
from nisamina_mcp.tools.lookup_headword import lookup_headword  # noqa: E402
from nisamina_mcp.tools.cite_sources import cite_sources  # noqa: E402
from nisamina_mcp.egress import enforce_egress, StripLinterError  # noqa: E402
from nisamina_mcp.rag import RAGRetriever, RAGResult  # noqa: E402
from nisamina_mcp.guardrails import (  # noqa: E402
    detect_crisis_signal, build_crisis_response,
    detect_impersonation_request, build_impersonation_refusal,
    detect_sacred_query, build_sacred_response,
    is_likely_off_topic,
    opening_disclosure,
    next_break_nudge, requires_hard_stop,
    content_tier_for_age,
)

# GarifunaBench: at 80_validation in local dev; at /app/garifuna_bench on HF Space (sibling)
if (_HERE / "garifuna_bench").exists():
    _BENCH_PATH = _HERE
else:
    _BENCH_PATH = _REPO_ROOT / "80_validation"
if str(_BENCH_PATH) not in sys.path:
    sys.path.insert(0, str(_BENCH_PATH))
from garifuna_bench.hallucination_detector import (  # noqa: E402
    extract_garifuna_tokens,
    HallucinationDetector,
)

try:
    from .brain import Brain, MockBrain
    from .tts_garifuna import GarifunaTTS, MockGarifunaTTS, TTSResult
except ImportError:
    from brain import Brain, MockBrain
    from tts_garifuna import GarifunaTTS, MockGarifunaTTS, TTSResult

# D-067 TUTOR.LIVE_BRAIN_WIRING — bring LMS tutor + verifier into chatbot orchestrator
_LMS_PATH = _HERE / ".." / "lms"
if not _LMS_PATH.exists():
    _LMS_PATH = _REPO_ROOT / "50_app" / "lms"
if str(_LMS_PATH.parent.resolve()) not in sys.path:
    sys.path.insert(0, str(_LMS_PATH.parent.resolve()))
try:
    from lms._engine.tutor import SocraticTutor, TutorState, TutorTurn  # type: ignore  # noqa: E402
    from lms._engine.tutor_verifier import (  # type: ignore  # noqa: E402
        CompositeVerifier, OrthographyVerifier, FoundryExistenceVerifier,
        VerifierResult, VerifierStatus,
    )
    from lms._engine.kgraph import KnowledgeGraph  # type: ignore  # noqa: E402
    from lms._engine.olm import OpenLearnerModel  # type: ignore  # noqa: E402
    from lms._engine.mastery import MasteryGate  # type: ignore  # noqa: E402
    from lms._engine.pathway import PathwayKind  # type: ignore  # noqa: E402
    _LMS_AVAILABLE = True
except ImportError:
    _LMS_AVAILABLE = False


SYSTEM_PROMPT_PATH = _MCP_PATH / "nisamina_mcp" / "guardrails" / "system_prompt_v1.md"
HALLUCINATION_THRESHOLD: float = 1.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_system_prompt() -> str:
    """Load the canonical system prompt v1; falls back to stub if missing."""
    if SYSTEM_PROMPT_PATH.exists():
        return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    return "You are Nisamina, a grounded-only Garifuna learning assistant."


@dataclass
class SessionState:
    session_start_iso: str = field(default_factory=_now_iso)
    message_count: int = 0
    age_tier: str = "general"
    region: Optional[str] = None  # belize / honduras / guatemala / nicaragua / us / None
    language: str = "en"
    fired_nudges: tuple[int, ...] = field(default_factory=tuple)
    hard_stopped: bool = False

    def increment(self) -> None:
        self.message_count += 1


@dataclass
class OrchestratorResponse:
    text: str
    citations: list[dict]
    flagged_garifuna_tokens: list[str]
    blocked_reason: Optional[str]
    session_state: SessionState
    audio_garifuna_wav: Optional[bytes] = None        # per F-058 §4.1: WAV bytes for Garifuna utterances
    audio_attribution: Optional[str] = None           # per F-058 §3: attribution chain for audio surface
    audio_synthesized_text: Optional[str] = None      # what was synthesized (Garifuna tokens only)

    @property
    def was_blocked(self) -> bool:
        return self.blocked_reason is not None

    @property
    def has_audio(self) -> bool:
        return self.audio_garifuna_wav is not None


class Orchestrator:
    """Wires the chatbot pipeline."""

    def __init__(
        self,
        brain: Optional[Brain] = None,
        foundry_index: Optional[FoundryIndex] = None,
        system_prompt: Optional[str] = None,
        tts: Optional[object] = None,
        audio_enabled: bool = True,
    ) -> None:
        self.brain = brain if brain is not None else MockBrain()
        self.foundry = foundry_index if foundry_index is not None else load()
        self.system_prompt = system_prompt if system_prompt is not None else _load_system_prompt()
        self.rag = RAGRetriever(self.foundry)
        # MMS-tts-cab wrapper per F-058. Mock by default for tests; HF Space passes
        # GarifunaTTS() for real-mode.
        self.tts = tts if tts is not None else MockGarifunaTTS()
        self.audio_enabled = audio_enabled

        # Hallucination detector uses MCP lookup_headword as its lookup_fn
        def _lookup(token: str) -> Optional[dict]:
            results = lookup_headword(self.foundry, token, mode="exact")
            return results[0] if results else None

        self.hallucination_detector = HallucinationDetector(lookup_fn=_lookup)

        # D-067 TUTOR.LIVE_BRAIN_WIRING — wire LMS SocraticTutor + CompositeVerifier
        # Lazy / opt-in: tutor session is created only when start_tutor_session() called.
        self._lms_available = _LMS_AVAILABLE
        self._tutor_brain_callable = self._make_tutor_brain_callable() if _LMS_AVAILABLE else None
        self._composite_verifier = self._make_composite_verifier() if _LMS_AVAILABLE else None

    def _make_tutor_brain_callable(self):
        """Build the SocraticBrainCallable that wraps self.brain.generate."""
        def _callable(prompt: str) -> str:
            try:
                return self.brain.generate(prompt, max_tokens=256, temperature=0.3)
            except Exception:  # noqa: BLE001 — tutor falls back to template on brain failure
                return ""
        return _callable

    def _make_composite_verifier(self):
        """Build the non-LLM verifier chain per D-066 (Khanmigo pattern)."""
        # Foundry-derived known headword set per D-067
        known_hw = self.foundry.known_headwords()
        return CompositeVerifier([
            OrthographyVerifier(),
            FoundryExistenceVerifier(known_headwords=known_hw),
        ])

    def start_tutor_session(
        self,
        learner_id: str,
        envir: str,
        target_headword: str,
        pathway: str = "novice",
    ):
        """Create a SocraticTutor + initial TutorTurn for the given learner.

        Returns (tutor, state, initial_turn). State persistence is the caller's
        responsibility (database row, session dict, etc.).
        Per D-067 + D-066 substrate.
        """
        if not self._lms_available:
            raise RuntimeError("LMS engine not available — tutor session requires lms._engine import")
        olm = OpenLearnerModel(learner_id=learner_id, envir=envir)
        # Minimal kgraph for now — production wires a per-envir VersionedKnowledgeGraph
        kg = KnowledgeGraph(envir=envir)
        try:
            from lms._engine.kgraph import Node, NodeKind  # type: ignore
            kg.add_node(Node(f"hw.{target_headword}", NodeKind.HEADWORD, target_headword, envir=envir))
        except Exception:  # noqa: BLE001
            pass
        pathway_kind = PathwayKind(pathway)
        gate = MasteryGate(olm=olm, kgraph=kg, pathway=pathway_kind)
        tutor = SocraticTutor(
            olm=olm,
            kgraph=kg,
            mastery_gate=gate,
            pathway=pathway_kind,
            brain=self._tutor_brain_callable,
        )
        initial = tutor.initial_turn(target_headword)
        # Build initial state from the tutor's first emission
        state = TutorState(
            learner_id=learner_id, envir=envir, target_concept=target_headword,
            current_scaffold_level=initial.scaffold_level,
            last_turn_id=initial.turn_id,
        )
        return tutor, state, initial

    def verify_brain_output(self, candidate_text: str, learner_envir: str = "garicomm") -> dict:
        """Apply the CompositeVerifier chain to a candidate brain output.

        Returns a dict {status, issues, candidate_text} for transparency. The
        orchestrator can call this before serving brain output to learners,
        per Khanmigo pattern (D-066).
        """
        if not self._lms_available or self._composite_verifier is None:
            return {"status": "lms_unavailable", "issues": [], "candidate_text": candidate_text}
        # Extract candidate Garifuna tokens from text via existing extractor
        cab_tokens = list(extract_garifuna_tokens(candidate_text))
        result = self._composite_verifier.verify(
            candidate_text,
            context={"cab_tokens": cab_tokens, "learner_envir": learner_envir},
        )
        return {
            "status": result.status.value,
            "issues": [
                {"verifier": i.verifier_name, "severity": i.severity,
                 "token": i.offending_token, "rationale": i.rationale}
                for i in result.issues
            ],
            "candidate_text": result.candidate_text,
            "passed": result.passed,
        }

    # ------------------------------------------------------------- #
    # The orchestrate() pipeline
    # ------------------------------------------------------------- #

    def orchestrate(
        self,
        message: str,
        session_state: SessionState,
        now_iso: Optional[str] = None,
    ) -> OrchestratorResponse:
        now = now_iso or _now_iso()

        # 1. Safety pre-screen (severity order)
        crisis_response = self._screen_crisis(message, session_state)
        if crisis_response is not None:
            return crisis_response

        impersonation_response = self._screen_impersonation(message, session_state)
        if impersonation_response is not None:
            return impersonation_response

        sacred_response = self._screen_sacred(message, session_state)
        if sacred_response is not None:
            return sacred_response

        off_topic_response = self._screen_off_topic(message, session_state)
        if off_topic_response is not None:
            return off_topic_response

        # 4. Hard-stop check (run before disclosure so we don't talk past it)
        if requires_hard_stop(session_state.session_start_iso, now):
            session_state.hard_stopped = True
            return OrchestratorResponse(
                text=(
                    "We've reached the 3-hour limit for one chatbot session, "
                    "per the California 2025 chatbot-safety law. Please end "
                    "the session now, take a real break, and come back fresh. "
                    "Your progress is saved. Buguya nuani."
                ),
                citations=[],
                flagged_garifuna_tokens=[],
                blocked_reason="hard_stop_3hr",
                session_state=session_state,
            )

        # 5. MCP retrieval — delegate to RAGRetriever (M-P3.B MEGA-RAG layer)
        rag_result: RAGResult = self.rag.retrieve(message, top_n=5)
        retrieved_records = rag_result.records
        retrieved_sources: set[str] = set()
        for rec in retrieved_records:
            for s in rec.get("sources", []):
                retrieved_sources.add(s)

        # 6. Augmented prompt — use RAG-formatted context block
        augmented_prompt = self._build_augmented_prompt_from_rag(
            message=message,
            rag_result=rag_result,
        )

        # 7. Brain generation
        raw_response = self.brain.generate(augmented_prompt)

        # 8. Hallucination post-screen
        hallu_report = self.hallucination_detector.check(
            response=raw_response,
            claimed_sources=retrieved_sources,
        )

        response_text = raw_response
        if hallu_report.score < HALLUCINATION_THRESHOLD and hallu_report.flagged_tokens:
            response_text = (
                f"{raw_response}\n\n"
                f"⚠ Possibly unverified Garifuna tokens flagged "
                f"(would benefit from elder / Commission review): "
                f"{', '.join(hallu_report.flagged_tokens[:5])}."
            )
        # Surface RAG warnings from multi-evidence + conflict-resolution
        if rag_result.warnings:
            response_text = (
                f"{response_text}\n\n"
                f"— RAG warnings ({len(rag_result.warnings)}): "
                + "; ".join(rag_result.warnings[:3])
            )

        # 2 + 3. Prepend first-message disclosure + any session-break nudge
        preamble_parts: list[str] = []
        if session_state.message_count == 0:
            preamble_parts.append(opening_disclosure(age_tier=session_state.age_tier))
        nudge = next_break_nudge(
            session_state.session_start_iso, now,
            already_fired_minutes=session_state.fired_nudges,
        )
        if nudge:
            preamble_parts.append(nudge)
            # Mark the just-fired boundary so it doesn't re-fire next turn
            session_state.fired_nudges = session_state.fired_nudges + (
                self._just_fired_boundary(session_state.session_start_iso, now),
            )

        full_text = "\n\n".join(preamble_parts + [response_text])

        # 9. Egress — final defense; raises if any gated content leaks
        try:
            payload = {
                "text": full_text,
                "citations": retrieved_records,
            }
            enforce_egress(payload, context="chatbot.orchestrate")
        except StripLinterError as e:
            return OrchestratorResponse(
                text=(
                    "I'm sorry — my response touched on content the platform "
                    "protects under community-consent policies. Let me re-try "
                    "with a narrower scope. (Detail: strip_linter blocked the "
                    "response at egress.)"
                ),
                citations=[],
                flagged_garifuna_tokens=hallu_report.flagged_tokens,
                blocked_reason=f"egress_strip_linter: {e}",
                session_state=session_state,
            )

        # 10. TTS synthesis (per F-058 §4.1) — only for Garifuna tokens, not full text
        audio_wav: Optional[bytes] = None
        audio_attr: Optional[str] = None
        audio_text: Optional[str] = None
        tts_tokens = list(rag_result.token_evidence.keys())
        if self.audio_enabled and tts_tokens:
            # Synthesize the user's Garifuna tokens (preserves bandwidth + reduces
            # synth-hallucination surface — no synth of English filler)
            synth_text = " ".join(tts_tokens[:5])
            try:
                tts_result: TTSResult = self.tts.synth(synth_text)
                audio_wav = tts_result.wav_bytes
                audio_attr = tts_result.attribution
                audio_text = synth_text
            except Exception:
                # TTS failure must NOT block the text response
                audio_wav = None

        # 11. Done
        session_state.increment()
        return OrchestratorResponse(
            text=full_text,
            citations=retrieved_records,
            flagged_garifuna_tokens=hallu_report.flagged_tokens,
            blocked_reason=None,
            session_state=session_state,
            audio_garifuna_wav=audio_wav,
            audio_attribution=audio_attr,
            audio_synthesized_text=audio_text,
        )

    # ------------------------------------------------------------- #
    # Pre-screen helpers
    # ------------------------------------------------------------- #

    def _screen_crisis(
        self, message: str, session_state: SessionState,
    ) -> Optional[OrchestratorResponse]:
        is_crisis, category = detect_crisis_signal(message)
        if not is_crisis or category is None:
            return None
        response_text = build_crisis_response(
            signal_category=category,
            region=session_state.region,
            language=session_state.language,
        )
        return OrchestratorResponse(
            text=response_text,
            citations=[],
            flagged_garifuna_tokens=[],
            blocked_reason=f"crisis_signal:{category}",
            session_state=session_state,
        )

    def _screen_impersonation(
        self, message: str, session_state: SessionState,
    ) -> Optional[OrchestratorResponse]:
        is_imp, role = detect_impersonation_request(message)
        if not is_imp or role is None:
            return None
        response_text = build_impersonation_refusal(role, language=session_state.language)
        return OrchestratorResponse(
            text=response_text,
            citations=[],
            flagged_garifuna_tokens=[],
            blocked_reason=f"impersonation_request:{role}",
            session_state=session_state,
        )

    def _screen_sacred(
        self, message: str, session_state: SessionState,
    ) -> Optional[OrchestratorResponse]:
        is_sacred, pattern = detect_sacred_query(message)
        if not is_sacred or pattern is None:
            return None
        response_text = build_sacred_response(pattern, language=session_state.language)
        return OrchestratorResponse(
            text=response_text,
            citations=[],
            flagged_garifuna_tokens=[],
            blocked_reason=f"sacred_knowledge:{pattern}",
            session_state=session_state,
        )

    def _screen_off_topic(
        self, message: str, session_state: SessionState,
    ) -> Optional[OrchestratorResponse]:
        if not is_likely_off_topic(message):
            return None
        response_text = (
            "I'm Nisamina, a Garifuna language + culture learning assistant. "
            "That question is outside my scope. Try asking me a Garifuna "
            "word, a translation, a curriculum question, or a heritage / "
            "cultural-context question — I cite my sources."
        )
        return OrchestratorResponse(
            text=response_text,
            citations=[],
            flagged_garifuna_tokens=[],
            blocked_reason="off_topic_redirect",
            session_state=session_state,
        )

    # ------------------------------------------------------------- #
    # Prompt building
    # ------------------------------------------------------------- #

    def _build_augmented_prompt_from_rag(
        self,
        message: str,
        rag_result: RAGResult,
    ) -> str:
        """Build prompt using RAG-formatted context block + warnings."""
        return (
            f"{self.system_prompt}\n\n"
            f"---\n\n"
            f"FOUNDRY CONTEXT (cite when using Garifuna terms; "
            f"NEVER invent Garifuna; confidence={rag_result.confidence:.2f}):\n"
            f"{rag_result.augmented_context}\n\n"
            f"---\n\n"
            f"user: {message}\n\n"
            f"assistant:"
        )

    def _build_augmented_prompt(
        self,
        message: str,
        retrieved_records: list[dict],
        session_state: SessionState,
    ) -> str:
        # Compact foundry context — top-N most-attested unique headwords
        seen: set[str] = set()
        ctx_lines: list[str] = []
        for rec in retrieved_records:
            hw = rec.get("headword_normalized", "")
            if hw in seen:
                continue
            seen.add(hw)
            senses = rec.get("senses") or []
            gloss = (senses[0].get("gloss_en") if senses else "") or ""
            n_sources = rec.get("n_sources", 0)
            tier = rec.get("tier", "?")
            sources_short = ", ".join(rec.get("sources", [])[:3])
            ctx_lines.append(
                f"- {hw} (Tier-{tier}, {n_sources} sources: {sources_short}) — {gloss[:120]}"
            )
            if len(ctx_lines) >= 5:
                break

        ctx_block = "\n".join(ctx_lines) if ctx_lines else "(no foundry matches for the user's tokens)"

        return (
            f"{self.system_prompt}\n\n"
            f"---\n\n"
            f"FOUNDRY CONTEXT (cite when using Garifuna terms; "
            f"NEVER invent Garifuna):\n{ctx_block}\n\n"
            f"---\n\n"
            f"user: {message}\n\n"
            f"assistant:"
        )

    def _just_fired_boundary(self, start_iso: str, now_iso: str) -> int:
        """Return the highest soft-nudge boundary <= elapsed minutes."""
        from nisamina_mcp.guardrails.session_breaks import (
            SOFT_NUDGE_MINUTES as _BOUNDS,
            minutes_since as _minutes_since,
        )
        elapsed = _minutes_since(start_iso, now_iso)
        for b in reversed(_BOUNDS):
            if b <= elapsed:
                return b
        return 0
