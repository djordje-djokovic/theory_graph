"""Aggregate k-run encodings into case-level IVs (breadth, n_domains, ...).

Logic ported from scripts/run_gotselected_analysis.py — kept path-independent.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


def load_case(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def breadth(case: dict) -> int:
    return len(case.get("premises") or [])


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


def aggregate_case_runs(run_cases: list[dict], case_id: str, meta: dict | None = None) -> dict:
    meta = meta or {}
    breadths = [breadth(c) for c in run_cases]
    truncated_flags = []
    confidences = []
    for c in run_cases:
        q = c.get("quality") or {}
        truncated_flags.append(bool(q.get("truncated")))
        try:
            confidences.append(float(q.get("coder_confidence")))
        except (TypeError, ValueError):
            pass
    return {
        "case_id": case_id,
        "id": meta.get("id") or case_id.removeprefix("pilot-"),
        "name": meta.get("name") or "",
        "batch": meta.get("batch") or "",
        "breadth": float(np.median(breadths)),
        "breadth_run_sd": float(np.std(breadths)) if len(breadths) > 1 else 0.0,
        "n_domains": consensus_domain_count(run_cases),
        "balance": float(np.nanmean([balance_of(c) for c in run_cases])),
        "granularity": float(np.nanmean([granularity_of(c) for c in run_cases])),
        "truncated": int(any(truncated_flags)),
        "coder_confidence": float(np.nanmean(confidences)) if confidences else np.nan,
        "n_runs": len(run_cases),
    }


def aggregate_batch(batch_id: str, corpus: Path) -> pd.DataFrame:
    """Aggregate one batch folder: corpus/batches/<batch_id>/{cases.csv,runs/run*/}."""
    batch_dir = corpus / "batches" / batch_id
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
        row = aggregate_case_runs(run_cases, cid, m)
        row["batch"] = batch_id
        rows.append(row)
    return pd.DataFrame(rows)


def aggregate_batches(batch_ids: list[str], corpus: Path) -> pd.DataFrame:
    frames = [aggregate_batch(b, corpus) for b in batch_ids]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def aggregate_run_dir(run_dir: Path, k_runs: int = 3) -> pd.DataFrame:
    """Aggregate an experiments/<run>/encodings/ tree."""
    enc = run_dir / "encodings"
    if not enc.exists():
        raise FileNotFoundError(f"missing {enc}")
    case_ids: set[str] = set()
    for r in range(1, k_runs + 1):
        d = enc / f"run{r}"
        if d.exists():
            case_ids.update(p.stem for p in d.glob("*.json"))
    rows = []
    for cid in sorted(case_ids):
        run_cases = []
        for r in range(1, k_runs + 1):
            p = enc / f"run{r}" / f"{cid}.json"
            if p.exists():
                run_cases.append(load_case(p))
        if run_cases:
            rows.append(aggregate_case_runs(run_cases, cid))
    return pd.DataFrame(rows)
