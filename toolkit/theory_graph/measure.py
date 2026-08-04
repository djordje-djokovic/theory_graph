"""Validate all encodings in an experiment run → validation/measures.csv."""
from __future__ import annotations

import csv
from pathlib import Path

from .config import ExperimentConfig
from .validate import FIELDS, load_transcript, measures, validate


def measure_run(run_dir: Path, transcripts: Path | None = None) -> Path:
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    rows = []
    for r in range(1, cfg.encoding.k_runs + 1):
        enc = run_dir / "encodings" / f"run{r}"
        if not enc.exists():
            continue
        for path in sorted(enc.glob("*.json")):
            import json

            case = json.loads(path.read_text(encoding="utf-8"))
            case_id = case.get("meta", {}).get("case_id") or path.stem
            transcript = load_transcript(transcripts, case_id) if transcripts else None
            errors = validate(case, transcript)
            row = {
                "case_id": case_id,
                "run": r,
                "valid": not errors,
                "n_errors": len(errors),
                "errors": "; ".join(errors),
                "spans_checked": transcript is not None,
            }
            row.update(measures(case))
            rows.append(row)

    out_dir = run_dir / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "measures.csv"
    fields = ["case_id", "run", "valid", "n_errors", "errors", "spans_checked"] + [
        f for f in FIELDS if f not in {"case_id", "valid", "n_errors", "errors", "spans_checked"}
    ]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return out
