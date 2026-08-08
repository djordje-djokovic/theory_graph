"""Run regressions from frozen config on aggregated/dataset.csv."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .aggregate import aggregate_batches
from .config import AnalysisBlock, ExperimentConfig
from .dataset import add_derived_columns, dataset_path, join_corpus


def _model_applies(df: pd.DataFrame, when: str | None) -> bool:
    if not when:
        return True
    if when.startswith("varies:"):
        col = when.split(":", 1)[1]
        return col in df.columns and df[col].nunique(dropna=True) > 1
    if when.startswith("column:"):
        col = when.split(":", 1)[1]
        return col in df.columns
    return when in df.columns


def run_custom_models(df: pd.DataFrame, analysis: AnalysisBlock) -> str:
    outcome = analysis.outcome
    lines = [f"{outcome} models (custom)", "=" * 60]
    if outcome not in df.columns:
        return "\n".join(lines + [f"\nMissing outcome column: {outcome}\n"])

    work = df.copy()
    n = int(work[outcome].notna().sum())
    lines[0] = f"{outcome} models (custom) — n={n} cases"

    for spec in analysis.models or []:
        if not _model_applies(work, spec.when):
            lines.append(f"\n## {spec.name}\nskipped ({spec.when or 'condition not met'})")
            continue
        d = work.dropna(subset=[outcome]).copy()
        try:
            m = smf.logit(spec.formula, data=d).fit(disp=0)
            lines.append(f"\n## {spec.name}\n```\n{m.summary().as_text()}\n```")
        except Exception as e:
            lines.append(f"\n## {spec.name}\nFAILED: {e}")

    return "\n".join(lines) + "\n"


def run_battlefield_preset(df: pd.DataFrame, outcome: str = "GotSelected") -> str:
    """Primary GotSelected models (legacy preset — same as published baselines)."""
    res_lines: list[str] = []
    n = int(df[outcome].notna().sum()) if outcome in df.columns else 0
    res_lines.append(f"{outcome} analysis — n={n} cases")
    res_lines.append("=" * 60)

    work = df.copy()
    if "n_domains" in work.columns and work["n_domains"].notna().any():
        work["n_domains_cat"] = np.where(
            work["n_domains"] <= 2,
            "1-2",
            np.where(work["n_domains"] >= 4, "4-5", "3"),
        )
        work["n_domains_cat"] = pd.Categorical(
            work["n_domains_cat"], categories=["3", "1-2", "4-5"]
        )

    def fit_logit(formula: str, label: str):
        d = work.dropna(subset=[outcome]).copy()
        try:
            m = smf.logit(formula.replace("GotSelected", outcome), data=d).fit(disp=0)
        except Exception as e:
            res_lines.append(f"\n## {label}\nFAILED: {e}")
            return None
        res_lines.append(f"\n## {label}\n```\n{m.summary().as_text()}\n```")
        return m

    m1 = fit_logit(
        f"{outcome} ~ breadth_z + I(breadth_z**2) + word_count_z",
        "M1 breadth quadratic + word count",
    )

    has_domains = "n_domains_cat" in work.columns
    if has_domains:
        fit_logit(
            f"{outcome} ~ n_domains_cat + word_count_z",
            "M2 domain count (collapsed) + word count",
        )
    else:
        res_lines.append("\nNo domain partition in this run; M2 skipped.")

    trunc_col = None
    if (
        "transcript_incomplete" in work.columns
        and work["transcript_incomplete"].nunique(dropna=True) > 1
    ):
        trunc_col = "transcript_incomplete"
    elif "truncated" in work.columns and work["truncated"].nunique(dropna=True) > 1:
        trunc_col = "truncated"
    trunc_term = f" + {trunc_col}" if trunc_col else ""
    trunc_label = (
        " + transcript incomplete"
        if trunc_col == "transcript_incomplete"
        else (" + truncation" if trunc_col else "")
    )
    if not trunc_col:
        res_lines.append(
            "\nTruncation does not vary in this run; joint models fit without the flag."
        )

    if has_domains:
        fit_logit(
            f"{outcome} ~ breadth_z + I(breadth_z**2) + n_domains_cat + word_count_z{trunc_term}",
            f"M3 joint{trunc_label}",
        )
        if all(c in work.columns for c in ("zBMI", "zAttractiveness", "zAgeAI", "Gender")):
            fit_logit(
                f"{outcome} ~ breadth_z + I(breadth_z**2) + n_domains_cat + word_count_z{trunc_term} "
                "+ zBMI + zAttractiveness + zAgeAI + C(Gender)",
                "M4 joint + appearance/demographics",
            )
    else:
        fit_logit(
            f"{outcome} ~ breadth_z + I(breadth_z**2) + word_count_z{trunc_term}",
            f"M3 breadth + word count{trunc_label}",
        )
        if all(c in work.columns for c in ("zBMI", "zAttractiveness", "zAgeAI", "Gender")):
            fit_logit(
                f"{outcome} ~ breadth_z + I(breadth_z**2) + word_count_z{trunc_term} "
                "+ zBMI + zAttractiveness + zAgeAI + C(Gender)",
                "M4 breadth + appearance/demographics",
            )

    has_composition = all(c in work.columns for c in ("breadth_D", "breadth_F", "breadth_V"))
    if has_composition:
        res_lines.append("\n## Composition — DFV (exploratory)")
        for tag_col, tag_label in (
            ("breadth_D", "Desirability"),
            ("breadth_F", "Feasibility"),
            ("breadth_V", "Viability"),
        ):
            if work[tag_col].nunique(dropna=True) > 1:
                fit_logit(
                    f"{outcome} ~ {tag_col} + word_count_z{trunc_term}",
                    f"{tag_label} count + word count{trunc_label}",
                )

    if "premise_sim_mean_z" in work.columns and work["premise_sim_mean_z"].notna().any():
        fit_logit(
            f"{outcome} ~ breadth_z + I(breadth_z**2) + premise_sim_mean_z + word_count_z{trunc_term}",
            f"M5 breadth + premise similarity control{trunc_label}",
        )
    if (
        "domain_sep_z" in work.columns
        and work["domain_sep_z"].notna().any()
        and "n_domains_z" in work.columns
    ):
        fit_logit(
            f"{outcome} ~ n_domains_z + domain_sep_z + word_count_z{trunc_term}",
            f"M6 domain count + domain separation control{trunc_label}",
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
            m0 = fit_logit(f"{outcome} ~ breadth_z + word_count_z", "M0 breadth linear (nested)")
            if m0 is not None:
                lrt = 2 * (m1.llf - m0.llf)
                res_lines.append(f"LRT quadratic vs linear: chi2(1)={lrt:.3f}")

    return "\n".join(res_lines) + "\n"


def run_analysis(df: pd.DataFrame, cfg: ExperimentConfig) -> str:
    analysis = cfg.analysis
    if analysis.preset == "custom" or analysis.models:
        return run_custom_models(df, analysis)
    return run_battlefield_preset(df, outcome=analysis.outcome)


def analyze_run(run_dir: Path) -> pd.DataFrame:
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    path = dataset_path(run_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"missing {path}; run: theory-graph measure --run {run_dir.name}"
        )
    df = pd.read_csv(path, dtype={"id": str, "case_id": str})
    out_ana = run_dir / "analysis"
    out_ana.mkdir(parents=True, exist_ok=True)
    (out_ana / "results.md").write_text(run_analysis(df, cfg), encoding="utf-8")
    return df


def analyze_reference_pipeline(
    corpus: Path,
    batch_ids: list[str],
    study_csv: Path,
    out_dir: Path,
) -> pd.DataFrame:
    """Reference reproduction path (unchanged outputs)."""
    from .config import DEFAULT_JOIN_COLUMNS

    arch = aggregate_batches(batch_ids, corpus)
    df = join_corpus(arch, study_csv, DEFAULT_JOIN_COLUMNS)
    if "GotSelected" in df.columns:
        df["GotSelected"] = pd.to_numeric(df["GotSelected"], errors="coerce")
    df = add_derived_columns(df)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "gotselected_analysis_cases.csv", index=False)
    (out_dir / "gotselected_results.md").write_text(
        run_battlefield_preset(df), encoding="utf-8"
    )
    return df


# backward compat alias
run_primary_logits = run_battlefield_preset
