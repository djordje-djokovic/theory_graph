"""Full breadth inverted-U grid search across samples and control sets."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from theory_graph.robustness import CONTROL_SETS, prep, term_p

HOLDOUTS = {"pilot-65", "pilot-620", "pilot-11"}

RUNS = [
    ("full_n375_gpt4o_mini", Path("experiments/full_n375_k3_v211_gpt4o_mini/aggregated/dataset.csv")),
    ("pilot_n50_qwen3", Path("experiments/pilot_n50_k3_v211_qwen3_32b/aggregated/dataset.csv")),
    ("battle_n20_gpt4o_mini", Path("experiments/battle_n20_k3_v211_gpt4o_mini/aggregated/dataset.csv")),
    ("battle_n20_qwen3", Path("experiments/battle_n20_k3_v211_qwen3_32b/aggregated/dataset.csv")),
]


def sample_masks(df: pd.DataFrame) -> dict[str, pd.Series]:
    ids = df["id"].astype(str)
    masks = {
        "all": pd.Series(True, index=df.index),
        "non_truncated": df["truncated"] == 0 if "truncated" in df.columns else pd.Series(True, index=df.index),
        "truncated_only": df["truncated"] == 1 if "truncated" in df.columns else pd.Series(False, index=df.index),
        "confirmatory": ~ids.isin(HOLDOUTS),
        "confirmatory_nontruncated": (~ids.isin(HOLDOUTS))
        & (df["truncated"] == 0 if "truncated" in df.columns else True),
        "low_dispersion": df["breadth_run_sd"] <= df["breadth_run_sd"].median()
        if "breadth_run_sd" in df.columns
        else pd.Series(True, index=df.index),
        "high_dispersion": df["breadth_run_sd"] > df["breadth_run_sd"].median()
        if "breadth_run_sd" in df.columns
        else pd.Series(False, index=df.index),
    }
    if "encoding_valid" in df.columns:
        masks["encoding_valid"] = df["encoding_valid"] == 1
    if "eventID" in df.columns:
        for eid, grp in df.groupby("eventID"):
            if grp.shape[0] >= 40:
                masks[f"event_{eid}"] = df["eventID"] == eid
    return masks


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


def turning_point_raw(df: pd.DataFrame, b_lin: float, b_quad: float) -> float | None:
    if b_quad == 0:
        return None
    z_tp = -b_lin / (2 * b_quad)
    mu, sd = df["breadth"].mean(), df["breadth"].std()
    if sd == 0:
        return None
    return z_tp * sd + mu


def grid_one(df: pd.DataFrame, run_name: str, sample_name: str) -> list[dict]:
    rows = []
    iv = "breadth_z"
    for ctrl_label, ctrl in CONTROL_SETS:
        formula = f"GotSelected ~ {iv} + I({iv}**2){ctrl}"
        row = {
            "run": run_name,
            "sample": sample_name,
            "controls": ctrl_label,
            "n": len(df),
            "n_selected": int(df["GotSelected"].sum()) if "GotSelected" in df.columns else np.nan,
            "breadth_mean": float(df["breadth"].mean()),
            "breadth_sd": float(df["breadth"].std()),
        }
        try:
            m = fit_logit(formula, df)
            b_lin, p_lin = term_p(m, iv)
            b_quad, p_quad = term_p(m, f"I({iv} ** 2)")
            p_lrt = lrt_quad(df, iv, ctrl)
            tp_z = (-b_lin / (2 * b_quad)) if b_quad not in (None, 0) else None
            tp_raw = (
                turning_point_raw(df, b_lin, b_quad)
                if b_lin is not None and b_quad is not None
                else None
            )
            inv_u = bool(
                b_lin is not None
                and b_quad is not None
                and b_lin > 0
                and b_quad < 0
            )
            inv_u_sig = bool(inv_u and p_quad is not None and p_quad < 0.05)
            inv_u_marginal = bool(inv_u and p_quad is not None and p_quad < 0.10)
            row.update(
                {
                    "linear_b": b_lin,
                    "linear_p": p_lin,
                    "quad_b": b_quad,
                    "quad_p": p_quad,
                    "lrt_quad_p": p_lrt,
                    "turning_point_z": tp_z,
                    "turning_point_breadth": tp_raw,
                    "inverted_u_shape": inv_u,
                    "inverted_u_sig_p05": inv_u_sig,
                    "inverted_u_marginal_p10": inv_u_marginal,
                    "converged": True,
                    "error": "",
                }
            )
        except Exception as e:
            row.update(
                {
                    "linear_b": np.nan,
                    "linear_p": np.nan,
                    "quad_b": np.nan,
                    "quad_p": np.nan,
                    "lrt_quad_p": np.nan,
                    "turning_point_z": np.nan,
                    "turning_point_breadth": np.nan,
                    "inverted_u_shape": False,
                    "inverted_u_sig_p05": False,
                    "inverted_u_marginal_p10": False,
                    "converged": False,
                    "error": str(e),
                }
            )
        rows.append(row)
    return rows


def main() -> None:
    all_rows: list[dict] = []
    for run_name, path in RUNS:
        if not path.exists():
            continue
        raw = pd.read_csv(path, dtype={"id": str, "case_id": str})
        base = prep(raw, include_balance_g=False)
        for sample_name, mask in sample_masks(base).items():
            sub = base.loc[mask].copy()
            if len(sub) < 30:
                continue
            if sub["GotSelected"].nunique(dropna=True) < 2:
                continue
            # re-zscore breadth within subset
            sub["breadth_z"] = (sub["breadth"] - sub["breadth"].mean()) / sub["breadth"].std()
            if "word_count" in sub.columns:
                sub["word_count_z"] = (sub["word_count"] - sub["word_count"].mean()) / sub[
                    "word_count"
                ].std()
            all_rows.extend(grid_one(sub, run_name, sample_name))

    grid = pd.DataFrame(all_rows)
    out_dir = Path("experiments/full_n375_k3_v211_gpt4o_mini/analysis")
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "breadth_inverted_u_grid.csv"
    grid.to_csv(csv_path, index=False)

    sig = grid[grid["inverted_u_sig_p05"]].sort_values("quad_p")
    marginal = grid[grid["inverted_u_marginal_p10"] & ~grid["inverted_u_sig_p05"]].sort_values(
        "quad_p"
    )
    shape = grid[grid["inverted_u_shape"]].sort_values("quad_p")

    lines = [
        "# Breadth inverted-U grid search",
        "",
        f"Total specifications: {len(grid)}",
        f"Runs searched: {', '.join(grid['run'].unique())}",
        "",
        "## Definition",
        "- **Inverted-U shape**: linear β > 0 AND quadratic β < 0",
        "- **Significant (p<0.05)**: inverted-U shape + quadratic p < 0.05",
        "- HC1 robust SEs; breadth re-zscored within each sample subset",
        "",
        f"## Significant inverted-U (p<0.05): {len(sig)} hits",
        "",
    ]
    if len(sig):
        lines.append(sig.to_string(index=False))
    else:
        lines.append("_None_")

    lines += [
        "",
        f"## Marginal inverted-U (p<0.10, not p<0.05): {len(marginal)} hits",
        "",
    ]
    if len(marginal):
        lines.append(marginal.to_string(index=False))
    else:
        lines.append("_None_")

    lines += [
        "",
        f"## All inverted-U shapes (any p): {len(shape)} specs",
        "",
    ]
    if len(shape):
        cols = [
            "run",
            "sample",
            "controls",
            "n",
            "linear_b",
            "linear_p",
            "quad_b",
            "quad_p",
            "lrt_quad_p",
            "turning_point_breadth",
        ]
        lines.append(shape[cols].to_string(index=False))
    else:
        lines.append("_None_")

    lines += [
        "",
        "## Full gpt-4o-mini n=376 summary (all control sets)",
        "",
    ]
    gpt = grid[grid["run"] == "full_n375_gpt4o_mini"].sort_values(["sample", "controls"])
    if len(gpt):
        lines.append(
            gpt[
                [
                    "sample",
                    "controls",
                    "n",
                    "linear_b",
                    "linear_p",
                    "quad_b",
                    "quad_p",
                    "inverted_u_shape",
                    "inverted_u_sig_p05",
                ]
            ].to_string(index=False)
        )

    md_path = out_dir / "breadth_inverted_u_grid.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {csv_path} ({len(grid)} rows)")
    print(f"Wrote {md_path}")
    print(f"Significant inverted-U: {len(sig)}")
    print(f"Inverted-U shape (any p): {len(shape)}")


if __name__ == "__main__":
    main()
