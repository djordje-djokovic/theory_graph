"""Locate the theory_encoding_lab root from any installed/copied location."""
from __future__ import annotations

from pathlib import Path


def lab_root() -> Path:
    """Return the theory_encoding_lab directory (parent of toolkit/)."""
    # toolkit/theory_lab/paths.py -> parents[2] = theory_encoding_lab
    return Path(__file__).resolve().parents[2]


def ensure_lab_root(override: Path | None = None) -> Path:
    root = Path(override) if override else lab_root()
    if not (root / "prompts").exists() and not (root / "data").exists():
        raise SystemExit(f"does not look like a theory_encoding_lab root: {root}")
    return root
