"""Unit tests for 30_lexicon/english_language_gate.py.

Catches English words that pass Cayetano grapheme conformance (because their
letters are all Cayetano-permitted) but are clearly not Garifuna.
"""
import pytest
from english_language_gate import (
    is_likely_english,
    has_geminate_pattern,
    has_garifuna_diacritic,
)


class TestIsLikelyEnglish:

    @pytest.mark.parametrize("word", [
        "give", "match", "above", "advise", "alive", "arrive",
        "abhorrent", "absolutely", "able", "approach", "begin",
        "language", "machine", "remember", "small", "today",
    ])
    def test_obvious_english_flagged(self, word):
        is_eng, reason = is_likely_english(word)
        assert is_eng, f"English {word!r} should be flagged; reason={reason}"

    @pytest.mark.parametrize("word", [
        "akkompany",  # English-loan transliteration with geminate kk
        "akkordeon",  # geminate kk
        "summer",     # geminate mm
        "running",    # geminate nn
    ])
    def test_geminate_loan_transliterations_flagged(self, word):
        is_eng, reason = is_likely_english(word)
        assert is_eng, f"{word!r} geminate-loan should be flagged"

    def test_documented_gap_no_geminate_unusual_spelling(self):
        """'komforting' is a stylized English spelling but has NO geminate cluster
        AND is not in /usr/share/dict/words. Both rules miss it — documented gap.
        Mitigation: in V0.1 such words appeared in Tier-X anyway (sources=[]); the
        problem is only for Tier-A/B records with similar pattern. Tracked, accepted."""
        is_eng, _ = is_likely_english("komforting")
        # Acknowledge current behavior; do not over-assert
        assert is_eng is False  # current gates miss this

    @pytest.mark.parametrize("word", [
        "magarada", "wamaraga", "aban", "iri", "lugia",
        "kasimirun", "hesukristu", "lubá", "yawara",
    ])
    def test_garifuna_words_NOT_flagged(self, word):
        is_eng, reason = is_likely_english(word)
        assert not is_eng, f"Garifuna {word!r} should NOT be flagged; got reason={reason}"

    @pytest.mark.parametrize("word", [
        "büngiu", "ladaürun", "aríha", "ñei", "ámuradügü",
    ])
    def test_diacritic_bearing_words_NOT_flagged(self, word):
        """Words with Garifuna-typical diacritics are exempt — definitely not English."""
        is_eng, _ = is_likely_english(word)
        assert not is_eng, f"Diacritic-bearing {word!r} should NOT be flagged"

    @pytest.mark.parametrize("word", ["ba", "bi", "la", "el", "is", "on"])
    def test_short_words_not_flagged(self, word):
        """Words shorter than MIN_LENGTH_FOR_WORDLIST_CHECK get a pass."""
        is_eng, _ = is_likely_english(word)
        assert not is_eng, f"Short {word!r} should not be flagged"

    def test_empty_input(self):
        assert is_likely_english("")[0] is False
        assert is_likely_english(None)[0] is False


class TestHelpers:
    def test_geminate_kk(self):
        assert has_geminate_pattern("akkompany")
    def test_geminate_nn(self):
        assert has_geminate_pattern("running")
    def test_no_geminate(self):
        assert not has_geminate_pattern("magarada")

    def test_garifuna_diacritic_detection(self):
        assert has_garifuna_diacritic("büngiu")
        assert has_garifuna_diacritic("aríha")
        assert has_garifuna_diacritic("ñei")
        assert not has_garifuna_diacritic("magarada")
        assert not has_garifuna_diacritic("aban")
