"""Post-pitch funding DVs from Crunchbase funding_rounds."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine

from .config import CB_DB, CB_DUMP_DATE
from .crunchbase import load_cb_funding_rounds


# Equity-investment types we keep. Excludes grants, debt, crowdfunding, ICOs, post-IPO, secondary.
EQUITY_TYPES = {
    "pre_seed", "seed", "angel", "series_a", "series_b", "series_c", "series_d",
    "series_e", "series_f", "series_g", "series_h", "series_i", "series_j",
    "series_unknown", "convertible_note", "corporate_round", "equity_crowdfunding",
    "private_equity",
}


def build_funding_dvs(exits_df: pd.DataFrame) -> pd.DataFrame:
    """Add funding DVs to the exit table.

    Unmatched firms (cb_matched = 0) stay NA on all funding fields.
    """
    engine = create_engine(CB_DB)
    rounds = load_cb_funding_rounds(engine)

    df = exits_df.copy()
    df["origin_date"] = pd.to_datetime(df["origin_date"], errors="coerce")
    df["censor_date"] = pd.to_datetime(df["censor_date"], errors="coerce")
    df["cb_last_funding_on"] = pd.to_datetime(df["cb_last_funding_on"], errors="coerce")

    # The pre/post split depends on the pitch date, and three firms pitched at two
    # different events, so the grouping key must be the firm-event, not the name.
    KEY = ["name", "event"]

    matched = df[df["cb_matched"] == 1][KEY + ["cb_org_uuid", "origin_date", "censor_date"]].copy()
    if matched.empty or rounds.empty:
        for col in [
            "pre_event_rounds", "pre_event_rounds_with_amount", "pre_event_funding_usd",
            "pre_event_funding_usd_real", "pct_amount_disclosed", "time_to_first_post_event_round",
            "last_funding_on", "first_post_event_round_on", "first_post_event_round_usd",
            "first_post_event_round_type", "post_event_rounds", "post_event_funding_usd",
            "post_event_rounds_with_amount", "reached_series_a", "first_post_event_round_investors",
            "first_post_event_round_valuation_usd", "post_event_round_observed",
            "funding_exposure_years", "first_round_same_month_as_pitch",
        ]:
            df[col] = pd.NA
        return df

    rounds = rounds[rounds["investment_type"].isin(EQUITY_TYPES)].copy()
    rounds["announced_on"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
    rounds = rounds[rounds["announced_on"].notna()]

    merged = matched.merge(rounds, left_on="cb_org_uuid", right_on="org_uuid", how="left")

    pre = merged[merged["announced_on"] <= merged["origin_date"]]
    post = merged[merged["announced_on"] > merged["origin_date"]]

    pre_counts = pre.groupby(KEY).size().reset_index(name="pre_event_rounds")
    pre_amounts = pre.groupby(KEY).agg(
        pre_event_funding_usd=("raised_amount_usd", "sum"),
        pre_event_rounds_with_amount=("raised_amount_usd", lambda x: x.notna().sum()),
    ).reset_index()

    post_first = post.sort_values("announced_on").drop_duplicates(KEY, keep="first")[
        KEY + ["announced_on", "raised_amount_usd", "investment_type", "investor_count",
               "post_money_valuation_usd"]
    ].rename(columns={
        "announced_on": "first_post_event_round_on",
        "raised_amount_usd": "first_post_event_round_usd",
        "investment_type": "first_post_event_round_type",
        "investor_count": "first_post_event_round_investors",
        "post_money_valuation_usd": "first_post_event_round_valuation_usd",
    })

    # Post-pitch totals. Counts and sums are exposure-confounded and subject to
    # disclosure bias, so they are covariates and secondary outcomes, not the primary DV.
    post_totals = post.groupby(KEY).agg(
        post_event_rounds=("uuid", "size"),
        post_event_funding_usd=("raised_amount_usd", "sum"),
        post_event_rounds_with_amount=("raised_amount_usd", lambda x: x.notna().sum()),
        post_event_max_valuation_usd=("post_money_valuation_usd", "max"),
    ).reset_index()

    # Graduating to an institutional round is a cleaner milestone than a dollar sum
    series_a_plus = {f"series_{c}" for c in "abcdefghij"}
    reached = post[post["investment_type"].isin(series_a_plus)].groupby(KEY).agg(
        first_series_a_on=("announced_on", "min"),
    ).reset_index()

    last_funding = merged.groupby(KEY)["announced_on"].max().reset_index().rename(
        columns={"announced_on": "last_funding_on"}
    )

    # Disclosure share
    total_rounds = rounds.groupby("org_uuid").size().reset_index(name="total_rounds")
    disclosed_rounds = rounds[rounds["raised_amount_usd"].notna()].groupby("org_uuid").size().reset_index(name="disclosed_rounds")
    disclosure = total_rounds.merge(disclosed_rounds, on="org_uuid", how="left")
    disclosure["disclosed_rounds"] = disclosure["disclosed_rounds"].fillna(0)
    disclosure["pct_amount_disclosed"] = disclosure["disclosed_rounds"] / disclosure["total_rounds"]

    # Merge back
    for frame in (pre_counts, pre_amounts, post_first, post_totals, reached, last_funding):
        df = df.merge(frame, on=KEY, how="left")
    df = df.merge(disclosure[["org_uuid", "pct_amount_disclosed"]], left_on="cb_org_uuid", right_on="org_uuid", how="left")
    df = df.drop(columns=["org_uuid"], errors="ignore")

    df = _build_time_to_funding(df)
    df = _flag_pitch_month_rounds(df)

    # Reaching an institutional round, as a milestone outcome
    df["reached_series_a"] = pd.NA
    df.loc[df["cb_matched"] == 1, "reached_series_a"] = df.loc[df["cb_matched"] == 1, "first_series_a_on"].notna().astype(int)

    # For matched firms with no rounds, a zero is the true value; fill only the counts.
    # Amount sums stay NA when no rounds exist (so they don't look like a disclosed $0).
    fill_zero_cols = [
        "pre_event_rounds", "pre_event_rounds_with_amount",
        "post_event_rounds", "post_event_rounds_with_amount",
    ]
    for col in fill_zero_cols:
        df.loc[df["cb_matched"] == 1, col] = df.loc[df["cb_matched"] == 1, col].fillna(0)

    # For unmatched firms, all funding fields stay NA
    df.loc[df["cb_matched"] == 0, [
        "pre_event_rounds", "pre_event_rounds_with_amount", "pre_event_funding_usd",
        "pre_event_funding_usd_real", "pct_amount_disclosed", "last_funding_on",
        "first_post_event_round_on", "time_to_first_post_event_round",
        "post_event_round_observed", "funding_exposure_years",
        "first_post_event_round_usd", "first_post_event_round_type",
        "first_post_event_round_investors", "first_post_event_round_valuation_usd",
        "post_event_rounds", "post_event_funding_usd", "post_event_rounds_with_amount",
        "post_event_max_valuation_usd", "reached_series_a", "first_round_same_month_as_pitch",
    ]] = pd.NA

    # Real-dollar placeholder: just copy nominal for now; add CPI deflator later
    df["pre_event_funding_usd_real"] = df["pre_event_funding_usd"]

    return df


def _build_time_to_funding(df: pd.DataFrame) -> pd.DataFrame:
    """Turn the first post-pitch round into a duration with an explicit censoring time.

    Exposure ends at the earliest of the Crunchbase dump date and the firm's own exit,
    because a firm that has already failed or been acquired is no longer at risk of
    raising an equity round. Firms with no observed round are right-censored at that
    exposure time rather than left as missing.
    """
    cb_end = pd.Timestamp(CB_DUMP_DATE)

    origin = pd.to_datetime(df["origin_date"], errors="coerce")
    first_round = pd.to_datetime(df.get("first_post_event_round_on"), errors="coerce")
    exit_date = pd.to_datetime(df.get("exit_date"), errors="coerce")

    # Exposure window: pitch -> min(CB dump, exit). Survivors run to the dump date.
    exposure_end = exit_date.fillna(cb_end).clip(upper=cb_end)
    exposure_end = exposure_end.where(exposure_end >= origin, origin)

    observed = first_round.notna() & (first_round <= cb_end)
    event_time = first_round.where(observed, exposure_end)

    df["post_event_round_observed"] = observed.astype("Int64")
    df["time_to_first_post_event_round"] = (event_time - origin).dt.days / 365.25
    df["funding_exposure_years"] = (exposure_end - origin).dt.days / 365.25

    # A round announced after the firm's recorded exit still counts as observed, so
    # the duration can exceed the exposure window; keep both so it stays auditable.
    negative = df["time_to_first_post_event_round"] < 0
    if negative.any():
        raise ValueError(
            f"{int(negative.sum())} firms have a post-pitch round dated before the pitch; "
            "the pre/post split is keyed incorrectly"
        )

    return df


def _flag_pitch_month_rounds(df: pd.DataFrame) -> pd.DataFrame:
    """Flag first rounds announced in the same calendar month as the pitch.

    The event-date table resolves the pitch to a month, so origin_date is the first of
    that month. A round announced later in the pitch month is therefore classified as
    post-pitch even though it may have closed before the firm actually presented.
    Attributing it to the pitch would overstate the effect, so it is flagged for a
    robustness specification that excludes it.
    """
    origin = pd.to_datetime(df["origin_date"], errors="coerce")
    first_round = pd.to_datetime(df.get("first_post_event_round_on"), errors="coerce")

    df["first_round_same_month_as_pitch"] = (
        first_round.notna() & (first_round.dt.to_period("M") == origin.dt.to_period("M"))
    ).astype(int)
    return df
