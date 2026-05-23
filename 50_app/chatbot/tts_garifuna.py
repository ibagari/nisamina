"""GarifunaTTS — explicit `facebook/mms-tts-cab` wrapper.

Per director directive 2026-05-23 "this MUST be explicitly utilized
https://huggingface.co/facebook/mms-tts-cab" + supervisor S16 brief F-058.

Model facts:
- HF repo: facebook/mms-tts-cab
- Architecture: VITS (variational inference + adversarial learning)
- Params: 36.3M; weights F32 safetensors
- Sampling rate: 22050 Hz
- License: CC-BY-NC 4.0 (consent_007 + attr_030 already in registry)
- Stochastic duration predictor — REQUIRES seed for determinism
- Citation: Pratap et al. 2023 arXiv 2305.13516

Pattern: lazy load on first synth() call (HF Space cold-start mitigation;
mock-friendly for tests that don't download 150 MB of weights).
"""

from __future__ import annotations

import io
import struct
from dataclasses import dataclass
from typing import Optional


# Lazy module-level holders; populated on first synth() call
_VitsModel = None
_AutoTokenizer = None
_torch = None

DEFAULT_SEED: int = 42
SAMPLE_RATE: int = 22050  # mms-tts-cab outputs 22 050 Hz
MODEL_REPO: str = "facebook/mms-tts-cab"


def _lazy_imports() -> None:
    """Import transformers + torch only on first real synth call.

    Raises ImportError with clear instructions if dependencies missing.
    """
    global _VitsModel, _AutoTokenizer, _torch
    if _VitsModel is not None:
        return
    try:
        from transformers import VitsModel, AutoTokenizer
        import torch
    except ImportError as e:
        raise ImportError(
            "transformers + torch required for GarifunaTTS real-mode. "
            "On HF Space: ensure requirements.txt includes "
            "'transformers>=4.33 torch'. "
            f"Underlying: {e}"
        ) from e
    _VitsModel = VitsModel
    _AutoTokenizer = AutoTokenizer
    _torch = torch


@dataclass
class TTSResult:
    """A synthesized audio output + attribution metadata."""

    wav_bytes: bytes        # PCM WAV file bytes (22 050 Hz, mono, 16-bit)
    text: str               # the Garifuna text that was synthesized
    duration_seconds: float
    sample_rate: int        # 22050
    attribution: str        # "Voice: facebook/mms-tts-cab — Pratap et al. 2023 ..."
    model_repo: str         # "facebook/mms-tts-cab"
    license_short: str      # "CC-BY-NC 4.0"
    seed: int               # for reproducibility


ATTRIBUTION_TEXT: str = (
    "Voice: facebook/mms-tts-cab — Pratap et al. 2023 arXiv 2305.13516 (Meta AI) "
    "— CC-BY-NC 4.0 (consent_007 + attr_030)"
)


def _waveform_to_wav_bytes(
    waveform: "object", sample_rate: int = SAMPLE_RATE
) -> bytes:
    """Convert a float32 waveform tensor to 16-bit PCM WAV bytes.

    Hand-rolled (no scipy.io.wavfile dep) so this module stays minimal
    on HF Space. Format: RIFF/WAVE/PCM.
    """
    # Convert to float32 numpy
    if hasattr(waveform, "cpu"):
        waveform = waveform.cpu()
    if hasattr(waveform, "numpy"):
        arr = waveform.numpy()
    else:
        arr = waveform

    # Flatten + clip + scale to int16
    arr = arr.flatten()
    # Clip to [-1, 1] then scale
    import struct as _struct
    samples_int16: list[int] = []
    for v in arr:
        v = max(-1.0, min(1.0, float(v)))
        samples_int16.append(int(v * 32767))

    n_samples = len(samples_int16)
    byte_rate = sample_rate * 2  # mono 16-bit = 2 bytes/sample
    data_size = n_samples * 2

    # WAV header (44 bytes) + PCM data
    header = b"RIFF"
    header += _struct.pack("<I", 36 + data_size)
    header += b"WAVE"
    header += b"fmt "
    header += _struct.pack("<I", 16)         # fmt chunk size
    header += _struct.pack("<H", 1)          # PCM format
    header += _struct.pack("<H", 1)          # mono
    header += _struct.pack("<I", sample_rate)
    header += _struct.pack("<I", byte_rate)
    header += _struct.pack("<H", 2)          # block align
    header += _struct.pack("<H", 16)         # bits per sample
    header += b"data"
    header += _struct.pack("<I", data_size)

    body = _struct.pack(f"<{n_samples}h", *samples_int16)
    return header + body


