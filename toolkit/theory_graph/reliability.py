"""Machine-reliability statistics across k independent encoding runs.

Called automatically at the end of `theory-graph measure` and via
`scripts/compute_reliability.py`.

Reports three layers (see prompts/registry.md):
  1. Breadth  (Pass A premises) — count + content agreement
  2. Modularity (Pass C domains) — domain count + grouping agreement
  3. Validation — schema compliance (from measures.csv)
"""
from __future__ import annotations

import csv
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics.pairwise import cosine_similarity

try:
    import krippendorff
except ImportError:  # pragma: no cover
    krippendorff = None

# Krippendorff's own interpretation bands (content-coding reliability).
ALPHA_GOOD = 0.800
ALPHA_TENTATIVE = 0.667

# Premise and domain counts are ratio-scaled (true zero, proportional
# differences meaningful). prompts/registry.md § Agreement protocol prescribes
# ratio-level alpha for breadth. Interval is retained as a disclosed
# sensitivity check, not as the headline figure.
COUNT_ALPHA_LEVEL = "ratio"
COUNT_ALPHA_SENSITIVITY_LEVEL = "interval"


def load_premises_runs(run_dir: Path, case_id: str, k: int) -> list[dict | None]:
    out: list[dict | None] = []
    for r in range(1, k + 1):
        p = run_dir / "encodings" / "premises" / f"run{r}" / f"{case_id}.json"
        out.append(json.loads(p.read_text(encoding="utf-8")) if p.exists() else None)
    return out


def load_domains_runs(run_dir: Path, case_id: str, k: int) -> list[dict | None]:
    out: list[dict | None] = []
    for r in range(1, k + 1):
        p = run_dir / "encodings" / "domains" / f"run{r}" / f"{case_id}.json"
        out.append(json.loads(p.read_text(encoding="utf-8")) if p.exists() else None)
    return out


def _krippendorff_alpha(mat: np.ndarray, level: str = COUNT_ALPHA_LEVEL) -> float | None:
    if krippendorff is None:
        return None
    if mat.shape[0] < 2 or np.all(np.isnan(mat)):
        return None
    try:
        return float(krippendorff.alpha(reliability_data=mat, level_of_measurement=level))
    except Exception:
        return None


def spearman_brown(alpha_single: float | None, k: int) -> float | None:
    """Reliability of an aggregate of k measurements, from single-run alpha.

    The analysis IV is not one run: `aggregate.py` writes `breadth` as the
    median of the k runs, so single-run alpha understates the reliability of
    the measure actually regressed. Spearman-Brown is exact for the *mean* of
    k, and the pipeline aggregates by median, so for k=3 this is a close
    approximation and should be read as an upper bound: the median of three is
    slightly noisier than their mean. Median is kept regardless because it is
    what stops a single runaway run from moving the case.
    """
    if alpha_single is None or k < 1:
        return None
    if alpha_single <= 0:
        return alpha_single
    denom = 1.0 + (k - 1) * alpha_single
    return float(k * alpha_single / denom) if denom else None


def attenuation_factor(reliability: float | None) -> float | None:
    """Ceiling on an observed correlation given imperfect measurement.

    A correlation between breadth and an outcome is attenuated by at most
    sqrt(reliability), so dividing an observed correlation by this factor gives
    the disattenuated upper bound.
    """
    if reliability is None or reliability <= 0:
        return None
    return float(np.sqrt(reliability))


def mean_absolute_difference(mat: np.ndarray) -> float | None:
    """Mean over cases of the mean pairwise |difference| between runs.

    Reported alongside alpha because alpha on a count is sensitive to
    between-case range restriction, which a raw discrepancy in premise
    counts is not.
    """
    if mat.shape[0] < 2:
        return None
    per_case: list[float] = []
    for j in range(mat.shape[1]):
        col = mat[:, j]
        col = col[~np.isnan(col)]
        if col.size < 2:
            continue
        diffs = [
            abs(col[a] - col[b])
            for a in range(col.size)
            for b in range(a + 1, col.size)
        ]
        per_case.append(float(np.mean(diffs)))
    return float(np.mean(per_case)) if per_case else None


