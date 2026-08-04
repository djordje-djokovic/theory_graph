"""CLI entrypoint: theory-graph init|encode|measure|analyze|compare|status|reproduce|equivalence."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from .config import ExperimentConfig
from .corpora import cases_csv, transcripts_dir
from .paths import ensure_lab_root, lab_root

app = typer.Typer(add_completion=False, no_args_is_help=True, help="theory_graph")


def _resolve_run(run: Path, root: Path) -> Path:
    p = Path(run)
    if not p.is_absolute():
        candidate = root / p
        if candidate.exists():
            return candidate
        candidate = root / "experiments" / p
        if candidate.exists():
            return candidate
    if not p.exists():
        raise typer.BadParameter(f"run not found: {run}")
    return p


@app.command()
def init(
    config: Path = typer.Option(..., "--config", "-c", help="Experiment YAML"),
    lab: Path | None = typer.Option(None, "--lab", help="Lab root (default: auto)"),
):
    """Create a new experiment run folder with snapshots and messages."""
    from .config import ExperimentConfig
    from .encode import init_experiment

    root = ensure_lab_root(lab)
    cfg = ExperimentConfig.load(config)
    run_dir = init_experiment(cfg, root)
    typer.echo(f"initialized {run_dir}")


@app.command()
def encode(
    run: Path = typer.Option(..., "--run", help="Experiment run dir"),
    resume: bool = typer.Option(True, help="Skip cases that already have JSON"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Call the LLM (or instruct for manual backend) for pending encodings."""
    from .encode import encode_run

    root = ensure_lab_root(lab)
    run_dir = _resolve_run(run, root)
    try:
        stats = encode_run(run_dir, resume=resume)
    except RuntimeError as e:
        typer.echo(str(e))
        raise typer.Exit(code=2)
    typer.echo(json.dumps(stats, indent=2))


@app.command()
def measure(
    run: Path = typer.Option(..., "--run"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Validate encodings and write validation/measures.csv."""
    from .measure import measure_run

    root = ensure_lab_root(lab)
    run_dir = _resolve_run(run, root)
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    out = measure_run(
        run_dir,
        transcripts=transcripts_dir(root, cfg.experiment.corpus),
    )
    typer.echo(f"wrote {out}")


@app.command()
def analyze(
    run: Path = typer.Option(..., "--run"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Aggregate IVs, join DV/controls, write logits."""
    from .analyze import analyze_run
    from .config import ExperimentConfig

    root = ensure_lab_root(lab)
    run_dir = _resolve_run(run, root)
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    df = analyze_run(
        run_dir,
        cases_csv(root, cfg.experiment.corpus),
        k_runs=cfg.encoding.k_runs,
    )
    typer.echo(f"analyzed n={len(df)} -> {run_dir / 'aggregated' / 'cases.csv'}")


@app.command()
def status(
    run: Path = typer.Option(..., "--run"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Show pending/done/failed encodings for a run."""
    from .config import ExperimentConfig

    root = ensure_lab_root(lab)
    run_dir = _resolve_run(run, root)
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    import csv

    with (run_dir / "cases.csv").open(encoding="utf-8") as fh:
        cases = list(csv.DictReader(fh))
    done = pending = 0
    for row in cases:
        for r in range(1, cfg.encoding.k_runs + 1):
            p = run_dir / "encodings" / f"run{r}" / f"{row['case_id']}.json"
            if p.exists():
                done += 1
            else:
                pending += 1
    typer.echo(f"done={done} pending={pending} cases={len(cases)} k={cfg.encoding.k_runs}")


@app.command()
def compare(
    runs: list[Path] = typer.Option(..., "--runs", help="Two run dirs"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Compare median breadth / n_domains between two aggregated runs."""
    import pandas as pd

    root = ensure_lab_root(lab)
    if len(runs) != 2:
        raise typer.BadParameter("pass exactly two --runs")
    a = _resolve_run(runs[0], root)
    b = _resolve_run(runs[1], root)
    da = pd.read_csv(a / "aggregated" / "cases.csv")
    db = pd.read_csv(b / "aggregated" / "cases.csv")
    for label, d in (("A", da), ("B", db)):
        typer.echo(
            f"{label}: n={len(d)} breadth_mean={d['breadth'].mean():.3f} "
            f"n_domains_mean={d['n_domains'].mean():.3f}"
        )
    m = da[["case_id", "breadth", "n_domains"]].merge(
        db[["case_id", "breadth", "n_domains"]],
        on="case_id",
        suffixes=("_a", "_b"),
        how="inner",
    )
    if len(m):
        typer.echo(
            f"paired n={len(m)} "
            f"Î”breadth={(m['breadth_b'] - m['breadth_a']).mean():.3f} "
            f"Î”domains={(m['n_domains_b'] - m['n_domains_a']).mean():.3f}"
        )


@app.command()
def reproduce(
    pipeline: str = typer.Option(
        "all",
        "--pipeline",
        help="v1_3_2_nested | v1_5_1_crossed | all",
    ),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Re-aggregate reference corpora and diff vs shipped analysis outputs."""
    from .reproduce import reproduce_all, reproduce_pipeline

    root = ensure_lab_root(lab)
    if pipeline == "all":
        ok = reproduce_all(root)
    else:
        ok = reproduce_pipeline(root, pipeline)
    raise typer.Exit(code=0 if ok else 1)


@app.command()
def equivalence(
    live: bool = typer.Option(False, "--live", help="Optional live LLM re-encode"),
    model: str = typer.Option("openai/gpt-4.1", "--model"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Run offline equivalence battery (and optional live check)."""
    from .equivalence import run_equivalence

    root = ensure_lab_root(lab)
    ok = run_equivalence(root, live=live, model=model)
    raise typer.Exit(code=0 if ok else 1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
