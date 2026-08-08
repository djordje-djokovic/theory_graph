"""Pre-encode readiness check for startup_battlefield corpus."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CORP = ROOT / "data/corpora/startup_battlefield"
CASES = CORP / "cases.csv"
PITCH = CORP / "transcripts"
QA = CORP / "transcripts_qa"
SAMPLE = CORP / "samples/full_n375.csv"


def main() -> int:
    cases = pd.read_csv(CASES, dtype={"case_id": str})
    if not SAMPLE.exists():
        # fall back to computed n
        sample = pd.read_csv(CORP / "samples/full_n376.csv", dtype={"case_id": str})
        sample = sample[sample.case_id != "pilot-108"]
    else:
        sample = pd.read_csv(SAMPLE, dtype={"case_id": str})

    excluded = cases[cases.get("excluded", 0) == 1] if "excluded" in cases.columns else pd.DataFrame()
    ids = list(sample.case_id)

    missing_pitch = [c for c in ids if not (PITCH / f"{c}.txt").exists()]
    missing_qa = [c for c in ids if not (QA / f"{c}.txt").exists()]
    empty_pitch = []
    for c in ids:
        p = PITCH / f"{c}.txt"
        if p.exists() and len(p.read_text(encoding="utf-8").split()) < 50:
            empty_pitch.append(c)

    in_sample_excluded = [c for c in ids if c in set(excluded.case_id)] if len(excluded) else []

    print("=== Encode readiness ===")
    print(f"Analysis sample: {SAMPLE.name} n={len(ids)}")
    print(f"Excluded in cases.csv: {len(excluded)} -> {list(excluded.case_id) if len(excluded) else []}")
    print(f"Missing PITCH transcript: {len(missing_pitch)} {missing_pitch[:5]}")
    print(f"Missing Q&A transcript: {len(missing_qa)} {missing_qa[:5]}")
    print(f"Very short PITCH (<50w): {len(empty_pitch)} {empty_pitch[:5]}")
    print(f"Excluded still in sample: {in_sample_excluded}")

    ready = not missing_pitch and not in_sample_excluded
    print(f"\nREADY FOR PITCH ENCODE: {ready}")
    if missing_qa:
        print("(Q&A gaps OK if encoding PITCH-only premises pass)")

    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
