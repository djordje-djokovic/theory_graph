"""Locate the theory_graph root from any installed/copied location."""
from __future__ import annotations

from pathlib import Path


def lab_root() -> Path:
    """Return the theory_graph directory (parent of toolkit/)."""
    # toolkit/theory_graph/paths.py -> parents[2] = theory_graph
    return Path(__file__).resolve().parents[2]


def ensure_lab_root(override: Path | None = None) -> Path:
    root = Path(override) if override else lab_root()
    if not (root / "prompts").exists() and not (root / "data").exists():
        raise SystemExit(f"does not look like a theory_graph root: {root}")
    return root
