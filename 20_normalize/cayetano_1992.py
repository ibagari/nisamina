#!/usr/bin/env python3
"""
Cayetano 1992 — Garifuna orthography canonical module.

This module encodes the rules from E. Roy Cayetano, *Towards a Common Garifuna
Orthography*, National Garifuna Council of Belize, June 1992 (the regional
standardization document).

Public API:
    ALPHABET                       — frozenset of canonical graphemes
    SIMPLE_ORAL_VOWELS, SIMPLE_NASAL_VOWELS, COMPOUND_VOWELS — sets
    DISALLOWED_PATTERNS            — regex list, each with rationale
    REPLACEMENT_RULES              — ordered list of (pattern, replacement, why)
    syllabify(word)                — return list[str] of syllables (best-effort)
    stress_pattern(word)           — return (expected_stress_index, has_irregular)
    is_conformant(word)            — (bool, list[reason])
    normalize(word)                — return Cayetano-normalized form + change-log
    audit_corpus(iterable_of_words)— return aggregated KPIs

This module is the SUPREME authority on what constitutes valid Garifuna writing
for Nisamina purposes.
"""
from __future__ import annotations
import re
import unicodedata
from typing import Iterable

# ---------- Section 1: alphabet ----------

CONSONANTS = ("b", "d", "ch", "f", "g", "h", "j", "k", "l", "m",
              "n", "p", "r", "s", "t", "w", "y", "ñ")
# Notes: `j` is a regional alternative to `h` (Honduras / Guatemala). Both are accepted in conformance,
# but the canonical default is `h`.

SIMPLE_ORAL_VOWELS = ("i", "e", "a", "o", "u", "ü")
SIMPLE_NASAL_VOWELS = ("in", "en", "an", "on", "un", "ün")  # vowel + nasal-coda n

COMPOUND_VOWELS = (
    "ie", "ia", "yü", "iu", "wü",
    "ua", "ui", "ue",
    "ei", "ou", "au", "aü",
)

# Stress vowels (acute-accented) — only used to mark exceptions
STRESS_VOWELS = ("á", "é", "í", "ó", "ú", "ǘ")
STRESS_VOWELS_TO_PLAIN = {"á":"a","é":"e","í":"i","ó":"o","ú":"u","ǘ":"ü"}

# Full alphabet: all graphemes that may legitimately appear in Cayetano writing
# (in lowercase; the writing system itself uses initial capitals on proper nouns)
ALPHABET = frozenset(
    list(CONSONANTS) +
    list(SIMPLE_ORAL_VOWELS) +
    ["ñ"] +    # palatal nasal already in CONSONANTS but listed for clarity
    list(STRESS_VOWELS) +
    ["'"]      # apostrophe (occasional in glosses; tolerated)
)

# ---------- Section 2: disallowed patterns (with rationale) ----------

DISALLOWED_PATTERNS = [
    # (pattern, why)
    (re.compile(r"qu", re.IGNORECASE),
     "`qu` is Spanish-orthography for /k/; Cayetano uses `k`."),
    (re.compile(r"c(?!h)", re.IGNORECASE),
     "`c` (not in `ch`) is dropped; Cayetano writes /k/ as `k`."),
    (re.compile(r"(?<=[bcdfghjklmnpqrstvwxyzñ])ai", re.IGNORECASE),
     "Internal `ai` after consonant is not phonemically distinct from `ei`; Cayetano writes `ei`."),
    # x / z / v are not in the Garifuna alphabet at all
    (re.compile(r"[xzv]", re.IGNORECASE),
     "Letter not in Cayetano alphabet (likely Spanish/English loan signal)."),
]

# ---------- Section 3: replacement rules (apply in order during normalization) ----------

REPLACEMENT_RULES = [
    # NOTE: order matters. Each is (compiled regex, replacement, rationale)
    (re.compile(r"qu", re.IGNORECASE), "k",
     "Cayetano §3: drop `qu`, write /k/ as `k`."),
    # `c` → `k` ONLY when not part of `ch`
    (re.compile(r"c(?!h)", re.IGNORECASE), "k",
     "Cayetano §3: drop `c`, write /k/ as `k`. `ch` remains intact."),
    # Internal `ai` → `ei` (but only where `ai` is actually a diphthong; we apply conservatively)
    (re.compile(r"(?<=[bcdfghjklmnpqrstvwyzñ])ai", re.IGNORECASE), "ei",
     "Cayetano §3: [ai] and [ei] are not distinct; write `ei`."),
    # `ao` (Taylor) → `aü` only at word end
    (re.compile(r"ao(?=$|\s)", re.IGNORECASE), "aü",
     "Cayetano §3: Taylor's `ao` written as `aü`."),
]

