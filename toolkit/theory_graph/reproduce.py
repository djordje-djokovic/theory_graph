"""Reproduce published reference pipelines and diff vs shipped outputs."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .analyze import analyze_reference_pipeline
from .corpora import cases_csv
from .robustness import write_robustness_grid

PIPELINES = {
    "v1_3_2_nested": {
        "batches": [
            "02_breadth_v131",
            "03_prod50",
            "04_breadth_v132",
            "06_full_remaining",
        ],
        "corpus": "startup_battlefield",
    },
    "v1_5_1_crossed": {
        "batches": [f"03_full_v151_w{i:02d}" for i in range(1, 9)],
        "corpus": "startup_battlefield",
    },
}

IV_COLS = ["breadth", "n_domains", "balance", "granularity", "truncated"]
TOL = 1e-6


def _diff_cases(shipped: Path, recomputed: Path) -> list[str]:
    errors: list[str] = []
    a = pd.read_csv(shipped, dtype={"id": str, "case_id": str})
    b = pd.read_csv(recomputed, dtype={"id": str, "case_id": str})
    if len(a) != len(b):
        errors.append(f"n mismatch shipped={len(a)} recomputed={len(b)}")
    m = a.merge(b, on="case_id", suffixes=("_s", "_r"), how="outer", indicator=True)
    missing = m[m["_merge"] != "both"]
    if len(missing):
        errors.append(f"case_id join failures: {len(missing)}")
    both = m[m["_merge"] == "both"]
    for col in IV_COLS:
        cs, cr = f"{col}_s", f"{col}_r"
        if cs not in both.columns or cr not in both.columns:
            continue
        s = pd.to_numeric(both[cs], errors="coerce")
        r = pd.to_numeric(both[cr], errors="coerce")
        # allow tiny float noise
        bad = (~np.isclose(s.fillna(0), r.fillna(0), rtol=0, atol=TOL, equal_nan=True)).sum()
        if bad:
            max_abs = float(np.nanmax(np.abs(s - r)))
            errors.append(f"{col}: {bad} rows differ (max|Δ|={max_abs:.3g})")
    return errors


def _diff_grid(shipped: Path, recomputed: Path) -> list[str]:
    if not shipped.exists():
        return [f"missing shipped grid {shipped}"]
    a = pd.read_csv(shipped)
    b = pd.read_csv(recomputed)
    if len(a) != len(b):
        return [f"grid n mismatch shipped={len(a)} recomputed={len(b)}"]
    errs = []
    for col in ("linear_b", "quad_b", "linear_p", "quad_p"):
        if col not in a.columns or col not in b.columns:
            continue
        s = pd.to_numeric(a[col], errors="coerce")
        r = pd.to_numeric(b[col], errors="coerce")
        # p-values / coeffs — allow looser tol for HC1 numeric path
        bad = (~np.isclose(s.fillna(0), r.fillna(0), rtol=1e-4, atol=1e-5, equal_nan=True)).sum()
        if bad:
            max_abs = float(np.nanmax(np.abs(s - r)))
            errs.append(f"grid {col}: {bad} rows differ (max|Δ|={max_abs:.3g})")
    return errs


def reproduce_pipeline(lab_root: Path, name: str) -> bool:
    if name not in PIPELINES:
        raise SystemExit(f"unknown pipeline {name}; choose {list(PIPELINES)}")
    meta = PIPELINES[name]
    ref = lab_root / "reference" / name
    corpus = ref / "corpus"
    study = cases_csv(lab_root, meta.get("corpus", "startup_battlefield"))
    out = ref / "analysis" / "_recomputed"
    print(f"== reproduce {name} ==")
    analyze_reference_pipeline(corpus, meta["batches"], study, out)
    write_robustness_grid(out / "gotselected_analysis_cases.csv", out)

    shipped_cases = ref / "analysis" / "gotselected_analysis_cases.csv"
    errs = _diff_cases(shipped_cases, out / "gotselected_analysis_cases.csv")
    shipped_grid = ref / "analysis" / "robustness_grid.csv"
    if shipped_grid.exists():
        errs.extend(_diff_grid(shipped_grid, out / "robustness_grid.csv"))

    if errs:
        print("FAIL:")
        for e in errs:
            print(f"  - {e}")
        return False
    print("PASS: aggregated IVs and robustness grid match shipped outputs")
    return True


def reproduce_all(lab_root: Path) -> bool:
    ok = True
    for name in PIPELINES:
        ok = reproduce_pipeline(lab_root, name) and ok
    return ok
