"""GarifunaBench task modules — one per evaluation type.

Each module exports `score(input, expected, response) -> float` in
[0, 1]. Higher is better. Stubs raise NotImplementedError when their
upstream dependency hasn't been built yet (pronunciation_grading
depends on M-P3.D Whisper-cab).
"""

from . import mt_en_to_cab
from . import mt_cab_to_en
from . import vocab_recall
from . import conversation_quality
from . import pronunciation_grading


__all__ = [
    "mt_en_to_cab",
    "mt_cab_to_en",
    "vocab_recall",
    "conversation_quality",
    "pronunciation_grading",
]
