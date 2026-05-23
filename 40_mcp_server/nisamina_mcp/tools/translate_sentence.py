"""MCP tool: translate_sentence — per-token glosses for a Garifuna sentence.

Cayetano-normalizes the input, tokenizes on whitespace + punctuation, and
runs `lookup_headword` (exact then fuzzy fallback) per token. Returns a list
of (token → list[gloss + source]) entries plus the normalized sentence.

No machine translation invention — every gloss comes from the foundry. Tokens
without a match are returned as `unmatched: true` so the LLM client can
report transparently rather than hallucinate.
"""
from __future__ import annotations
import re

from ..egress import enforce_egress
from ..foundry_loader import FoundryIndex
from .cayetano_normalize import cayetano_normalize
from .lookup_headword import lookup_headword

_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿñÑüÜ'\-]+", re.UNICODE)


def translate_sentence(index: FoundryIndex, sentence: str, fuzzy_fallback: bool = True) -> dict:
    """Per-token gloss of a Garifuna sentence using the foundry.

    Args:
        index: a loaded `FoundryIndex`.
        sentence: input Garifuna sentence.
        fuzzy_fallback: if True, tokens with no exact match get a fuzzy
                        lookup (top 3 close matches, cutoff 0.75).

    Returns:
        Dict with:
          - input: original sentence
          - normalized: Cayetano-normalized sentence
          - tokens: list of {token, normalized_token, matched_records: [...],
                              fuzzy_candidates: [...], unmatched: bool}
                    matched_records carries the same foundry schema as
                    lookup_headword. fuzzy_candidates only populated if
                    exact failed AND fuzzy_fallback=True.
    """
    if not isinstance(sentence, str):
        raise TypeError(f"sentence must be str, got {type(sentence).__name__}")

    # Sentence-level normalization (applied word-by-word via the tool)
    norm_words: list[str] = []
    for tok in _TOKEN_RE.findall(sentence):
        norm_words.append(cayetano_normalize(tok)["normalized"])
    normalized_sentence = " ".join(norm_words)

    token_results: list[dict] = []
    for raw_tok in _TOKEN_RE.findall(sentence):
        norm_tok = cayetano_normalize(raw_tok)["normalized"]
        exact = lookup_headword(index, norm_tok, mode="exact", limit=3)
        fuzzy: list[dict] = []
        if not exact and fuzzy_fallback:
            fuzzy = index.lookup_fuzzy(norm_tok, limit=3, cutoff=0.75)
            # Run the fuzzy through egress too (lookup_fuzzy is a direct index
            # call, so the egress wrapper wasn't invoked yet).
            fuzzy = enforce_egress(fuzzy, context="translate_sentence:fuzzy")
        token_results.append({
            "token": raw_tok,
            "normalized_token": norm_tok,
            "matched_records": exact,
            "fuzzy_candidates": fuzzy,
            "unmatched": (not exact and not fuzzy),
        })

    report = {
        "input": sentence,
        "normalized": normalized_sentence,
        "tokens": token_results,
    }
    # Top-level wrapper run for uniformity; inner lists already ran egress.
    return enforce_egress(report, context="translate_sentence")
