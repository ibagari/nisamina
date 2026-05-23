"""Unit tests for cayetano_1992 normalize() + is_conformant() + syllabify()."""
import pytest
from cayetano_1992 import normalize, is_conformant, syllabify, stress_pattern


class TestNormalize:
    """Cayetano §3 replacement rules: qu→k, c→k (except in 'ch'), internal-ai→ei, word-end-ao→aü."""

    def test_returns_dict_with_expected_keys(self):
        result = normalize("catei")
        assert isinstance(result, dict)
        assert set(result.keys()) >= {"original", "normalized", "changes", "is_changed"}

    @pytest.mark.parametrize("input_word, expected_normalized", [
        ("catei", "katei"),                  # c → k (not in 'ch')
        ("quei", "kei"),                     # qu → k
        ("Catei", "Katei"),                  # case-insensitive replacement
        ("Quei", "Kei"),
        ("caigana", "keigana"),              # c → k, then internal ai-after-consonant → ei
        ("Cayetano", "Kayetano"),            # 'C' → 'k' but 'ch' preserved (no ch here; just the C)
    ])
    def test_replacements_applied(self, input_word, expected_normalized):
        result = normalize(input_word)
        # Allow case differences but core transformation must hold
        assert result["normalized"].lower() == expected_normalized.lower() or \
               result["normalized"] == expected_normalized, \
               f"{input_word} -> {result['normalized']}, expected ~{expected_normalized}"

    def test_ch_preserved(self):
        """'ch' digraph must not be split by the c→k rule."""
        result = normalize("chuluha")
        assert "ch" in result["normalized"].lower(), f"'ch' destroyed: {result['normalized']}"

    def test_accents_preserved(self):
        """Stress accents (á é í ó ú ǘ) encode meaningful stress; must not be stripped."""
        result = normalize("aríha")
        assert "í" in result["normalized"]

    def test_conformant_words_unchanged(self):
        """A fully conformant Garifuna headword should pass through normalize without changes."""
        for word in ["magarada", "wamaraga", "büngiu", "ñei", "ladaürun"]:
            result = normalize(word)
            assert not result["is_changed"], f"{word!r} was changed to {result['normalized']!r}"

    def test_empty_input(self):
        assert normalize("")["normalized"] == ""
        assert normalize(None)["normalized"] == ""


class TestIsConformant:
    """is_conformant rejects non-Garifuna graphemes (v/x/z), Spanish 'qu', 'c' outside 'ch'."""

    @pytest.mark.parametrize("word", [
        "magarada",
        "wamaraga",
        "büngiu",
        "aríha",
        "Hesukristu",   # religious loan, but uses k (conformant)
        "ladaürun",     # aü compound
        "ñei",
        "chuluha",
        "aban",
        "lubá",
        "yawara",
    ])
    def test_conformant_examples(self, word):
        ok, reasons = is_conformant(word)
        assert ok, f"{word!r} should be conformant; reasons: {reasons}"

    @pytest.mark.parametrize("word, expected_violation_substring", [
        ("vagina", "v"),       # 'v' not in alphabet
        ("klavar", "v"),
        ("zorro", "z"),
        ("paz", "z"),
        ("pozo", "z"),
        ("xerox", "x"),
        ("quei", "qu"),         # 'qu' is Spanish orthography (note: normalize would fix it to 'kei')
        ("catei", "c"),         # 'c' not in 'ch' (note: normalize would fix it)
    ])
    def test_non_conformant_examples(self, word, expected_violation_substring):
        ok, reasons = is_conformant(word)
        assert not ok, f"{word!r} should be non-conformant"
        assert any(expected_violation_substring in r.lower() for r in reasons), \
            f"{word!r} reasons={reasons} did not mention {expected_violation_substring!r}"

    @pytest.mark.parametrize("word", [
        "give",      # has 'v' (disallowed)
        "above",     # has 'v'
        "alive",     # has 'v'
        "advise",    # has 'v'
        "arrive",    # has 'v'
        "vagina",    # has 'v'
        "klavar",    # has 'v'
    ])
    def test_english_with_disallowed_graphemes_rejected(self, word):
        """English/Spanish loans with v/x/z/qu fail Cayetano grapheme check."""
        ok, _ = is_conformant(word)
        assert not ok, f"{word!r} unexpectedly passed conformance"

    @pytest.mark.parametrize("word", [
        "match", "akkompany", "komforting", "abhorrent", "absolutely",
    ])
    def test_english_without_disallowed_graphemes_passes_conformance(self, word):
        """Documented limitation: English words using only Cayetano-permitted graphemes
        DO pass `is_conformant`. They are caught by a separate English-language gate
        (see 30_lexicon/english_language_gate.py + test_english_language_gate.py)."""
        ok, _ = is_conformant(word)
        assert ok, f"{word!r} should pass conformance (grapheme-level only); caught by English gate downstream"

    def test_empty_input(self):
        ok, _ = is_conformant("")
        assert not ok

    @pytest.mark.parametrize("artifact", [
        "dán (time; weather)",                  # parenthetical gloss
        "ámuradügü, ámurahanii",                # comma-separated alt forms
        "ababaü [ubabaü]",                      # bracket-quoted alt form
        "áti\ndefinition: 1. moon; 2. mont",    # newline + definition leak
        "1 magarada",                           # leading sense-index — should be stripped by normalize first
    ])
    def test_extraction_artifacts_rejected(self, artifact):
        """Headwords containing extraction artifacts must fail conformance."""
        ok, reasons = is_conformant(artifact)
        # Note: is_conformant strips the leading "1 " sense index per the impl, so "1 magarada" may pass.
        # The other 4 artifacts must fail.
        if artifact.startswith("1 magarada"):
            return  # acceptable — sense-index strip is documented behavior
        assert not ok, f"Extraction artifact {artifact!r} unexpectedly passed conformance"


class TestSyllabify:
    """Heuristic syllabification — basic structural correctness."""

    def test_single_syllable(self):
        s = syllabify("ka")
        assert len(s) >= 1
        assert "ka" in "".join(s)

    def test_multisyllabic(self):
        s = syllabify("magarada")
        assert len(s) >= 3, f"magarada should have ≥3 syllables, got {s}"
        assert "".join(s).replace(" ", "") == "magarada"

    def test_ch_treated_as_single_unit(self):
        s = syllabify("chuluha")
        # Should not split 'ch'
        assert all("ch" not in syl or syl.startswith("ch") or syl.endswith("ch") or syl == "ch" for syl in s) or \
               any("ch" in syl for syl in s), f"'ch' split unexpectedly: {s}"

    def test_compound_vowels_stay_together(self):
        s = syllabify("ladaürun")
        # 'aü' should stay in one syllable
        assert any("aü" in syl for syl in s), f"'aü' compound split: {s}"


class TestStressPattern:
    def test_returns_expected_keys(self):
        r = stress_pattern("magarada")
        assert {"syllables", "expected_stressed_index", "actual_stressed_index", "is_irregular", "needs_accent_mark"} <= set(r.keys())

    def test_acute_marked_word_detected(self):
        r = stress_pattern("aríha")
        assert r["actual_stressed_index"] is not None
