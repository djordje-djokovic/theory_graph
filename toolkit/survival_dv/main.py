"""Orchestration entry point for the survival DV pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import PATHS
from .crunchbase import build_exit_table
from .derive import build_panel, derive_duration
from .event_dates import lookup
from .funding import build_funding_dvs
from .io import load_attractiveness_companies, load_cases
from .join_cases import join_to_cases, write_outputs
from .rescrape import apply_fresh_statuses
from .scan import run_wayback_scan


def stage_event_dates():
    from .event_dates import to_table
    import csv

    rows = to_table()
    out = PATHS["event_dates"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["event", "origin_year", "origin_month", "origin_date", "source"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")


def stage_cb_only():
    companies = load_attractiveness_companies()
    companies["origin_date"] = companies["event"].map(lookup)
    companies["origin_year"] = pd.to_datetime(companies["origin_date"], errors="coerce").dt.year

    exits = build_exit_table(companies)

    out = PATHS["diagnostics"] / "cb_exit_table.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    exits.to_csv(out, index=False)
    print(f"Wrote CB-only exit table to {out}")
    print(f"  rows: {len(exits)}")
    print(f"  CB domain matched: {exits['cb_matched'].sum()}")
    print("  exit_type:", exits["exit_type"].value_counts(dropna=False).to_dict())
    print("  death_source:", exits["death_source"].value_counts(dropna=False).to_dict())
    print("  acq_date_source:", exits["acq_date_source"].value_counts(dropna=False).to_dict())
    return exits


def stage_cb_only_and_outputs():
    companies = load_attractiveness_companies()
    companies = apply_fresh_statuses(companies)
    companies["origin_date"] = companies["event"].map(lookup)
    companies["origin_year"] = pd.to_datetime(companies["origin_date"], errors="coerce").dt.year

    exits = build_exit_table(companies)
    exits = derive_duration(exits)
    exits = build_funding_dvs(exits)

    # Join before expanding so the panel carries case_id
    joined = join_to_cases(exits)
    panel = build_panel(joined)
    write_outputs(joined, panel)

    # Write diagnostics
    diag = PATHS["diagnostics"] / "cb_exit_table.csv"
    PATHS["diagnostics"].mkdir(parents=True, exist_ok=True)
    exits.to_csv(diag, index=False)
    print(f"Wrote diagnostics to {diag}")
    print(f"  rows: {len(exits)}")
    print(f"  CB domain matched: {exits['cb_matched'].sum()}")
    print("  exit_type:", exits["exit_type"].value_counts(dropna=False).to_dict())
    print("  death_source:", exits["death_source"].value_counts(dropna=False).to_dict())
    print("  acq_date_source:", exits["acq_date_source"].value_counts(dropna=False).to_dict())
    print("  panel rows:", len(panel))


def stage_full():
    companies = load_attractiveness_companies()
    companies = apply_fresh_statuses(companies)
    companies["origin_date"] = companies["event"].map(lookup)
    companies["origin_year"] = pd.to_datetime(companies["origin_date"], errors="coerce").dt.year

    exits = build_exit_table(companies)
    exits = derive_duration(exits)
    exits = run_wayback_scan(exits)
    exits = derive_duration(exits)  # re-derive after Wayback dates
    exits = build_funding_dvs(exits)

    # Join to cases.csv before expanding the panel so the panel inherits case_id
    # and can be merged with the breadth/modularity covariates.
    joined = join_to_cases(exits)
    panel = build_panel(joined)
    write_outputs(joined, panel)
    print("Full pipeline complete. Run the Wayback scan incrementally for large batches.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["event_dates", "cb_only", "cb_outputs", "full"])
    args = parser.parse_args()

    if args.stage == "event_dates":
        stage_event_dates()
    elif args.stage == "cb_only":
        stage_cb_only()
    elif args.stage == "cb_outputs":
        stage_cb_only_and_outputs()
    elif args.stage == "full":
        stage_full()


if __name__ == "__main__":
    main()
