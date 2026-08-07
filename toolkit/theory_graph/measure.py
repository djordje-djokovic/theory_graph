"""Validate encodings and build aggregated/dataset.csv."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .config import ExperimentConfig
from .dataset import build_dataset, write_dataset
from .validate import FIELDS, load_transcript, measures, validate


def measure_run(run_dir: Path, transcripts: Path | None = None) -> Path:
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    enc_root = run_dir / "encodings"
    rows = []

    pass_names = [
        d.name for d in enc_root.iterdir()
        if d.is_dir() and not d.name.startswith("run")
    ] if enc_root.exists() else []

    if pass_names:
        for p in cfg.resolved_passes():
            for r in range(1, p.k_runs + 1):
                enc_dir = enc_root / p.name / f"run{r}"
                for path in sorted(enc_dir.glob("*.json")) if enc_dir.exists() else []:
                    rows.append(_measure_file(path, p.name, r, transcripts))
    else:
        for r in range(1, cfg.encoding.k_runs + 1):
            enc_dir = enc_root / f"run{r}"
            for path in sorted(enc_dir.glob("*.json")) if enc_dir.exists() else []:
                case = json.loads(path.read_text(encoding="utf-8"))
                rows.append(_measure_file(
                    path, case.get("meta", {}).get("pass", "structure"), r, transcripts,
                ))

    val_dir = run_dir / "validation"
    val_dir.mkdir(parents=True, exist_ok=True)
    measures_csv = val_dir / "measures.csv"
    fields = ["case_id", "pass", "run", "valid", "n_errors", "errors", "spans_checked"] + [
        f for f in FIELDS if f not in {"case_id", "valid", "n_errors", "errors", "spans_checked"}
    ]
    with measures_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    from .corpora import cases_csv

    lab_root = run_dir.parents[1]
    study_csv = cases_csv(lab_root, cfg.experiment.corpus)
    df = build_dataset(
        run_dir,
        cfg,
        study_csv,
        k_runs=cfg.encoding.k_runs,
        transcripts=transcripts,
        measures_csv=measures_csv,
    )
    out = write_dataset(df, run_dir)

    with (run_dir / "cases.csv").open(encoding="utf-8") as fh:
        case_ids = [row["case_id"] for row in csv.DictReader(fh)]
    passes = cfg.resolved_passes()
    k_premises = next((p.k_runs for p in passes if p.name == "premises"), cfg.encoding.k_runs)
    k_domains = next((p.k_runs for p in passes if p.name == "domains"), 1)
    from .reliability import write_reliability_report

    write_reliability_report(
        run_dir,
        case_ids,
        k_premises=k_premises,
        k_domains=k_domains,
        measures_csv=measures_csv,
    )
    return out


def _measure_file(path: Path, pass_name: str, run: int, transcripts: Path | None) -> dict:
    case = json.loads(path.read_text(encoding="utf-8"))
    case_id = case.get("meta", {}).get("case_id") or path.stem
    transcript = load_transcript(transcripts, case_id) if transcripts else None
    errors = validate(case, transcript)
    row = {
        "case_id": case_id,
        "pass": pass_name,
        "run": run,
        "valid": not errors,
        "n_errors": len(errors),
        "errors": "; ".join(errors),
        "spans_checked": transcript is not None,
    }
    row.update(measures(case))
    return row
