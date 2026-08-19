"""Paths and constants for the survival DV pipeline."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ATTRACTIVENESS = Path("C:/Projects/uni/sources/attractiveness")

PATHS = {
    "attractiveness_companies": ATTRACTIVENESS / "startup_battlefield" / "startup_battlefield_companies.csv",
    "attractiveness_data": ATTRACTIVENESS / "startup_battlefield" / "startup_battlefield_data.csv",
    "cases": ROOT / "data" / "corpora" / "startup_battlefield" / "cases.csv",
    "out_dir": ROOT / "data" / "corpora" / "startup_battlefield" / "survival_dv",
    "survival_dv": ROOT / "data" / "corpora" / "startup_battlefield" / "survival_dv" / "survival_dv.csv",
    "survival_panel": ROOT / "data" / "corpora" / "startup_battlefield" / "survival_dv" / "survival_panel.csv",
    "diagnostics": ROOT / "data" / "corpora" / "startup_battlefield" / "survival_dv" / "diagnostics",
    "event_dates": ROOT / "data" / "corpora" / "startup_battlefield" / "survival_dv" / "diagnostics" / "event_dates.csv",
}

CB_DB = "postgresql://postgres:password@localhost:5433/uni"


def _analysis_end_date() -> str:
    """Use the TechCrunch scrape date if available, otherwise fall back to the old placeholder."""
    scrape_date_file = PATHS["diagnostics"] / "techcrunch_scrape_date.txt"
    if scrape_date_file.exists():
        return scrape_date_file.read_text(encoding="utf-8").strip()
    return "2024-03-31"  # placeholder when no fresh scrape has been run


def _cb_dump_date() -> str:
    """Vintage of the Crunchbase dump.

    Survival status comes from TechCrunch and the Wayback Machine, which are current,
    but every funding round comes from Crunchbase, so funding exposure cannot extend
    past the dump. Using the survival end date for funding would silently record
    years of "no funding" that were never observed.
    """
    dump_date_file = PATHS["diagnostics"] / "crunchbase_dump_date.txt"
    if dump_date_file.exists():
        return dump_date_file.read_text(encoding="utf-8").strip()
    # max(announced_on) in crunchbase.funding_rounds for the loaded dump
    return "2024-04-10"


# Survival censoring: TechCrunch status and the Wayback scan are the governing evidence
ANALYSIS_END_DATE = _analysis_end_date()

# Funding censoring: bounded by the Crunchbase vintage, which is older
CB_DUMP_DATE = _cb_dump_date()
