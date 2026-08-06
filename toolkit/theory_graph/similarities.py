"""Semantic similarity controls on premise text (AMJ robustness covariates)."""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .aggregate import load_case
from .config import ExperimentConfig

SIMILARITY_COLS = (
    "premise_sim_mean",
    "within_domain_sim",
    "between_domain_sim",
    "domain_sep",
)


def pairwise_mean_sim(mat: np.ndarray) -> float:
    n = mat.shape[0]
    if n < 2:
        return float("nan")
    sims = [float(mat[i, j]) for i, j in combinations(range(n), 2)]
    return float(np.mean(sims)) if sims else float("nan")


def case_similarities(case: dict, vectorizer: TfidfVectorizer) -> dict[str, float]:
    """Mean premise similarity and within/between domain separation for one encoding."""
    premises = case.get("premises") or []
    texts = [(p.get("text") or "").strip() or " " for p in premises]
    ids = [p.get("id") for p in premises]
    empty = {col: float("nan") for col in SIMILARITY_COLS}
    if len(texts) < 2:
        return empty

    sim = cosine_similarity(vectorizer.transform(texts))
    prem_sim = pairwise_mean_sim(sim)

    lookup: dict[str, str] = {}
    for domain in case.get("domains") or []:
        for pid in domain.get("premise_ids") or []:
            lookup[pid] = domain["id"]

    within_sims: list[float] = []
    between_sims: list[float] = []
    for i, j in combinations(range(len(ids)), 2):
        s = float(sim[i, j])
        di, dj = lookup.get(ids[i]), lookup.get(ids[j])
        if di is not None and di == dj:
            within_sims.append(s)
        elif di is not None and dj is not None and di != dj:
            between_sims.append(s)

    within = float(np.mean(within_sims)) if within_sims else float("nan")
    between = float(np.mean(between_sims)) if between_sims else float("nan")
    domain_sep = (
        within - between
        if not (np.isnan(within) or np.isnan(between))
        else float("nan")
    )
    return {
        "premise_sim_mean": prem_sim,
        "within_domain_sim": within,
        "between_domain_sim": between,
        "domain_sep": domain_sep,
    }


def _pass_dirs(enc: Path) -> list[Path] | None:
    dirs = [d for d in enc.iterdir() if d.is_dir() and not d.name.startswith("run")]
    return dirs or None


def _k_for(cfg: ExperimentConfig, pass_name: str, fallback: int) -> int:
    for p in cfg.resolved_passes():
        if p.name == pass_name:
            return p.k_runs
    return fallback


def merged_case_dicts(
    run_dir: Path,
    cfg: ExperimentConfig,
    case_id: str,
    *,
    k_runs: int = 3,
) -> list[dict]:
    """Premises (+ optional domains) per extraction run, merged for similarity."""
    enc = run_dir / "encodings"
    if not enc.exists():
        return []

    pass_dirs = _pass_dirs(enc)
    k_premises = _k_for(cfg, "premises", k_runs)
    k_domains = _k_for(cfg, "domains", 1)
    merged: list[dict] = []

    if pass_dirs:
        premises_dir = next((d for d in pass_dirs if d.name == "premises"), None)
        domains_dir = next((d for d in pass_dirs if d.name == "domains"), None)
        if premises_dir:
            for r in range(1, k_premises + 1):
                p_path = premises_dir / f"run{r}" / f"{case_id}.json"
                if not p_path.exists():
                    continue
                case = load_case(p_path)
                if domains_dir:
                    d_run = min(r, k_domains)
                    d_path = domains_dir / f"run{d_run}" / f"{case_id}.json"
                    if d_path.exists():
                        case = {**case, "domains": load_case(d_path).get("domains") or []}
                merged.append(case)
        else:
            for pdir in pass_dirs:
                for r in range(1, _k_for(cfg, pdir.name, k_runs) + 1):
                    p_path = pdir / f"run{r}" / f"{case_id}.json"
                    if p_path.exists():
                        merged.append(load_case(p_path))
    else:
        for r in range(1, k_runs + 1):
            p_path = enc / f"run{r}" / f"{case_id}.json"
            if p_path.exists():
                merged.append(load_case(p_path))
    return merged


def _all_premise_texts(cases: list[dict]) -> list[str]:
    texts: list[str] = []
    for case in cases:
        for prem in case.get("premises") or []:
            t = (prem.get("text") or "").strip()
            texts.append(t if t else " ")
    return texts


def similarity_frame(
    run_dir: Path,
    cfg: ExperimentConfig,
    case_ids: list[str],
    *,
    k_runs: int = 3,
) -> pd.DataFrame:
    """Case-level similarity measures (median across premise runs)."""
    all_cases: list[dict] = []
    per_case_runs: dict[str, list[dict]] = {}
    for cid in case_ids:
        runs = merged_case_dicts(run_dir, cfg, cid, k_runs=k_runs)
        per_case_runs[cid] = runs
        all_cases.extend(runs)

    if not all_cases:
        return pd.DataFrame(columns=["case_id", *SIMILARITY_COLS])

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    vectorizer.fit(_all_premise_texts(all_cases))

    rows: list[dict] = []
    for cid in case_ids:
        run_metrics = [case_similarities(c, vectorizer) for c in per_case_runs.get(cid, [])]
        if not run_metrics:
            continue
        row: dict[str, float | str] = {"case_id": cid}
        for col in SIMILARITY_COLS:
            vals = [m[col] for m in run_metrics if not np.isnan(m[col])]
            row[col] = float(np.median(vals)) if vals else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)
