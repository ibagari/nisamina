"""RAG layer (MEGA-RAG multi-evidence) for the Nisamina chatbot.

Per M-P3.B. Wraps M-P2 MCP retrieval (lookup_headword) with explicit
multi-evidence rules + source-conflict resolution + tier-gated trust.

Used by 50_app/chatbot/orchestrator.py step 5 (retrieval).
Replaces ad-hoc inline retrieval; surfaces warnings for downstream prompt
context + post-screen.
"""

from .retriever import RAGRetriever, RAGResult
from .multi_evidence import (
    MultiEvidenceCheck,
    MIN_SOURCES_TIER_A,
    MIN_SOURCES_TIER_B,
    check_tier_evidence,
)
from .conflict_resolution import (
    SourcePriority,
    resolve_conflicts,
    tier_rank,
)


__all__ = [
    "RAGRetriever",
    "RAGResult",
    "MultiEvidenceCheck",
    "MIN_SOURCES_TIER_A",
    "MIN_SOURCES_TIER_B",
    "check_tier_evidence",
    "SourcePriority",
    "resolve_conflicts",
    "tier_rank",
]
