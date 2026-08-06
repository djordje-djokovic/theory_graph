"""Build case-level analysis dataset (IVs + outcomes + controls + optional embeddings)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .aggregate import aggregate_run_dir
from .config import ExperimentConfig
from .validate import load_transcript


NUMERIC_IV_COLS = (
    "word_count", "breadth", "breadth_explicit", "balance", "granularity", "n_domains",
    "breadth_D", "breadth_F", "breadth_V", "breadth_O", "concentration", "balance_DFV",
    "premise_sim_mean", "within_domain_sim", "between_domain_sim", "domain_sep",
)


def zscore(s: pd.Series) -> pd.Series:
    std = s.std()
    if std == 0 or pd.isna(std):
        return s * 0.0
    return (s - s.mean()) / std


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in NUMERIC_IV_COLS:
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
    if "n_domains" in df.columns and df["n_domains"].notna().any():
        df["n_domains_z"] = zscore(df["n_domains"])
        df["n_domains_cat"] = np.where(
            df["n_domains"] <= 2,
            "1-2",
            np.where(df["n_domains"] >= 4, "4-5", "3"),
        )
        df["n_domains_cat"] = pd.Categorical(
            df["n_domains_cat"], categories=["3", "1-2", "4-5"]
        )
    for col in ("premise_sim_mean", "domain_sep", "within_domain_sim", "between_domain_sim"):
        if col in df.columns and df[col].notna().any():
            df[f"{col}_z"] = zscore(df[col])
    return df


def join_corpus(arch: pd.DataFrame, study_csv: Path, join_columns: list[str]) -> pd.DataFrame:
    arch = arch.copy()
    arch["id"] = arch["id"].astype(str)
    study = pd.read_csv(study_csv, dtype={"id": str})
    keep = ["id"] + [c for c in join_columns if c in study.columns]
    study = study[keep].copy()
    return arch.merge(study, on="id", how="left", suffixes=("", "_study"))


def attach_validation_summary(df: pd.DataFrame, measures_csv: Path) -> pd.DataFrame:
    if not measures_csv.exists():
        return df
    m = pd.read_csv(measures_csv, dtype={"case_id": str})
    if m.empty:
        return df
    summary = (
        m.groupby("case_id", as_index=False)
        .agg(
            encoding_valid=("valid", "all"),
            n_encoding_errors=("n_errors", "sum"),
            n_encoding_files=("valid", "count"),
        )
    )
    return df.merge(summary, on="case_id", how="left")


def _premises_text(run_dir: Path, case_id: str, k: int) -> str:
    parts = []
    for r in range(1, k + 1):
        p = run_dir / "encodings" / "premises" / f"run{r}" / f"{case_id}.json"
        if p.exists():
            obj = json.loads(p.read_text(encoding="utf-8"))
            for prem in obj.get("premises") or []:
                parts.append(prem.get("text") or "")
    return "\n".join(parts)


def add_similarities(
    df: pd.DataFrame,
    cfg: ExperimentConfig,
    run_dir: Path,
    *,
    k_runs: int = 3,
) -> pd.DataFrame:
    sim_cfg = cfg.dataset.similarities
    if not sim_cfg.enabled:
        return df
    if sim_cfg.method != "tfidf":
        raise RuntimeError(f"unsupported similarity method: {sim_cfg.method!r}")

    from .similarities import similarity_frame

    case_ids = [str(c) for c in df["case_id"].tolist()]
    sims = similarity_frame(run_dir, cfg, case_ids, k_runs=k_runs)
    if sims.empty:
        return df
    out = df.copy()
    out["case_id"] = out["case_id"].astype(str)
    return out.merge(sims, on="case_id", how="left")


def add_embeddings(
    df: pd.DataFrame,
    cfg: ExperimentConfig,
    run_dir: Path,
    transcripts: Path | None,
) -> pd.DataFrame:
    emb = cfg.dataset.embeddings
    if not emb.enabled:
        return df
    try:
        import litellm
    except ImportError as e:
        raise RuntimeError("embeddings.enabled requires litellm (pip install litellm)") from e

    premises_k = next((p.k_runs for p in cfg.resolved_passes() if p.name == "premises"), 3)
    vectors: list[list[float] | None] = []
    for _, row in df.iterrows():
        case_id = row["case_id"]
        if emb.source == "premises":
            text = _premises_text(run_dir, case_id, premises_k)
        else:
            text = load_transcript(transcripts, case_id) if transcripts else None
        if not text or not str(text).strip():
            vectors.append(None)
            continue
        resp = litellm.embedding(model=emb.model, input=[text])
        vectors.append(list(resp.data[0]["embedding"]))

    dim = max((len(v) for v in vectors if v), default=0)
    if dim == 0:
        return df
    out = df.copy()
    for i in range(dim):
        out[f"emb_{i}"] = [v[i] if v and len(v) > i else np.nan for v in vectors]
    return out


def build_dataset(
    run_dir: Path,
    cfg: ExperimentConfig,
    study_csv: Path,
    *,
    k_runs: int = 3,
    transcripts: Path | None = None,
    measures_csv: Path | None = None,
) -> pd.DataFrame:
    arch = aggregate_run_dir(run_dir, k_runs=k_runs, transcripts=transcripts)
    df = join_corpus(arch, study_csv, cfg.resolved_join_columns())
    outcome = cfg.dataset.outcome
    if outcome in df.columns:
        df[outcome] = pd.to_numeric(df[outcome], errors="coerce")
    df = add_similarities(df, cfg, run_dir, k_runs=k_runs)
    df = add_derived_columns(df)
    if measures_csv:
        df = attach_validation_summary(df, measures_csv)
    df = add_embeddings(df, cfg, run_dir, transcripts)
    return df


def dataset_path(run_dir: Path) -> Path:
    return run_dir / "aggregated" / "dataset.csv"


def write_dataset(df: pd.DataFrame, run_dir: Path) -> Path:
    out_dir = run_dir / "aggregated"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = dataset_path(run_dir)
    df.to_csv(path, index=False)
    df.to_csv(out_dir / "cases.csv", index=False)
    return path
