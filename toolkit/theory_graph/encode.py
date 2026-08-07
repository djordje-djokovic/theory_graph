"""Init + encode experiment runs."""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import environment
from .config import ExperimentConfig, PassBlock, downstream_passes, standard_pass
from .corpora import samples_dir, transcripts_dir
from .prompts import load_prompt, messages_for_case, snapshot_prompts


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


_PASS_SUFFIXES = ("_premises", "_dfv", "_domains")


def _codebook_version(prompt_version: str) -> str:
    """Codebook version recorded in `meta`, e.g. v2_1_1_premises -> 2.1.1.

    The pass suffix names which file of a multi-pass codebook was used, not a
    separate codebook, so it is stripped before the version is recorded.
    """
    single_pass = {"v1_3_2": "1.3.2", "v1_5_1": "1.5.1", "v2_0_0": "2.0.0"}
    if prompt_version in single_pass:
        return single_pass[prompt_version]
    stem = prompt_version
    for suffix in _PASS_SUFFIXES:
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem.removeprefix("v").replace("_", ".")


def _transcript_path(tdir: Path, case_id: str, tid: str | None = None) -> Path:
    p = tdir / f"{case_id}.txt"
    if p.exists():
        return p
    p = tdir / f"pitch_{tid or case_id.removeprefix('pilot-')}.txt"
    if not p.exists():
        raise FileNotFoundError(f"transcript missing for {case_id}")
    return p


