"""Nisamina MCP server — Garifuna corpus access for MCP-compatible LLM clients.

Five tools (`lookup_headword`, `translate_sentence`, `parse_morphology`,
`cayetano_normalize`, `cite_sources`) over the foundry_v6 V0.2 lexicon, with
every response passing through the `99_publish/strip_linter` egress gate.

Authority: plan v1 §3 + Phase 2; plan v1.1 §2.1 (distribution) + §2.3 (egress);
D-008 (pip + HF Space); D-016 (chatbot grounding layer).
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
