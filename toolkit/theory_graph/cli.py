"""CLI entrypoint: theory-graph init|encode|measure|analyze|compare|status|smoke|reproduce|equivalence."""
from __future__ import annotations

from pathlib import Path

import typer

from .config import ExperimentConfig
from .corpora import transcripts_dir
from .dataset import dataset_path
from .paths import ensure_lab_root

app = typer.Typer(add_completion=False, no_args_is_help=True, help="theory_graph")


def _parse_passes(raw: list[str] | None) -> list[str] | None:
    if not raw:
        return None
    out: list[str] = []
    for v in raw:
        out.extend(p for p in v.replace(",", " ").split() if p)
    return out or None


def _resolve_run(run: Path, root: Path) -> Path:
    p = Path(run)
    if not p.is_absolute():
        for candidate in (root / p, root / "experiments" / p):
            if candidate.exists():
                return candidate
    if not p.exists():
        raise typer.BadParameter(f"run not found: {run}")
    return p


def _run_label(run_dir: Path, run_arg: str | None = None) -> str:
    return run_arg or run_dir.name


def _friendly_path(path: Path) -> str:
    """Shorter path when it lives under experiments/."""
    parts = path.parts
    if "experiments" in parts:
        i = parts.index("experiments")
        return str(Path(*parts[i:]))
    return str(path)


def _echo_next_step(run_dir: Path, run_arg: str | None = None) -> None:
    from .encode import run_status

    shown = _run_label(run_dir, run_arg)
    try:
        cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
        info = run_status(run_dir)
    except Exception:
        return

    for p in cfg.resolved_passes():
        counts = info["passes"].get(p.name, {})
        if counts.get("pending"):
            typer.echo(f"\nNext step:  theory-graph encode --run {shown} -p {p.name}")
            return
    if not dataset_path(run_dir).exists():
        typer.echo(f"\nNext step:  theory-graph measure --run {shown}")
        return
    if not (run_dir / "analysis" / "results.md").exists():
        typer.echo(f"\nNext step:  theory-graph analyze --run {shown}  (optional — skip if you only need the CSV)")
        return
    typer.echo("\nAll done.")
    typer.echo(f"  Spreadsheet: {_friendly_path(dataset_path(run_dir))}")
    typer.echo(f"  Regressions: {_friendly_path(run_dir / 'analysis' / 'results.md')}")


def _echo_encode_summary(stats: dict) -> None:
    done = stats.get("done", 0)
    skipped = stats.get("skipped", 0)
    failed = stats.get("failed", 0)
    if failed:
        typer.echo(f"Finished with errors: {done} encoded, {skipped} skipped, {failed} failed.")
    elif skipped and not done:
        typer.echo(f"Nothing new to encode ({skipped} already done).")
    elif skipped:
        typer.echo(f"Encoded {done} pitch files ({skipped} were already done).")
    else:
        typer.echo(f"Encoded {done} pitch files.")


@app.command()
def init(
    config: Path = typer.Option(..., "--config", "-c", help="Experiment YAML"),
    lab: Path | None = typer.Option(None, "--lab", help="Lab root (default: auto)"),
):
    """Create experiment folder; freeze config.snapshot.yaml."""
    from .encode import init_experiment

    root = ensure_lab_root(lab)
    cfg = ExperimentConfig.load(config)
    run_dir = init_experiment(cfg, root)
    typer.echo(f"Created experiment folder: {_friendly_path(run_dir)}")
    typer.echo(f"Settings saved to:      {_friendly_path(run_dir / 'config.snapshot.yaml')}")
    typer.echo("(Later commands use the saved settings in that folder, not your original YAML file.)")
    _echo_next_step(run_dir)


