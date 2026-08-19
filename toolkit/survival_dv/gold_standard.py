"""Prepare a gold-standard sample of archived snapshots for human labeling."""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

from .config import PATHS
from .crunchbase import extract_domain
from .io import load_attractiveness_companies
from .wayback import cdx_yearly_snapshots


SAMPLE_SIZE = 100


def select_firms(exit_table_path: Path) -> pd.DataFrame:
    """Select firms whose timing is uncertain and would benefit from human labeling."""
    df = pd.read_csv(exit_table_path)

    # Priority 1: CB-dated failures with year-stamp precision (need narrowing)
    year_stamp = (df["exit_type"] == "failure") & (df["exit_date_precision"] == "year")
    # Priority 2: undated failures (no CB date, will rely on Wayback)
    undated_failure = (df["exit_type"] == "failure") & df["exit_date"].isna()
    # Priority 3: undated acquisitions (redirect or no signal)
    undated_acq = (df["exit_type"] == "acquired") & df["exit_date"].isna()

    selected = pd.concat([
        df[year_stamp].assign(sample_reason="year_stamp_cb"),
        df[undated_failure].assign(sample_reason="undated_failure"),
        df[undated_acq].assign(sample_reason="undated_acquired"),
    ]).drop_duplicates("name")

    # Cap sample size
    if len(selected) > SAMPLE_SIZE:
        selected = selected.sample(n=SAMPLE_SIZE, random_state=42)
    return selected


def build_sample():
    exit_table = PATHS["diagnostics"] / "cb_exit_table.csv"
    if not exit_table.exists():
        print(f"Exit table not found: {exit_table}")
        return

    selected = select_firms(exit_table)
    print(f"Selected {len(selected)} firms for gold-standard sampling")

    companies = load_attractiveness_companies()
    companies["domain"] = companies["website"].map(extract_domain)

    rows = []
    for _, row in selected.iterrows():
        name = row["name"]
        reason = row["sample_reason"]
        company = companies[companies["name"] == name]
        if company.empty:
            continue
        domain = company.iloc[0]["domain"]
        if not domain:
            continue

        # Pick a relevant year based on the sample reason
        if reason == "year_stamp_cb":
            # Snapshot from the year before the CB date to confirm alive, and the year of to confirm dead
            cb_year = pd.to_datetime(row["exit_date"]).year
            years = [cb_year - 1, cb_year]
        elif reason == "undated_failure":
            # Snapshot from a few years after origin
            origin_year = pd.to_datetime(row["origin_date"]).year if pd.notna(row["origin_date"]) else None
            if origin_year:
                years = [origin_year + 2, origin_year + 5]
            else:
                years = [2020, 2022]
        else:  # undated_acquired
            years = [2020, 2022]

        for year in years:
            snap = f"https://web.archive.org/web/{year}0101000000*/http://{domain}"
            rows.append({
                "name": name,
                "domain": domain,
                "event": row["event"],
                "sample_reason": reason,
                "year": year,
                "snapshot_url": snap,
                "predicted_exit_type": row["exit_type"],
                "human_label": None,  # to be filled by the human labeler
                "human_notes": None,
            })

    sample_df = pd.DataFrame(rows)
    out = PATHS["diagnostics"] / "gold_standard_sample.csv"
    sample_df.to_csv(out, index=False)
    print(f"Wrote gold-standard sample to {out}")
    print(sample_df["sample_reason"].value_counts().to_string())


if __name__ == "__main__":
    build_sample()
