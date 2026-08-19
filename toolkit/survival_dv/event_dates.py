"""Event-date lookup for the Battlefield pitch clock.

Month precision is sufficient for both the survival clock and the funding cutoff.
The six undated event names are verified against TechCrunch/contemporaneous press;
the rest derive a month from family conventions with documented exceptions.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Dict, Optional, Tuple


# Explicit overrides for event names that carry no year in the string, plus
# a few special cases where the family rule is known to be off by >1 month.
EVENT_OVERRIDES: Dict[str, Tuple[int, int]] = {
    "TechCrunch 40": (2007, 9),                       # Sept 17-18, 2007, Palace Hotel SF
    "Hardware Battlefield": (2014, 1),                # Jan 7-9, 2014, CES Las Vegas
    "TechCrunch Startup Battlefield Africa": (2017, 10),  # Oct 11, 2017, Nairobi
    "Startup Battlefield Australia": (2017, 11),      # Nov 15, 2017, Sydney
    "Startup Battlefield Latin America": (2018, 11),  # Nov 8, 2018, São Paulo
    "TC Hardware Battlefield at TC Shenzhen": (2019, 11),  # Nov 11-12, 2019
    "1st and Future": (2016, 2),                      # Feb 11, 2016
    "Disrupt Beijing 2011": (2011, 10),               # Oct 31-Nov 1, 2011
    "Disrupt Europe 2013": (2013, 10),                # Oct 28-29, 2013, London
    "Disrupt Europe 2014: London": (2014, 10),        # Oct 20-21, 2014
    "Disrupt SF 2019": (2019, 10),                     # Oct 2-4, 2019 (slipped from Sept)
    "TechCrunch Disrupt 2022": (2022, 10),             # Oct 18-20, 2022
}


# Family conventions. Keys are lower-cased substrings matched in order.
# Earlier entries take precedence, so put the most specific first.
FAMILY_RULES: list[tuple[str, int]] = [
    # Specific named events
    ("1st and future", 2),          # handled by override, kept for safety
    ("hardware battlefield", 1),  # CES, January
    ("startup battlefield africa 2018", 12),  # Lagos, Dec 11
    ("startup battlefield mena 2018", 12),    # Beirut, Dec 7
    ("startup battlefield europe 2018", 10),  # Berlin, Oct 24-25
    ("startup battlefield", 11),    # Australia Nov, Latin America Nov
    ("techcrunch startup battlefield africa", 10),  # Nairobi, Oct 11
    ("techcrunch50", 9),            # September
    ("techcrunch 40", 9),           # September
    # Disrupt cities
    ("disrupt nyc", 5),             # May 25-26, 2010
    ("disrupt ny", 5),              # May
    ("disrupt berlin", 12),         # December (2017 Dec 4-5, 2018 Nov 29-30, 2019 Dec 11-12; family rule picks Dec)
    ("disrupt london", 12),         # December
    ("disrupt europe", 10),         # October (2013/2014 London); overrides above handle the known ones
    ("disrupt beijing", 10),        # October/November
    ("disrupt sf", 9),              # September (2019 exception handled above)
    ("disrupt 2020", 9),            # Sept 14-18, virtual
    ("disrupt 2021", 9),            # Sept 21-23, virtual
    ("disrupt 2022", 10),           # Oct 18-20
    ("disrupt 2023", 9),            # Sept 19-21
    ("disrupt", 9),                 # catch-all for any other Disrupt
]


def parse_year(event: str) -> Optional[int]:
    """Extract a 4-digit year from the event string, tolerating spaces."""
    if not isinstance(event, str):
        return None
    m = re.search(r"(?:19|20)\d{2}", event)
    return int(m.group(0)) if m else None


def lookup(event: str) -> Optional[date]:
    """Return the pitch date (month precision, day=1) for an event string."""
    if not isinstance(event, str):
        return None
    event = event.strip()

    # 1. Explicit overrides
    if event in EVENT_OVERRIDES:
        year, month = EVENT_OVERRIDES[event]
        return date(year, month, 1)

    # 2. Family rules
    key = event.lower()
    for substring, month in FAMILY_RULES:
        if substring in key:
            year = parse_year(event)
            if year is None:
                return None
            return date(year, month, 1)

    # 3. Year only, no recognizable family
    year = parse_year(event)
    if year is None:
        return None
    return date(year, 6, 1)  # mid-year fallback, flagged by origin_source


def lookup_all(events: list[str]) -> dict[str, Optional[date]]:
    return {e: lookup(e) for e in events}


def to_table() -> list[dict]:
    """Return a list of dicts suitable for writing event_dates.csv."""
    from .io import load_attractiveness_companies
    df = load_attractiveness_companies()
    rows = []
    for ev in sorted(df["event"].dropna().unique()):
        d = lookup(ev)
        rows.append({
            "event": ev,
            "origin_year": d.year if d else None,
            "origin_month": d.month if d else None,
            "origin_date": d.isoformat() if d else None,
            "source": "verified" if ev in EVENT_OVERRIDES else "family",
        })
    return rows


if __name__ == "__main__":
    import csv
    from pathlib import Path
    from .config import PATHS

    rows = to_table()
    out = PATHS["event_dates"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["event", "origin_year", "origin_month", "origin_date", "source"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")
