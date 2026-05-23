#!/usr/bin/env python3
"""build_foundry_v6.py — canonical foundry build script.

Authority: M-P1.E.fix manifest at 90_supervisor/manifests/M-P1E_fix_foundry_v6_v0_2.md.
Replaces /tmp/build_foundry_v6_v0_1_fixed.py (F-019 hardening).

Changes vs V0.1:
    1. Cayetano conformance filter — non-conformant headwords routed to Tier-X (F-016)
    2. Extraction-artifact rejector — newline/paren/bracket/comma headwords skipped (F-016)
    3. Per-row V_VAULT attestation — only Sentences_VERIFIED 01.ods counts as V_VAULT (F-017)
    4. Garifuna-side-only headword sources — never English/Spanish gloss text (F-016 root cause)
    5. Gate modules imported (jw_quarantine_filter, magarada_preliminary_gate, catatu_archival_gate) (F-018)
    6. Hardened into 60_training/scripts/ with self-hash recorded in BUILD_MANIFEST (F-019)

Usage:
    python3 build_foundry_v6.py --version v0_2
"""
from __future__ import annotations
import argparse
import json
import hashlib
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path

# Resolve nisamina-app root from this script's location
SCRIPT_PATH = Path(__file__).resolve()
APP_ROOT = SCRIPT_PATH.parent.parent.parent   # nisamina-app/
DRIVE_ROOT = APP_ROOT.parent                  # /Volumes/AI External/Nisamina_ai_Claude/

