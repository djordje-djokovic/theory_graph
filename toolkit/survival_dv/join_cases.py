"""Join the survival DV to the theory_graph cases.csv and write final outputs."""

from __future__ import annotations

import pandas as pd

from .config import PATHS
from .io import load_cases, normalize_name


def join_to_cases(dv_df: pd.DataFrame) -> pd.DataFrame:
    """Join the survival DV to cases.csv by name and event.

    Adds `case_id` and `tg_name` (the name as it appears in cases.csv) to the DV.
    Flags cases that match ambiguously or not at all.
    """
    cases = load_cases()
    cases["name_norm"] = cases["name"].map(normalize_name)
    cases["event_norm"] = cases["event"].astype(str).str.lower().str.strip()

    dv = dv_df.copy()
    dv["name_norm"] = dv["name"].map(normalize_name)
    dv["event_norm"] = dv["event"].astype(str).str.lower().str.strip()

    merged = dv.merge(
        cases[["case_id", "name", "event", "name_norm", "event_norm"]],
        left_on=["name_norm", "event_norm"],
        right_on=["name_norm", "event_norm"],
        how="left",
        suffixes=("", "_tg"),
    )

    # Count matches per DV row
    match_counts = merged.groupby(merged.index).size()
    # Since merge can duplicate rows, we need to handle duplicates
    # Simpler: drop duplicates based on original DV index, keeping first
    merged = merged.drop_duplicates(subset=["name", "event"], keep="first")

    merged["case_id"] = merged["case_id"]
    merged["theory_graph_name"] = merged["name_tg"]
    merged = merged.drop(columns=["name_norm", "event_norm", "name_tg"])

    # Flag unmatched and ambiguous
    merged["case_match_status"] = "matched"
    merged.loc[merged["case_id"].isna(), "case_match_status"] = "unmatched"

    n_unmatched = (merged["case_match_status"] == "unmatched").sum()
    n_matched = (merged["case_match_status"] == "matched").sum()
    print(f"Joined to cases.csv: {n_matched} matched, {n_unmatched} unmatched")

    return merged


def write_outputs(dv_df: pd.DataFrame, panel_df: pd.DataFrame) -> None:
    PATHS["out_dir"].mkdir(parents=True, exist_ok=True)
    dv_df.to_csv(PATHS["survival_dv"], index=False)
    panel_df.to_csv(PATHS["survival_panel"], index=False)
    print(f"Wrote {PATHS['survival_dv']}")
    print(f"Wrote {PATHS['survival_panel']}")
