"""Full annual Wayback scan and integration with the CB-derived exit table."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from .config import PATHS
from .derive import build_panel, derive_duration
from .event_dates import lookup
from .io import load_attractiveness_companies
from .join_cases import join_to_cases, write_outputs
from .wayback import classify_snapshots


def run_wayback_scan(exits_df: pd.DataFrame, resume_path: Optional[Path] = None) -> pd.DataFrame:
    """Run the annual Wayback scan for firms whose dates are not already set by CB.

    Updates exit_date, exit_date_precision, last_alive_date, first_dead_date,
    death_interval_days, death_source, and n_inspect for scanned firms.
    """
    df = exits_df.copy()
    df["origin_date"] = pd.to_datetime(df["origin_date"], errors="coerce")
    df["censor_date"] = pd.to_datetime(df["censor_date"], errors="coerce")

    # Scan only firms needing a date (undated failures + undated acquisitions + year-stamped CB dates)
    need_scan = (
        ((df["exit_type"] == "failure") & df["exit_date"].isna()) |
        ((df["exit_type"] == "acquired") & df["exit_date"].isna()) |
        (df["exit_date_precision"] == "year")
    )
    scan_df = df[need_scan].copy()
    print(f"Wayback scan: {len(scan_df)} firms need timing")

    if resume_path and resume_path.exists():
        scanned = pd.read_csv(resume_path)
        scanned = dict(zip(scanned["name"], scanned.to_dict("records")))
    else:
        scanned = {}

    diag = PATHS["diagnostics"] / "wayback_scan_results.csv"
    diag.parent.mkdir(parents=True, exist_ok=True)

    # Load any existing partial results so the scan can resume
    if resume_path and resume_path.exists():
        existing = pd.read_csv(resume_path)
    elif diag.exists():
        existing = pd.read_csv(diag)
    else:
        existing = pd.DataFrame(columns=["name", "last_alive_year", "first_dead_year", "n_inspect", "error"])
    scanned = dict(zip(existing["name"], existing.to_dict("records")))

    results = existing.to_dict("records")
    for i, (_, row) in enumerate(scan_df.iterrows(), 1):
        name = row["name"]
        if name in scanned:
            continue

        domain = row["website"]
        if not isinstance(domain, str) or not domain.startswith("http"):
            domain = f"http://{domain}"

        origin = row["origin_date"]
        censor = row["censor_date"]
        if pd.isna(origin) or pd.isna(censor):
            rec = {
                "name": name, "last_alive_year": None, "first_dead_year": None,
                "n_inspect": 0, "error": "missing_origin_or_censor"
            }
        else:
            try:
                origin_date = origin.date()
                censor_date = censor.date()
                result = classify_snapshots(domain, origin_date, censor_date, timeout=120)
                rec = {
                    "name": name,
                    "last_alive_year": result["last_alive_year"],
                    "first_dead_year": result["first_dead_year"],
                    "n_inspect": result["n_inspect"],
                    "error": None,
                }
            except Exception as e:
                rec = {
                    "name": name, "last_alive_year": None, "first_dead_year": None,
                    "n_inspect": 0, "error": str(e)
                }

        results.append(rec)
        scanned[name] = rec

        # Write after every firm so a crash is recoverable
        pd.DataFrame(results).to_csv(diag, index=False)

        if i % 10 == 0:
            print(f"  scanned {i}/{len(scan_df)}: {name}")

    scan_results = pd.DataFrame(results)
    print(f"Wrote Wayback scan results to {diag}")

    # Rename scan columns before merging so the source is unambiguous
    scan_results = scan_results.rename(columns={
        "last_alive_year": "last_alive_year_wb",
        "first_dead_year": "first_dead_year_wb",
        "n_inspect": "n_inspect_wb",
        "error": "error_wb",
    })

    # Merge results back
    df = df.merge(scan_results, on="name", how="left")

    # A dead reading followed by a later alive reading is a false positive, so the
    # death year is not usable. Older result files were written before
    # classify_snapshots enforced this, so drop the bad death years here too and
    # leave the firm undated rather than dating it too early.
    revived = (
        df["last_alive_year_wb"].notna()
        & df["first_dead_year_wb"].notna()
        & (pd.to_numeric(df["last_alive_year_wb"], errors="coerce")
           > pd.to_numeric(df["first_dead_year_wb"], errors="coerce"))
    )
    if revived.any():
        print(f"  dropped {int(revived.sum())} death years contradicted by a later live snapshot")
        df.loc[revived, "first_dead_year_wb"] = pd.NA

    def _year_to_date(series: pd.Series, month_day: str) -> pd.Series:
        """Convert a float/Series of years to datetime for non-null values."""
        years = pd.to_numeric(series, errors="coerce")
        dates = pd.to_datetime(years.dropna().astype("Int64").astype(str) + month_day)
        return dates.reindex(series.index)

    # Update failures with Wayback dates. Use the end of the death year so the
    # panel year_index is never negative (i.e. death is not before the pitch).
    wb_failure = (df["exit_type"] == "failure") & df["first_dead_year_wb"].notna()
    df.loc[wb_failure, "exit_date"] = _year_to_date(df.loc[wb_failure, "first_dead_year_wb"], "-12-31")
    df.loc[wb_failure, "exit_date_precision"] = "year"
    df.loc[wb_failure, "last_alive_date"] = _year_to_date(df.loc[wb_failure, "last_alive_year_wb"], "-12-31")
    df.loc[wb_failure, "first_dead_date"] = _year_to_date(df.loc[wb_failure, "first_dead_year_wb"], "-12-31")
    df.loc[wb_failure, "death_interval_days"] = (df.loc[wb_failure, "first_dead_date"] - df.loc[wb_failure, "last_alive_date"]).dt.days
    df.loc[wb_failure, "death_source"] = "wayback"
    df.loc[wb_failure, "n_inspect"] = df.loc[wb_failure, "n_inspect_wb"]

    # Update acquisitions with Wayback redirect dates (best-effort year). Use the
    # same end-of-year convention as failures, and never overwrite a Crunchbase
    # date, which is stronger evidence than the year a site went dark.
    wb_acq = (
        (df["exit_type"] == "acquired")
        & df["first_dead_year_wb"].notna()
        & df["exit_date"].isna()
    )
    df.loc[wb_acq, "exit_date"] = _year_to_date(df.loc[wb_acq, "first_dead_year_wb"], "-12-31")
    df.loc[wb_acq, "exit_date_precision"] = "year"
    df.loc[wb_acq, "acq_date_source"] = "wayback_redirect"

    return df