@app.command()
def encode(
    run: Path = typer.Option(..., "--run", help="Experiment run dir"),
    passes: list[str] | None = typer.Option(
        None, "--pass", "-p", help="Pass names: -p premises,dfv,domains",
    ),
    all_passes: bool = typer.Option(False, "--all", help="Encode all declared passes."),
    force: bool = typer.Option(False, "--force", help="Redo passes; clears downstream."),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Call the AI; write encodings/<pass>/run{k}/*.json."""
    from .encode import encode_run

    root = ensure_lab_root(lab)
    run_dir = _resolve_run(run, root)
    try:
        stats = encode_run(
            run_dir,
            resume=not force,
            force=force,
            encode_all=all_passes,
            only_passes=_parse_passes(passes),
        )
    except RuntimeError as e:
        typer.echo(str(e))
        raise typer.Exit(code=2)
    _echo_encode_summary(stats)
    _echo_next_step(run_dir, str(run))


@app.command()
def measure(
    run: Path = typer.Option(..., "--run"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Validate JSON + build aggregated/dataset.csv (full analysis spreadsheet)."""
    from .measure import measure_run

    root = ensure_lab_root(lab)
    run_dir = _resolve_run(run, root)
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    out = measure_run(run_dir, transcripts=transcripts_dir(root, cfg.experiment.corpus))
    typer.echo(f"Built analysis spreadsheet: {_friendly_path(out)}")
    typer.echo(f"Validation details:       {_friendly_path(run_dir / 'validation' / 'measures.csv')}")
    _echo_next_step(run_dir, str(run))


@app.command()
def analyze(
    run: Path = typer.Option(..., "--run"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Run regressions from config snapshot → analysis/results.md."""
    from .analyze import analyze_run

    root = ensure_lab_root(lab)
    run_dir = _resolve_run(run, root)
    df = analyze_run(run_dir)
    typer.echo(f"Ran regressions for {len(df)} pitches.")
    typer.echo(f"Results: {_friendly_path(run_dir / 'analysis' / 'results.md')}")
    _echo_next_step(run_dir, str(run))


@app.command()
def status(
    run: Path = typer.Option(..., "--run"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Show encode progress (done / pending per pass)."""
    from .encode import run_status

    root = ensure_lab_root(lab)
    run_dir = _resolve_run(run, root)
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    info = run_status(run_dir)
    n_cases = info["cases"]
    for p in cfg.resolved_passes():
        counts = info["passes"][p.name]
        done = counts["done"]
        pending = counts["pending"]
        total = done + pending
        if total == 0:
            typer.echo(f"{p.name}: not started ({n_cases} pitches × {p.k_runs} runs each)")
        elif pending == 0:
            typer.echo(f"{p.name}: complete ({done}/{total} files)")
        else:
            typer.echo(f"{p.name}: {done}/{total} done ({pending} still missing)")
    if dataset_path(run_dir).exists():
        typer.echo(f"Spreadsheet ready: {_friendly_path(dataset_path(run_dir))}")
    _echo_next_step(run_dir, str(run))


@app.command()
def compare(
    runs: list[Path] = typer.Option(..., "--runs", help="Two run dirs"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Compare breadth / n_domains between two runs."""
    import pandas as pd

    def _load_cases(run_dir: Path) -> pd.DataFrame:
        p = dataset_path(run_dir)
        if not p.exists():
            p = run_dir / "aggregated" / "cases.csv"
        return pd.read_csv(p)

    root = ensure_lab_root(lab)
    if len(runs) != 2:
        raise typer.BadParameter("pass exactly two --runs")
    a = _resolve_run(runs[0], root)
    b = _resolve_run(runs[1], root)
    da, db = _load_cases(a), _load_cases(b)
    for label, d, run_dir in (("Run A", da, a), ("Run B", db, b)):
        typer.echo(
            f"{label} ({_run_label(run_dir)}): {len(d)} pitches, "
            f"avg breadth {d['breadth'].mean():.2f}, avg domains {d['n_domains'].mean():.2f}"
        )
    m = da[["case_id", "breadth", "n_domains"]].merge(
        db[["case_id", "breadth", "n_domains"]], on="case_id", suffixes=("_a", "_b"), how="inner",
    )
    if len(m):
        typer.echo(
            f"Same pitches in both runs: {len(m)} — "
            f"avg breadth change {((m['breadth_b'] - m['breadth_a']).mean()):+.2f}, "
            f"avg domains change {((m['n_domains_b'] - m['n_domains_a']).mean()):+.2f}"
        )


@app.command()
def smoke(
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Synthetic v2.1 pipeline smoke test (no API key)."""
    from .smoke import run_smoke

    root = ensure_lab_root(lab)
    ok = run_smoke(root)
    raise typer.Exit(code=0 if ok else 1)


@app.command()
def reproduce(
    pipeline: str = typer.Option("all", "--pipeline"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Re-aggregate reference corpora and diff vs shipped outputs."""
    from .reproduce import reproduce_all, reproduce_pipeline

    root = ensure_lab_root(lab)
    ok = reproduce_all(root) if pipeline == "all" else reproduce_pipeline(root, pipeline)
    raise typer.Exit(code=0 if ok else 1)


@app.command()
def equivalence(
    live: bool = typer.Option(False, "--live"),
    model: str = typer.Option("openai/gpt-4.1", "--model"),
    lab: Path | None = typer.Option(None, "--lab"),
):
    """Offline equivalence battery (optional live check)."""
    from .equivalence import run_equivalence

    root = ensure_lab_root(lab)
    ok = run_equivalence(root, live=live, model=model)
    raise typer.Exit(code=0 if ok else 1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
