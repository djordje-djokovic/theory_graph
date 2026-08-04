"""Package helper: refresh fixtures and print lab size."""
from __future__ import annotations

from pathlib import Path

from theory_lab.equivalence import _ensure_fixtures
from theory_lab.paths import lab_root


def main() -> int:
    root = lab_root()
    fix = _ensure_fixtures(root)
    print(f"fixtures ready under {fix}")
    n_json = sum(1 for _ in (root / "reference").rglob("*.json"))
    print(f"reference JSON encodings: {n_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
