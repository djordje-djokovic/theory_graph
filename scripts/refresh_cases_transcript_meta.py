"""Refresh cases.csv transcript-derived fields from PITCH corpus files."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "toolkit") not in sys.path:
    sys.path.insert(0, str(ROOT / "toolkit"))

from theory_graph.validate import (  # noqa: E402
    load_transcript,
    transcript_incomplete,
    transcript_opening_truncated,
    transcript_template_leak,
    transcript_truncated,
)

CASES = ROOT / "data/corpora/startup_battlefield/cases.csv"
TRANSCRIPTS = ROOT / "data/corpora/startup_battlefield/transcripts"
OUT = ROOT / "data/corpora/startup_battlefield/analysis/cases_transcript_refresh.csv"


def main() -> int:
    cases = pd.read_csv(CASES, dtype={"id": str, "case_id": str})
    changes = []

    for i, row in cases.iterrows():
        case_id = row["case_id"]
        old_wc = row.get("word_count")
        old_trunc = row.get("truncated")
        text = load_transcript(TRANSCRIPTS, case_id)

        if text is None:
            new_wc = None
            new_trunc = 1
            trailing = opening = template = incomplete = None
        else:
            words = text.split()
            new_wc = len(words)
            trailing = bool(transcript_truncated(text))
            opening = bool(transcript_opening_truncated(text))
            template = bool(transcript_template_leak(text))
            incomplete = bool(transcript_incomplete(text))
            new_trunc = int(incomplete)

        cases.at[i, "word_count"] = new_wc if new_wc is not None else old_wc
        cases.at[i, "truncated"] = new_trunc

        try:
            old_wc_i = int(float(old_wc)) if pd.notna(old_wc) else None
        except (TypeError, ValueError):
            old_wc_i = None
        try:
            old_trunc_i = int(float(old_trunc)) if pd.notna(old_trunc) else None
        except (TypeError, ValueError):
            old_trunc_i = None

        if old_wc_i != new_wc or old_trunc_i != new_trunc:
            changes.append(
                {
                    "case_id": case_id,
                    "name": row.get("name"),
                    "excluded": row.get("excluded", 0),
                    "old_word_count": old_wc_i,
                    "new_word_count": new_wc,
                    "delta_words": (new_wc or 0) - (old_wc_i or 0),
                    "old_truncated": old_trunc_i,
                    "new_truncated": new_trunc,
                    "trailing_cut": trailing,
                    "opening_cut": opening,
                    "template_leak": template,
                }
            )

    cases["word_count"] = cases["word_count"].astype("Int64")
    cases["truncated"] = cases["truncated"].astype(int)
    cases.to_csv(CASES, index=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    ch = pd.DataFrame(changes).sort_values(
        "delta_words", key=lambda s: s.abs(), ascending=False
    )
    ch.to_csv(OUT, index=False)

    study = cases[cases.get("excluded", 0) != 1]
    print(f"Updated {CASES}")
    print(f"Changed rows: {len(changes)} / {len(cases)}")
    print(f"Audit: {OUT}")
    print(f"\nAnalysis set (n={len(study)}):")
    print(f"  word_count median: {study.word_count.median():.0f}")
    print(f"  truncated=1: {int(study.truncated.sum())} ({100*study.truncated.mean():.1f}%)")
    print(f"  word_count <400: {int((study.word_count < 400).sum())}")

    big = ch[ch["delta_words"].abs() >= 100].head(15)
    if len(big):
        print("\nLargest word_count changes:")
        print(
            big[
                [
                    "case_id",
                    "name",
                    "old_word_count",
                    "new_word_count",
                    "delta_words",
                    "old_truncated",
                    "new_truncated",
                ]
            ].to_string(index=False)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
