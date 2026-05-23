"""Tests for GarifunaTTS — facebook/mms-tts-cab wrapper.

Mock-friendly: real-mode requires VitsModel weights (150MB); test suite uses
MockGarifunaTTS for assertions on the wrapper contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


_CHATBOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_CHATBOT_DIR.parent))

from chatbot.tts_garifuna import (  # noqa: E402
    GarifunaTTS,
    MockGarifunaTTS,
    TTSResult,
    ATTRIBUTION_TEXT,
    SAMPLE_RATE,
    MODEL_REPO,
)


class TestMockGarifunaTTS:
    def test_synth_returns_wav_bytes(self):
        tts = MockGarifunaTTS()
        result = tts.synth("buguya nuani")
        assert isinstance(result, TTSResult)
        assert result.wav_bytes.startswith(b"RIFF")
        assert b"WAVE" in result.wav_bytes[:12]
        assert result.sample_rate == 22050
        assert result.text == "buguya nuani"

    def test_synth_empty_text_raises(self):
        tts = MockGarifunaTTS()
        with pytest.raises(ValueError):
            tts.synth("")
        with pytest.raises(ValueError):
            tts.synth("   ")

    def test_attribution_present(self):
        tts = MockGarifunaTTS()
        result = tts.synth("agüriahati")
        assert "facebook/mms-tts-cab" in result.attribution
        assert "Pratap" in result.attribution
        assert "CC-BY-NC 4.0" in result.attribution

    def test_seed_propagates(self):
        tts = MockGarifunaTTS(seed=99)
        result = tts.synth("ababagüda")
        assert result.seed == 99
        # Override via kwarg
        result2 = tts.synth("ababagüda", seed=7)
        assert result2.seed == 7


class TestGarifunaTTSWrapper:
    def test_init_doesnt_download(self):
        """Constructor must NOT trigger model download."""
        tts = GarifunaTTS()
        assert tts._loaded is False
        assert tts.model_repo == MODEL_REPO
        assert tts.seed == 42

    def test_synth_empty_text_raises_before_load(self):
        tts = GarifunaTTS()
        with pytest.raises(ValueError):
            tts.synth("")
        # _loaded must still be False — empty-input rejection happens
        # before the lazy model load
        assert tts._loaded is False


class TestWavStructure:
    def test_wav_header_structure(self):
        tts = MockGarifunaTTS()
        result = tts.synth("test")
        wav = result.wav_bytes
        assert wav[0:4] == b"RIFF"
        assert wav[8:12] == b"WAVE"
        assert wav[12:16] == b"fmt "
        assert wav[36:40] == b"data"

    def test_wav_sample_rate_in_header(self):
        tts = MockGarifunaTTS()
        result = tts.synth("test")
        wav = result.wav_bytes
        import struct
        sr_from_header = struct.unpack("<I", wav[24:28])[0]
        assert sr_from_header == 22050

    def test_wav_mono_16bit(self):
        tts = MockGarifunaTTS()
        result = tts.synth("test")
        wav = result.wav_bytes
        import struct
        num_channels = struct.unpack("<H", wav[22:24])[0]
        bits_per_sample = struct.unpack("<H", wav[34:36])[0]
        assert num_channels == 1
        assert bits_per_sample == 16


class TestAttributionContract:
    def test_attribution_text_includes_required_elements(self):
        # Per F-058 §3: every audio surface must carry attribution chain
        required = [
            "facebook/mms-tts-cab",
            "Pratap et al. 2023",
            "arXiv 2305.13516",
            "Meta AI",
            "CC-BY-NC 4.0",
            "consent_007",
            "attr_030",
        ]
        for r in required:
            assert r in ATTRIBUTION_TEXT, f"required attribution element missing: {r!r}"
