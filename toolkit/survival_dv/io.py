"""Load source tables for the survival DV pipeline."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import pandas as pd

from .config import PATHS


def load_attractiveness_companies() -> pd.DataFrame:
    df = pd.read_csv(PATHS["attractiveness_companies"])
    df["status"] = df["status"].astype(str).str.lower().str.strip()
    return df


def load_attractiveness_data() -> pd.DataFrame:
    return pd.read_csv(PATHS["attractiveness_data"])


def load_cases() -> pd.DataFrame:
    return pd.read_csv(PATHS["cases"])


def normalize_name(name: Optional[str]) -> Optional[str]:
    """Case-insensitive, punctuation-insensitive name for cross-project matching."""
    if not isinstance(name, str):
        return None
    n = name.lower().strip()
    n = re.sub(r"[^a-z0-9]+", "", n)
    return n or None
