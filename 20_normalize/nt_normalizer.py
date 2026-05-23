#!/usr/bin/env python3
"""
NT Normalizer — Cayetano-normalize NWT-derived text for INTERNAL corroboration
only, never for public release or for training-corpus inclusion.

Authority: plan v1 §5.2 ("Implemented in 20_normalize/nt_normalizer.py with raw
text never exiting 10_ingest"), plan v1.1 §1.2, jw_remining_policy.md.

Operational invariant:
    Raw NWT text MUST NOT leave 10_ingest. This module accepts a path under
    10_ingest/, applies Cayetano normalization, and returns the derived text
    in-memory only. It REFUSES to write anywhere except a 10_ingest-scoped
    output directory. Callers wanting headword corroboration must use
    `extract_headwords_for_corroboration()` which yields strings + never
    persists raw text.

Status: STUB for M-P1.D. Real implementation lands when the Religious 84GB
provenance audit runs (M-P1.D). This stub:
    - Defines the public API contract
    - Enforces the path safety invariant (refuses to write outside 10_ingest)
    - Exposes the Cayetano integration point
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterator
import sys

# Cayetano normalizer (sibling module)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cayetano_1992 import normalize, is_conformant  # type: ignore


INGEST_ROOT = Path("/Volumes/AI External/Nisamina_ai_Claude/nisamina-app/10_ingest")


def _assert_within_ingest(p: Path) -> None:
    """Raise unless path resolves inside 10_ingest/. Defense against raw-text leakage."""
    rp = p.resolve()
    if INGEST_ROOT.resolve() not in rp.parents and rp != INGEST_ROOT.resolve():
        raise PermissionError(
            f"NT normalizer refuses to operate on {rp} — must be under {INGEST_ROOT}. "
            "Per jw_remining_policy.md: NWT raw text never leaves 10_ingest."
        )


def normalize_nt_text(text: str) -> dict:
    """Cayetano-normalize a single NT string. Returns the dict from cayetano_1992.normalize()."""
    return normalize(text)


def extract_headwords_for_corroboration(input_path: Path) -> Iterator[str]:
    """Yield Cayetano-normalized conformant headword candidates from an NT source file.

    Path must be under 10_ingest/. Output is in-memory strings; nothing is persisted.
    Implementation deferred to M-P1.D — this stub enforces the safety invariant + raises NotImplementedError.
    """
    _assert_within_ingest(Path(input_path))
    raise NotImplementedError(
        "extract_headwords_for_corroboration is a stub until M-P1.D opens. "
        "When M-P1.D begins, implement: tokenize NT text → cay_norm each token → "
        "filter via is_conformant → yield conformant unique strings. Caller must "
        "feed these into jw_quarantine_filter triangulation flow, not into the "
        "public foundry build."
    )


def normalize_to_ingest_only(input_path: Path, output_path: Path) -> None:
    """Write Cayetano-normalized NT text to a 10_ingest-scoped output path.

    Refuses if either input or output escapes 10_ingest/.
    """
    _assert_within_ingest(Path(input_path))
    _assert_within_ingest(Path(output_path))
    raise NotImplementedError(
        "normalize_to_ingest_only is a stub until M-P1.D opens. "
        "Path safety invariant is enforced; the body implements line-by-line Cayetano "
        "normalize() over the input + writes derivative to the output (which must remain "
        "in 10_ingest/ per policy)."
    )


if __name__ == "__main__":
    # Self-test: confirm the safety invariant rejects out-of-scope paths.
    print("=== NT normalizer safety invariant self-test ===")
    bad_paths = [
        Path("/tmp/nwt_dump.txt"),
        Path("/Volumes/AI External/Nisamina_ai_Claude/30_lexicon/something.txt"),
        Path("/Volumes/AI External/Nisamina_ai_Claude/99_publish/leak.txt"),
    ]
    for p in bad_paths:
        try:
            _assert_within_ingest(p)
            print(f"  ✗ {p} — should have been rejected")
        except PermissionError as e:
            print(f"  ✓ {p} — correctly rejected: {str(e)[:80]}...")
    print(f"  ✓ INGEST_ROOT = {INGEST_ROOT}")
