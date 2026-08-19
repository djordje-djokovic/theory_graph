"""Wayback Machine CDX queries and annual snapshot classification."""

from __future__ import annotations

import time
from datetime import date, datetime
from typing import Optional

import requests

from .classify import HEADERS, classify_page, fetch_page


CDX_URL = "http://web.archive.org/cdx/search/cdx"


def cdx_yearly_snapshots(domain: str, start_year: int, end_year: int, timeout: int = 120) -> list[dict]:
    """Return one representative status-200 snapshot per year.

    Uses a single CDX query with collapse=timestamp:4, so one request per domain
    rather than one per year. The snapshot is the first one in each calendar year;
    a later refinement can pick the one nearest to the pitch anniversary.
    """
    params = {
        "url": domain,
        "output": "json",
        "from": f"{start_year}0101",
        "to": f"{end_year}1231",
        "fl": "timestamp,statuscode,digest,length",
        "filter": "statuscode:200",
        "collapse": "timestamp:4",
    }
    snapshots = []
    try:
        r = requests.get(CDX_URL, params=params, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        rows = r.json()
        if len(rows) > 1:
            for snap in rows[1:]:
                year = int(snap[0][:4])
                snapshots.append({
                    "timestamp": snap[0],
                    "statuscode": int(snap[1]),
                    "digest": snap[2],
                    "length": int(snap[3]) if snap[3] else None,
                    "year": year,
                    "wayback_url": f"https://web.archive.org/web/{snap[0]}/{domain}",
                })
    except Exception as e:
        snapshots.append({
            "timestamp": None,
            "statuscode": None,
            "digest": None,
            "length": None,
            "year": None,
            "wayback_url": None,
            "error": str(e),
        })
    return snapshots


def classify_snapshots(domain: str, origin_date: date, censor_date: date, timeout: int = 60) -> dict:
    """Classify one snapshot per year from origin to censor, returning alive/dead trajectory."""
    start_year = origin_date.year
    end_year = censor_date.year

    snaps = cdx_yearly_snapshots(domain, start_year, end_year, timeout=timeout)
    classifications = []
    for s in snaps:
        if s.get("wayback_url") is None:
            classifications.append({**s, "alive": None, "dead": None, "inspect": True, "reason": s.get("error") or "no_snapshot"})
            continue
        try:
            r = requests.get(s["wayback_url"], headers=HEADERS, timeout=timeout)
            c = classify_page(s["wayback_url"], r.text, r.url, r.status_code)
            classifications.append({**s, **c})
        except Exception as e:
            classifications.append({**s, "alive": None, "dead": None, "inspect": True, "reason": f"fetch_error:{type(e).__name__}"})
        time.sleep(1.0)

    transition = find_death_transition(classifications)

    return {
        "domain": domain,
        "classifications": classifications,
        "n_snapshots": len(snaps),
        "n_inspect": sum(1 for c in classifications if c.get("inspect")),
        **transition,
    }


def find_death_transition(classifications: list[dict]) -> dict:
    """Locate the alive-to-dead transition in a chronological snapshot sequence.

    A dead snapshot followed by a later alive snapshot is a false positive, caused
    by a transient outage, a fetch error, or a relaunch. The death is therefore the
    first dead year with no alive year after it, not simply the first dead reading.
    """
    dated = sorted(
        (c for c in classifications if c.get("year") is not None),
        key=lambda c: c["year"],
    )
    alive_years = [c["year"] for c in dated if c.get("alive")]
    dead_years = [c["year"] for c in dated if c.get("dead")]

    last_alive = max(alive_years) if alive_years else None
    if last_alive is None:
        # Never confirmed alive, so the earliest dead reading is all we have
        first_dead = min(dead_years) if dead_years else None
    else:
        after = [y for y in dead_years if y > last_alive]
        first_dead = min(after) if after else None

    return {
        "last_alive_year": last_alive,
        "first_dead_year": first_dead,
        "n_alive": len(alive_years),
        "n_dead": len(dead_years),
        "revived": bool(last_alive is not None and dead_years and min(dead_years) < last_alive),
    }