VOWELS_SET = set("aeiouüáéíóúǘ")
CONSONANTS_SET = set("bdfghjklmnprstwyñ")  # exclude digraphs c/ch which we handle separately

# ---------- Section 4: syllabification (heuristic) ----------

def _strip_accent(ch: str) -> str:
    """Strip a single acute accent from a single char."""
    return STRESS_VOWELS_TO_PLAIN.get(ch, ch)

def _is_vowel(ch: str) -> bool:
    return ch.lower() in VOWELS_SET

def syllabify(word: str) -> list[str]:
    """Best-effort Garifuna syllabification.
    Rules (Cayetano-inspired):
      - `ch` is treated as a single consonant.
      - Vowels form syllable nuclei; consonants attach to the right (CV preferred).
      - Compound vowels (ie/ia/iu/ua/ui/ue/ei/ou/au/aü) stay together as one nucleus.
      - `n` at end of syllable indicates nasalization (stays with nucleus).
    """
    w = word.lower().strip()
    if not w:
        return []
    # Tokenize into graphemes (treating ch as one unit)
    units: list[str] = []
    i = 0
    while i < len(w):
        # check for 'ch' digraph
        if w[i:i+2] == "ch":
            units.append("ch"); i += 2; continue
        units.append(w[i]); i += 1

    # Find vowel-nuclei (group adjacent vowels per COMPOUND_VOWELS heuristic)
    nuclei: list[tuple[int, int]] = []  # list of (start_idx, end_idx) in units
    n = len(units)
    i = 0
    while i < n:
        if _is_vowel(units[i]):
            j = i
            # Consume up to 2 more vowels if they form a recognized compound
            while j + 1 < n and _is_vowel(units[j+1]):
                pair = (_strip_accent(units[j]) + _strip_accent(units[j+1])).lower()
                if pair in COMPOUND_VOWELS:
                    j += 1
                    continue
                # If next is the same vowel as current (e.g., "uu") break the nucleus
                break
            nuclei.append((i, j))
            i = j + 1
        else:
            i += 1

    if not nuclei:
        return [w]

    # Walk through, assigning consonants. Onset prefers CV; max 1 consonant onset per syllable.
    syllables: list[str] = []
    last_end = -1
    for k, (s, e) in enumerate(nuclei):
        # onset: any consonants between last_end+1 and s
        onset_start = last_end + 1
        onset_units = units[onset_start:s]
        # If there are multiple consonants in onset and not the first syllable, split: last consonant
        # goes with this syllable's onset, prior consonants go with previous syllable's coda
        if syllables and len(onset_units) > 1:
            coda_take = onset_units[:-1]
            syllables[-1] += "".join(coda_take)
            onset_units = onset_units[-1:]
        # If this is the last nucleus, take everything remaining (incl. final coda)
        if k == len(nuclei) - 1:
            tail = units[e+1:]
            syl = "".join(onset_units) + "".join(units[s:e+1]) + "".join(tail)
        else:
            syl = "".join(onset_units) + "".join(units[s:e+1])
        syllables.append(syl)
        last_end = e
    return syllables

# ---------- Section 5: stress pattern ----------

def stress_pattern(word: str) -> dict:
    """Determine the expected and actual stress.
    Returns: {
        'syllables': [...],
        'expected_stressed_index': int,   # 0-based
        'actual_stressed_index': int|None,  # based on acute-accent location
        'is_irregular': bool,
        'needs_accent_mark': bool,
    }
    """
    syl = syllabify(word)
    n = len(syl)
    expected = None
    if n == 0:
        expected = None
    elif n == 1:
        expected = 0
    elif n == 2:
        expected = 0  # default: first syllable
    else:
        expected = 1  # default: second syllable
    # Find the syllable carrying an acute-accented vowel
    actual = None
    for i, s in enumerate(syl):
        for ch in s:
            if ch in STRESS_VOWELS:
                actual = i; break
        if actual is not None:
            break
    is_irregular = (actual is not None and actual != expected)
    # A word "needs accent mark" iff actual stress differs from expected
    needs_mark = is_irregular  # by Cayetano rule
    return {
        "syllables": syl,
        "expected_stressed_index": expected,
        "actual_stressed_index": actual,
        "is_irregular": is_irregular,
        "needs_accent_mark": needs_mark,
    }

# ---------- Section 6: conformance check ----------

def _strip_all_accents(s: str) -> str:
    out = []
    for ch in s:
        if ch in STRESS_VOWELS_TO_PLAIN:
            out.append(STRESS_VOWELS_TO_PLAIN[ch])
        else:
            decomp = unicodedata.normalize("NFD", ch)
            base = "".join(c for c in decomp if unicodedata.category(c) != "Mn")
            out.append(base)
    return "".join(out)

