"""Init + encode experiment runs."""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .config import ExperimentConfig
from .corpora import samples_dir, transcripts_dir
from .prompts import load_prompt, messages_for_case


def _slug_model(model: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", model.replace("/", "-"))


def _parse_json_loose(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def load_sample_ids(samples_dir: Path, sample_name: str) -> list[dict]:
    path = samples_dir / f"{sample_name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"sample not found: {path}")
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def init_experiment(cfg: ExperimentConfig, lab_root: Path) -> Path:
    """Create experiments/<ts>_<prompt>_<model>_<sample>/ with snapshots + messages."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_name = (
        f"{ts}_{cfg.experiment.corpus}_{cfg.experiment.prompt_version}_"
        f"{_slug_model(cfg.llm.model)}_{cfg.experiment.sample}"
    )
    run_dir = lab_root / "experiments" / run_name
    if run_dir.exists():
        raise SystemExit(f"run already exists: {run_dir}")

    prompt_text = load_prompt(lab_root / "prompts", cfg.experiment.prompt_version)
    cases = load_sample_ids(samples_dir(lab_root, cfg.experiment.corpus), cfg.experiment.sample)
    tdir = transcripts_dir(lab_root, cfg.experiment.corpus)

    (run_dir / "messages").mkdir(parents=True)
    (run_dir / "raw").mkdir()
    for r in range(1, cfg.encoding.k_runs + 1):
        (run_dir / "encodings" / f"run{r}").mkdir(parents=True)

    cfg.dump(run_dir / "config.snapshot.yaml")
    (run_dir / "prompt.snapshot.md").write_text(prompt_text, encoding="utf-8")

    codebook_version = cfg.experiment.prompt_version.lstrip("v").replace("_", ".")
    # keep known versions pretty
    codebook_version = {
        "1.3.2": "1.3.2",
        "1.5.1": "1.5.1",
        "2.0.0": "2.0.0",
    }.get(codebook_version, codebook_version)

    rows_out = []
    for row in cases:
        case_id = row.get("case_id") or f"pilot-{row['id']}"
        tid = row.get("id") or case_id.removeprefix("pilot-")
        tpath = tdir / f"{case_id}.txt"
        if not tpath.exists():
            tpath = tdir / f"pitch_{tid}.txt"
        if not tpath.exists():
            raise FileNotFoundError(f"transcript missing for {case_id}")
        transcript = tpath.read_text(encoding="utf-8")
        for r in range(1, cfg.encoding.k_runs + 1):
            msgs = messages_for_case(
                codebook_text=prompt_text,
                codebook_version=codebook_version,
                case_id=case_id,
                transcript=transcript,
                model_id=cfg.llm.model,
                extraction_run=r,
            )
            md = (
                f"# messages for {case_id} run{r}\n\n"
                f"## system\n\n{msgs[0]['content']}\n\n"
                f"## user\n\n{msgs[1]['content']}\n"
            )
            (run_dir / "messages" / f"{case_id}_run{r}.md").write_text(md, encoding="utf-8")
        rows_out.append(
            {
                "id": tid,
                "case_id": case_id,
                "GotSelected": row.get("GotSelected", ""),
            }
        )

    with (run_dir / "cases.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "case_id", "GotSelected"])
        w.writeheader()
        w.writerows(rows_out)

    (run_dir / "RUN.md").write_text(
        f"# Run {run_name}\n\n"
        f"- created: {ts}\n"
        f"- corpus: {cfg.experiment.corpus}\n"
        f"- prompt: {cfg.experiment.prompt_version}\n"
        f"- model: {cfg.llm.model}\n"
        f"- sample: {cfg.experiment.sample}\n"
        f"- design: {cfg.experiment.design}\n"
        f"- backend: {cfg.encoding.backend}\n"
        f"- k_runs: {cfg.encoding.k_runs}\n"
        f"- n_cases: {len(rows_out)}\n"
        f"- status: init\n",
        encoding="utf-8",
    )
    return run_dir


def encode_run(run_dir: Path, *, resume: bool = True) -> dict:
    """Call the configured backend for every pending case/run."""
    from dotenv import load_dotenv

    from .backends import LiteLLMBackend, ManualBackend
    from .config import ExperimentConfig

    load_dotenv(run_dir.parents[1] / ".env")  # theory_graph/.env
    load_dotenv()

    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    prompt_text = (run_dir / "prompt.snapshot.md").read_text(encoding="utf-8")
    codebook_version = cfg.experiment.prompt_version.lstrip("v").replace("_", ".")
    codebook_version = {
        "1.3.2": "1.3.2",
        "1.5.1": "1.5.1",
        "2.0.0": "2.0.0",
    }.get(codebook_version, codebook_version)

    if cfg.encoding.backend == "manual":
        ManualBackend().complete([])  # raises with instructions

    backend = LiteLLMBackend()
    with (run_dir / "cases.csv").open(encoding="utf-8") as fh:
        cases = list(csv.DictReader(fh))

    lab_root = run_dir.parents[1]
    tdir = transcripts_dir(lab_root, cfg.experiment.corpus)
    done = failed = skipped = 0

    for row in cases:
        case_id = row["case_id"]
        tid = row["id"]
        tpath = tdir / f"{case_id}.txt"
        if not tpath.exists():
            tpath = tdir / f"pitch_{tid}.txt"
        transcript = tpath.read_text(encoding="utf-8")
        for r in range(1, cfg.encoding.k_runs + 1):
            out_json = run_dir / "encodings" / f"run{r}" / f"{case_id}.json"
            if resume and out_json.exists():
                skipped += 1
                continue
            msgs = messages_for_case(
                codebook_text=prompt_text,
                codebook_version=codebook_version,
                case_id=case_id,
                transcript=transcript,
                model_id=cfg.llm.model,
                extraction_run=r,
            )
            last_err = None
            for attempt in range(cfg.encoding.json_retry + 1):
                try:
                    result = backend.complete(
                        msgs,
                        model=cfg.llm.model,
                        temperature=cfg.llm.temperature,
                        max_tokens=cfg.llm.max_tokens,
                        timeout_s=cfg.llm.timeout_s,
                    )
                    (run_dir / "raw" / f"{case_id}_run{r}.txt").write_text(
                        result.raw, encoding="utf-8"
                    )
                    obj = _parse_json_loose(result.text)
                    meta = obj.setdefault("meta", {})
                    meta.setdefault("case_id", case_id)
                    meta.setdefault("codebook_version", codebook_version)
                    meta.setdefault("pass", "structure")
                    meta["model_id"] = cfg.llm.model
                    meta["model_provider"] = result.provider
                    meta["extraction_run"] = r
                    meta["extracted_at"] = datetime.now(timezone.utc).isoformat()
                    meta["temperature"] = cfg.llm.temperature
                    meta["temperature_controlled"] = True
                    out_json.write_text(
                        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                    done += 1
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
            if last_err is not None:
                failed += 1
                (run_dir / "raw" / f"{case_id}_run{r}.ERROR.txt").write_text(
                    str(last_err), encoding="utf-8"
                )

    status = "done" if failed == 0 else "partial"
    run_md = (run_dir / "RUN.md").read_text(encoding="utf-8")
    run_md = re.sub(r"- status:.*", f"- status: {status}", run_md)
    run_md += f"\n- encode_done: {done}\n- encode_skipped: {skipped}\n- encode_failed: {failed}\n"
    (run_dir / "RUN.md").write_text(run_md, encoding="utf-8")
    return {"done": done, "skipped": skipped, "failed": failed, "status": status}


def run_status(run_dir: Path) -> dict:
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    with (run_dir / "cases.csv").open(encoding="utf-8") as fh:
        cases = list(csv.DictReader(fh))
    pending = done = 0
    for row in cases:
        for r in range(1, cfg.encoding.k_runs + 1):
            p = run_dir / "encodings" / f"run{r}" / f"{row['case_id']}.json"
            if p.exists():
                done += 1
            else:
                pending += 1
    return {
        "cases": len(cases),
        "slots_done": done,
        "slots_pending": pending,
        "k_runs": cfg.encoding.k_runs,
    }
