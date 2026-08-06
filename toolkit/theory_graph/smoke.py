"""Synthetic v2.1 pipeline smoke test (no API key).

Coverage matrix (see run_smoke steps):
  init | measure | analyze | status | compare
  staged encode: premises → dfv → domains (separate -p calls)
  force: premises (clears all) | dfv (dfv only) | domains (domains only)
  join: dataset.csv columns from all passes + corpus + similarities
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from .analyze import analyze_run
from .config import ExperimentConfig
from .corpora import transcripts_dir
from .dataset import dataset_path
from .encode import encode_run, init_experiment, run_status
from .measure import measure_run

RUN_ID = "_synthetic_smoke"
RUN_ID_B = "_synthetic_smoke_b"
RUN_ID_GUARD = "_synthetic_guard"
RUN_ID_GUARD2 = "_synthetic_guard2"
FIXTURE_CONFIG = Path("tests/fixtures/synthetic_v2_1/config_premises.yaml")
GUARD_CONFIG = Path("tests/fixtures/synthetic_v2_1/config_guard.yaml")

SYNTHETIC_CASES = [
    {
        "case_id": "pilot-1",
        "id": "1",
        "GotSelected": "0",
        "premises": [
            {
                "id": "P1",
                "text": "The blood testing market is large and fragmented",
                "status": "explicit",
                "evidence_span": "The blood testing market is huge",
            },
            {
                "id": "P2",
                "text": "Testing works without a dedicated analyzer device",
                "status": "explicit",
                "evidence_span": "eliminating the analyzer altogether",
            },
            {
                "id": "P3",
                "text": "A phone dongle runs the test from a drop of blood",
                "status": "explicit",
                "evidence_span": "hooks up to your phone with a dongle",
            },
            {
                "id": "P4",
                "text": "The first market is emergency veterinary care",
                "status": "explicit",
                "evidence_span": "launching this into the veterinary space",
            },
        ],
        "run3_extra": [
            {
                "id": "P5",
                "text": "Validation shows strong assay accuracy",
                "status": "explicit",
                "evidence_span": "achieved an R-squared of 0.97",
            },
        ],
        "dfv": {
            "P1": "DESIRABILITY",
            "P2": "FEASIBILITY",
            "P3": "FEASIBILITY",
            "P4": "VIABILITY",
        },
        "domains": [
            {"id": "D1", "name": "market problem", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "product and launch", "premise_ids": ["P3", "P4"]},
        ],
    },
    {
        "case_id": "pilot-880",
        "id": "880",
        "GotSelected": "1",
        "premises": [
            {
                "id": "P1",
                "text": "In-car technology feels outdated quickly",
                "status": "explicit",
                "evidence_span": "outdated the technology in your car",
            },
            {
                "id": "P2",
                "text": "Almost any post-1996 car can be connected",
                "status": "explicit",
                "evidence_span": "car manufactured after 1996",
            },
            {
                "id": "P3",
                "text": "Developers get a simple API to the car",
                "status": "explicit",
                "evidence_span": "simplified the complicated car into a simple API call",
            },
        ],
        "dfv": {
            "P1": "DESIRABILITY",
            "P2": "FEASIBILITY",
            "P3": "VIABILITY",
        },
        "domains": [
            {"id": "D1", "name": "consumer problem", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "platform", "premise_ids": ["P3"]},
        ],
    },
    {
        "case_id": "pilot-701",
        "id": "701",
        "GotSelected": "1",
        "premises": [
            {
                "id": "P1",
                "text": "Healthcare can be rebuilt as a connected system",
                "status": "explicit",
                "evidence_span": "building a healthcare system from scratch",
            },
            {
                "id": "P2",
                "text": "Technology replaces much hospital administration",
                "status": "explicit",
                "evidence_span": "replace most of these things with technology",
            },
            {
                "id": "P3",
                "text": "Care combines virtual and in-clinic visits",
                "status": "explicit",
                "evidence_span": "seamless hybrid of virtual and in-person care",
            },
            {
                "id": "P4",
                "text": "A San Francisco clinic pilots the model",
                "status": "explicit",
                "evidence_span": "opening Carbon in our pilot primary care clinic",
            },
        ],
        "dfv": {
            "P1": "DESIRABILITY",
            "P2": "FEASIBILITY",
            "P3": "FEASIBILITY",
            "P4": "VIABILITY",
        },
        "domains": [
            {"id": "D1", "name": "system thesis", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "care delivery", "premise_ids": ["P3", "P4"]},
        ],
    },
]


def _meta(case_id: str, pass_name: str, run: int) -> dict:
    return {
        "codebook_version": "2.1.0",
        "pass": pass_name,
        "unit": "pitch_transcript",
        "case_id": case_id,
        "model_id": "synthetic/fixture",
        "model_provider": "smoke-test",
        "temperature": 0.0,
        "temperature_controlled": True,
        "extraction_run": run,
        "extracted_at": "2026-08-06T12:00:00Z",
    }


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _premises_for_run(case: dict, run: int) -> list[dict]:
    premises = [dict(p) for p in case["premises"]]
    if run == 3 and case.get("run3_extra"):
        premises.extend(dict(p) for p in case["run3_extra"])
    return premises


def install_encodings(
    run_dir: Path,
    *,
    premises: bool = False,
    dfv: bool = False,
    domains: bool = False,
) -> None:
    for case in SYNTHETIC_CASES:
        cid = case["case_id"]
        if premises:
            for r in (1, 2, 3):
                obj = {
                    "meta": _meta(cid, "premises", r),
                    "premises": _premises_for_run(case, r),
                    "notes": "synthetic smoke fixture",
                }
                _write_json(run_dir / "encodings" / "premises" / f"run{r}" / f"{cid}.json", obj)
        if dfv:
            pids = [p["id"] for p in _premises_for_run(case, 1)]
            obj = {
                "meta": _meta(cid, "dfv", 1),
                "assignments": [
                    {"premise_id": pid, "tag": case["dfv"][pid]} for pid in pids if pid in case["dfv"]
                ],
                "notes": "synthetic smoke fixture",
            }
            _write_json(run_dir / "encodings" / "dfv" / "run1" / f"{cid}.json", obj)
        if domains:
            obj = {
                "meta": _meta(cid, "domains", 1),
                "domains": case["domains"],
                "notes": "synthetic smoke fixture",
            }
            _write_json(run_dir / "encodings" / "domains" / "run1" / f"{cid}.json", obj)


def _assert(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def _read_dataset(run_dir: Path) -> pd.DataFrame:
    path = dataset_path(run_dir)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, dtype={"id": str, "case_id": str})


def _encoding_count(run_dir: Path, pass_name: str) -> int:
    enc = run_dir / "encodings" / pass_name
    if not enc.exists():
        return 0
    return len(list(enc.rglob("*.json")))


def _measure(run_dir: Path, lab_root: Path, corpus: str) -> pd.DataFrame:
    measure_run(run_dir, transcripts=transcripts_dir(lab_root, corpus))
    return _read_dataset(run_dir)


def _compare_datasets(run_a: Path, run_b: Path) -> tuple[int, float, float]:
    """Return (n_matched, avg_breadth_delta, avg_domains_delta) like the compare CLI."""
    da = _read_dataset(run_a)
    db = _read_dataset(run_b)
    m = da[["case_id", "breadth", "n_domains"]].merge(
        db[["case_id", "breadth", "n_domains"]], on="case_id", suffixes=("_a", "_b"), how="inner",
    )
    if m.empty:
        return 0, float("nan"), float("nan")
    bd = (m["breadth_b"] - m["breadth_a"]).mean()
    dd = (m["n_domains_b"] - m["n_domains_a"]).mean()
    return len(m), float(bd), float(dd)


def _cleanup_runs(lab_root: Path, *run_ids: str) -> None:
    for rid in run_ids:
        p = lab_root / "experiments" / rid
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)


def _run_guard_tests(lab_root: Path, corpus: str, errors: list[str], lines: list[str]) -> None:
    guard_cfg = ExperimentConfig.load(lab_root / GUARD_CONFIG)
    guard_dir = lab_root / "experiments" / RUN_ID_GUARD

    init_experiment(guard_cfg, lab_root)
    try:
        init_experiment(guard_cfg, lab_root)
        _assert(False, "duplicate init should raise SystemExit", errors)
    except SystemExit:
        pass

    try:
        measure_run(guard_dir, transcripts=transcripts_dir(lab_root, corpus))
        _assert(False, "measure with no encodings should fail", errors)
    except KeyError:
        pass

    install_encodings(guard_dir, premises=True)
    encode_run(guard_dir, only_passes=None, encode_all=False)
    names = {p.name for p in ExperimentConfig.load(guard_dir / "config.snapshot.yaml").resolved_passes()}
    _assert(names == {"premises"}, f"default encode registered extra passes: {names}", errors)

    guard2_cfg = guard_cfg.model_copy(deep=True)
    guard2_cfg.experiment.run_id = RUN_ID_GUARD2
    init_experiment(guard2_cfg, lab_root)
    guard2_dir = lab_root / "experiments" / RUN_ID_GUARD2
    try:
        encode_run(guard2_dir, only_passes=["dfv"])
        _assert(False, "encode dfv before premises should raise RuntimeError", errors)
    except RuntimeError as e:
        _assert("premises" in str(e).lower(), f"unexpected error: {e}", errors)

    lines.append("[14] PASS guards (duplicate init, empty measure, default encode, encode-before-premises)")

    _cleanup_runs(lab_root, RUN_ID_GUARD, RUN_ID_GUARD2)


def _set_custom_analysis(run_dir: Path) -> None:
    import yaml

    snap = yaml.safe_load((run_dir / "config.snapshot.yaml").read_text(encoding="utf-8"))
    snap["analysis"] = {
        "preset": "custom",
        "outcome": "GotSelected",
        "models": [
            {
                "name": "Smoke linear breadth",
                "formula": "GotSelected ~ breadth_z + word_count_z",
            },
        ],
    }
    (run_dir / "config.snapshot.yaml").write_text(
        yaml.safe_dump(snap, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def run_smoke(lab_root: Path) -> bool:
    config_path = lab_root / FIXTURE_CONFIG
    run_dir = lab_root / "experiments" / RUN_ID
    run_dir_b = lab_root / "experiments" / RUN_ID_B
    errors: list[str] = []
    lines: list[str] = ["== synthetic v2.1 smoke =="]
    corpus = "startup_battlefield"

    _cleanup_runs(lab_root, RUN_ID, RUN_ID_B, RUN_ID_GUARD, RUN_ID_GUARD2)

    try:
        cfg = ExperimentConfig.load(config_path)
        init_experiment(cfg, lab_root)
        lines.append("[1] PASS init")

        install_encodings(run_dir, premises=True)
        df1 = _measure(run_dir, lab_root, corpus)
        _assert(len(df1) == 3, f"expected 3 rows, got {len(df1)}", errors)
        _assert(df1["premise_sim_mean"].notna().all(), "premise_sim_mean missing", errors)
        _assert(
            "domain_sep" not in df1.columns or df1["domain_sep"].isna().all(),
            "domain_sep set before domains pass",
            errors,
        )
        _assert("GotSelected" in df1.columns, "corpus join missing GotSelected", errors)
        lines.append("[2] PASS measure (premises + corpus join + similarities)")

        encode_run(run_dir, only_passes=["dfv"])
        _assert({"dfv"} <= {p.name for p in ExperimentConfig.load(run_dir / "config.snapshot.yaml").resolved_passes()}, "dfv not registered", errors)
        install_encodings(run_dir, dfv=True)
        df2 = _measure(run_dir, lab_root, corpus)
        _assert(df2["breadth_D"].notna().all(), "dfv columns missing after dfv pass", errors)
        _assert(df2["n_domains"].isna().all(), "n_domains set before domains pass", errors)
        _assert(_encoding_count(run_dir, "domains") == 0, "domains files should not exist yet", errors)
        lines.append("[3] PASS staged encode -p dfv -> measure (composition only)")

        encode_run(run_dir, only_passes=["domains"])
        install_encodings(run_dir, domains=True)
        df3 = _measure(run_dir, lab_root, corpus)
        _assert(df3["n_domains"].notna().all(), "n_domains missing after domains pass", errors)
        _assert(df3["domain_sep"].notna().all(), "domain_sep missing", errors)
        _assert(df3["breadth_D"].notna().all(), "dfv columns lost after domains pass", errors)
        for cid in ("pilot-1", "pilot-880", "pilot-701"):
            row = df3[df3["case_id"] == cid].iloc[0]
            _assert(row["breadth"] >= 3, f"{cid}: breadth too low", errors)
            _assert(row["n_domains"] == 2, f"{cid}: expected 2 domains", errors)
        lines.append("[4] PASS staged encode -p domains -> measure (full join by case_id)")

        # encode --all with dfv/domains missing (manual backend registers only)
        for name in ("dfv", "domains"):
            enc = run_dir / "encodings" / name
            if enc.exists():
                shutil.rmtree(enc)
        stats_all = encode_run(run_dir, encode_all=True)
        _assert(stats_all["status"] == "done", f"encode --all failed: {stats_all}", errors)
        st_all = run_status(run_dir)
        _assert(st_all["passes"]["dfv"]["pending"] > 0, "encode --all: dfv should be pending", errors)
        _assert(st_all["passes"]["domains"]["pending"] > 0, "encode --all: domains should be pending", errors)
        install_encodings(run_dir, dfv=True, domains=True)
        _measure(run_dir, lab_root, corpus)
        lines.append("[5] PASS encode --all (all declared passes; manual skips API)")

        analyze_run(run_dir)
        text = (run_dir / "analysis" / "results.md").read_text(encoding="utf-8")
        _assert("M5 breadth + premise similarity control" in text, "M5 missing", errors)
        _assert("M6 domain count + domain separation control" in text, "M6 missing", errors)
        lines.append("[6] PASS analyze (battlefield + similarity controls)")

        dataset_mtime = dataset_path(run_dir).stat().st_mtime
        _set_custom_analysis(run_dir)
        analyze_run(run_dir)
        custom = (run_dir / "analysis" / "results.md").read_text(encoding="utf-8")
        _assert("Smoke linear breadth" in custom, "custom analysis model missing", errors)
        _assert("GotSelected models (custom)" in custom, "custom preset header missing", errors)
        _assert(
            dataset_path(run_dir).stat().st_mtime == dataset_mtime,
            "analyze-only should not rebuild dataset.csv",
            errors,
        )
        lines.append("[7] PASS analyze-only (custom preset from edited snapshot)")

        st = run_status(run_dir)
        _assert(st["cases"] == 3, "status case count", errors)
        for name in ("premises", "dfv", "domains"):
            _assert(st["passes"][name]["pending"] == 0, f"status: {name} incomplete", errors)
        _assert(dataset_path(run_dir).exists(), "status: dataset.csv missing", errors)
        lines.append("[8] PASS status (all passes complete, dataset ready)")

        encode_run(run_dir, only_passes=["dfv"], force=True)
        _assert(_encoding_count(run_dir, "dfv") == 0, "force dfv: dfv not cleared", errors)
        _assert(_encoding_count(run_dir, "domains") == 3, "force dfv: domains wrongly cleared", errors)
        _assert(_encoding_count(run_dir, "premises") > 0, "force dfv: premises wrongly cleared", errors)
        install_encodings(run_dir, dfv=True)
        lines.append("[9] PASS force -p dfv (clears dfv only; domains kept)")

        encode_run(run_dir, only_passes=["domains"], force=True)
        _assert(_encoding_count(run_dir, "domains") == 0, "force domains: not cleared", errors)
        _assert(_encoding_count(run_dir, "dfv") == 3, "force domains: dfv wrongly cleared", errors)
        install_encodings(run_dir, domains=True)
        lines.append("[10] PASS force -p domains (clears domains only)")

        encode_run(run_dir, only_passes=["premises"], force=True)
        _assert(_encoding_count(run_dir, "premises") == 0, "force premises: premises not cleared", errors)
        _assert(_encoding_count(run_dir, "dfv") == 0, "force premises: dfv not cleared", errors)
        _assert(_encoding_count(run_dir, "domains") == 0, "force premises: domains not cleared", errors)
        lines.append("[11] PASS force -p premises (clears premises + dfv + domains)")

        install_encodings(run_dir, premises=True, dfv=True, domains=True)
        df4 = _measure(run_dir, lab_root, corpus)
        measures = pd.read_csv(run_dir / "validation" / "measures.csv")
        _assert(measures["valid"].all(), "validation failures after restore", errors)
        _assert(df4["domain_sep"].notna().all(), "restore: domain_sep missing", errors)
        lines.append("[12] PASS restore all passes + measure + validate")

        shutil.copytree(run_dir, run_dir_b)
        n, bd, dd = _compare_datasets(run_dir, run_dir_b)
        _assert(n == 3, f"compare: expected 3 matched cases, got {n}", errors)
        _assert(bd == 0.0 and dd == 0.0, f"compare: expected zero delta, got breadth={bd}, domains={dd}", errors)
        lines.append("[13] PASS compare (two identical runs, zero delta)")

        _run_guard_tests(lab_root, corpus, errors, lines)

    except Exception as e:
        errors.append(f"exception: {e}")
    finally:
        _cleanup_runs(lab_root, RUN_ID, RUN_ID_B, RUN_ID_GUARD, RUN_ID_GUARD2)

    for line in lines:
        print(line)
    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  - {e}")
        print("FAIL")
        return False
    print("PASS")
    return True
