"""Exclude pilot-108 and build full_n375 analysis sample."""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CORP = ROOT / "data/corpora/startup_battlefield"
CASES = CORP / "cases.csv"
SAMPLES = CORP / "samples"
EXCLUDE_ID = "pilot-108"
REASON = (
    "Transcript-metadata mismatch: cases.csv labels Disrupt 2023 Glide but transcript "
    "is 2013 Glide (Jonathan Karas); no 2023 source video in perfect_pitch."
)

cases = pd.read_csv(CASES, dtype={"id": str, "case_id": str})
if EXCLUDE_ID not in set(cases.case_id):
    raise SystemExit(f"{EXCLUDE_ID} not found in cases.csv")

if "excluded" not in cases.columns:
    cases["excluded"] = 0
if "exclude_reason" not in cases.columns:
    cases["exclude_reason"] = ""

cases.loc[cases.case_id == EXCLUDE_ID, "excluded"] = 1
cases.loc[cases.case_id == EXCLUDE_ID, "exclude_reason"] = REASON
cases.to_csv(CASES, index=False)

# exclusions audit file
excl = cases[cases.excluded == 1][["case_id", "name", "event", "year", "exclude_reason"]]
excl_path = CORP / "exclusions.csv"
excl.to_csv(excl_path, index=False)

# full sample minus excluded
full = pd.read_csv(SAMPLES / "full_n376.csv", dtype={"case_id": str})
study = full[full.case_id != EXCLUDE_ID].copy()
out = SAMPLES / f"full_n{len(study)}.csv"
study.to_csv(out, index=False)

# refresh smoke if pilot-108 was in it
smoke_path = SAMPLES / "pilot_n50.csv"
if smoke_path.exists():
    smoke = pd.read_csv(smoke_path, dtype={"case_id": str})
    if EXCLUDE_ID in set(smoke.case_id):
        smoke = smoke[smoke.case_id != EXCLUDE_ID]
        smoke.to_csv(smoke_path, index=False)
        print(f"updated {smoke_path} n={len(smoke)}")

print(f"marked excluded: {EXCLUDE_ID}")
print(f"wrote {excl_path}")
print(f"wrote {out} n={len(study)}")