def count_matrix(loader, run_dir: Path, case_ids: list[str], k: int, field: str) -> np.ndarray:
    """Shape (k, N): rows = runs, columns = cases."""
    mat = np.full((k, len(case_ids)), np.nan)
    for j, cid in enumerate(case_ids):
        runs = loader(run_dir, cid, k)
        for i, obj in enumerate(runs):
            if obj is None:
                continue
            if field == "breadth":
                mat[i, j] = len(obj.get("premises") or [])
            elif field == "n_domains":
                mat[i, j] = len(obj.get("domains") or [])
    return mat


def breadth_matrix(run_dir: Path, case_ids: list[str], k: int) -> np.ndarray:
    return count_matrix(load_premises_runs, run_dir, case_ids, k, "breadth")


def n_domains_matrix(run_dir: Path, case_ids: list[str], k: int) -> np.ndarray:
    return count_matrix(load_domains_runs, run_dir, case_ids, k, "n_domains")


def krippendorff_alpha_breadth(mat: np.ndarray) -> float | None:
    return _krippendorff_alpha(mat)


def _premise_partition(case: dict) -> dict[str, str]:
    """Map each premise_id -> domain_id for one domains encoding."""
    out: dict[str, str] = {}
    for d in case.get("domains") or []:
        did = d.get("id") or ""
        for pid in d.get("premise_ids") or []:
            out[str(pid)] = str(did)
    return out


def partition_ari(a: dict[str, str], b: dict[str, str]) -> float | None:
    """Adjusted Rand Index on premise→domain assignments (same premise IDs)."""
    pids = sorted(set(a.keys()) | set(b.keys()))
    if len(pids) < 2:
        return None
    labels_a = [a.get(pid, "__unassigned__") for pid in pids]
    labels_b = [b.get(pid, "__unassigned__") for pid in pids]
    return float(adjusted_rand_score(labels_a, labels_b))


def _fit_vectorizer(run_dir: Path, case_ids: list[str], k: int) -> TfidfVectorizer:
    texts: list[str] = []
    for cid in case_ids:
        for obj in load_premises_runs(run_dir, cid, k):
            if obj is None:
                continue
            for p in obj.get("premises") or []:
                t = (p.get("text") or "").strip()
                texts.append(t if t else " ")
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    vec.fit(texts or [" "])
    return vec


def _align_pair(texts_a: list[str], texts_b: list[str], vec: TfidfVectorizer) -> list[float]:
    if not texts_a or not texts_b:
        return [0.0] * max(len(texts_a), len(texts_b))
    sim = cosine_similarity(vec.transform(texts_a), vec.transform(texts_b))
    row_ind, col_ind = linear_sum_assignment(-sim)
    matched = {int(r): float(sim[r, c]) for r, c in zip(row_ind, col_ind)}
    n = max(len(texts_a), len(texts_b))
    return [matched.get(i, 0.0) for i in range(len(texts_a))] + [0.0] * (n - len(texts_a))


def content_alignment_report(
    run_dir: Path, case_ids: list[str], k: int, *, threshold: float = 0.35,
) -> tuple[pd.DataFrame, dict]:
    vec = _fit_vectorizer(run_dir, case_ids, k)
    rows: list[dict] = []
    for cid in case_ids:
        runs = load_premises_runs(run_dir, cid, k)
        texts = [
            [(p.get("text") or "").strip() for p in (obj.get("premises") or [])]
            if obj is not None else []
            for obj in runs
        ]
        pair_sims: list[float] = []
        pair_match_shares: list[float] = []
        for i, j in combinations(range(k), 2):
            sims = _align_pair(texts[i], texts[j], vec)
            if not sims:
                continue
            pair_sims.extend(sims)
            pair_match_shares.append(float(np.mean([s >= threshold for s in sims])))
        rows.append({
            "case_id": cid,
            "n_runs_present": sum(1 for t in texts if t),
            "breadths": [len(t) for t in texts],
            "mean_best_match_sim": float(np.mean(pair_sims)) if pair_sims else float("nan"),
            "matched_share_at_threshold": float(np.mean(pair_match_shares)) if pair_match_shares else float("nan"),
        })
    df = pd.DataFrame(rows)
    summary = {
        "n_cases": len(df),
        "mean_best_match_sim": float(df["mean_best_match_sim"].mean()),
        "median_best_match_sim": float(df["mean_best_match_sim"].median()),
        "mean_matched_share_at_threshold": float(df["matched_share_at_threshold"].mean()),
        "median_matched_share_at_threshold": float(df["matched_share_at_threshold"].median()),
        "threshold": threshold,
    }
    return df, summary


