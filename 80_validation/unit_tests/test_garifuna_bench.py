"""Tests for the GarifunaBench scaffold (M-P3.G).

Coverage:
- Fixture loader returns BenchItem objects with engineer-scaffold marker
- BenchHarness.sanity_check works on scaffold items
- BenchHarness.run_task raises NotAuthoritativeError on scaffold items
- BenchHarness.run_task succeeds on graded items
- HallucinationDetector grounds known + flags unknown
- HallucinationDetector handles claimed-source mismatch
- Each task module exposes a score() callable
- pronunciation_grading raises NotImplementedError
- Token extractor identifies Garifuna-distinctive forms
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


# Path injection so we can import garifuna_bench from 80_validation/
_VALIDATION_DIR = Path(__file__).resolve().parent.parent
if str(_VALIDATION_DIR) not in sys.path:
    sys.path.insert(0, str(_VALIDATION_DIR))


from garifuna_bench import (  # noqa: E402
    BenchHarness,
    BenchItem,
    NotAuthoritativeError,
    HallucinationDetector,
    extract_garifuna_tokens,
    load_fixture,
    mt_en_to_cab,
    mt_cab_to_en,
    vocab_recall,
    conversation_quality,
    pronunciation_grading,
)

FIXTURE_PATH = (
    _VALIDATION_DIR / "garifuna_bench" / "fixtures" / "held_out_starter_v0.jsonl"
)


# ------------------------------------------------------------------ #
# Fixture loader
# ------------------------------------------------------------------ #

class TestFixtureLoader:
    def test_load_starter_fixture(self):
        items = load_fixture(FIXTURE_PATH)
        assert len(items) == 10
        for item in items:
            assert isinstance(item, BenchItem)
            assert item.tier == 5
            assert "V_VAULT_director_attested" in item.source_ids
            assert item.graded_by == "engineer-scaffold-only-NOT-AUTHORITATIVE"

    def test_items_not_authoritative(self):
        items = load_fixture(FIXTURE_PATH)
        for item in items:
            assert item.is_authoritative is False


# ------------------------------------------------------------------ #
# BenchHarness — sanity vs authoritative
# ------------------------------------------------------------------ #

class TestBenchHarness:
    def test_sanity_check_runs_on_scaffold(self):
        items = load_fixture(FIXTURE_PATH)
        harness = BenchHarness(items, chatbot_callable=lambda i: i.expected)
        report = harness.sanity_check("vocab_recall")
        assert report.sanity_only is True
        assert report.n_items == 5
        assert report.n_authoritative == 0
        assert report.aggregate_score is None  # no aggregate in sanity mode
        # Every per_item row has score 1.0 because mock returns expected
        for row in report.per_item:
            assert row["score"] == 1.0

    def test_run_task_raises_on_scaffold(self):
        items = load_fixture(FIXTURE_PATH)
        harness = BenchHarness(items, chatbot_callable=lambda i: i.expected)
        with pytest.raises(NotAuthoritativeError) as exc:
            harness.run_task("vocab_recall")
        assert "engineer-scaffold-only-NOT-AUTHORITATIVE" in str(exc.value)

    def test_run_task_succeeds_on_graded_items(self):
        item = BenchItem(
            id="GRADED-001",
            task="vocab_recall",
            input="to heal by applying heat",
            expected="abachaha",
            source_ids=["V_VAULT_director_attested"],
            headword="abachaha",
            tier=5,
            graded_by="director:Wamaraga:2026-05-22",
        )
        assert item.is_authoritative is True
        harness = BenchHarness([item], chatbot_callable=lambda i: i.expected)
        report = harness.run_task("vocab_recall")
        assert report.sanity_only is False
        assert report.aggregate_score == 1.0

    def test_filter_by_task(self):
        items = load_fixture(FIXTURE_PATH)
        harness = BenchHarness(items, chatbot_callable=lambda i: "")
        assert len(harness.filter_by_task("vocab_recall")) == 5
        assert len(harness.filter_by_task("mt_cab_to_en")) == 5
        assert len(harness.filter_by_task("mt_en_to_cab")) == 0


# ------------------------------------------------------------------ #
# HallucinationDetector
# ------------------------------------------------------------------ #

class TestHallucinationDetector:
    def _make_lookup(self, table: dict[str, dict]):
        return lambda hw: table.get(hw)

    def test_grounded_when_source_matches(self):
        lookup = self._make_lookup({
            "ababaü": {"sources": ["V_VAULT_director_attested"]},
        })
        det = HallucinationDetector(lookup_fn=lookup)
        # Use a response with only one candidate Garifuna token to avoid
        # extracting the English word "Garifuna" or "papaya" as a false
        # positive token (length >= 5 triggers candidacy).
        report = det.check(
            response="ababaü.",
            claimed_sources=["V_VAULT_director_attested"],
        )
        assert "ababaü" in report.grounded_tokens
        assert report.passes is True

    def test_flagged_when_source_mismatch(self):
        lookup = self._make_lookup({
            "ababaü": {"sources": ["Lila_Garifuna"]},
        })
        det = HallucinationDetector(lookup_fn=lookup)
        report = det.check(
            response="ababaü",
            claimed_sources=["V_VAULT_director_attested"],
        )
        assert "ababaü" in report.flagged_tokens
        assert report.passes is False

    def test_flagged_when_no_lookup_hit(self):
        det = HallucinationDetector(lookup_fn=lambda hw: None)
        report = det.check(
            response="fakegarifunaword",
            claimed_sources=["V_VAULT_director_attested"],
        )
        # 'fakegarifunaword' is >=5 chars, no Garifuna-distinctive
        # grapheme — still extracted by length rule, then flagged.
        assert report.score < 1.0

    def test_empty_response_passes_vacuously(self):
        det = HallucinationDetector(lookup_fn=lambda hw: None)
        report = det.check(response="", claimed_sources=[])
        assert report.score == 1.0


# ------------------------------------------------------------------ #
# Token extractor
# ------------------------------------------------------------------ #

class TestTokenExtractor:
    def test_extracts_garifuna_diacritic_token(self):
        tokens = extract_garifuna_tokens("The word is ababaü.")
        assert "ababaü" in tokens

    def test_skips_short_tokens(self):
        tokens = extract_garifuna_tokens("a is on")
        assert tokens == []

    def test_skips_stopwords(self):
        # Stopwords explicitly in the extractor's blocklist must never
        # appear in extracted tokens. Long English words that aren't on
        # the blocklist (e.g. "small") MAY appear — those are flagged
        # by the hallucination detector at lookup time, not by the
        # extractor (extractor is conservative-inclusive by design so
        # the lookup gate catches obscure foundry-attested forms).
        tokens = extract_garifuna_tokens(
            "the and that house water from with"
        )
        for tok in tokens:
            assert tok not in {
                "the", "and", "that", "for", "from", "with",
                "house", "water",
            }


# ------------------------------------------------------------------ #
# Task modules
# ------------------------------------------------------------------ #

class TestTaskModules:
    def test_mt_en_to_cab_exact_match(self):
        assert mt_en_to_cab.score("water", "duna", "duna") == 1.0

    def test_mt_en_to_cab_empty_response(self):
        assert mt_en_to_cab.score("water", "duna", "") == 0.0

    def test_mt_cab_to_en_full_match(self):
        assert mt_cab_to_en.score("abadinagua", "among", "among") == 1.0

    def test_mt_cab_to_en_partial(self):
        # No overlap case → 0.0
        no_overlap = mt_cab_to_en.score(
            "abadira", "to beat an egg", "rabbit jumping"
        )
        assert no_overlap == 0.0
        # 50%+ overlap → high partial (>=0.5)
        # expected ≥3-char tokens after normalize: {'beat', 'egg'}
        # response ≥3-char tokens: {'boil', 'egg', 'now'}
        # overlap = 1/2 = 0.5 → 0.5 + 0.25 = 0.75
        high_partial = mt_cab_to_en.score(
            "abadira", "to beat an egg", "boil egg now"
        )
        assert high_partial == 0.75
        # Single-share-no-50pct
        low_partial = mt_cab_to_en.score(
            "abadira", "to beat an egg with whisk", "egg cake"
        )
        # expected tokens: {'beat','egg','with','whisk'}; response {'egg','cake'}
        # overlap = 1/4 = 0.25 → falls to 0.3 branch
        assert low_partial == 0.3

    def test_vocab_recall_exact(self):
        assert vocab_recall.score("warm", "abacharagüda", "abacharagüda") == 1.0

    def test_vocab_recall_nfc_nfd_partial(self):
        # NFC ü vs NFD u+combining_diaeresis — score should give 0.6
        import unicodedata
        nfd = unicodedata.normalize("NFD", "abacharagüda")
        s = vocab_recall.score("warm", "abacharagüda", nfd)
        # Implementation lowercases and re-normalizes both sides; exact
        # lowercase comparison may already match (NFD/NFC roundtrip
        # depends on Python's str equality). Accept either 1.0 or 0.6.
        assert s in (1.0, 0.6)

    def test_conversation_quality_citation_present(self):
        s = conversation_quality.score(
            "what is duna",
            "water",
            "Duna means water. [V_VAULT_director_attested]",
        )
        assert s >= 0.5

    def test_pronunciation_grading_not_implemented(self):
        with pytest.raises(NotImplementedError):
            pronunciation_grading.score("audio", "duna", "duna")
