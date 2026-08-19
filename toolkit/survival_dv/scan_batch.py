"""Run the Wayback scan in small, resumable batches."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import PATHS
from .crunchbase import build_exit_table
from .derive import build_panel, derive_duration
from .event_dates import lookup
from .funding import build_funding_dvs
from .io import load_attractiveness_companies
from .join_cases import join_to_cases, write_outputs
from .rescrape import apply_fresh_statuses
from .scan import run_wayback_scan


def run_batch(start_idx: int, batch_size: int, output_stage: str):
    companies = load_attractiveness_companies()
    companies = apply_fresh_statuses(companies)
    companies["origin_date"] = companies["event"].map(lookup)

    exits = build_exit_table(companies)
    exits = derive_duration(exits)

    # Identify firms needing scan, then limit to batch
    df = exits.copy()
    df["origin_date"] = pd.to_datetime(df["origin_date"], errors="coerce")
    df["censor_date"] = pd.to_datetime(df["censor_date"], errors="coerce")
    need_scan = (
        ((df["exit_type"] == "failure") & df["exit_date"].isna()) |
        ((df["exit_type"] == "acquired") & df["exit_date"].isna()) |
        (df["exit_date_precision"] == "year")
    )
    scan_names = df[need_scan]["name"].tolist()
    batch_names = scan_names[start_idx:start_idx + batch_size]

    print(f"Batch {start_idx}-{start_idx + batch_size - 1}: {len(batch_names)} firms")

    # Mark non-batch firms as already done so the scan skips them
    exits["_skip_wayback"] = True
    exits.loc[exits["name"].isin(batch_names), "_skip_wayback"] = False

    # Custom scan for just this batch
    from .wayback import classify_snapshots
    results = []
    for i, name in enumerate(batch_names, 1):
        row = exits[exits["name"] == name].iloc[0]
        domain = row["website"]
        if not isinstance(domain, str) or not domain.startswith("http"):
            domain = f"http://{domain}"
        origin = pd.to_datetime(row["origin_date"]).date()
        censor = pd.to_datetime(row["censor_date"]).date()
        print(f"  {i}/{len(batch_names)}: {name} ({domain})", flush=True)
        try:
            result = classify_snapshots(domain, origin, censor, timeout=120)
            print(f"    -> alive={result['last_alive_year']}, dead={result['first_dead_year']}, inspect={result['n_inspect']}", flush=True)
            results.append({
                "name": name,
                "last_alive_year": result["last_alive_year"],
                "first_dead_year": result["first_dead_year"],
                "n_inspect": result["n_inspect"],
                "error": None,
            })
        except Exception as e:
            print(f"    -> ERROR: {e}", flush=True)
            results.append({
                "name": name, "last_alive_year": None, "first_dead_year": None,
                "n_inspect": 0, "error": str(e)
            })
        # Save incremental results
        out_path = PATHS["diagnostics"] / f"wayback_scan_batch_{start_idx}.csv"
        pd.DataFrame(results).to_csv(out_path, index=False)

    # Merge batch results into exits and produce partial outputs if requested
    batch_results = pd.DataFrame(results)
    exits = exits.merge(batch_results, on="name", how="left", suffixes=("", "_batch"))

    # Apply batch results to the same columns as run_wayback_scan
    wb_failure = (exits["exit_type"] == "failure") & exits["first_dead_year_batch"].notna()
    exits.loc[wb_failure, "exit_date"] = pd.to_datetime(exits.loc[wb_failure, "first_dead_year_batch"].astype(int).astype(str) + "-06-30")
    exits.loc[wb_failure, "exit_date_precision"] = "year"
    exits.loc[wb_failure, "last_alive_date"] = pd.to_datetime(exits.loc[wb_failure, "last_alive_year_batch"].astype(int).astype(str) + "-12-31")
    exits.loc[wb_failure, "first_dead_date"] = pd.to_datetime(exits.loc[wb_failure, "first_dead_year_batch"].astype(int).astype(str) + "-06-30")
    exits.loc[wb_failure, "death_interval_days"] = (exits.loc[wb_failure, "first_dead_date"] - exits.loc[wb_failure, "last_alive_date"]).dt.days
    exits.loc[wb_failure, "death_source"] = "wayback"
    exits.loc[wb_failure, "n_inspect"] = exits.loc[wb_failure, "n_inspect_batch"]

    exits = exits.drop(columns=["_skip_wayback"], errors="ignore")
    exits = derive_duration(exits)
    exits = build_funding_dvs(exits)
    panel = build_panel(exits)
    joined = join_to_cases(exits)
    write_outputs(joined, panel)
    print(f"Batch complete. Outputs written for stage {output_stage}.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--stage", type=str, default="batch")
    args = parser.parse_args()
    run_batch(args.start, args.batch_size, args.stage)


if __name__ == "__main__":
    main()
