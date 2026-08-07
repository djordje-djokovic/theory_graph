"""Ad hoc reliability report (same output as `theory-graph measure`).

Usage:
    .venv\\Scripts\\python.exe scripts\\compute_reliability.py --run battle_n20_k3_qwen3_32b
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toolkit"))

from theory_graph.config import ExperimentConfig  # noqa: E402
from theory_graph.reliability import write_reliability_report  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Write validation/reliability_report.md for a run.")
    ap.add_argument("--run", required=True, help="Experiment run_id under experiments/")
    ap.add_argument("--threshold", type=float, default=0.35, help="Content-alignment cosine threshold")
    args = ap.parse_args()

    lab_root = Path(__file__).resolve().parents[1]
    run_dir = lab_root / "experiments" / args.run
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    passes = cfg.resolved_passes()
    k_premises = next((p.k_runs for p in passes if p.name == "premises"), cfg.encoding.k_runs)
    k_domains = next((p.k_runs for p in passes if p.name == "domains"), 1)

    with (run_dir / "cases.csv").open(encoding="utf-8") as fh:
        case_ids = [row["case_id"] for row in csv.DictReader(fh)]

    out = write_reliability_report(
        run_dir,
        case_ids,
        k_premises=k_premises,
        k_domains=k_domains,
        content_threshold=args.threshold,
    )
    print(f"Wrote {out}")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
