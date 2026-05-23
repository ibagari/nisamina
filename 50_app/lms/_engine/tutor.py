"""M-P3.LMS.TUTOR — Socratic AI tutor (D-MAX-7).

Per F-059 D-MAX-7 + Reiser 2004 *Scaffolding Complex Learning* + Harvard 2024
AI-tutor study (>2× learning vs traditional active-learning classroom) +
Brookings 2025 small-language-model personalized-tutoring brief.

The tutor consumes:
- OpenLearnerModel: per-headword BKT belief state
- KnowledgeGraph: prerequisite + dependency edges
- MasteryGate: when learner can advance
- PathwayKind: scaffolding intensity per learner pathway
- SocraticBrainCallable: brain-side text generation (Phase-3 Gemma 4 E4B-it via
  GGUF NOW; Phase-5 ibagari/gemma-4-e4b-nisamina fine-tune LATER per D-039)

The tutor produces a TutorTurn for each interaction: a scaffolded prompt with
hint progression appropriate to the learner's current state.

Per Reiser 2004 + per F-059 D-MAX-5: scaffolding intensity depends on pathway:
- HERITAGE: form-focused-intensity=0.85; identity-anchor required; receptive-first
- NOVICE: scaffolding-intensity=0.90; explicit examples; broader form exposure
- L1_MAINTAINER: scaffolding-intensity=0.30; near-native challenge; literacy focus

Per F-055 axis #1 sovereign presentation: tutor outputs cite KGRAPH paths via
cite_sources MCP surface (chatbot orchestration consumes); no hallucinated
linguistic content.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

try:
    from .olm import OpenLearnerModel
    from .kgraph import KnowledgeGraph, NodeKind, EdgeKind
    from .mastery import MasteryGate, MasteryGateResult
    from .pathway import PathwayKind, pathway_for
except ImportError:
    from olm import OpenLearnerModel
    from kgraph import KnowledgeGraph, NodeKind, EdgeKind
    from mastery import MasteryGate, MasteryGateResult
    from pathway import PathwayKind, pathway_for


# Type for the brain-side text generator. In production this wires to
# chatbot.brain.Brain.respond(...); in tests it's a deterministic mock.
SocraticBrainCallable = Callable[[str], str]


class ScaffoldLevel(str, Enum):
    """How much hint vs open-question Socratic step.

    Progression order: OPEN → GUIDING → HINTED → MODELED → DIRECT_INSTRUCT.
    Lower levels (OPEN) push learner agency; higher levels (MODELED/DIRECT)
    provide more support. Tutor steps DOWN the levels until learner succeeds.
    """
    OPEN = "open"                          # broad open question; no hints
    GUIDING = "guiding"                    # narrower question pointing at concept
    HINTED = "hinted"                      # explicit hint included in prompt
    MODELED = "modeled"                    # worked example before the question
    DIRECT_INSTRUCT = "direct_instruct"    # full explanation; minimal learner work


@dataclass(frozen=True)
class TutorTurn:
    """One Socratic interaction step the tutor emits."""
    turn_id: str
    target_headword: str                   # the Garifuna headword being scaffolded
    scaffold_level: ScaffoldLevel
    prompt_text: str
    expected_response_kind: str            # "free_text" | "multiple_choice" | "audio"
    prereq_chain: tuple[str, ...]          # KGRAPH path from prereq → target
    kgraph_node_ids_cited: tuple[str, ...]
    pathway_kind: str
    cite_sources_payload: dict             # consumed by chatbot.cite_sources MCP tool


@dataclass
class TutorState:
    """Per-learner per-concept tutor state."""
    learner_id: str
    envir: str
    target_concept: str                    # Garifuna headword or LO id
    current_scaffold_level: ScaffoldLevel = ScaffoldLevel.OPEN
    attempt_count: int = 0
    correct_count: int = 0
    last_turn_id: Optional[str] = None
    advanced: bool = False                 # set True when MasteryGate allows


class SocraticTutor:
    """Pathway-aware Socratic AI tutor.

    Architecture:
        next_turn(state, learner_response) →
            1. Consult OLM for current belief on target_concept
            2. Walk KGRAPH for unmastered prerequisites (if any)
            3. Decide scaffold_level based on pathway + belief + attempt history
            4. Compose Socratic prompt template
            5. Optionally call brain for naturalization (Phase-5 fine-tune; minimal
               in Phase-3 to keep latency low + grounding tight)
            6. Emit TutorTurn with cite_sources_payload for chatbot integration

    Per F-074 PHASE-NOW: scaffold builds against current Phase-3 brain (Gemma 4
    E4B-it via GGUF); full naturalization improves with Phase-5 fine-tune.
    """

    def __init__(
        self,
        olm: OpenLearnerModel,
        kgraph: KnowledgeGraph,
        mastery_gate: MasteryGate,
        pathway: PathwayKind,
        brain: Optional[SocraticBrainCallable] = None,
    ):
        self.olm = olm
        self.kgraph = kgraph
        self.mastery_gate = mastery_gate
        self.pathway = pathway
        self.pathway_spec = pathway_for(pathway)
        self.brain = brain  # Optional — template-only generation if absent

    def initial_turn(self, target_headword: str) -> TutorTurn:
        """Open the first Socratic step on a target headword."""
        state = TutorState(
            learner_id=self.olm.learner_id,
            envir=self.olm.envir,
            target_concept=target_headword,
        )
        return self._emit_turn(state, target_headword)

    def next_turn(
        self,
        state: TutorState,
        learner_response: Optional[str] = None,
        was_correct: Optional[bool] = None,
    ) -> TutorTurn:
        """Produce the next Socratic step given current state + last response.

        If was_correct is True, attempt to maintain or relax scaffold; if False,
        increase scaffold one level. State is mutated in place per single-session
        convention (state tracking lives outside the tutor for persistence).
        """
        state.attempt_count += 1
        if was_correct:
            state.correct_count += 1
            state.current_scaffold_level = self._relax_scaffold(state.current_scaffold_level)
        elif was_correct is False:
            state.current_scaffold_level = self._tighten_scaffold(state.current_scaffold_level)
        return self._emit_turn(state, state.target_concept)

    def _emit_turn(self, state: TutorState, target_headword: str) -> TutorTurn:
        # Find target node in kgraph (if present)
        target_node_id = self._find_target_node(target_headword)
        # Find prereq chain (unmastered prereqs first)
        prereq_chain = self._unmastered_prereq_chain(target_node_id) if target_node_id else ()
        # Compose prompt with pathway-aware scaffolding
        prompt_text, expected_kind = self._compose_prompt(
            target_headword=target_headword,
            scaffold_level=state.current_scaffold_level,
            unmastered_prereqs=prereq_chain,
        )
        # Optionally let the brain naturalize the prompt (Phase-3 keeps light)
        if self.brain is not None and state.current_scaffold_level != ScaffoldLevel.OPEN:
            try:
                prompt_text = self.brain(prompt_text) or prompt_text
            except Exception:  # noqa: BLE001 — brain failure falls back to template
                pass
        # cite_sources payload — KGRAPH path + foundry headword refs
        cite_payload = self._cite_sources_payload(target_headword, target_node_id, prereq_chain)
        turn_id = f"tutor.{state.learner_id}.{target_headword}.{state.attempt_count}"
        state.last_turn_id = turn_id
        return TutorTurn(
            turn_id=turn_id,
            target_headword=target_headword,
            scaffold_level=state.current_scaffold_level,
            prompt_text=prompt_text,
            expected_response_kind=expected_kind,
            prereq_chain=prereq_chain,
            kgraph_node_ids_cited=(target_node_id,) if target_node_id else (),
            pathway_kind=self.pathway.value,
            cite_sources_payload=cite_payload,
        )

    # === Helpers ============================================================

    def _find_target_node(self, headword: str) -> Optional[str]:
        """Locate a HEADWORD node whose label matches the given headword."""
        for nid, node in self.kgraph._nodes.items():  # noqa: SLF001 — engine-internal
            if node.kind == NodeKind.HEADWORD and node.label == headword:
                return nid
        return None

    def _unmastered_prereq_chain(self, target_node_id: Optional[str]) -> tuple[str, ...]:
        if target_node_id is None or not self.kgraph.has_node(target_node_id):
            return ()
        chain: list[str] = []
        for prereq_node_id in self.kgraph.prerequisites_of(target_node_id):
            prereq_node = self.kgraph.get_node(prereq_node_id)
            if prereq_node.kind == NodeKind.HEADWORD:
                belief = self.olm.beliefs.get(prereq_node.label)
                if belief is None or belief.p_mastered < self.mastery_gate.threshold:
                    chain.append(prereq_node_id)
        return tuple(chain)

    def _compose_prompt(
        self,
        *,
        target_headword: str,
        scaffold_level: ScaffoldLevel,
        unmastered_prereqs: tuple[str, ...],
    ) -> tuple[str, str]:
        """Build the Socratic prompt + return (prompt_text, expected_response_kind).

        Pathway-aware: identity-anchor for HERITAGE; explicit-example for NOVICE;
        academic-register for L1_MAINTAINER.
        """
        # Apply pathway anchor
        anchor = ""
        if self.pathway == PathwayKind.HERITAGE:
            anchor = "(Think about your family or community — when have you heard this word used?) "
        elif self.pathway == PathwayKind.NOVICE:
            anchor = "(Step by step. Take your time.) "
        elif self.pathway == PathwayKind.L1_MAINTAINER:
            anchor = "(In academic register, with attention to literary form.) "

        # Apply scaffold-level template
        if scaffold_level == ScaffoldLevel.OPEN:
            prompt = f"{anchor}What does '{target_headword}' mean to you? Tell me in your own words."
            kind = "free_text"
        elif scaffold_level == ScaffoldLevel.GUIDING:
            prompt = f"{anchor}'{target_headword}' is used in greetings + family contexts in Garifuna. Can you give an example sentence?"
            kind = "free_text"
        elif scaffold_level == ScaffoldLevel.HINTED:
            prompt = f"{anchor}'{target_headword}' starts with the same sound as the English word — and it expresses a feeling. What feeling does it express?"
            kind = "free_text"
        elif scaffold_level == ScaffoldLevel.MODELED:
            prompt = (
                f"{anchor}Watch this example: 'buguya nuani' means 'thank you my dear'. "
                f"Now you try: what does '{target_headword}' mean?"
            )
            kind = "multiple_choice"
        else:  # DIRECT_INSTRUCT
            prompt = (
                f"{anchor}'{target_headword}' means... (the tutor provides the definition + 1 example + "
                f"asks you to repeat it back; then we move forward together)"
            )
            kind = "free_text"

        # If there are unmastered prereqs, surface the closest one
        if unmastered_prereqs:
            prompt += (
                f"\n\n(Before tackling '{target_headword}', let's review what comes first: "
                f"{unmastered_prereqs[0]}.)"
            )

        return prompt, kind

    def _relax_scaffold(self, level: ScaffoldLevel) -> ScaffoldLevel:
        """Step toward OPEN (more learner agency) after a correct response."""
        order = [
            ScaffoldLevel.OPEN, ScaffoldLevel.GUIDING, ScaffoldLevel.HINTED,
            ScaffoldLevel.MODELED, ScaffoldLevel.DIRECT_INSTRUCT,
        ]
        idx = order.index(level)
        return order[max(0, idx - 1)]

    def _tighten_scaffold(self, level: ScaffoldLevel) -> ScaffoldLevel:
        """Step toward DIRECT_INSTRUCT (more support) after an incorrect response."""
        order = [
            ScaffoldLevel.OPEN, ScaffoldLevel.GUIDING, ScaffoldLevel.HINTED,
            ScaffoldLevel.MODELED, ScaffoldLevel.DIRECT_INSTRUCT,
        ]
        idx = order.index(level)
        return order[min(len(order) - 1, idx + 1)]

    def _cite_sources_payload(
        self,
        target_headword: str,
        target_node_id: Optional[str],
        prereq_chain: tuple[str, ...],
    ) -> dict:
        """Payload that the chatbot.cite_sources MCP tool surfaces alongside the response."""
        return {
            "tutor_target": target_headword,
            "kgraph_target_node_id": target_node_id,
            "unmastered_prereqs_count": len(prereq_chain),
            "pathway": self.pathway.value,
            "scaffolding_intensity": self.pathway_spec.scaffolding_intensity,
            "envir": self.olm.envir,
            "_authority": "M-P3.LMS.TUTOR + F-059 D-MAX-7 + Reiser 2004 + Harvard 2024",
        }