class GarifunaTTS:
    """Wrapper around facebook/mms-tts-cab.

    Lazy-loads weights on first synth() call.
    Use seed= for reproducibility (golden-snapshot tests + lesson player).
    """

    def __init__(self, model_repo: str = MODEL_REPO, seed: int = DEFAULT_SEED) -> None:
        self.model_repo = model_repo
        self.seed = seed
        self._model = None
        self._tokenizer = None
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        _lazy_imports()
        self._model = _VitsModel.from_pretrained(self.model_repo)
        self._tokenizer = _AutoTokenizer.from_pretrained(self.model_repo)
        self._loaded = True

    def synth(
        self,
        text: str,
        seed: Optional[int] = None,
    ) -> TTSResult:
        """Synthesize a Garifuna utterance.

        Args:
            text: Cayetano-orthography-normalized Garifuna text. Empty input
                raises ValueError.
            seed: deterministic-seed override; defaults to self.seed.

        Returns:
            TTSResult with PCM WAV bytes + attribution + duration.
        """
        if not text or not text.strip():
            raise ValueError("GarifunaTTS.synth requires non-empty text")

        self._ensure_loaded()
        use_seed = seed if seed is not None else self.seed

        _torch.manual_seed(use_seed)
        inputs = self._tokenizer(text, return_tensors="pt")
        with _torch.no_grad():
            output = self._model(**inputs).waveform

        wav_bytes = _waveform_to_wav_bytes(output, sample_rate=SAMPLE_RATE)
        n_samples_pcm = (len(wav_bytes) - 44) // 2
        duration = n_samples_pcm / SAMPLE_RATE if SAMPLE_RATE else 0.0

        return TTSResult(
            wav_bytes=wav_bytes,
            text=text,
            duration_seconds=duration,
            sample_rate=SAMPLE_RATE,
            attribution=ATTRIBUTION_TEXT,
            model_repo=self.model_repo,
            license_short="CC-BY-NC 4.0",
            seed=use_seed,
        )


@dataclass
class MockGarifunaTTS:
    """Test-friendly TTS that produces a small deterministic WAV.

    Used in: pytest, engineer-side dev without transformers, and any path
    that needs a sound-shaped artifact without the model download.
    Output is a tiny silent WAV with the requested duration; sufficient for
    "audio_garifuna_wav is not None" assertions in orchestrator tests.
    """

    seed: int = DEFAULT_SEED

    def synth(
        self,
        text: str,
        seed: Optional[int] = None,
    ) -> TTSResult:
        if not text or not text.strip():
            raise ValueError("MockGarifunaTTS.synth requires non-empty text")
        # Tiny 0.1s silence at 22050 Hz mono 16-bit
        n_samples = int(SAMPLE_RATE * 0.1)
        import struct as _struct
        body = _struct.pack(f"<{n_samples}h", *([0] * n_samples))
        data_size = len(body)
        header = (
            b"RIFF"
            + _struct.pack("<I", 36 + data_size)
            + b"WAVE"
            + b"fmt "
            + _struct.pack("<I", 16)
            + _struct.pack("<H", 1)
            + _struct.pack("<H", 1)
            + _struct.pack("<I", SAMPLE_RATE)
            + _struct.pack("<I", SAMPLE_RATE * 2)
            + _struct.pack("<H", 2)
            + _struct.pack("<H", 16)
            + b"data"
            + _struct.pack("<I", data_size)
        )
        wav = header + body
        return TTSResult(
            wav_bytes=wav,
            text=text,
            duration_seconds=0.1,
            sample_rate=SAMPLE_RATE,
            attribution=ATTRIBUTION_TEXT + " [MOCK]",
            model_repo="mock://MockGarifunaTTS",
            license_short="CC-BY-NC 4.0",
            seed=seed if seed is not None else self.seed,
        )