def _consensus_premises(run_dir: Path, case_id: str, k: int) -> dict | None:
    candidates = []
    for r in range(1, k + 1):
        p = run_dir / "encodings" / "premises" / f"run{r}" / f"{case_id}.json"
        if p.exists():
            candidates.append(json.loads(p.read_text(encoding="utf-8")))
    if not candidates:
        return None
    breadths = sorted(len(c.get("premises") or []) for c in candidates)
    median_b = breadths[len(breadths) // 2]
    return min(candidates, key=lambda c: abs(len(c.get("premises") or []) - median_b))


def _ensure_dirs(run_dir: Path, passes: list[PassBlock]) -> None:
    for p in passes:
        for r in range(1, p.k_runs + 1):
            (run_dir / "encodings" / p.name / f"run{r}").mkdir(parents=True, exist_ok=True)


def _write_messages(
    run_dir: Path, lab_root: Path, cfg: ExperimentConfig,
    passes: list[PassBlock], cases: list[dict], tdir: Path,
) -> None:
    prompts_root = lab_root / "prompts"
    snapshot_dir = run_dir / "prompts"
    snapshot_prompts(prompts_root, [p.prompt_version for p in passes], snapshot_dir)
    for row in cases:
        case_id = row["case_id"]
        transcript = _transcript_path(tdir, case_id, row.get("id")).read_text(encoding="utf-8")
        for p in passes:
            prompt_text = load_prompt(prompts_root, p.prompt_version, snapshot_dir)
            cbv = _codebook_version(p.prompt_version)
            for r in range(1, p.k_runs + 1):
                msgs = messages_for_case(
                    codebook_text=prompt_text, codebook_version=cbv, case_id=case_id,
                    transcript=transcript, model_id=cfg.llm.model, extraction_run=r,
                )
                md = f"# {case_id} {p.name} run{r}\n\n## system\n\n{msgs[0]['content']}\n\n## user\n\n{msgs[1]['content']}\n"
                (run_dir / "messages" / f"{case_id}_{p.name}_run{r}.md").write_text(md, encoding="utf-8")


def _register_passes(run_dir: Path, names: list[str], lab_root: Path, default_k: int) -> None:
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    existing = {p.name for p in cfg.resolved_passes()}
    to_add = []
    for name in names:
        if name in existing:
            continue
        spec = standard_pass(name, default_k_runs=default_k)
        if spec.requires and spec.requires not in existing:
            raise RuntimeError(f"pass {name!r} requires {spec.requires!r}, which is not in this run")
        to_add.append(spec)
    if not to_add:
        return
    cfg.passes = list(cfg.passes or cfg.resolved_passes()) + to_add
    cfg.dump(run_dir / "config.snapshot.yaml")
    tdir = transcripts_dir(lab_root, cfg.experiment.corpus)
    with (run_dir / "cases.csv").open(encoding="utf-8") as fh:
        cases = list(csv.DictReader(fh))
    _ensure_dirs(run_dir, to_add)
    _write_messages(run_dir, lab_root, cfg, to_add, cases, tdir)


def init_experiment(cfg: ExperimentConfig, lab_root: Path) -> Path:
    run_name = (cfg.experiment.run_id or cfg.experiment.prompt_version).strip()
    if not run_name or "/" in run_name or "\\" in run_name or ".." in run_name:
        raise SystemExit(f"invalid experiment.run_id: {run_name!r}")
    run_dir = lab_root / "experiments" / run_name
    if run_dir.exists():
        raise SystemExit(f"run already exists: {run_dir}")

    sample_path = samples_dir(lab_root, cfg.experiment.corpus) / f"{cfg.experiment.sample}.csv"
    if not sample_path.exists():
        raise FileNotFoundError(f"sample not found: {sample_path}")
    tdir = transcripts_dir(lab_root, cfg.experiment.corpus)
    passes = cfg.resolved_passes()

    (run_dir / "messages").mkdir(parents=True)
    (run_dir / "raw").mkdir()
    _ensure_dirs(run_dir, passes)
    cfg.dump(run_dir / "config.snapshot.yaml")

    cases = []
    with sample_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            case_id = row.get("case_id") or f"pilot-{row['id']}"
            _transcript_path(tdir, case_id, row.get("id"))
            cases.append({
                "id": row.get("id") or case_id.removeprefix("pilot-"),
                "case_id": case_id,
                "GotSelected": row.get("GotSelected", ""),
            })

    _write_messages(run_dir, lab_root, cfg, passes, cases, tdir)
    with (run_dir / "cases.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "case_id", "GotSelected"])
        w.writeheader()
        w.writerows(cases)
    return run_dir


def encode_run(
    run_dir: Path,
    *,
    resume: bool = True,
    force: bool = False,
    encode_all: bool = False,
    only_passes: list[str] | None = None,
) -> dict:
    from dotenv import load_dotenv
    from .backends import LiteLLMBackend

    load_dotenv(run_dir.parents[1] / ".env")
    load_dotenv()

    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    lab_root = run_dir.parents[1]
    tdir = transcripts_dir(lab_root, cfg.experiment.corpus)

    selected = None if encode_all else (only_passes if only_passes is not None else cfg.encoding.run_passes)
    if selected:
        _register_passes(run_dir, list(selected), lab_root, cfg.encoding.k_runs)
        cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")

    all_passes = cfg.resolved_passes()
    pass_by_name = {p.name: p for p in all_passes}
    passes = all_passes if selected is None else [p for p in all_passes if p.name in selected]
    selected_names = {p.name for p in passes}

    if force:
        to_clear = selected_names | {p.name for p in downstream_passes(all_passes, selected_names)}
        for name in to_clear:
            enc = run_dir / "encodings" / name
            if enc.exists():
                for path in enc.rglob("*.json"):
                    path.unlink()

    for p in passes:
        if p.requires and p.requires not in selected_names:
            up = run_dir / "encodings" / p.requires
            if not up.exists() or not any(up.rglob("*.json")):
                raise RuntimeError(
                    f"cannot encode {p.name!r}: run premises first: "
                    f"theory-graph encode --run {run_dir.name} -p {p.requires}"
                )

    if cfg.encoding.backend == "manual":
        return {"done": 0, "skipped": 0, "failed": 0, "status": "done"}

    backend = LiteLLMBackend()
    prompts_root = lab_root / "prompts"
    snapshot_dir = run_dir / "prompts"

    env = environment.capture(
        model=cfg.llm.model,
        temperature=cfg.llm.temperature,
        max_tokens=cfg.llm.max_tokens,
        num_ctx=cfg.llm.num_ctx,
        backend=cfg.encoding.backend,
    )
    environment.record(run_dir, env)
    env_stamp = environment.provenance_stamp(env)

    with (run_dir / "cases.csv").open(encoding="utf-8") as fh:
        cases = list(csv.DictReader(fh))

    done = failed = skipped = 0
    for row in cases:
        case_id = row["case_id"]
        transcript = _transcript_path(tdir, case_id, row["id"]).read_text(encoding="utf-8")

        for p in passes:
            prompt_text = load_prompt(prompts_root, p.prompt_version, snapshot_dir)
            cbv = _codebook_version(p.prompt_version)
            for r in range(1, p.k_runs + 1):
                out_json = run_dir / "encodings" / p.name / f"run{r}" / f"{case_id}.json"
                if resume and out_json.exists():
                    skipped += 1
                    continue

                frozen = None
                if p.requires:
                    upstream = _consensus_premises(run_dir, case_id, pass_by_name[p.requires].k_runs)
                    if upstream is None:
                        failed += 1
                        continue
                    frozen = "\n".join(f"- {x['id']}: {x.get('text', '')}" for x in upstream.get("premises") or [])

                msgs = messages_for_case(
                    codebook_text=prompt_text, codebook_version=cbv, case_id=case_id,
                    transcript=transcript, model_id=cfg.llm.model, extraction_run=r,
                    frozen_premises=frozen,
                )

                for attempt in range(cfg.encoding.json_retry + 1):
                    try:
                        result = backend.complete(
                            msgs, model=cfg.llm.model, temperature=cfg.llm.temperature,
                            max_tokens=cfg.llm.max_tokens, timeout_s=cfg.llm.timeout_s,
                            num_ctx=cfg.llm.num_ctx,
                        )
                        (run_dir / "raw" / f"{case_id}_{p.name}_run{r}.txt").write_text(result.raw, encoding="utf-8")
                        obj = _parse_json(result.text)
                        meta = obj.setdefault("meta", {})
                        meta["case_id"] = case_id
                        meta["codebook_version"] = cbv
                        meta["pass"] = p.name
                        meta["model_id"] = cfg.llm.model
                        meta["model_provider"] = result.provider
                        meta["extraction_run"] = r
                        meta["extracted_at"] = datetime.now(timezone.utc).isoformat()
                        # Sampling was pinned by this harness, so record it here
                        # rather than accepting the model's account of it.
                        meta["temperature"] = cfg.llm.temperature
                        meta["temperature_controlled"] = cfg.llm.temperature is not None
                        if env_stamp:
                            meta["environment"] = env_stamp
                        out_json.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                        done += 1
                        break
                    except Exception:
                        if attempt == cfg.encoding.json_retry:
                            failed += 1

    return {"done": done, "skipped": skipped, "failed": failed, "status": "done" if failed == 0 else "partial"}


def run_status(run_dir: Path) -> dict:
    cfg = ExperimentConfig.load(run_dir / "config.snapshot.yaml")
    with (run_dir / "cases.csv").open(encoding="utf-8") as fh:
        cases = list(csv.DictReader(fh))
    per_pass = {}
    for p in cfg.resolved_passes():
        done = pending = 0
        for row in cases:
            for r in range(1, p.k_runs + 1):
                if (run_dir / "encodings" / p.name / f"run{r}" / f"{row['case_id']}.json").exists():
                    done += 1
                else:
                    pending += 1
        per_pass[p.name] = {"done": done, "pending": pending}
    return {"cases": len(cases), "passes": per_pass}