# Module imports
for sub in ("20_normalize", "30_lexicon"):
    p = str(APP_ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from cayetano_1992 import normalize, is_conformant  # type: ignore
from jw_quarantine_filter import is_jw_source        # type: ignore
from magarada_preliminary_gate import is_magarada_source  # type: ignore
from catatu_archival_gate import is_catatu_source    # type: ignore
from english_language_gate import is_likely_english  # type: ignore


# ----------------------------------------------------------------------
# Inputs (canonical paths)
# ----------------------------------------------------------------------

INPUTS = {
    "foundry_v5": DRIVE_ROOT / "garifuna-dictionary-master-foundry/outputs/trilingual_gold_v3/dictionary_master_v1_trilingual_release_v5_gold_refined.jsonl",
    "cross_attestation": APP_ROOT / "30_lexicon" / "CROSS_ATTESTATION_MATRIX.jsonl",
    "new_garifuna_words": APP_ROOT / "10_ingest" / "extracted" / "ods_csv" / "new_garifuna_words.jsonl",
    "lgd_new_headwords": APP_ROOT / "10_ingest" / "extracted" / "ods_csv" / "lgd_new_headwords.jsonl",
    "verified_sentences": APP_ROOT / "10_ingest" / "extracted" / "combined_report" / "verified_sentences.json",
}

# Strict V_VAULT (plan v1 §4 row 1 — verified_sentences_051826.ods / Sentences_VERIFIED 01.ods)
V_VAULT_SOURCE_FILES = {"Sentences_VERIFIED 01.ods"}

# Extraction-artifact rejection (run BEFORE cay_norm; before conformance check)
EXTRACTION_ARTIFACT_PATTERNS = [
    re.compile(r"\n|\r"),                     # newline
    re.compile(r"\bdefinition:", re.IGNORECASE),
    re.compile(r"\bdefn:", re.IGNORECASE),
    re.compile(r"\([\w\s,;]{3,}\)"),          # parenthetical gloss with content
    re.compile(r"\[[^\]]+\]"),                # bracket-quoted alt form
    re.compile(r";"),                         # semicolon (multi-form / definition leakage)
    re.compile(r",\s+\w"),                    # comma-space-letter (multi-form alt)
    re.compile(r"@"),
    re.compile(r"https?://"),
    re.compile(r"\bsee also\b", re.IGNORECASE),
    re.compile(r"\(proposed", re.IGNORECASE),
    re.compile(r"\(addition\)", re.IGNORECASE),
    re.compile(r"^a practical guide", re.IGNORECASE),
    re.compile(r"^\d+\.\s"),                  # leading "1. " enumeration (different from sense index "1 word")
]

MAX_HEADWORD_LEN = 30   # Garifuna headwords are typically <25 chars; >30 is suspicious


# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------

def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def is_extraction_artifact(s: str) -> tuple[bool, str | None]:
    """True if s shows extraction artifacts. Returns (is_artifact, reason)."""
    if not s or not isinstance(s, str):
        return True, "empty_or_non_string"
    if len(s) > MAX_HEADWORD_LEN:
        return True, f"exceeds_max_len_{MAX_HEADWORD_LEN}"
    if len(s.strip()) < 1:
        return True, "blank_after_strip"
    for p in EXTRACTION_ARTIFACT_PATTERNS:
        if p.search(s):
            return True, f"matches_{p.pattern!r}"
    return False, None


def cay_norm(word: str) -> str:
    """Cayetano-normalize a headword. Returns the normalized string (lowercased)."""
    if not word or not isinstance(word, str):
        return ""
    w = word.strip()
    if not w:
        return ""
    try:
        result = normalize(w)
        return (result["normalized"] or w).strip().lower()
    except Exception:
        return w.lower()


def is_row_v_vault(rec: dict) -> bool:
    """True iff the record has at least one source[].source_file in V_VAULT_SOURCE_FILES."""
    srcs = rec.get("sources") or []
    for s in srcs:
        if isinstance(s, dict) and s.get("source_file") in V_VAULT_SOURCE_FILES:
            return True
        # Fallback for legacy string sources
        if isinstance(s, str) and any(v in s for v in V_VAULT_SOURCE_FILES):
            return True
    return False


# ----------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------

def build(version: str, out_dir: Path, manifest_id: str = "M-P1.E.fix") -> dict:
    print(f"=== build_foundry_v6 version={version} ===")
    out_dir.mkdir(parents=True, exist_ok=True)
    input_sha = {k: sha256_path(p) for k, p in INPUTS.items()}

    # Load
    foundry_v5 = [json.loads(l) for l in open(INPUTS["foundry_v5"]) if l.strip()]
    new_words = [json.loads(l) for l in open(INPUTS["new_garifuna_words"]) if l.strip()]
    lgd_words = [json.loads(l) for l in open(INPUTS["lgd_new_headwords"]) if l.strip()]
    with open(INPUTS["verified_sentences"]) as f:
        vs_data = json.load(f)
    verified_records = vs_data.get("records", [])

    # Cross-attestation aggregated per Cayetano-normalized key
    attestation: dict[str, set[str]] = {}
    cross_skipped = 0
    with open(INPUTS["cross_attestation"]) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            raw_key = r.get("lexical_key", "")
            is_art, _ = is_extraction_artifact(raw_key)
            if is_art:
                cross_skipped += 1
                continue
            key_norm = cay_norm(raw_key)
            if not key_norm:
                cross_skipped += 1
                continue
            attestation.setdefault(key_norm, set()).update(r.get("sources", []))

    print(f"  foundry_v5: {len(foundry_v5)} sense-level entries")
    print(f"  cross_attestation: {len(attestation)} unique normalized keys ({cross_skipped} artifact-skipped)")
    print(f"  new_garifuna_words: {len(new_words)} records")
    print(f"  lgd: {len(lgd_words)} records")
    print(f"  verified_sentences: {len(verified_records)} records")

    # Aggregate per Cayetano-normalized headword
    agg: dict[str, dict] = defaultdict(lambda: {
        "headword": None, "headword_normalized": None,
        "senses": [], "sources": set(),
        "vault_attested": False, "bsb_attested": False,
        "examples": [],
    })
    artifact_skipped = 0
    quarantine_examples: list[dict] = []  # first N artifacts for BUILD_MANIFEST

    def maybe_quarantine(hw_raw: str, source_label: str, reason: str):
        nonlocal artifact_skipped
        artifact_skipped += 1
        if len(quarantine_examples) < 50:
            quarantine_examples.append({"raw": hw_raw[:100], "source": source_label, "reason": reason})

    # 1. foundry v5 (spine)
    fv5_new = 0
    for rec in foundry_v5:
        hw = rec.get("garifuna_headword", "") or rec.get("garifuna_headword_key", "")
        is_art, reason = is_extraction_artifact(hw)
        if is_art:
            maybe_quarantine(hw, "foundry_v5", reason)
            continue
        hw_norm = cay_norm(hw)
        if not hw_norm:
            continue
        a = agg[hw_norm]
        if a["headword"] is None:
            a["headword"] = hw
            a["headword_normalized"] = hw_norm
            fv5_new += 1
        a["sources"].update(rec.get("source_families", []) or [])
        a["sources"].add("foundry_v5")
        a["senses"].append({
            "cluster_id": rec.get("cluster_id"),
            "sense_index": rec.get("sense_index"),
            "gloss_en": rec.get("english_gloss_short_effective") or rec.get("english_gloss_short_source"),
            "gloss_es": rec.get("spanish_gloss_canonical"),
            "synonyms": rec.get("english_synonyms_effective"),
            "source": "foundry_v5",
        })
    print(f"  foundry_v5 contributed: {fv5_new} unique normalized headwords → {len(agg)} total")

    # 2. cross-attestation
    cross_new = 0
    for key, srcs in attestation.items():
        a = agg[key]
        if a["headword"] is None:
            a["headword"] = key
            a["headword_normalized"] = key
            cross_new += 1
        a["sources"].update(srcs)
    print(f"  cross_attestation: {cross_new} NEW headwords")

    # 3. new_garifuna_words
    ngw_new = 0
    for rec in new_words:
        hw = rec.get("Garifuna Word", "")
        is_art, reason = is_extraction_artifact(hw)
        if is_art:
            maybe_quarantine(hw, "new_garifuna_words", reason)
            continue
        hw_norm = cay_norm(hw)
        if not hw_norm:
            continue
        a = agg[hw_norm]
        if a["headword"] is None:
            a["headword"] = hw
            a["headword_normalized"] = hw_norm
            ngw_new += 1
        a["sources"].add("new_garifuna_words_expert")
        morph = rec.get("Morphology", "") or ""
        if "BSB" in morph or "verse" in morph.lower():
            a["bsb_attested"] = True
            a["sources"].add("BSB")
        a["senses"].append({
            "cluster_id": None, "sense_index": None,
            "gloss_en": rec.get("English Gloss"), "gloss_es": None,
            "pos": rec.get("Part of Speech"), "noun_class": rec.get("Noun Class"),
            "morphology": rec.get("Morphology"), "source": "new_garifuna_words_expert",
        })
        if rec.get("Garifuna Sentence"):
            a["examples"].append({
                "gar": rec.get("Garifuna Sentence"),
                "en": rec.get("English Translation.1"),
                "source": "new_garifuna_words_expert",
                "provenance": morph,
            })
    print(f"  new_garifuna_words: {ngw_new} NEW headwords")

    # 4. lgd
    lgd_new = 0
    for rec in lgd_words:
        hw = rec.get("Canonical_Form") or rec.get("New_Headword", "")
        is_art, reason = is_extraction_artifact(hw)
        if is_art:
            maybe_quarantine(hw, "lgd_new_headwords", reason)
            continue
        hw_norm = cay_norm(hw)
        if not hw_norm:
            continue
        a = agg[hw_norm]
        if a["headword"] is None:
            a["headword"] = hw
            a["headword_normalized"] = hw_norm
            lgd_new += 1
        a["sources"].add("lgd_living_dictionary")
        a["senses"].append({
            "cluster_id": None, "sense_index": None,
            "gloss_en": None, "gloss_es": None,
            "source_headword": rec.get("Source_Headword"),
            "source": "lgd_living_dictionary",
        })
        if rec.get("Garifuna_Sentence_Orig"):
            a["examples"].append({
                "gar": rec.get("Garifuna_Sentence_Orig"),
                "en": rec.get("Translation_Sentence_Orig"),
                "source": "lgd_living_dictionary",
            })
    print(f"  lgd: {lgd_new} NEW headwords")

    # 5. verified_sentences — STRICT per-row V_VAULT
    vs_new = 0
    vault_recs = 0
    for rec in verified_records:
        hw = rec.get("canonical_form") or rec.get("headword", "")
        is_art, reason = is_extraction_artifact(hw)
        if is_art:
            maybe_quarantine(hw, "verified_sentences", reason)
            continue
        hw_norm = cay_norm(hw)
        if not hw_norm:
            continue
        a = agg[hw_norm]
        if a["headword"] is None:
            a["headword"] = hw
            a["headword_normalized"] = hw_norm
            vs_new += 1
        is_vault = is_row_v_vault(rec)
        if is_vault:
            a["vault_attested"] = True
            a["sources"].add("V_VAULT_director_attested")
            vault_recs += 1
            a["sources"].add("verified_sentences_VERIFIED_01")
        else:
            a["sources"].add("verified_sentences_2026_05_18")
        a["senses"].append({
            "cluster_id": None, "sense_index": None,
            "gloss_en": rec.get("english_gloss"), "gloss_es": None,
            "pos": rec.get("part_of_speech"), "noun_class": rec.get("noun_class"),
            "morphology": rec.get("morphology"),
            "source": ("verified_sentences_VERIFIED_01" if is_vault else "verified_sentences_2026_05_18"),
        })
        if rec.get("garifuna_sentence"):
            a["examples"].append({
                "gar": rec.get("garifuna_sentence"),
                "en": rec.get("english_translation"),
                "source": ("verified_sentences_VERIFIED_01" if is_vault else "verified_sentences_2026_05_18"),
            })
    print(f"  verified_sentences: {vs_new} NEW headwords; {vault_recs} V_VAULT-attested records (STRICT)")
    print(f"  extraction-artifact-skipped: {artifact_skipped}")

    # ----------------------------------------------------------------------
    # Gate enforcement + tier classification + conformance filter
    # ----------------------------------------------------------------------
    print("\n=== Gate enforcement + tier classification + Cayetano conformance filter ===")
    jw_stripped = magarada_stripped = catatu_stripped = 0
    non_conformant_total = 0
    tier_counts: Counter = Counter()
    source_counts: Counter = Counter()
    public_count = 0
    final: list[dict] = []

    for hw_norm, a in agg.items():
        if not a["headword"]:
            continue

        # Strip gated sources (JW + Magarada + Catatu)
        srcs = set(a["sources"])
        jw_srcs = {s for s in srcs if is_jw_source(s)}
        mag_srcs = {s for s in srcs if is_magarada_source(s)}
        cat_srcs = {s for s in srcs if is_catatu_source(s)}
        jw_corr = bool(jw_srcs); mag_corr = bool(mag_srcs); cat_corr = bool(cat_srcs)
        if jw_corr: jw_stripped += 1
        if mag_corr: magarada_stripped += 1
        if cat_corr: catatu_stripped += 1
        srcs -= jw_srcs; srcs -= mag_srcs; srcs -= cat_srcs

        # Conformance check (Cayetano grapheme-level)
        ok, reasons = is_conformant(a["headword_normalized"])
        non_conf = not ok
        # English-language check (catches English words with Cayetano-permitted letters)
        is_eng, eng_reason = is_likely_english(a["headword_normalized"])
        contamination = non_conf or is_eng
        if contamination:
            non_conformant_total += 1

        # Tier classification
        n = len(srcs)
        if contamination:
            tier = "X"  # non-conformant OR likely-English → internal only
        elif a["vault_attested"]:
            tier = "5"
        elif n >= 4:
            tier = "A"
        elif n >= 2:
            tier = "B"
        elif n >= 1:
            tier = "C"
        else:
            tier = "X"  # all sources stripped

        # public_release: NOT contamination AND tier in {5,A,B} AND (n>=2 OR tier==5)
        public_release = (
            (not contamination)
            and tier in ("5", "A", "B")
            and (n >= 2 or tier == "5")
        )

        tier_counts[tier] += 1
        if public_release:
            public_count += 1
        for s in srcs:
            source_counts[s] += 1

        rec_out = {
            "headword": a["headword"],
            "headword_normalized": a["headword_normalized"],
            "senses": a["senses"],
            "examples": a["examples"],
            "sources": sorted(srcs),
            "n_sources": n,
            "tier": tier,
            "vault_attested": a["vault_attested"],
            "bsb_attested": a["bsb_attested"],
            "jw_corroborated": jw_corr,
            "magarada_corroborated": mag_corr,
            "catatu_corroborated": cat_corr,
            "public_release": public_release,
            "non_conformant": non_conf,
            "likely_english": is_eng,
        }
        if non_conf:
            rec_out["non_conformant_reasons"] = reasons[:5]
        if is_eng:
            rec_out["english_gate_reason"] = eng_reason
        final.append(rec_out)

    print(f"  JW-stripped: {jw_stripped} headwords (flagged jw_corroborated, sources removed)")
    print(f"  Magarada-stripped: {magarada_stripped} headwords")
    print(f"  Catatu-stripped: {catatu_stripped} headwords")
    print(f"  Contamination routed to Tier-X (non-Cayetano + likely-English): {non_conformant_total} headwords")
    print(f"  TOTAL: {len(final)} | tiers: {dict(tier_counts)} | public_release: {public_count}")

    # Sort by tier + headword
    tier_order = {"5": 0, "A": 1, "B": 2, "C": 3, "X": 4}
    final.sort(key=lambda r: (tier_order.get(r["tier"], 9), r["headword_normalized"]))

    # ----------------------------------------------------------------------
    # Outputs
    # ----------------------------------------------------------------------
    out_jsonl = out_dir / f"foundry_v6_{version}.jsonl"
    out_summary = out_dir / f"foundry_v6_{version}.summary.md"
    out_manifest = out_dir / f"foundry_v6_{version}.BUILD_MANIFEST.json"

    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in final:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Summary
    with open(out_summary, "w", encoding="utf-8") as f:
        f.write(f"# foundry_v6 {version} — Build Summary\n\n")
        f.write(f"**Built:** {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"**Manifest:** {manifest_id}\n")
        f.write(f"**Build script:** `60_training/scripts/build_foundry_v6.py`\n\n")
        f.write(f"## Totals\n\n")
        f.write(f"- Total unique normalized headwords: **{len(final)}**\n")
        f.write(f"- Public-release eligible: **{public_count}** ({100*public_count/len(final):.1f}% of total)\n")
        f.write(f"- Extraction-artifact-skipped at ingest: **{artifact_skipped}**\n")
        f.write(f"- Non-Cayetano-conformant routed to Tier-X: **{non_conformant_total}**\n")
        f.write(f"- V_VAULT-attested records (strict per-row): **{vault_recs}** source rows → **{tier_counts.get('5',0)}** unique Tier-5 headwords\n\n")
        f.write(f"## Tier distribution\n\n| Tier | Definition | Count | Public-eligible |\n|---|---|---:|---:|\n")
        defs = {
            "5": "Vault (per-row V_VAULT_director_attested via Sentences_VERIFIED 01.ods)",
            "A": "4+ public sources (gates applied)",
            "B": "2-3 public sources",
            "C": "1 public source (internal-only until triangulated)",
            "X": "all sources stripped OR non-Cayetano-conformant (internal-only)",
        }
        for t in ["5","A","B","C","X"]:
            pub = tier_counts.get(t, 0) if t in ("5", "A", "B") else 0
            f.write(f"| **{t}** | {defs[t]} | {tier_counts.get(t,0)} | {pub} |\n")
        f.write(f"\n## Strict output stripping (v1.1 §1.2 + §1.5 + §1.7 enforcement)\n\n")
        f.write(f"- JW source IDs stripped: **{jw_stripped}** headwords flagged `jw_corroborated: true` (internal-only)\n")
        f.write(f"- Magarada PRELIMINARY source IDs stripped: **{magarada_stripped}** headwords\n")
        f.write(f"- Catatu source IDs stripped: **{catatu_stripped}** headwords\n\n")
        f.write(f"## Top 20 source contributions (after stripping)\n\n| Source | Count |\n|---|---:|\n")
        for s, c in source_counts.most_common(20):
            f.write(f"| `{s}` | {c} |\n")
        f.write(f"\n## Per-input contribution\n\n| Input | Records loaded | NEW headwords added |\n|---|---:|---:|\n")
        f.write(f"| foundry_v5 | {len(foundry_v5)} | (spine; {fv5_new} unique post-dedup) |\n")
        f.write(f"| cross_attestation | {len(attestation)} | {cross_new} |\n")
        f.write(f"| new_garifuna_words | {len(new_words)} | {ngw_new} |\n")
        f.write(f"| lgd | {len(lgd_words)} | {lgd_new} |\n")
        f.write(f"| verified_sentences | {len(verified_records)} | {vs_new} ({vault_recs} V_VAULT) |\n")

    # BUILD_MANIFEST
    out_jsonl_sha = sha256_path(out_jsonl)
    out_summary_sha = sha256_path(out_summary)
    script_sha = sha256_path(SCRIPT_PATH)
    build_meta = {
        "build_id": f"foundry_v6_{version}",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "manifest_ref": manifest_id,
        "build_script": {
            "path": str(SCRIPT_PATH.relative_to(DRIVE_ROOT)),
            "sha256": script_sha,
        },
        "changes_vs_v0_1": [
            "Cayetano conformance filter applied (F-016 part 1) — non-conformant headwords routed to Tier-X with reasons",
            "English-language gate applied (F-016 part 2) — /usr/share/dict/words match OR geminate-loan pattern → Tier-X",
            "Extraction-artifact rejector at ingest (F-016 part 3) — newline/paren/bracket/comma/definition leaks dropped",
            "Strict per-row V_VAULT attestation (F-017) — only Sentences_VERIFIED 01.ods rows count",
            "Gate modules imported from 30_lexicon/{jw_quarantine_filter, magarada_preliminary_gate, catatu_archival_gate, english_language_gate}.py (F-018)",
            "Hardened build script into 60_training/scripts/ with self-hash (F-019)",
        ],
        "inputs": {k: {"path": str(v), "sha256": input_sha[k]} for k, v in INPUTS.items()},
        "outputs": {
            out_jsonl.name: {"sha256": out_jsonl_sha, "records": len(final)},
            out_summary.name: {"sha256": out_summary_sha},
        },
        "tier_distribution": {k: tier_counts.get(k, 0) for k in ["5", "A", "B", "C", "X"]},
        "public_release_count": public_count,
        "vault_attested_unique_headwords": tier_counts.get("5", 0),
        "vault_attested_source_rows": vault_recs,
        "stripping": {
            "jw_stripped": jw_stripped,
            "magarada_stripped": magarada_stripped,
            "catatu_stripped": catatu_stripped,
        },
        "extraction_artifact_skipped": artifact_skipped,
        "non_conformant_to_tier_X": non_conformant_total,
        "quarantine_examples_first_50": quarantine_examples,
    }
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(build_meta, f, indent=2, ensure_ascii=False)

    print(f"\nWROTE:\n  {out_jsonl}\n  {out_summary}\n  {out_manifest}")
    return build_meta


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", default="v0_2", help="output version suffix (default v0_2)")
    p.add_argument("--out-dir", default=str(APP_ROOT / "30_lexicon" / "foundry_v6"))
    p.add_argument("--manifest", default="M-P1.E.fix")
    args = p.parse_args()
    build(args.version, Path(args.out_dir), manifest_id=args.manifest)


if __name__ == "__main__":
    main()
