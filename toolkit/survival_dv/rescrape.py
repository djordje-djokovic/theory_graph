"""Re-scrape TechCrunch Startup Battlefield directory and align to the original 1,300 firms."""

from __future__ import annotations

import csv
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .config import PATHS
from .io import load_attractiveness_companies


BASE_URL = "https://techcrunch.com/wp-json/tc/v1/get-companies-data?pg="
MAX_PAGES = 200  # safety cap; stop when a page returns empty


def scrape_directory(max_pages: int = MAX_PAGES, sleep: float = 1.0, max_retries: int = 3) -> list[dict]:
    """Scrape all pages of the TechCrunch companies API, with retry on transient errors."""
    all_companies = []
    for page in range(1, max_pages + 1):
        url = BASE_URL + str(page)
        companies = None
        last_error = None
        for attempt in range(max_retries):
            try:
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                data = r.json()
                companies = data.get("data", {}).get("companies", [])
                break
            except Exception as e:
                last_error = e
                print(f"\n  Page {page} attempt {attempt + 1} failed: {e}")
                time.sleep(sleep * (attempt + 1))
        if companies is None:
            print(f"\nGiving up on page {page}: {last_error}")
            break
        if not companies:
            print(f"Page {page} empty; stopping.")
            break
        for company in companies:
            link = company.get("link")
            if not link:
                continue
            company["fresh_status"] = company.get("status", "").lower().strip()
            company["fresh_label"] = company.get("label", "")
            company["fresh_money_raised"] = company.get("money_raised", "")
            company["fresh_founded_date"] = company.get("founded_date", "")
            company["fresh_event"] = company.get("event", "")
            company["page"] = page
            all_companies.append(company)
        print(f"Page {page}: {len(companies)} companies (total {len(all_companies)})", end="\r")
        time.sleep(sleep)
    print()
    return all_companies


def enrich_with_website(companies: list[dict], sleep: float = 1.0) -> list[dict]:
    """Fetch the company page to get the website and founded date if not in API."""
    for i, company in enumerate(companies):
        link = company.get("link")
        if not link or company.get("website"):
            continue
        try:
            r = requests.get(link, timeout=30)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.content, "html.parser")
            rows = soup.find_all("div", class_="company--table-row")
            for row in rows:
                header = row.find("strong")
                if not header:
                    continue
                if header.text == "Website":
                    a = row.find("a")
                    if a:
                        company["website"] = a.get("href")
                elif header.text == "Founded Date":
                    p = row.find("p")
                    if p:
                        company["founded_date"] = p.text.strip()
            founder_h3 = soup.find("h3", string="Founders")
            if founder_h3:
                founder_row = founder_h3.find_next_sibling("p", class_="company--table-row")
                if founder_row:
                    strong = founder_row.find("strong")
                    if strong:
                        company["founder_name"] = strong.text.strip()
        except Exception as e:
            company["fetch_error"] = str(e)
        if i % 10 == 0:
            print(f"Enriched {i}/{len(companies)}", end="\r")
        time.sleep(sleep)
    print()
    return companies


def align_to_original(fresh_df: pd.DataFrame, original_df: pd.DataFrame) -> pd.DataFrame:
    """Match the fresh scrape to the original 1,300 firms by link."""
    original = original_df[["name", "link", "status"]].copy()
    original = original.rename(columns={"status": "tc_status_2024"})
    merged = original.merge(
        fresh_df[["link", "fresh_status", "fresh_label", "fresh_money_raised", "fresh_founded_date", "fresh_event", "page"]],
        on="link", how="left"
    )
    merged = merged.rename(columns={"fresh_status": "tc_status"})
    merged["status_changed"] = merged["tc_status"] != merged["tc_status_2024"]
    return merged


def load_fresh_statuses() -> pd.DataFrame:
    """Load the aligned fresh statuses if they have been scraped; otherwise return None."""
    aligned_path = PATHS["diagnostics"] / "techcrunch_fresh_aligned.csv"
    if not aligned_path.exists():
        return None
    return pd.read_csv(aligned_path)


def apply_fresh_statuses(companies_df: pd.DataFrame) -> pd.DataFrame:
    """Merge fresh TechCrunch statuses into the companies table."""
    fresh = load_fresh_statuses()
    if fresh is None:
        return companies_df

    df = companies_df.copy()
    df = df.merge(
        fresh[["link", "tc_status", "tc_status_2024", "status_changed"]],
        on="link", how="left", suffixes=("", "_fresh")
    )
    # If fresh status is missing, fall back to the 2024 status
    df["tc_status"] = df["tc_status"].fillna(df["status"])
    df["tc_status_2024"] = df["tc_status_2024"].fillna(df["status"])
    # Replace the normalized status column with the fresh one for downstream use
    df["status"] = df["tc_status"]
    return df


def main():
    out_dir = PATHS["diagnostics"]
    out_dir.mkdir(parents=True, exist_ok=True)

    fresh_raw_path = out_dir / "techcrunch_fresh_scrape_raw.csv"
    aligned_path = out_dir / "techcrunch_fresh_aligned.csv"

    original = load_attractiveness_companies()

    print("Scraping TechCrunch directory...")
    fresh = scrape_directory()
    fresh_df = pd.DataFrame(fresh)
    fresh_df.to_csv(fresh_raw_path, index=False)
    print(f"Wrote raw fresh scrape to {fresh_raw_path} ({len(fresh_df)} firms)")

    print("\nAligning to original 1,300 firms...")
    aligned = align_to_original(fresh_df, original)
    aligned.to_csv(aligned_path, index=False)
    print(f"Wrote aligned statuses to {aligned_path}")

    print("\nStatus change summary:")
    print(aligned[["tc_status_2024", "tc_status"]].value_counts(dropna=False).to_string())
    print(f"\nFirms with status change: {aligned['status_changed'].sum()}")
    print(f"Firms not found in fresh scrape: {aligned['tc_status'].isna().sum()}")

    scrape_date_path = out_dir / "techcrunch_scrape_date.txt"
    scrape_date = datetime.now().strftime("%Y-%m-%d")
    scrape_date_path.write_text(scrape_date, encoding="utf-8")
    print(f"Scrape date recorded: {scrape_date}")


if __name__ == "__main__":
    main()
