"""Robustness grid (shared controls) — path-independent port of run_robustness_grid.py."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

CONTROL_SETS: list[tuple[str, str]] = [
    ("C0 none", ""),
    ("C1 word_count_z", " + word_count_z"),
    ("C2 BMI_paper_raw", " + C(Gender) + AgeAI + RaceAI + Attractiveness + ent_formality_13"),
    ("C3 BMI_paper_z", " + C(Gender) + zAgeAI + zRaceAI + zAttractiveness + ent_formality_13"),
    ("C4 BMI+eventFE", " + C(Gender) + zAgeAI + zRaceAI + zAttractiveness + ent_formality_13 + C(eventID)"),
    ("C5 BMI+eventFE+zBMI", " + zBMI + C(Gender) + zAgeAI + zRaceAI + zAttractiveness + ent_formality_13 + C(eventID)"),
    ("C6 meas_plan", " + word_count_z + truncated + presenter_count"),
    ("C7 meas+appearance", " + word_count_z + truncated + presenter_count + zBMI + zAttractiveness + zAgeAI + zRaceAI + C(Gender)"),
    ("C8 meas+appearance+eventFE", " + word_count_z + truncated + presenter_count + zBMI + zAttractiveness + zAgeAI + zRaceAI + C(Gender) + C(eventID)"),
    ("C9 full+BMI_moderators", " + word_count_z + truncated + presenter_count + zBMI + zAttractiveness + zAgeAI + zRaceAI + C(Gender) + know_cent_biz + cust_cent_biz + C(eventID)"),
    ("C10 full+industry", " + word_count_z + truncated + presenter_count + zBMI + zAttractiveness + zAgeAI + zRaceAI + C(Gender) + know_cent_biz + cust_cent_biz + C(eventID) + C(industry)"),
    ("C11 full+year", " + word_count_z + truncated + presenter_count + zBMI + zAttractiveness + zAgeAI + zRaceAI + C(Gender) + know_cent_biz + cust_cent_biz + C(eventID) + year"),
]


def zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std()


def prep(df: pd.DataFrame, include_balance_g: bool = True) -> pd.DataFrame:
    df = df.copy()
    df["GotSelected"] = pd.to_numeric(df["GotSelected"], errors="coerce")
    for v in [
        "breadth",
        "n_domains",
        "balance",
        "granularity",
        "word_count",
        "presenter_count",
        "know_cent_biz",
        "cust_cent_biz",
        "year",
    ]:
        if v in df.columns:
            df[v] = pd.to_numeric(df[v], errors="coerce")
    df["breadth_z"] = zscore(df["breadth"])
    df["n_domains_z"] = zscore(df["n_domains"])
    if include_balance_g and "balance" in df.columns:
        df["balance_z"] = zscore(df["balance"])
    if include_balance_g and "granularity" in df.columns:
        df["granularity_z"] = zscore(df["granularity"])
    if "word_count" in df.columns:
        df["word_count_z"] = zscore(df["word_count"])
    return df.dropna(subset=["GotSelected"])


def term_p(model, stem: str) -> tuple[float | None, float | None]:
    for k in model.params.index:
        if k.replace(" ", "") == stem.replace(" ", "") or k == stem:
            return float(model.params[k]), float(model.pvalues[k])
    return None, None


def fit_logit(formula: str, df: pd.DataFrame):
    return smf.logit(formula, data=df).fit(disp=0, cov_type="HC1")


def lrt_quad(df: pd.DataFrame, iv: str, controls: str) -> float | None:
    lin = f"GotSelected ~ {iv} {controls}".strip()
    quad = f"GotSelected ~ {iv} + I({iv}**2) {controls}".strip()
    try:
        m0 = fit_logit(lin, df)
        m1 = fit_logit(quad, df)
        stat = 2 * (m1.llf - m0.llf)
        return float(stats.chi2.sf(stat, 1))
    except Exception:
        return None


def run_grid(df: pd.DataFrame, ivs: list[tuple[str, str]]) -> pd.DataFrame:
    rows = []
    for label, ctrl in CONTROL_SETS:
        for iv_name, iv_z in ivs:
            if iv_z not in df.columns:
                continue
            formula = f"GotSelected ~ {iv_z} + I({iv_z}**2){ctrl}"
            try:
                m = fit_logit(formula, df)
                b_lin, p_lin = term_p(m, iv_z)
                b_quad, p_quad = term_p(m, f"I({iv_z} ** 2)")
                p_lrt = lrt_quad(df, iv_z, ctrl)
                inv_u = bool(
                    b_quad is not None and b_quad < 0 and p_quad is not None and p_quad < 0.05
                )
                rows.append(
                    {
                        "controls": label,
                        "iv": iv_name,
                        "n": int(m.nobs),
                        "linear_b": b_lin,
                        "linear_p": p_lin,
                        "quad_b": b_quad,
                        "quad_p": p_quad,
                        "lrt_quad_p": p_lrt,
                        "inverted_u_sig": inv_u,
                        "converged": bool(getattr(m, "mle_retvals", {}).get("converged", True)),
                        "error": "",
                    }
                )
            except Exception as e:
                rows.append(
                    {
                        "controls": label,
                        "iv": iv_name,
                        "n": len(df),
                        "linear_b": np.nan,
                        "linear_p": np.nan,
                        "quad_b": np.nan,
                        "quad_p": np.nan,
                        "lrt_quad_p": np.nan,
                        "inverted_u_sig": False,
                        "converged": False,
                        "error": str(e),
                    }
                )
    return pd.DataFrame(rows)


def write_robustness_grid(
    cases_csv: Path,
    out_dir: Path,
    ivs: list[str] | None = None,
) -> pd.DataFrame:
    ivs = ivs or ["breadth", "modularity", "balance", "granularity"]
    include_bg = any(x in ivs for x in ("balance", "granularity"))
    df = prep(pd.read_csv(cases_csv, dtype={"id": str}), include_balance_g=include_bg)
    out_dir.mkdir(parents=True, exist_ok=True)
    iv_map = {
        "breadth": ("breadth", "breadth_z"),
        "modularity": ("modularity", "n_domains_z"),
        "balance": ("balance", "balance_z"),
        "granularity": ("granularity", "granularity_z"),
    }
    grid = run_grid(df, [iv_map[k] for k in ivs if k in iv_map])
    grid.to_csv(out_dir / "robustness_grid.csv", index=False)
    lines = [
        "# Robustness grid — breadth vs modularity (shared controls)",
        "",
        f"n = {len(df)} cases, HC1 robust SEs",
        f"cases file: `{cases_csv}`",
        f"IVs: {', '.join(ivs)}",
        "",
        grid.to_string(index=False),
        "",
    ]
    (out_dir / "robustness_grid.md").write_text("\n".join(lines), encoding="utf-8")
    return grid
