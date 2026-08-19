"""Integrity audit of the written survival DV outputs.

Reads the CSVs from disk (not the in-memory pipeline) and checks the invariants we
care about, so a failed assumption shows up as a printed FAIL rather than silently
surviving into the regression.
"""

from __future__ import annotations

import pandas as pd

from .config import ANALYSIS_END_DATE, CB_DUMP_DATE, PATHS


DATE_COLS = ["origin_date", "exit_date", "censor_date", "last_alive_date", "first_dead_date"]


def _load():
    dv = pd.read_csv(PATHS["survival_dv"])
    panel = pd.read_csv(PATHS["survival_panel"])
    for c in DATE_COLS:
        if c in dv.columns:
            dv[c] = pd.to_datetime(dv[c], errors="coerce")
    for c in ["year_start", "year_end"]:
        if c in panel.columns:
            panel[c] = pd.to_datetime(panel[c], errors="coerce")
    return dv, panel


def _check(label: str, ok: bool, detail: str = "") -> bool:
    """Print a check result. `detail` explains a failure, so it is shown only on failure."""
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{('' if ok or not detail else ' -> ' + detail)}")
    return ok


def audit() -> bool:
    dv, panel = _load()
    passed = True

    print(f"Vintages: survival ends {ANALYSIS_END_DATE}, funding ends {CB_DUMP_DATE}")
    print(f"survival_dv.csv: {len(dv)} rows | survival_panel.csv: {len(panel)} rows")

    print("\nExit dates")
    for t in ["failure", "acquired", "ipo", "censored"]:
        s = dv[dv["exit_type"] == t]
        print(f"  {t:9s} n={len(s):4d}  dated={s['exit_date'].notna().sum():4d}  undated={s['exit_date'].isna().sum():4d}")

    print("\nDate integrity")
    passed &= _check(
        "no exit_date before its pitch",
        (dv["exit_date"] < dv["origin_date"]).sum() == 0,
        f"{(dv['exit_date'] < dv['origin_date']).sum()} violations",
    )
    passed &= _check("no negative lower bound", (dv["time_lower_years"] < 0).sum() == 0)
    passed &= _check(
        "upper bound never below lower bound",
        (dv["time_upper_years"] < dv["time_lower_years"]).sum() == 0,
    )
    passed &= _check("every firm has a pitch date", dv["origin_date"].notna().all(),
                     f"{dv['origin_date'].isna().sum()} missing")
    passed &= _check("date_conflict flag is clear", int(dv["date_conflict"].sum()) == 0,
                     f"{int(dv['date_conflict'].sum())} flagged")
    passed &= _check(
        "censoring never runs past the survival vintage",
        (dv["censor_date"] > pd.Timestamp(ANALYSIS_END_DATE)).sum() == 0,
    )

    print("\nFailure bounds")
    fail = dv[dv["exit_type"] == "failure"]
    passed &= _check("every failure has both bounds",
                     fail["time_lower_years"].notna().all() and fail["time_upper_years"].notna().all())
    exact = int((fail["time_upper_years"] - fail["time_lower_years"] <= 0.01).sum())
    print(f"  interval-censored: {int(dv['interval_censored'].sum())} | exact: {exact} | undated exits: {int(dv['undated_exit'].sum())}")

    print("\nPanel vs DV")
    passed &= _check("panel carries firm_id for clustering", "firm_id" in panel.columns)
    passed &= _check("panel carries case_id for the cases join", "case_id" in panel.columns)

    dv_keys = set(map(tuple, dv[["name", "event"]].dropna().values))
    pan_keys = set(map(tuple, panel[["name", "event"]].dropna().values))
    passed &= _check("every DV firm-event appears in the panel", not (dv_keys - pan_keys),
                     f"{len(dv_keys - pan_keys)} missing")
    passed &= _check("panel introduces no firm-event absent from the DV", not (pan_keys - dv_keys),
                     f"{len(pan_keys - dv_keys)} extra")

    agg = panel.groupby(["name", "event"])["failed"].max().rename("panel_failed").reset_index()
    merged = dv[["name", "event", "failed"]].merge(agg, on=["name", "event"], how="left")
    mismatch = int((merged["failed"] != merged["panel_failed"]).sum())
    passed &= _check("failure indicator agrees between DV and panel", mismatch == 0,
                     f"{mismatch} mismatches")
    passed &= _check("no firm-event fails more than once in the panel",
                     int(panel.groupby(["name", "event"])["failed"].sum().max()) <= 1)
    passed &= _check("panel failure total equals DV failure total",
                     int(panel["failed"].sum()) == int((dv["exit_type"] == "failure").sum()),
                     f"panel={int(panel['failed'].sum())} dv={int((dv['exit_type'] == 'failure').sum())}")

    print("\nFunding")
    matched = dv[dv["cb_matched"] == 1]
    passed &= _check("matched firms all have a funding duration",
                     matched["time_to_first_post_event_round"].notna().all())
    passed &= _check("funding durations are non-negative",
                     (dv["time_to_first_post_event_round"] < 0).sum() == 0)
    passed &= _check("unmatched firms carry no funding duration",
                     dv[dv["cb_matched"] == 0]["time_to_first_post_event_round"].isna().all())

    # The pre/post split is keyed on firm-event, so a firm that pitched twice must not
    # inherit the other pitch's round.
    first_round = pd.to_datetime(dv["first_post_event_round_on"], errors="coerce")
    passed &= _check(
        "no post-pitch round predates its own pitch",
        (first_round < dv["origin_date"]).sum() == 0,
        f"{int((first_round < dv['origin_date']).sum())} violations",
    )
    repeat = dv[dv.duplicated("firm_id", keep=False)]
    if len(repeat):
        shared = repeat.groupby("firm_id")["first_post_event_round_on"].nunique(dropna=False)
        passed &= _check(
            "repeat-pitch firms are keyed per event, not per name",
            bool((shared > 1).any()) or repeat["first_post_event_round_on"].isna().all(),
            "all pitches share one round date, so the split is keyed on name",
        )
    passed &= _check(
        "an observed round always has a round date",
        dv.loc[dv["post_event_round_observed"] == 1, "first_post_event_round_on"].notna().all(),
    )
    obs = int((dv["post_event_round_observed"] == 1).sum())
    amt = int(dv["first_post_event_round_usd"].notna().sum())
    print(f"  next round observed: {obs} | amount disclosed: {amt} ({amt / max(obs, 1):.0%} of those)")
    print(f"  first round in the pitch month (may predate the pitch): {int(dv['first_round_same_month_as_pitch'].sum())}")

    print("\nKeys")
    passed &= _check("no duplicate name/event rows", not dv[["name", "event"]].duplicated().any(),
                     f"{int(dv[['name', 'event']].duplicated().sum())} duplicates")
    print(f"  rows: {len(dv)} | unique firm_id: {dv['firm_id'].nunique()} | matched to cases.csv: {int((dv['case_match_status'] == 'matched').sum())}")

    print("\nAUDIT " + ("PASSED" if passed else "FAILED"))
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if audit() else 1)
