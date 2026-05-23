"""GarifunaBench — evaluation harness for Garifuna-language ML systems.

Per M-P3.G manifest. Templates:
- FormosanBench (Jun 2025) — endangered Austronesian languages MT/ASR
- MEGA-RAG (PMC 2025) — multi-evidence hallucination detection
- Rodríguez et al. 2025 — interpretability-based evaluation for low-resource

Plan v1 §6 rule 2: never self-graded. Held-out items require
director / commission / community grading; the
`engineer-scaffold-only-NOT-AUTHORITATIVE` marker on starter items
gates the harness from emitting an authoritative score.

This is a SCAFFOLD — not a complete bench. Curating real held-out
items and running it against any model is M-P3.A + ongoing community
work.
"""

from .harness import (
    BenchHarness,
    BenchItem,
    NotAuthoritativeError,
    load_fixture,
)
from .hallucination_detector import (
    HallucinationDetector,
    HallucinationReport,
    extract_garifuna_tokens,
)
from .tasks import (
    mt_en_to_cab,
    mt_cab_to_en,
    vocab_recall,
    conversation_quality,
    pronunciation_grading,
)


__all__ = [
    "BenchHarness",
    "BenchItem",
    "NotAuthoritativeError",
    "load_fixture",
    "HallucinationDetector",
    "HallucinationReport",
    "extract_garifuna_tokens",
    "mt_en_to_cab",
    "mt_cab_to_en",
    "vocab_recall",
    "conversation_quality",
    "pronunciation_grading",
]
