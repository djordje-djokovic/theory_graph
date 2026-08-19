"""Derive duration variables and the person-year panel from the exit table."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import pandas as pd

from .config import ANALYSIS_END_DATE
from .io import normalize_name


# Survival observation ends at the TechCrunch scrape date, the vintage of the
# status that governs exit type. Recorded in diagnostics/techcrunch_scrape_date.txt.
DEFAULT_ANALYSIS_END = pd.Timestamp(ANALYSIS_END_DATE)


def derive_duration(exits_df: pd.DataFrame, analysis_end: Optional[pd.Timestamp] = None) -> pd.DataFrame:
    """Add duration columns to the exit table.

    For CB-only runs, undated failures/acquisitions remain censored at analysis_end
    with death_interval_days = NaN. The Wayback stage will fill them later.
    """
    if analysis_end is None:
        analysis_end = DEFAULT_ANALYSIS_END

    df = exits_df.copy()
    df["origin_date"] = pd.to_datetime(df["origin_date"], errors="coerce")
    df["exit_date"] = pd.to_datetime(df["exit_date"], errors="coerce")
    for col in ["cb_last_funding_on", "cb_closed_on", "cb_founded_on"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = pd.NaT

    # Firms that pitched at more than one Battlefield event stay as separate rows
    # (the pitch is the unit of observation), so firm_id is the clustering key.
    df["firm_id"] = df["name"].map(normalize_name)

    df["age_at_pitch_years"] = (df["origin_date"] - df["cb_founded_on"]).dt.days / 365.25

    df["censor_date"] = analysis_end

    # Flag exit dates that fall before the pitch; clamp them so the panel is defined.
    df["date_conflict"] = df["exit_date"].notna() & (df["exit_date"] < df["origin_date"])
    df.loc[df["date_conflict"], "manual_review"] = 1
    df.loc[df["date_conflict"], "exit_date"] = df.loc[df["date_conflict"], "origin_date"] + pd.Timedelta(days=1)

    # For now, censor_date is the earliest of analysis_end and (if dated) exit_date.
    # For undated events, censor_date stays analysis_end.
    dated = df["exit_date"].notna()
    df.loc[dated, "censor_date"] = df.loc[dated, "exit_date"].clip(upper=analysis_end)

    # Also ensure censor_date is not before origin_date (can happen if analysis_end is stale)
    df["censor_date"] = df[["censor_date", "origin_date"]].max(axis=1)

    df["failed"] = (df["exit_type"] == "failure").astype(int)
    df["time_years"] = (df["censor_date"] - df["origin_date"]).dt.days / 365.25
    df["time_years_founding"] = (df["censor_date"] - df["cb_founded_on"]).dt.days / 365.25

    # Interval bounds for Wayback-dated events (CB-only stage leaves these NaT).
    # These must be preserved, not reset, because derive_duration runs again after
    # the Wayback scan has already populated them.
    for col in ["last_alive_date", "first_dead_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = pd.NaT
    if "death_interval_days" not in df.columns:
        df["death_interval_days"] = pd.NA

    # For CB-dated failures with day precision, last_alive = exit_date - 1 day,
    # first_dead = exit_date. For year precision, bracket to the year.
    cb_failure = (df["exit_type"] == "failure") & (df["death_source"] == "crunchbase")
    day_prec = cb_failure & (df["exit_date_precision"] == "day")
    year_prec = cb_failure & (df["exit_date_precision"] == "year")
    df.loc[day_prec, "first_dead_date"] = df.loc[day_prec, "exit_date"]
    df.loc[day_prec, "last_alive_date"] = df.loc[day_prec, "exit_date"] - pd.Timedelta(days=1)
    df.loc[year_prec, "first_dead_date"] = df.loc[year_prec, "exit_date"] + pd.DateOffset(years=1) - pd.Timedelta(days=1)
    df.loc[year_prec, "last_alive_date"] = df.loc[year_prec, "exit_date"] - pd.Timedelta(days=1)

    has_interval = df["first_dead_date"].notna() & df["last_alive_date"].notna()
    df.loc[has_interval, "death_interval_days"] = (df.loc[has_interval, "first_dead_date"] - df.loc[has_interval, "last_alive_date"]).dt.days

    # Ensure time_years is non-negative and finite
    df["time_years"] = df["time_years"].clip(lower=0)
    df.loc[df["time_years_founding"].isna() | (df["time_years_founding"] < 0), "time_years_founding"] = pd.NA

    df = _add_interval_bounds(df, analysis_end)

    return df


def _add_interval_bounds(df: pd.DataFrame, analysis_end: pd.Timestamp) -> pd.DataFrame:
    """Add explicit lower/upper bounds on the failure time for interval-censored models.

    Every firm gets a bound pair in years since the pitch:
      - dated failure: [last_alive, first_dead], narrow for CB day precision
      - undated failure: [max(pitch, last_funding_on), analysis_end], the widest honest bound
      - acquired / ipo / open: right-censored, so the upper bound is NA

    Deleting the undated failures or recoding them as censored would both bias the
    hazard downward, so they are bounded instead.
    """
    origin = df["origin_date"]

    def _year_end(series: pd.Series) -> pd.Series:
        years = pd.to_numeric(series, errors="coerce")
        out = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
        ok = years.notna()
        out[ok] = pd.to_datetime(years[ok].astype(int).astype(str) + "-12-31")
        return out

    lower = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    upper = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")

    is_failure = df["exit_type"] == "failure"

    # Wayback-dated failures. last_alive_year is often unknown because no snapshot
    # in the window was confidently classified as alive; in that case the site is
    # only known to be dead *by* first_dead_year, so the lower bound is the pitch.
    if "first_dead_year_wb" in df.columns:
        wb = is_failure & df["first_dead_year_wb"].notna()
        lower[wb] = _year_end(df["last_alive_year_wb"])[wb]
        upper[wb] = _year_end(df["first_dead_year_wb"])[wb]

    # Crunchbase-dated failures carry explicit bounds from derive_duration
    cb = is_failure & df["death_source"].eq("crunchbase") & df["first_dead_date"].notna()
    lower[cb] = df.loc[cb, "last_alive_date"]
    upper[cb] = df.loc[cb, "first_dead_date"]

    # Undated failures: alive at least until the last observed signal, dead by the
    # end of observation. This is the widest honest bound. A confirmed-live Wayback
    # snapshot is the strongest of the available lower bounds.
    undated_failure = is_failure & df["exit_date"].isna()
    signals = ["origin_date", "cb_last_funding_on"]
    if "last_alive_year_wb" in df.columns:
        df["_wb_last_alive"] = _year_end(df["last_alive_year_wb"])
        signals.append("_wb_last_alive")
    last_signal = df[signals].max(axis=1)
    lower[undated_failure] = last_signal[undated_failure]
    upper[undated_failure] = analysis_end
    df = df.drop(columns=["_wb_last_alive"], errors="ignore")

    # Any remaining dated failure without bounds falls back to its point estimate
    residual = is_failure & upper.isna() & df["exit_date"].notna()
    lower[residual] = df.loc[residual, "exit_date"]
    upper[residual] = df.loc[residual, "exit_date"]

    # An unknown lower bound means the firm is only known to have died by the
    # upper bound, so the pitch is the earliest it could have happened.
    lower[is_failure & lower.isna()] = origin[is_failure & lower.isna()]

    # Right-censored observations (open, acquired, ipo) have no upper bound
    right_censored = ~is_failure
    lower[right_censored] = df.loc[right_censored, "censor_date"]

    # Bounds cannot precede the pitch, and the upper cannot precede the lower
    lower = lower.where(lower.isna() | (lower >= origin), origin)
    upper = upper.where(upper.isna() | (upper >= lower), lower)

    df["time_lower_years"] = (lower - origin).dt.days / 365.25
    df["time_upper_years"] = (upper - origin).dt.days / 365.25
    df["undated_exit"] = (df["exit_date"].isna() & df["exit_type"].isin(["failure", "acquired"])).astype(int)
    df["interval_censored"] = (
        is_failure & (df["time_upper_years"] - df["time_lower_years"] > 1 / 365.25)
    ).astype(int)

    # Restate the interval width from the final bounds so it covers every failure,
    # not just the Crunchbase-dated ones.
    df.loc[is_failure, "death_interval_days"] = (upper - lower).dt.days[is_failure]

    # Midpoint point-estimate for the Cox robustness specification
    df["exit_date_midpoint"] = pd.NaT
    df.loc[is_failure, "exit_date_midpoint"] = lower[is_failure] + (upper[is_failure] - lower[is_failure]) / 2
    df["time_years_midpoint"] = (df["exit_date_midpoint"] - origin).dt.days / 365.25

    return df


def build_panel(exits_df: pd.DataFrame, analysis_end: Optional[pd.Timestamp] = None) -> pd.DataFrame:
    """Build the person-year panel from the exit table."""
    if analysis_end is None:
        analysis_end = DEFAULT_ANALYSIS_END

    df = exits_df.copy()
    df["origin_date"] = pd.to_datetime(df["origin_date"], errors="coerce")
    df["exit_date"] = pd.to_datetime(df["exit_date"], errors="coerce")

    rows = []
    for _, row in df.iterrows():
        origin = row["origin_date"]
        if pd.isna(origin):
            continue

        exit_type = row["exit_type"]
        exit_date = row["exit_date"] if pd.notna(row["exit_date"]) else analysis_end
        exit_date = min(exit_date, analysis_end)

        # Event time in years (continuous, for reference), then floor to year index
        event_years = (exit_date - origin).days / 365.25
        max_year = int(event_years)

        for year_index in range(max_year + 1):
            year_start = origin + pd.DateOffset(years=year_index)
            year_end = origin + pd.DateOffset(years=year_index + 1)
            if year_start > analysis_end:
                break

            at_risk = 1
            failed = 0
            censored = 0

            if exit_type == "failure":
                if exit_date <= year_end:
                    failed = 1
                    at_risk = 1
                if exit_date < year_start:
                    # Should not happen because we stop at max_year
                    at_risk = 0
            elif exit_type in ("acquired", "ipo", "censored"):
                if exit_date <= year_end and exit_date > year_start:
                    censored = 1
                if exit_date < year_start:
                    at_risk = 0

            if at_risk == 0:
                continue

            rows.append({
                "case_id": row.get("case_id"),
                "name": row["name"],
                "firm_id": row.get("firm_id"),
                "event": row["event"],
                "year_index": year_index,
                "year_start": year_start,
                "year_end": year_end,
                "at_risk": at_risk,
                "failed": failed,
                "censored": censored,
                "exit_type": exit_type,
                "undated_exit": row.get("undated_exit", 0),
                "interval_censored": row.get("interval_censored", 0),
            })

    panel = pd.DataFrame(rows)
    return panel
