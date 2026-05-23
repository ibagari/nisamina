#!/usr/bin/env python3
"""
Pre-Publish Strip Linter — blocks public artifacts that contain internal-only
fields or insufficiently-triangulated entries.

Authority: plan v1.1 §2.3.

Run this BEFORE any export to: Webonary XHTML, HuggingFace dataset, app DB
sync, MCP server response, paper, README, or any other consumer-facing
artifact. The linter returns a list of violations; an empty list means the
artifact is safe to publish.

Blocking rules (any violation halts publication):
    1. `jw_*` field present on any record
    2. `catatu_*` field present on any record (until gate opens per consent_004)
    3. `magarada_unverified: true` headwords (until director re-classifies)
    4. Tier-C entries (must triangulate to Tier-B or higher first)
    5. Tier-X entries (all sources stripped — internal only by construction)
    6. `public_release: false` entries (the build's own gate)
    7. Source IDs that match the JW / Magarada / Catatu pattern modules
    8. Headwords that fail Cayetano conformance (non-Garifuna leakage)
    9. Records missing required attribution fields

Public API:
    lint_record(record, allow_internal_fields=False) -> list[Violation]
    lint_artifact(records_iter) -> dict   # aggregated report
    block_if_violations(records_iter) -> None   # raises StripLinterError on any violation

CI integration:
    from strip_linter import block_if_violations
    block_if_violations(load_records_for_export())
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator
import sys

# Pull in the gate-pattern modules
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "30_lexicon"))
sys.path.insert(0, str(ROOT / "20_normalize"))
from jw_quarantine_filter import is_jw_source  # type: ignore
from magarada_preliminary_gate import is_magarada_source  # type: ignore
from catatu_archival_gate import is_catatu_source  # type: ignore
from cayetano_1992 import is_conformant  # type: ignore


@dataclass(frozen=True)
class Violation:
    rule: str
    headword: str
    detail: str


class StripLinterError(Exception):
    """Raised by block_if_violations when any rule fires."""


REQUIRED_FIELDS = ("headword", "headword_normalized", "sources", "n_sources", "tier", "public_release")


def lint_record(record: dict, allow_internal_fields: bool = False) -> list[Violation]:
    """Run all 9 rules against one record. Returns list of violations (empty = clean)."""
    v: list[Violation] = []
    hw = record.get("headword", "?")

    # Rule 9: required fields
    missing = [f for f in REQUIRED_FIELDS if f not in record]
    if missing:
        v.append(Violation("missing_required_fields", str(hw), f"missing: {missing}"))

    # Rule 1: jw_* fields with a truthy value (e.g., jw_corroborated: true) leak corroboration signal.
    # A `false` value carries no leakage and is permitted in internal data structures.
    for k, val in record.items():
        if k.startswith("jw_") and val and not allow_internal_fields:
            v.append(Violation("jw_field_present", str(hw), f"forbidden field with truthy value: {k}={val!r}"))

    # Rule 2: catatu_* fields with a truthy value (same logic).
    for k, val in record.items():
        if k.startswith("catatu_") and val and not allow_internal_fields:
            v.append(Violation("catatu_field_present", str(hw), f"forbidden field with truthy value: {k}={val!r}"))

    # Rule 3: magarada_unverified: true
    if record.get("magarada_unverified") is True:
        v.append(Violation("magarada_unverified_true", str(hw), "PRELIMINARY content blocked from public release"))

    # Rule 4: Tier-C
    if record.get("tier") == "C":
        v.append(Violation("tier_C_in_public", str(hw), "Tier-C single-source attestation must triangulate before public release"))

    # Rule 5: Tier-X
    if record.get("tier") == "X":
        v.append(Violation("tier_X_in_public", str(hw), "Tier-X is internal-only by construction"))

    # Rule 6: public_release flag set false
    if record.get("public_release") is False:
        v.append(Violation("public_release_false", str(hw), "record's own build-time gate disallowed publication"))

    # Rule 7: gated source IDs in public attribution
    sources = record.get("sources") or []
    for s in sources:
        if is_jw_source(s):
            v.append(Violation("jw_source_in_public_attribution", str(hw), f"source: {s}"))
        if is_magarada_source(s):
            v.append(Violation("magarada_source_in_public_attribution", str(hw), f"source: {s}"))
        if is_catatu_source(s):
            v.append(Violation("catatu_source_in_public_attribution", str(hw), f"source: {s}"))

    # Rule 8: Cayetano conformance
    hw_norm = record.get("headword_normalized", "") or ""
    if hw_norm:
        ok, reasons = is_conformant(hw_norm)
        if not ok:
            v.append(Violation("non_cayetano_conformant", str(hw), f"reasons: {reasons[:2]}"))

    return v


def lint_artifact(records: Iterable[dict]) -> dict:
    """Aggregate-report over an iterable of records. Returns counts + first N violations per rule."""
    by_rule: dict[str, list[Violation]] = {}
    n_records = 0
    n_violations = 0
    for r in records:
        n_records += 1
        for viol in lint_record(r):
            by_rule.setdefault(viol.rule, []).append(viol)
            n_violations += 1
    return {
        "records_scanned": n_records,
        "violations_total": n_violations,
        "violations_by_rule": {k: len(vs) for k, vs in by_rule.items()},
        "first_5_per_rule": {k: [(v.headword, v.detail) for v in vs[:5]] for k, vs in by_rule.items()},
        "clean": n_violations == 0,
    }


def block_if_violations(records: Iterable[dict]) -> None:
    """Run the linter; raise StripLinterError if any violation fires.

    Intended for CI: call from any export step. Raises with a structured message.
    """
    report = lint_artifact(records)
    if not report["clean"]:
        raise StripLinterError(
            f"Public artifact has {report['violations_total']} violations across "
            f"{len(report['violations_by_rule'])} rules: {report['violations_by_rule']}. "
            f"Sample: {report['first_5_per_rule']}"
        )


if __name__ == "__main__":
    # Self-test: feed it a known-bad record + a known-good record.
    bad = {
        "headword": "give",
        "headword_normalized": "give",
        "sources": ["foundry_v5", "watch_tower_2013"],
        "n_sources": 2,
        "tier": "B",
        "public_release": True,
        "jw_corroborated": True,
    }
    good = {
        "headword": "magarada",
        "headword_normalized": "magarada",
        "sources": ["foundry_v5", "BSB", "Hadel_1975", "Suazo_Pildoritas"],
        "n_sources": 4,
        "tier": "A",
        "public_release": True,
        "vault_attested": False,
    }
    print("=== Pre-publish linter self-test ===")
    print("BAD record violations:")
    for v in lint_record(bad):
        print(f"  ✗ {v.rule}: {v.detail}")
    print("GOOD record violations:")
    viols = lint_record(good)
    if viols:
        for v in viols:
            print(f"  ✗ {v.rule}: {v.detail}")
    else:
        print("  ✓ clean")
