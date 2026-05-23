"""Pytest configuration: add nisamina-app subpackages to sys.path."""
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent.parent  # nisamina-app/
for sub in ("20_normalize", "30_lexicon", "99_publish"):
    p = str(APP / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
