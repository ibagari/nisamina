"""RAG retriever — MEGA-RAG multi-evidence + augmented context builder.

Per M-P3.B §3. Wraps lookup_headword + cite_sources with multi-evidence
checks (`multi_evidence.check_tier_evidence`) and conflict resolution
(`conflict_resolution.resolve_conflicts`) to produce a `RAGResult` ready
for the orchestrator's augmented-prompt builder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RAGResult:
    """RAG retrieval verdict + augmented-context substrate."""

    records: list[dict] = field(default_factory=list)
    token_evidence: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    augmented_context: str = ""
    confidence: float = 1.0  # aggregate; 1.0 if all records authoritative

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)

    @property
    def n_records(self) -> int:
        return len(self.records)


class RAGRetriever:
    """High-level retrieval combining lookup + multi-evidence + conflict resolution.

    `foundry_index` is a `FoundryIndex` from `nisamina_mcp.foundry_loader.load()`.
    """

    def __init__(self, foundry_index) -> None:
        self.foundry = foundry_index

    def retrieve(
        self,
        query: str,
        top_n: int = 5,
        min_token_length: int = 3,
        include_fuzzy_fallback: bool = True,
    ) -> RAGResult:
        """Run the MEGA-RAG retrieval pipeline.

        Steps:
          1. Extract candidate Garifuna tokens from `query`.
          2. For each token: lookup_headword exact → fuzzy fallback if no hit.
          3. Apply per-record multi-evidence check (tier-gated).
          4. Resolve conflicts (dedup by headword, sort by tier-rank).
          5. Top-N selection.
          6. Build augmented_context block.
          7. Compute aggregate confidence.

        Returns: RAGResult.
        """
        from ..tools.lookup_headword import lookup_headword
        from .multi_evidence import check_tier_evidence
        from .conflict_resolution import resolve_conflicts, tier_rank

        # Lazy-import so this module is independent of garifuna_bench location
        import sys
        from pathlib import Path
        bench_path = Path(__file__).resolve().parents[3] / "80_validation"
        if str(bench_path) not in sys.path:
            sys.path.insert(0, str(bench_path))
        from garifuna_bench.hallucination_detector import extract_garifuna_tokens

        warnings: list[str] = []
        all_records: list[dict] = []
        token_evidence: dict[str, list[str]] = {}

        # 1. Extract tokens
        tokens = extract_garifuna_tokens(query)
        tokens = [t for t in tokens if len(t) >= min_token_length]

        # 2. Retrieve per token
        for tok in tokens[:10]:  # cap to avoid runaway
            hits = lookup_headword(self.foundry, tok, mode="exact")
            if not hits and include_fuzzy_fallback:
                hits = lookup_headword(self.foundry, tok, mode="fuzzy", limit=2)
            for rec in hits[:2]:
                all_records.append(rec)
                token_evidence.setdefault(tok, []).extend(rec.get("sources", []))

        # 3. Multi-evidence check per record
        authoritative_count = 0
        for rec in all_records:
            verdict = check_tier_evidence(rec)
            if verdict.needs_flag and verdict.flag_message:
                warnings.append(verdict.flag_message)
            if verdict.is_authoritative:
                authoritative_count += 1

        # 4. Resolve conflicts
        kept, conflict_warnings = resolve_conflicts(all_records)
        warnings.extend(conflict_warnings)

        # 5. Top-N selection (already sorted by resolve_conflicts)
        kept = kept[:top_n]

        # 6. Build augmented context for prompt
        augmented = self._format_context(kept, warnings)

        # 7. Aggregate confidence (authoritative-records / total)
        confidence = 1.0
        if all_records:
            confidence = authoritative_count / len(all_records)

        return RAGResult(
            records=kept,
            token_evidence=token_evidence,
            warnings=warnings,
            augmented_context=augmented,
            confidence=confidence,
        )

    def _format_context(
        self,
        records: list[dict],
        warnings: list[str],
    ) -> str:
        """Render the records + warnings as a prompt-ready context block."""
        if not records:
            return "(no foundry matches for the user's tokens)"

        lines: list[str] = []
        for rec in records:
            hw = rec.get("headword_normalized", "?")
            tier = rec.get("tier", "?")
            n_sources = rec.get("n_sources", 0)
            sources = rec.get("sources", [])
            sources_short = ", ".join(s for s in sources[:3])
            senses = rec.get("senses") or []
            gloss = (senses[0].get("gloss_en") if senses else "") or ""
            lines.append(
                f"- {hw} (Tier-{tier}, {n_sources} sources: {sources_short}) — "
                f"{gloss[:120]}"
            )

        block = "\n".join(lines)
        if warnings:
            warn_block = "\n".join(f"  ⚠ {w}" for w in warnings[:5])
            block = f"{block}\n\nWARNINGS:\n{warn_block}"
        return block
