"""Sample validation of the Wayback annual scan on a handful of firms."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from .config import PATHS
from .event_dates import lookup
from .io import load_attractiveness_companies
from .wayback import classify_snapshots


SAMPLE = [
    ("3DLT", "Revival case"),
    ("aboutlastnight.com", "Prior-owner domain"),
    ("Wisebatt", "Junk website field"),
    ("Pressly", "Site points at acquirer"),
    ("Mint", "Short generic name, CB-dated acquisition"),
    ("Atlas Wearables", "Year-stamped acquisition"),
]


def main():
    companies = load_attractiveness_companies()
    companies["origin_date"] = companies["event"].map(lookup)

    out = []
    for name, note in SAMPLE:
        row = companies[companies["name"] == name]
        if row.empty:
            print(f"MISSING: {name}")
            continue
        row = row.iloc[0]
        domain = row["website"]
        if not isinstance(domain, str) or not domain.startswith("http"):
            domain = f"http://{domain}"
        origin = pd.to_datetime(row["origin_date"]).date()
        censor = date(2024, 3, 31)
        print(f"\n{name} ({note}) — {domain}, origin {origin}")
        result = classify_snapshots(domain, origin, censor, timeout=30)
        print(f"  last_alive_year: {result['last_alive_year']}, first_dead_year: {result['first_dead_year']}, inspect: {result['n_inspect']}")
        for c in result["classifications"]:
            print(f"    {c['year']}: alive={c.get('alive')}, dead={c.get('dead')}, inspect={c.get('inspect')}, reason={c.get('reason')}")
        out.append({"name": name, "note": note, **result})

    diag = PATHS["diagnostics"] / "wayback_sample.json"
    diag.parent.mkdir(parents=True, exist_ok=True)
    with diag.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nWrote sample results to {diag}")


if __name__ == "__main__":
    main()
