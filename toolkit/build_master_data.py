"""Rebuild cases/samples for a corpus that already lives in the lab.

Parent-repo Study 2 CSV is no longer shipped. Prefer editing
data/corpora/<corpus>/cases.csv directly, or restore a source extract
under lab data/sources/ if you need to regenerate from raw.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

import pandas as pd

LAB = Path(__file__).resolve().parents[1]
CORPUS_ID = "startup_battlefield"
CORP = LAB / "data" / "corpora" / CORPUS_ID
CASES = CORP / "cases.csv"
# Optional local raw extract (not required for normal use)
OPTIONAL_SOURCE = LAB / "data" / "sources" / "input_startup_battlefield_study2_with_videos.csv"


def refresh_samples_from_cases() -> int:
    if not CASES.exists():
        raise SystemExit(f"missing {CASES}; nothing to rebuild")
    study = pd.read_csv(CASES, dtype={"id": str})
    rng = random.Random(20260731)
    rows = study.to_dict(orient="records")
    by_sel = {0: [], 1: []}
    for r in rows:
        try:
            g = int(float(r.get("GotSelected") or 0))
        except ValueError:
            g = 0
        by_sel[1 if g == 1 else 0].append(r)
    rng.shuffle(by_sel[0])
    rng.shuffle(by_sel[1])

    def take(n: int) -> list[dict]:
        n_sel = max(1, round(n * 0.30))
        n_not = n - n_sel
        chosen = by_sel[1][:n_sel] + by_sel[0][:n_not]
        if len(chosen) < n:
            rest = [r for r in rows if r not in chosen]
            rng.shuffle(rest)
            chosen.extend(rest[: n - len(chosen)])
        rng.shuffle(chosen)
        return chosen[:n]

    samples_dir = CORP / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    fields = ["id", "case_id", "GotSelected", "name", "corpus"]
    for name, n in (("smoke_n20", min(20, len(study))), ("full_n376", len(study))):
        # keep historical name even if n != 376
        out_name = name if name != "full_n376" else f"full_n{len(study)}"
        if name == "full_n376" and len(study) == 376:
            out_name = "full_n376"
        chosen = take(n) if n < len(study) else rows
        path = samples_dir / f"{out_name}.csv"
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in chosen:
                w.writerow({k: r.get(k, "") for k in fields})
        print(f"wrote {path} n={len(chosen)}")
    print(f"cases unchanged at {CASES} n={len(study)}")
    if not OPTIONAL_SOURCE.exists():
        print(f"(optional raw source not present: {OPTIONAL_SOURCE})")
    return 0


def main() -> int:
    return refresh_samples_from_cases()


if __name__ == "__main__":
    raise SystemExit(main())
