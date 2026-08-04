"""Join aggregated IVs to study master and run primary logit models."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .aggregate import aggregate_batches, aggregate_run_dir

PRESENTER_COL = "10.Presentercount(numberofpresentersofthisstartup)"

STUDY_KEEP = [
    "id",
    "GotSelected",
    "event",
    "eventID",
    "year",
    "industry",
    "BMI",
    "zBMI",
    "Gender",
    "Attractiveness",
    "zAttractiveness",
    "AgeAI",
    "zAgeAI",
    "RaceAI",
    "zRaceAI",
    "ent_formality_13",
    "presenter_count",
    "know_cent_biz",
    "cust_cent_biz",
    "word_count",
]


def zscore(s: pd.Series) -> pd.Series:
    std = s.std()
    if std == 0 or pd.isna(std):
        return s * 0.0
    return (s - s.mean()) / std


def join_study(arch: pd.DataFrame, study_csv: Path) -> pd.DataFrame:
    arch = arch.copy()
    arch["id"] = arch["id"].astype(str)
    study = pd.read_csv(study_csv, dtype={"id": str})
    keep = [c for c in STUDY_KEEP if c in study.columns]
    study = study[keep].copy()
    df = arch.merge(study, on="id", how="left", suffixes=("", "_study"))
    if "GotSelected" in df.columns:
        df["GotSelected"] = pd.to_numeric(df["GotSelected"], errors="coerce")
    for col in ("word_count", "breadth", "balance", "granularity", "n_domains"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "word_count" in df.columns:
        df["word_count_z"] = zscore(df["word_count"])
    if "breadth" in df.columns:
        df["breadth_z"] = zscore(df["breadth"])
    if "balance" in df.columns:
        df["balance_z"] = zscore(df["balance"])
    if "granularity" in df.columns:
        df["granularity_z"] = zscore(df["granularity"])
    if "n_domains" in df.columns:
        df["n_domains_z"] = zscore(df["n_domains"])
    return df


def run_primary_logits(df: pd.DataFrame) -> str:
    """Return markdown dump of primary GotSelected models (same formulas as repo)."""
    res_lines: list[str] = []
    n = int(df["GotSelected"].notna().sum()) if "GotSelected" in df.columns else 0
    res_lines.append(f"GotSelected analysis — n={n} cases")
    res_lines.append("=" * 60)

    work = df.copy()
    if "n_domains" in work.columns:
        work["n_domains_cat"] = np.where(
            work["n_domains"] <= 2,
            "1-2",
            np.where(work["n_domains"] >= 4, "4-5", "3"),
        )
        work["n_domains_cat"] = pd.Categorical(
            work["n_domains_cat"], categories=["3", "1-2", "4-5"]
        )

    def fit_logit(formula: str, label: str):
        d = work.dropna(subset=["GotSelected"]).copy()
        try:
            m = smf.logit(formula, data=d).fit(disp=0)
        except Exception as e:
            res_lines.append(f"\n## {label}\nFAILED: {e}")
            return None
        res_lines.append(f"\n## {label}\n```\n{m.summary().as_text()}\n```")
        return m

    m1 = fit_logit(
        "GotSelected ~ breadth_z + I(breadth_z**2) + word_count_z",
        "M1 breadth quadratic + word count",
    )
    fit_logit(
        "GotSelected ~ n_domains_cat + word_count_z",
        "M2 domain count (collapsed) + word count",
    )
    fit_logit(
        "GotSelected ~ breadth_z + I(breadth_z**2) + n_domains_cat + word_count_z + truncated",
        "M3 joint + truncation",
    )
    if all(c in work.columns for c in ("zBMI", "zAttractiveness", "zAgeAI", "Gender")):
        fit_logit(
            "GotSelected ~ breadth_z + I(breadth_z**2) + n_domains_cat + word_count_z + truncated "
            "+ zBMI + zAttractiveness + zAgeAI + C(Gender)",
            "M4 joint + appearance/demographics",
        )

    if m1 is not None:
        b1 = m1.params.get("breadth_z")
        b2 = m1.params.get("I(breadth_z ** 2)")
        res_lines.append("\n## Breadth curvature")
        res_lines.append(
            f"linear: {b1:.4f} (p={m1.pvalues.get('breadth_z', float('nan')):.4f})"
        )
        res_lines.append(
            f"quadratic: {b2:.4f} (p={m1.pvalues.get('I(breadth_z ** 2)', float('nan')):.4f})"
        )
        if b2 is not None and b2 < 0:
            tp = -b1 / (2 * b2)
            res_lines.append(f"turning point (z): {tp:.3f}")
            res_lines.append(
                f"breadth_z range: [{work['breadth_z'].min():.2f}, {work['breadth_z'].max():.2f}]"
            )
            res_lines.append(
                "Turning point inside observed range: "
                + str(work["breadth_z"].min() <= tp <= work["breadth_z"].max())
            )
            m0 = fit_logit("GotSelected ~ breadth_z + word_count_z", "M0 breadth linear (nested)")
            if m0 is not None:
                lrt = 2 * (m1.llf - m0.llf)
                res_lines.append(f"LRT quadratic vs linear: chi2(1)={lrt:.3f}")
        else:
            res_lines.append("No inverted U (quadratic not negative).")

    return "\n".join(res_lines) + "\n"


def analyze_run(run_dir: Path, study_csv: Path, k_runs: int = 3) -> pd.DataFrame:
    arch = aggregate_run_dir(run_dir, k_runs=k_runs)
    df = join_study(arch, study_csv)
    out_agg = run_dir / "aggregated"
    out_ana = run_dir / "analysis"
    out_agg.mkdir(parents=True, exist_ok=True)
    out_ana.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_agg / "cases.csv", index=False)
    (out_ana / "results.md").write_text(run_primary_logits(df), encoding="utf-8")
    return df


def analyze_reference_pipeline(
    corpus: Path,
    batch_ids: list[str],
    study_csv: Path,
    out_dir: Path,
) -> pd.DataFrame:
    arch = aggregate_batches(batch_ids, corpus)
    df = join_study(arch, study_csv)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "gotselected_analysis_cases.csv", index=False)
    (out_dir / "gotselected_results.md").write_text(run_primary_logits(df), encoding="utf-8")
    return df
