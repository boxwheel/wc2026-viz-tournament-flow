"""Shared helpers for every plot: import path setup, output paths."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def out_paths(name: str):
    return ART / f"{name}.png", ART / f"{name}.svg"