def modularity_reliability_report(
    run_dir: Path, case_ids: list[str], k: int,
) -> tuple[pd.DataFrame, dict]:
    rows: list[dict] = []
    for cid in case_ids:
        runs = load_domains_runs(run_dir, cid, k)
        partitions = [_premise_partition(obj) for obj in runs if obj is not None]
        n_domains_list = [len(obj.get("domains") or []) for obj in runs if obj is not None]
        pair_aris: list[float] = []
        for i, j in combinations(range(len(partitions)), 2):
            ari = partition_ari(partitions[i], partitions[j])
            if ari is not None:
                pair_aris.append(ari)
        rows.append({
            "case_id": cid,
            "n_runs_present": len(partitions),
            "n_domains_runs": n_domains_list,
            "mean_pairwise_ari": float(np.mean(pair_aris)) if pair_aris else float("nan"),
        })
    df = pd.DataFrame(rows)
    mat = n_domains_matrix(run_dir, case_ids, k)
    summary = {
        "n_cases": len(df),
        "k_domains": k,
        "krippendorff_alpha_n_domains": _krippendorff_alpha(mat),
        "mean_pairwise_ari": float(df["mean_pairwise_ari"].mean()),
        "median_pairwise_ari": float(df["mean_pairwise_ari"].median()),
        "cases_with_k_runs": int((df["n_runs_present"] >= k).sum()),
    }
    return df, summary


def _validation_summary(measures_csv: Path) -> dict[str, dict]:
    if not measures_csv.exists():
        return {}
    df = pd.read_csv(measures_csv)
    out: dict[str, dict] = {}
    for pass_name in df["pass"].unique():
        sub = df[df["pass"] == pass_name]
        out[str(pass_name)] = {
            "n_files": len(sub),
            "valid_rate": float(sub["valid"].mean()),
            "mean_errors": float(sub["n_errors"].mean()),
        }
    return out


def _alpha_band(alpha: float | None) -> str:
    if alpha is None:
        return "not computed (need k≥2 runs with data)"
    if alpha >= ALPHA_GOOD:
        return "good (≥0.80)"
    if alpha >= ALPHA_TENTATIVE:
        return "tentative (0.67–0.80)"
    return "below tentative (<0.67)"


def _fmt_num(x: float | None, *, digits: int = 3) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/a"
    return f"{x:.{digits}f}"


