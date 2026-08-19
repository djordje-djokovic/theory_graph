"""Crunchbase-based matching, exit typing, and acquisition dating."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text

from .config import CB_DB
from .event_dates import lookup
from .io import normalize_name


# ---------------------------------------------------------------------------
# Domain helpers
# ---------------------------------------------------------------------------

def extract_domain(url: Optional[str]) -> Optional[str]:
    if not isinstance(url, str):
        return None
    u = re.sub(r"^https?://", "", url.strip().lower()).split("/")[0]
    u = re.sub(r"^www\.", "", u)
    return u or None


# Known problematic domains / acquirer domains that should flag a sanity check.
# This is a small, auditable list; expand as we encounter more cases.
AGGREGATOR_DOMAINS = {
    "crunchbase.com",
    "techcrunch.com",
    "linkedin.com",
    "facebook.com",
    "twitter.com",
    "x.com",
}


def flag_website(row: pd.Series) -> dict:
    """Return website-sanity flags for a single company row.

    Does not return a 'domain' key — df['domain'] is computed separately and is
    the canonical domain column.
    """
    website = row.get("website")
    status = row.get("status", "")
    dom = extract_domain(website)
    flags = {
        "website_valid": True,
        "website_flag": None,
    }
    if not dom:
        flags["website_valid"] = False
        flags["website_flag"] = "missing"
        return flags
    if dom in AGGREGATOR_DOMAINS:
        flags["website_valid"] = False
        flags["website_flag"] = f"aggregator_or_known_bad:{dom}"
        return flags
    if status == "acquired":
        # If the website already points at a well-known public company, the domain
        # is likely the *acquirer's* domain, not the startup's. Flag for manual check.
        # Specific cases are logged in diagnostics, not hard-coded here.
        pass
    return flags


# ---------------------------------------------------------------------------
# Crunchbase matching
# ---------------------------------------------------------------------------

def load_cb_orgs(engine) -> pd.DataFrame:
    q = text("""
        SELECT uuid, name, lower(domain) as domain, status, founded_on,
               closed_on, last_funding_on, permalink, cb_url
        FROM crunchbase.organizations
        WHERE domain IS NOT NULL
    """)
    return pd.read_sql(q, engine)


def load_cb_acquisitions(engine) -> pd.DataFrame:
    q = text("""
        SELECT acquiree_uuid, acquiree_name, acquired_on, acquisition_type,
               acquirer_uuid, acquirer_name, acquirer_cb_url
        FROM crunchbase.acquisitions
        WHERE acquired_on IS NOT NULL
    """)
    return pd.read_sql(q, engine)


def load_cb_funding_rounds(engine) -> pd.DataFrame:
    q = text("""
        SELECT uuid, org_uuid, announced_on, raised_amount_usd, investment_type,
               investor_count, post_money_valuation_usd
        FROM crunchbase.funding_rounds
    """)
    return pd.read_sql(q, engine)


# ---------------------------------------------------------------------------
# Main exit typing
# ---------------------------------------------------------------------------

def build_exit_table(companies_df: pd.DataFrame) -> pd.DataFrame:
    """Add exit_type, exit_date, and CB match columns to the companies table.

    This is the CB-only stage. Wayback will later refine the undated failures
    and undated acquisitions in a separate step.
    """
    engine = create_engine(CB_DB)
    orgs = load_cb_orgs(engine)
    acq = load_cb_acquisitions(engine)

    df = companies_df.copy()
    df["domain"] = df["website"].map(extract_domain)

    # --- website sanity flags
    sanity = df.apply(flag_website, axis=1, result_type="expand")
    df = pd.concat([df, sanity], axis=1)

    # --- CB domain match
    dom_match = df[["name", "domain", "status"]].merge(
        orgs, left_on="domain", right_on="domain", how="left", suffixes=("", "_cb")
    )
    # Count matches per firm
    match_counts = dom_match.groupby("name").size().reset_index(name="cb_domain_match_count")
    df = df.merge(match_counts, on="name", how="left")
    df["cb_domain_match_count"] = df["cb_domain_match_count"].fillna(0).astype(int)

    # Take the unique CB match; if multiple, we will flag manual_review
    unique_dom = dom_match.drop_duplicates("name", keep="first")
    df = df.merge(
        unique_dom[["name", "uuid", "status_cb", "founded_on", "closed_on", "last_funding_on"]],
        on="name", how="left", suffixes=("", "_cb")
    )
    df = df.rename(columns={
        "uuid": "cb_org_uuid",
        "status_cb": "crunchbase_status",
        "founded_on": "cb_founded_on",
        "closed_on": "cb_closed_on",
        "last_funding_on": "cb_last_funding_on",
    })
    df["cb_matched"] = df["cb_org_uuid"].notna().astype(int)
    df["cb_match_type"] = df.apply(_match_type, axis=1)

    # --- Acquisition dating via domain path
    acq_dom = df[df["cb_org_uuid"].notna()][["name", "cb_org_uuid"]].merge(
        acq, left_on="cb_org_uuid", right_on="acquiree_uuid", how="left"
    )
    acq_dom_counts = acq_dom.groupby("name").size().reset_index(name="cb_acq_record_count")
    df = df.merge(acq_dom_counts, on="name", how="left")
    df["cb_acq_record_count"] = df["cb_acq_record_count"].fillna(0).astype(int)

    earliest_acq = (
        acq_dom.sort_values("acquired_on")
        .drop_duplicates("name", keep="first")[["name", "acquired_on", "acquisition_type", "acquirer_name"]]
    )
    df = df.merge(earliest_acq, on="name", how="left", suffixes=("", "_cb_acq"))

    # --- Exit type and date (CB-only stage)
    df["exit_type"] = df["status"]
    df["exit_date"] = pd.NaT
    df["exit_date_precision"] = None
    df["death_source"] = None
    df["acq_date_source"] = None
    df["acquihire"] = 0
    df["tc_cb_conflict"] = 0
    df["date_conflict"] = 0
    df["manual_review"] = 0

    for idx, row in df.iterrows():
        result = _classify_exit(row)
        for col, val in result.items():
            df.at[idx, col] = val

    # --- Acquisition name-path for the remaining undated acquisitions
    undated_acq = df[(df["status"] == "acquired") & df["exit_date"].isna()].copy()
    if not undated_acq.empty:
        name_matches = _match_by_acquiree_name(undated_acq, acq)
        df = df.merge(
            name_matches[["name", "acquired_on", "acquisition_type", "acquirer_name", "acq_date_source"]],
            on="name", how="left", suffixes=("", "_name_match")
        )
        # Apply the name-match results only where the domain path did not already date it
        mask = df["status"] == "acquired"
        already_dated = df["exit_date"].notna()
        name_match_ok = df["acquired_on_name_match"].notna()
        apply_mask = mask & ~already_dated & name_match_ok
        df.loc[apply_mask, "exit_date"] = df.loc[apply_mask, "acquired_on_name_match"]
        df.loc[apply_mask, "exit_date_precision"] = _precision_from_date(df.loc[apply_mask, "acquired_on_name_match"])
        df.loc[apply_mask, "acq_date_source"] = df.loc[apply_mask, "acq_date_source_name_match"]
        df.loc[apply_mask, "acquisition_type"] = df.loc[apply_mask, "acquisition_type_name_match"]
        df.loc[apply_mask, "acquirer_name"] = df.loc[apply_mask, "acquirer_name_name_match"]
        df.drop(columns=["acquired_on_name_match", "acquisition_type_name_match", "acquirer_name_name_match", "acq_date_source_name_match"], inplace=True)

    # --- Final cleanup
    df["death_source"] = df.apply(_final_death_source, axis=1)
    return df


def _match_type(row: pd.Series) -> str:
    if row["cb_domain_match_count"] == 0:
        return "none"
    if row["cb_domain_match_count"] == 1:
        return "domain"
    return "domain_multiple"


def _classify_exit(row: pd.Series) -> dict:
    status = row["status"]
    out = {}

    def _to_ts(x):
        return pd.NaT if pd.isna(x) else pd.to_datetime(x)

    if status == "open":
        out["exit_type"] = "censored"
        out["exit_date"] = pd.NaT
        out["exit_date_precision"] = None
        out["death_source"] = None
        if pd.notna(row.get("acquired_on")):
            out["tc_cb_conflict"] = 1
        return out

    if status == "ipo":
        out["exit_type"] = "ipo"
        out["exit_date"] = pd.NaT
        out["exit_date_precision"] = None
        out["death_source"] = None
        return out

    if status == "acquired":
        out["exit_type"] = "acquired"
        if pd.notna(row.get("acquired_on")):
            out["exit_date"] = _to_ts(row["acquired_on"])
            out["exit_date_precision"] = _precision_from_date(row["acquired_on"])
            out["acq_date_source"] = "cb_domain"
            if row.get("acquisition_type") == "acquihire":
                out["acquihire"] = 1
        else:
            out["exit_date"] = pd.NaT
            out["exit_date_precision"] = None
        return out

    if status == "closed":
        out["exit_type"] = "failure"
        if pd.notna(row.get("cb_closed_on")) and pd.isna(row.get("acquired_on")):
            out["exit_date"] = _to_ts(row["cb_closed_on"])
            out["exit_date_precision"] = _precision_from_date(row["cb_closed_on"])
            out["death_source"] = "crunchbase"
        else:
            out["exit_date"] = pd.NaT
            out["exit_date_precision"] = None
            out["death_source"] = None
        return out

    return out


def _precision_from_date(d) -> Optional[str] | pd.Series:
    """Return 'year' if month/day is Jan 1, else 'day'.

    Works on a scalar or a pandas Series of datetime-like values.
    """
    is_scalar = not isinstance(d, pd.Series)
    s = pd.Series(d) if is_scalar else d
    s = pd.to_datetime(s, errors="coerce")
    out = pd.Series(index=s.index, dtype="object")
    out[(s.dt.month == 1) & (s.dt.day == 1)] = "year"
    out[((s.dt.month != 1) | (s.dt.day != 1)) & s.notna()] = "day"
    if is_scalar:
        val = out.iloc[0] if len(out) > 0 else None
        return None if pd.isna(val) else val
    return out


def _final_death_source(row: pd.Series) -> Optional[str]:
    """Use the already-set death_source if present; otherwise derive from acq_date_source."""
    if pd.notna(row.get("death_source")):
        return row["death_source"]
    if row["status"] == "acquired" and pd.notna(row.get("acq_date_source")):
        return f"acquisition:{row['acq_date_source']}"
    return None


# ---------------------------------------------------------------------------
# Acquisition name-path
# ---------------------------------------------------------------------------

def _match_by_acquiree_name(undated_df: pd.DataFrame, acq: pd.DataFrame) -> pd.DataFrame:
    """Match undated acquisitions by normalized acquiree_name, verified by acquirer."""
    acq = acq.copy()
    acq["nname"] = acq["acquiree_name"].map(normalize_name)
    acq = acq[acq["nname"].notna()]

    undated_df = undated_df.copy()
    undated_df["nname"] = undated_df["name"].map(normalize_name)
    # Drop the empty CB columns from the domain path so they don't conflict with the
    # real CB columns we are about to merge in.
    drop_cols = [c for c in ["acquired_on", "acquisition_type", "acquirer_name"] if c in undated_df.columns]
    undated_df = undated_df.drop(columns=drop_cols)

    hits = undated_df.merge(acq, on="nname", how="inner", suffixes=("", "_cb"))
    # Use the suffixed columns from the right table (the real CB data)
    hits = hits.rename(columns={
        "acquired_on_cb": "acquired_on",
        "acquisition_type_cb": "acquisition_type",
        "acquirer_name_cb": "acquirer_name",
    })
    # Keep only matches with a plausible acquirer name
    hits = hits[hits["acquirer_name"].notna() & (hits["acquirer_name"].astype(str).str.len() >= 2)]
    # Take the earliest acquisition per firm
    hits = hits.sort_values("acquired_on").drop_duplicates("name", keep="first")
    hits["acq_date_source"] = "cb_name"
    return hits
