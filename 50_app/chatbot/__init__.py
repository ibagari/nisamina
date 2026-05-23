"""Nisamina chatbot — Phase-3 interim Gemma 3 4B-Instruct.

Per M-P3.A. Grounded-only conversation orchestrator wiring:
- system_prompt_v1.md (from 40_mcp_server/nisamina_mcp/guardrails/)
- M-P3.E safety guardrails (sacred_knowledge / crisis_fallback / no_impersonation /
  off_topic / session_breaks / disclosure / age_appropriate)
- M-P2 MCP server (lookup_headword / cite_sources / cayetano_normalize /
  parse_morphology / translate_sentence)
- M-P3.G GarifunaBench callable wrapper
- nisamina_mcp.egress recursive strip_linter

Phase-5 target: swap brain to Gemma-4-E4B-Nisamina (fine-tune of Gemma 4 E4B per
F-033-OVERRIDE) — same family; minimal architectural drift.
"""

from .orchestrator import Orchestrator, SessionState, OrchestratorResponse
from .brain import Brain, MockBrain, load_brain


__all__ = [
    "Orchestrator",
    "SessionState",
    "OrchestratorResponse",
    "Brain",
    "MockBrain",
    "load_brain",
]
