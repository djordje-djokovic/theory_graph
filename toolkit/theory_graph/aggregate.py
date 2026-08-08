"""Aggregate k-run encodings into case-level IVs (breadth, composition, ...).

Logic ported from scripts/run_gotselected_analysis.py — kept path-independent.
Supports both single-pass (v2.0.0 and earlier) and two-pass (v2.1.0) layouts.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from .validate import transcript_incomplete, transcript_truncated


def load_case(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_transcript(transcripts: Path | None, case_id: str) -> str | None:
    if transcripts is None:
        return None
    for name in (f"{case_id}.txt", f"{case_id.removeprefix('pilot-')}.txt"):
        path = transcripts / name
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


def breadth(case: dict) -> int:
    return len(case.get("premises") or [])


def breadth_explicit(case: dict) -> int:
    return sum(1 for p in case.get("premises") or [] if p.get("status") == "explicit")


def n_domains(case: dict) -> int:
    return len(case.get("domains") or [])


def balance_of(case: dict) -> float:
    n_p = breadth(case)
    if not n_p:
        return float("nan")
    counts = [len(d.get("premise_ids") or []) for d in case.get("domains") or []]
    counts = [c for c in counts if c]
    if not counts:
        return float("nan")
    return 1.0 - sum((c / n_p) ** 2 for c in counts)


def granularity_of(case: dict) -> float:
    n_p = breadth(case)
    if not n_p:
        return float("nan")
    return n_domains(case) / n_p


def composition_measures(assignments: list[dict]) -> dict:
    """Compute DFV composition from Pass B assignments."""
    tags = [a.get("tag", "OTHER") for a in assignments if a.get("tag")]
    n = len(tags)
    if not n:
        return {
            "breadth_D": 0, "breadth_F": 0, "breadth_V": 0, "breadth_O": 0,
            "concentration": float("nan"), "balance_DFV": float("nan"),
        }
    counts = Counter(tags)
    breadth_D = counts.get("DESIRABILITY", 0)
    breadth_F = counts.get("FEASIBILITY", 0)
    breadth_V = counts.get("VIABILITY", 0)
    breadth_O = counts.get("OTHER", 0)
    shares = [c / n for c in (breadth_D, breadth_F, breadth_V, breadth_O)]
    concentration = max(shares)
    balance_dfv = 1.0 - sum(s**2 for s in shares)
    return {
        "breadth_D": breadth_D, "breadth_F": breadth_F,
        "breadth_V": breadth_V, "breadth_O": breadth_O,
        "concentration": concentration, "balance_DFV": balance_dfv,
    }


def consensus_domain_count(cases: list[dict]) -> int:
    """Majority co-membership consensus partition; falls back to median domain count."""
    if not cases:
        return 0
    d_counts = [n_domains(c) for c in cases]
    all_p = sorted({p["id"] for c in cases for p in c.get("premises", [])})
    if len(all_p) < 2:
        return int(round(np.median(d_counts)))
    votes: Counter = Counter()
    total: Counter = Counter()
    for c in cases:
        lookup = {}
        for d in c.get("domains", []):
            for pid in d.get("premise_ids", []):
                lookup[pid] = d["id"]
        for a, b in combinations(all_p, 2):
            if a in lookup and b in lookup:
                total[(a, b)] += 1
                if lookup[a] == lookup[b]:
                    votes[(a, b)] += 1
    parent = {p: p for p in all_p}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for (a, b), v in votes.items():
        if total[(a, b)] and v / total[(a, b)] > 0.5:
            union(a, b)
    groups: dict = {}
    for p in all_p:
        groups.setdefault(find(p), 0)
    n = len(groups)
    if n == 0 or n > max(d_counts) + 2:
        n = int(round(np.median(d_counts)))
    return n


def aggregate_case_runs(
    run_cases: list[dict],
    case_id: str,
    meta: dict | None = None,
    transcript: str | None = None,
    dfv_cases: list[dict] | None = None,
    strategic_cases: list[dict] | None = None,
) -> dict:
    meta = meta or {}
    breadths = [breadth(c) for c in run_cases]
    truncated_flags = []
    confidences = []
    coded_truncation = False
    for c in run_cases:
        q = c.get("quality") or {}
        if "truncated" in q:
            coded_truncation = True
        truncated_flags.append(bool(q.get("truncated")))
        try:
            confidences.append(float(q.get("coder_confidence")))
        except (TypeError, ValueError):
            pass

    derived = transcript_truncated(transcript)
    incomplete = transcript_incomplete(transcript)
    if coded_truncation:
        truncated = int(any(truncated_flags))
    elif derived is None:
        truncated = 0
    else:
        truncated = int(derived)

    row = {
        "case_id": case_id,
        "id": meta.get("id") or case_id.removeprefix("pilot-"),
        "name": meta.get("name") or "",
        "batch": meta.get("batch") or "",
        "breadth": float(np.median(breadths)),
        "breadth_explicit": float(np.median([breadth_explicit(c) for c in run_cases])),
        "breadth_run_sd": float(np.std(breadths)) if len(breadths) > 1 else 0.0,
        "truncated": truncated,
        "transcript_incomplete": 0 if incomplete is None else int(incomplete),
        "coder_confidence": float(np.nanmean(confidences)) if confidences else np.nan,
        "n_runs": len(run_cases),
    }

    has_domains = any(c.get("domains") for c in run_cases)
    if has_domains:
        row["n_domains"] = consensus_domain_count(run_cases)
        row["balance"] = float(np.nanmean([balance_of(c) for c in run_cases]))
        row["granularity"] = float(np.nanmean([granularity_of(c) for c in run_cases]))
    elif strategic_cases:
        # Pass C may itself have k>1: use the consensus partition across its runs.
        row["n_domains"] = consensus_domain_count(strategic_cases)
        row["balance"] = np.nan
        row["granularity"] = np.nan
        row["n_domain_runs"] = len(strategic_cases)
    else:
        row["n_domains"] = np.nan
        row["balance"] = np.nan
        row["granularity"] = np.nan

    if dfv_cases:
        # Pass B may have k>1: average each composition measure across its runs.
        comps = [composition_measures(c.get("assignments") or []) for c in dfv_cases]
        for key in comps[0]:
            row[key] = float(np.nanmean([c[key] for c in comps]))
        row["n_dfv_runs"] = len(dfv_cases)

    return row


def aggregate_batch(batch_id: str, corpus: Path) -> pd.DataFrame:
    """Aggregate one batch folder: corpus/batches/<batch_id>/{cases.csv,runs/run*/}."""
    batch_dir = corpus / "batches" / batch_id
    transcripts = corpus / "transcripts"
    cases_csv = batch_dir / "cases.csv"
    if not cases_csv.exists():
        raise FileNotFoundError(f"missing {cases_csv}")
    with cases_csv.open(encoding="utf-8") as fh:
        meta_rows = {r["case_id"]: r for r in csv.DictReader(fh)}
    rows = []
    for cid, m in meta_rows.items():
        run_cases = []
        for r in (1, 2, 3):
            p = batch_dir / "runs" / f"run{r}" / f"{cid}.json"
            if p.exists():
                run_cases.append(load_case(p))
        if not run_cases:
            continue
        row = aggregate_case_runs(run_cases, cid, m, load_transcript(transcripts, cid))
        row["batch"] = batch_id
        rows.append(row)
    return pd.DataFrame(rows)


def aggregate_batches(batch_ids: list[str], corpus: Path) -> pd.DataFrame:
    frames = [aggregate_batch(b, corpus) for b in batch_ids]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def aggregate_run_dir(
    run_dir: Path,
    k_runs: int = 3,
    transcripts: Path | None = None,
) -> pd.DataFrame:
    """Aggregate an experiments/<run>/encodings/ tree.

    Handles both single-pass (encodings/run{1,2,3}/) and two-pass
    (encodings/premises/run{1,2,3}/ + encodings/domains/run1/) layouts.

    Each pass is read up to its own ``k_runs`` from the frozen config, so a pass
    declared with more runs than ``encoding.k_runs`` is not silently truncated.
    ``k_runs`` is the fallback for runs with no config snapshot.
    """
    enc = run_dir / "encodings"
    if not enc.exists():
        raise FileNotFoundError(f"missing {enc}")

    declared_k: dict[str, int] = {}
    snapshot = run_dir / "config.snapshot.yaml"
    if snapshot.exists():
        from .config import ExperimentConfig
        declared_k = {p.name: p.k_runs for p in ExperimentConfig.load(snapshot).resolved_passes()}

    def k_for(pass_name: str) -> int:
        return declared_k.get(pass_name, k_runs)

    pass_dirs = [d for d in enc.iterdir() if d.is_dir() and not d.name.startswith("run")]
    if not pass_dirs:
        pass_dirs = None

    case_ids: set[str] = set()
    if pass_dirs:
        for pdir in pass_dirs:
            for r in range(1, k_for(pdir.name) + 1):
                rd = pdir / f"run{r}"
                if rd.exists():
                    case_ids.update(p.stem for p in rd.glob("*.json"))
    else:
        for r in range(1, k_runs + 1):
            d = enc / f"run{r}"
            if d.exists():
                case_ids.update(p.stem for p in d.glob("*.json"))

    rows = []
    for cid in sorted(case_ids):
        run_cases = []
        dfv_cases = []
        strategic_cases = []

        if pass_dirs:
            premises_dir = next((d for d in pass_dirs if d.name == "premises"), None)
            dfv_dir = next((d for d in pass_dirs if d.name == "dfv"), None)
            strategic_dir = next((d for d in pass_dirs if d.name == "domains"), None)

            if premises_dir:
                for r in range(1, k_for("premises") + 1):
                    p = premises_dir / f"run{r}" / f"{cid}.json"
                    if p.exists():
                        run_cases.append(load_case(p))
            if dfv_dir:
                for r in range(1, k_for("dfv") + 1):
                    p = dfv_dir / f"run{r}" / f"{cid}.json"
                    if p.exists():
                        dfv_cases.append(load_case(p))
            if strategic_dir:
                for r in range(1, k_for("domains") + 1):
                    p = strategic_dir / f"run{r}" / f"{cid}.json"
                    if p.exists():
                        strategic_cases.append(load_case(p))
        else:
            for r in range(1, k_runs + 1):
                p = enc / f"run{r}" / f"{cid}.json"
                if p.exists():
                    run_cases.append(load_case(p))

        if run_cases:
            rows.append(
                aggregate_case_runs(
                    run_cases, cid, None,
                    load_transcript(transcripts, cid),
                    dfv_cases=dfv_cases if dfv_cases else None,
                    strategic_cases=strategic_cases if strategic_cases else None,
                )
            )
    return pd.DataFrame(rows)