def write_reliability_report(
    run_dir: Path,
    case_ids: list[str],
    *,
    k_premises: int = 3,
    k_domains: int = 3,
    content_threshold: float = 0.35,
    measures_csv: Path | None = None,
) -> Path:
    """Write human-readable reliability report; return path to markdown file."""
    measures_csv = measures_csv or (run_dir / "validation" / "measures.csv")
    val_dir = run_dir / "validation"
    val_dir.mkdir(parents=True, exist_ok=True)

    b_mat = breadth_matrix(run_dir, case_ids, k_premises)
    alpha_breadth = _krippendorff_alpha(b_mat)
    alpha_breadth_interval = _krippendorff_alpha(b_mat, COUNT_ALPHA_SENSITIVITY_LEVEL)
    mad_breadth = mean_absolute_difference(b_mat)
    sb_ratio = spearman_brown(alpha_breadth, k_premises)
    sb_interval = spearman_brown(alpha_breadth_interval, k_premises)
    atten_ratio = attenuation_factor(sb_ratio)
    prem_df, prem_sum = content_alignment_report(
        run_dir, case_ids, k_premises, threshold=content_threshold,
    )
    prem_df.to_csv(val_dir / "reliability_premises_per_case.csv", index=False)

    dom_k = k_domains
    dom_df, dom_sum = modularity_reliability_report(run_dir, case_ids, dom_k)
    dom_df.to_csv(val_dir / "reliability_domains_per_case.csv", index=False)

    validation = _validation_summary(measures_csv)
    n_complete_b = int(sum(1 for j in range(b_mat.shape[1]) if not np.any(np.isnan(b_mat[:, j]))))

    lines = [
        "# Reliability report",
        "",
        f"Experiment: `{run_dir.name}`",
        f"Cases: {len(case_ids)} | Premises runs (k): {k_premises} | Domains runs (k): {dom_k}",
        "",
        "This file is produced automatically when you run **`theory-graph measure`**.",
        "It summarizes **within-model** agreement: how consistently the same AI model",
        "codes the same pitch when run multiple times on the same prompt.",
        "",
        "---",
        "",
        "## Quick glossary",
        "",
        "| Term | Plain English |",
        "|---|---|",
        "| **Breadth** | How many premises (claims) the model extracts from a pitch (Pass A). |",
        "| **Modularity** | How the model groups those premises into strategic domains (Pass C). |",
        "| **Krippendorff's α** | Agreement on a *number* across runs (e.g. premise count or domain count). "
        "1.0 = perfect; ≥0.80 good; 0.67–0.80 tentative; <0.67 weak. Computed from all k runs, and it "
        "reports how reliable a *single* run would be as a measure. |",
        "| **Spearman-Brown** | Converts that into the reliability of an *aggregate* of k runs — which is "
        "what the analysis actually uses, since `breadth` is the median of the runs. |",
        "| **Content alignment** | Do the *wordings* of premises match across runs? "
        "(Needed because each run labels claims P1, P2… independently.) |",
        "| **ARI (Adjusted Rand Index)** | Do runs put the *same premises in the same domain groups*? "
        "1.0 = identical grouping; 0 = chance. |",
        "| **Validation %** | Share of JSON files that pass schema checks (not agreement — "
        "one run per file). |",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| What | Metric | Value | Interpretation |",
        "|---|---|---|---|",
        f"| Breadth: agree on **count**? | Krippendorff α (ratio), one run as the measure | "
        f"{_fmt_num(alpha_breadth)} | "
        f"{_alpha_band(alpha_breadth)} |",
        f"| Breadth: how far apart are the counts? | Mean absolute difference | "
        f"{_fmt_num(mad_breadth)} | "
        "Premises, on average, between any two runs of the same pitch. |",
        f"| Breadth: reliability of the **analysed** variable | "
        f"Aggregate α, median of {k_premises} | "
        f"{_fmt_num(sb_ratio)} | {_alpha_band(sb_ratio)} |",
        f"| Breadth: agree on **wording**? | Content match share (≥{content_threshold}) | "
        f"{prem_sum['mean_matched_share_at_threshold']:.3f} | "
        "Higher is better; ~1.0 means runs extract the same claims. |",
        f"| Modularity: agree on **domain count**? | Krippendorff α (n_domains) | "
        f"{_fmt_num(dom_sum['krippendorff_alpha_n_domains'])} | "
        f"{_alpha_band(dom_sum['krippendorff_alpha_n_domains'])} |",
        f"| Modularity: agree on **grouping**? | Mean pairwise ARI | "
        f"{_fmt_num(dom_sum['mean_pairwise_ari'])} | "
        "≥0.80 strong; 0.50–0.80 moderate; <0.50 weak. |",
        "",
    ]

    if validation:
        lines.extend(["### Validation (schema compliance, not agreement)", ""])
        for pname, stats in sorted(validation.items()):
            lines.append(
                f"- **{pname}**: {stats['valid_rate']*100:.0f}% valid "
                f"({stats['n_files']} files, avg {stats['mean_errors']:.1f} errors/file)"
            )
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Pass A — Premises (breadth)",
        "",
        "**Question:** When we ask the model three times to list the main claims in a pitch,",
        "does it find the same number of claims and roughly the same content?",
        "",
        f"- Krippendorff α on premise count, **ratio** level: **{_fmt_num(alpha_breadth)}** "
        f"({n_complete_b}/{len(case_ids)} cases with all {k_premises} runs)",
        f"- Mean absolute difference in premise count between runs: **{_fmt_num(mad_breadth)}**",
        f"- Mean content-match share: **{prem_sum['mean_matched_share_at_threshold']:.3f}**",
        f"- Per-case detail: `validation/reliability_premises_per_case.csv`",
        "",
        "### Reliability of the measure actually analysed",
        "",
        f"`aggregated/dataset.csv` records `breadth` as the **median of the {k_premises} runs**, "
        "not a single run, so the figures above are the reliability of one run and understate the "
        "reliability of the analysed variable. Per-case dispersion is kept in `breadth_run_sd`, "
        "which is the column to filter on when selecting cases for human adjudication.",
        "",
        "Both rows below are estimated from **all "
        f"{k_premises} runs**; α cannot be computed from one run. What differs is how many runs "
        "make up the measure being evaluated, not how much data the estimate uses. This is the "
        "usual distinction between the reliability of one rater and the reliability of an average "
        "of several: α answers the first by construction, Spearman-Brown extrapolates to the "
        "second.",
        "",
        "| Measure being evaluated | α (ratio) | α (interval) | Reading |",
        "|---|---|---|---|",
        f"| One run, if it were used alone | {_fmt_num(alpha_breadth)} | "
        f"{_fmt_num(alpha_breadth_interval)} | Conservative floor; not what is analysed. |",
        f"| Median of {k_premises} runs — **the analysed variable** | "
        f"**{_fmt_num(sb_ratio)}** | {_fmt_num(sb_interval)} | "
        f"{_alpha_band(sb_ratio)} at ratio, {_alpha_band(sb_interval)} at interval. |",
        "",
        f"Ceiling on an observed correlation given this reliability: **{_fmt_num(atten_ratio)}** — "
        "divide an observed correlation by it for the disattenuated bound.",
        "",
        "Spearman-Brown is exact for the mean of k and the pipeline uses the median, so for k=3 the "
        "aggregate figures are close approximations and should be read as upper bounds — the median "
        "of three is slightly noisier than their mean. Median is retained deliberately, because it "
        "is what prevents one runaway run from moving a case.",
        "",
        "Because measurement error in an independent variable biases coefficients toward zero, "
        "breadth effects estimated from this data are attenuated rather than inflated: an observed "
        "association is a lower bound on the true one, while a null result is weaker evidence of "
        "absence than it would be under perfect measurement. Report the aggregate reliability "
        "alongside any breadth coefficient. Note also that this addresses random error only — "
        "systematic over- or under-splitting is shared across runs of the same model and survives "
        "aggregation, which is what human–model agreement is needed to detect.",
        "",
        "Breadth is a count with a true zero, so α is computed at **ratio** level per",
        "`prompts/registry.md` § Agreement protocol. Because α on a count is sensitive to",
        "between-case range restriction, the mean absolute difference is reported alongside it,",
        "and the interval-level figure is disclosed as a sensitivity check:",
        f"α (interval) = **{_fmt_num(alpha_breadth_interval)}**.",
        "",
        "## Pass C — Domains (modularity)",
        "",
        "**Question:** Given the *same* frozen premise list, does the model group premises",
        "into the same strategic domains across repeated runs?",
        "",
        f"- Cases with all {dom_k} domain runs: **{dom_sum['cases_with_k_runs']}/{len(case_ids)}**",
        f"- Krippendorff α on domain count (n_domains): "
        f"**{_fmt_num(dom_sum['krippendorff_alpha_n_domains'])}**",
        f"- Mean pairwise ARI on grouping: "
        f"**{_fmt_num(dom_sum['mean_pairwise_ari'])}**",
        f"- Per-case detail: `validation/reliability_domains_per_case.csv`",
        "",
        "## What this report does *not* include",
        "",
        "- **Human–model agreement** (compare model to human-coded gold standard).",
        "- **Within-human agreement** (two human coders on the same pitch).",
        "- **DFV tag agreement** (Pass B); run k≥3 on `dfv` separately if needed.",
        "",
        "See `prompts/registry.md` § Agreement protocol for the full reliability design.",
        "",
    ])

    out_path = val_dir / "reliability_report.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
