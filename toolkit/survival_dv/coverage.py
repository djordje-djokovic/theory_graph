"""Report DV coverage for the theory_graph analysis sample.

cases.csv holds the 376-case breadth/modularity corpus. The survival pipeline runs on
all 1,300 Battlefield firms, so this reports coverage for the subset that will actually
enter the regression.
"""

from __future__ import annotations

import pandas as pd

from .config import PATHS


def report() -> None:
    dv = pd.read_csv(PATHS["survival_dv"])
    panel = pd.read_csv(PATHS["survival_panel"])
    dv["exit_date"] = pd.to_datetime(dv["exit_date"], errors="coerce")

    sample = dv[dv["case_match_status"] == "matched"].copy()
    panel_sample = panel[panel["case_id"].notna()]

    print(f"Analysis sample: {len(sample)} cases ({sample['firm_id'].nunique()} unique firms)")
    print(f"Full corpus:     {len(dv)} Battlefield firm-events\n")

    print("Exit type")
    for t, n in sample["exit_type"].value_counts().items():
        print(f"  {t:9s} {n:4d}  ({n / len(sample):5.1%})")

    print("\nDating")
    for t in ["failure", "acquired"]:
        s = sample[sample["exit_type"] == t]
        dated = int(s["exit_date"].notna().sum())
        print(f"  {t:9s} n={len(s):3d}  dated={dated:3d}  undated={len(s) - dated:3d}")
    print(f"  interval-censored failures: {int(sample['interval_censored'].sum())}")
    print(f"  undated exits:              {int(sample['undated_exit'].sum())}")

    print("\nPanel")
    print(f"  rows: {len(panel_sample)}")
    print(f"  failures: {int(panel_sample['failed'].sum())}")
    if len(sample):
        print(f"  mean years observed per case: {len(panel_sample) / len(sample):.2f}")

    print("\nFunding: timing of the next round (primary funding DV)")
    print(f"  matched to Crunchbase: {int(sample['cb_matched'].sum())} of {len(sample)}")
    print(f"  round observed:        {int((sample['post_event_round_observed'] == 1).sum())}")
    print(f"  right-censored:        {int((sample['post_event_round_observed'] == 0).sum())}")
    print(f"  no Crunchbase match:   {int(sample['post_event_round_observed'].isna().sum())}")
    flagged = int(sample["first_round_same_month_as_pitch"].sum())
    print(f"  round in the pitch month (day unknown, may predate the pitch): {flagged}")

    print("\nFunding: values, as a share of firms that actually raised")
    raised = sample[sample["post_event_round_observed"] == 1]
    n = max(len(raised), 1)
    for col, desc in [
        ("first_post_event_round_usd", "amount of the next round"),
        ("first_post_event_round_investors", "investor count"),
        ("first_post_event_round_valuation_usd", "valuation"),
        ("post_event_funding_usd", "total post-pitch funding"),
        ("post_event_max_valuation_usd", "max post-pitch valuation"),
    ]:
        if col in raised.columns:
            present = int(raised[col].notna().sum())
            print(f"  {desc:28s} {present:4d} of {len(raised)} ({present / n:5.1%})")

    print("\nFunding: milestone outcomes (no disclosure requirement)")
    if "reached_series_a" in sample.columns:
        ra = sample["reached_series_a"]
        print(f"  reached Series A or later: {int((ra == 1).sum())} yes, {int((ra == 0).sum())} no, {int(ra.isna().sum())} unmatched")
    if "post_event_rounds" in sample.columns:
        pr = sample["post_event_rounds"]
        print(f"  post-pitch round count:    mean {pr.mean():.2f}, max {pr.max():.0f}")

    print("\nCovariate availability in the analysis sample")
    for col in ["age_at_pitch_years", "pre_event_rounds", "pre_event_funding_usd", "BMI"]:
        if col in sample.columns:
            print(f"  {col:24s} present for {int(sample[col].notna().sum()):3d} of {len(sample)}")


if __name__ == "__main__":
    report()
