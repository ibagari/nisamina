"""Task: pronunciation grading (audio + expected text → score).

BLOCKED on M-P3.D — Whisper-cab fine-tune + MMS-tts-cab pipeline.

Skeleton signature so harness dispatch doesn't break; calling the
scorer raises NotImplementedError with a forward pointer.
"""

from __future__ import annotations


def score(input_text: str, expected: str, response: str) -> float:
    raise NotImplementedError(
        "pronunciation_grading requires M-P3.D Whisper-cab integration. "
        "See M-P3.D manifest (not yet written) + plan v1.1 §1.3 + "
        "70_audio/ scope."
    )