def is_conformant(word: str, allow_loan: bool = True) -> tuple[bool, list[str]]:
    """Check if `word` conforms to Cayetano 1992.
    Returns (ok, reasons). When ok=False, reasons explain each violation.
    `allow_loan` — if True, accept the word as a loan tagged elsewhere and
    only flag violations (do not auto-reject).
    """
    reasons: list[str] = []
    if not word or not isinstance(word, str):
        return False, ["empty input"]
    w = word.strip()
    if not w:
        return False, ["empty after strip"]
    wl = w.lower()
    # Strip leading sense index "1 word"
    wl = re.sub(r"^\d+\s+", "", wl)
    for pattern, why in DISALLOWED_PATTERNS:
        if pattern.search(wl):
            reasons.append(f"disallowed: {pattern.pattern!r} — {why}")
    # Stress check
    sp = stress_pattern(wl)
    if sp["is_irregular"] and sp["actual_stressed_index"] is None:
        reasons.append("possibly missing stress mark (irregular position)")
    # Forbidden characters (after strip): only allow the alphabet + space + apostrophe + hyphen
    stripped = _strip_all_accents(wl)
    for ch in stripped:
        if ch in " '-/()":
            continue
        if ch in CONSONANTS_SET: continue
        if ch == "c" and stripped[stripped.index(ch):stripped.index(ch)+2] == "ch":
            continue
        if ch in "aeiouü":
            continue
        if ch.isdigit():
            continue
        # Anything else is foreign
        reasons.append(f"non-Cayetano grapheme: '{ch}'")
    return (len(reasons) == 0), reasons

# ---------- Section 7: normalization ----------

def normalize(word: str) -> dict:
    """Apply Cayetano replacement rules. Return both normalized form and a delta log."""
    original = word or ""
    w = re.sub(r"^\d+\s+", "", original.strip())
    changes: list[dict] = []
    for pattern, repl, why in REPLACEMENT_RULES:
        new, n = pattern.subn(repl, w)
        if n > 0:
            changes.append({
                "pattern": pattern.pattern,
                "replacement": repl,
                "occurrences": n,
                "rationale": why,
                "before": w,
                "after": new,
            })
            w = new
    # Final: don't strip accents — they encode meaningful stress
    return {
        "original": original,
        "normalized": w,
        "changes": changes,
        "is_changed": len(changes) > 0,
    }

# ---------- Section 8: corpus audit ----------

def audit_corpus(words: Iterable[str]) -> dict:
    """Run conformance on a corpus and aggregate violations by rule."""
    from collections import Counter
    total = 0
    conformant = 0
    violations_by_reason: Counter[str] = Counter()
    samples_by_reason: dict[str, list[str]] = {}
    for w in words:
        total += 1
        ok, reasons = is_conformant(w)
        if ok:
            conformant += 1
        else:
            for r in reasons:
                # Trim long reasons to first sentence for grouping
                key = r.split(" — ")[0].split("(")[0].strip()
                violations_by_reason[key] += 1
                if key not in samples_by_reason:
                    samples_by_reason[key] = []
                if len(samples_by_reason[key]) < 5:
                    samples_by_reason[key].append(w)
    return {
        "total": total,
        "conformant": conformant,
        "conformant_pct": round(100.0 * conformant / total, 2) if total else 0.0,
        "violations_by_reason": dict(violations_by_reason.most_common()),
        "samples_by_reason": samples_by_reason,
    }

# ---------- Self-test ----------

if __name__ == "__main__":
    tests = [
        "magarada",       # all-native, conformant
        "wamaraga",       # conformant
        "büngiu",         # conformant, has ü
        "aríha",          # has stress accent
        "Hesukristu",     # religious loan, has k but otherwise ok
        "catei",          # disallowed: starts with c
        "quei",           # disallowed: starts with qu
        "abandonar",      # Spanish loan
        "ladaürun",       # has aü compound, conformant
        "ñei",            # has ñ, conformant
        "iauara",         # cohune palm — should be re-written as yawara (semi-vowel rule)
    ]
    print("=== Conformance check ===")
    for w in tests:
        ok, reasons = is_conformant(w)
        sp = stress_pattern(w)
        flag = "✓" if ok else "✗"
        print(f"  {flag} {w:<14} syllables={sp['syllables']} expected_stress={sp['expected_stressed_index']} actual={sp['actual_stressed_index']}")
        for r in reasons:
            print(f"      ! {r}")
    print("\n=== Normalization ===")
    for w in ["catei", "quei", "abandonar", "magarada", "ladauruN"]:
        d = normalize(w)
        print(f"  {w:<14} -> {d['normalized']:<14} changes={len(d['changes'])}")
        for c in d["changes"]:
            print(f"      ~ {c['rationale']}")
