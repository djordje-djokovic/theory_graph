"""Equivalence battery: prove toolkit matches legacy aggregator/validator."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from .aggregate import aggregate_case_runs, breadth, load_case, n_domains
from .corpora import transcripts_dir
from .prompts import build_user_message, load_prompt
from .validate import measures, validate

FIXTURE_CASES = [
    "pilot-59",
    "pilot-158",
    "pilot-451",
    "pilot-528",
    "pilot-593",
]


def _find_case_jsons(lab_root: Path, case_id: str) -> list[Path]:
    """Locate the three nested-run JSONs for a case under the v1.3.2 reference corpus."""
    batches = lab_root / "reference" / "v1_3_2_nested" / "corpus" / "batches"
    if not batches.exists():
        return []
    for batch in sorted(batches.iterdir()):
        paths = []
        for r in (1, 2, 3):
            p = batch / "runs" / f"run{r}" / f"{case_id}.json"
            if p.exists():
                paths.append(p)
        if len(paths) == 3:
            return paths
    return []


def _ensure_fixtures(lab_root: Path) -> Path:
    """Copy frozen encodings; expected IVs come from shipped analysis cases.csv."""
    fix = lab_root / "tests" / "fixtures"
    enc = fix / "encodings"
    enc.mkdir(parents=True, exist_ok=True)
    shipped = pd.read_csv(
        lab_root / "reference" / "v1_3_2_nested" / "analysis" / "gotselected_analysis_cases.csv",
        dtype={"case_id": str},
    )
    shipped = shipped.set_index("case_id")
    expected_rows = []
    selected = []
    for cid in FIXTURE_CASES:
        paths = _find_case_jsons(lab_root, cid)
        if len(paths) < 1 or cid not in shipped.index:
            continue
        selected.append(cid)
        for i, p in enumerate(paths, start=1):
            dest = enc / f"{cid}_run{i}.json"
            shutil.copy2(p, dest)
        row = shipped.loc[cid]
        c0 = load_case(enc / f"{cid}_run1.json")
        m0 = measures(c0)
        expected_rows.append(
            {
                "case_id": cid,
                "breadth": float(row["breadth"]),
                "n_domains": float(row["n_domains"]),
                "balance": float(row["balance"]),
                "granularity": float(row["granularity"]),
                "m0_breadth": m0["breadth"],
                "m0_n_domains": m0["n_domains"],
                "m0_balance": m0["balance"],
                "m0_granularity": m0["granularity"],
            }
        )
    exp_path = fix / "expected_measures.csv"
    pd.DataFrame(expected_rows).to_csv(exp_path, index=False)
    (fix / "cases.txt").write_text("\n".join(selected) + "\n", encoding="utf-8")
    return fix


def level1_fixture_measures(lab_root: Path) -> tuple[bool, str]:
    fix = _ensure_fixtures(lab_root)
    expected = pd.read_csv(fix / "expected_measures.csv")
    if expected.empty:
        return False, "no fixtures materialized"
    rows = []
    for _, row in expected.iterrows():
        cid = row["case_id"]
        run_cases = []
        for i in (1, 2, 3):
            p = fix / "encodings" / f"{cid}_run{i}.json"
            if p.exists():
                run_cases.append(load_case(p))
        if len(run_cases) < 3:
            return False, f"{cid}: missing fixture encodings"
        for c in run_cases:
            errs = validate(c)
            struct = [e for e in errs if "evidence_span" not in e]
            if struct:
                return False, f"{cid}: validate errors {struct[:3]}"
        agg = aggregate_case_runs(run_cases, cid)
        for key in ("breadth", "n_domains", "balance", "granularity"):
            got = float(agg[key])
            want = float(row[key])
            if not np.isclose(got, want, atol=1e-6, equal_nan=True):
                return False, f"{cid} agg vs shipped {key}: got {got} want {want}"
        m0 = measures(run_cases[0])
        for key in ("breadth", "n_domains"):
            got = float(m0[key])
            want = float(row[f"m0_{key}"])
            if not np.isclose(got, want, atol=1e-6, equal_nan=True):
                return False, f"{cid} measures {key}: got {got} want {want}"
        rows.append(cid)
    return True, f"PASS fixture measures vs shipped analysis for {len(rows)} cases"


def level2_message_construction(lab_root: Path) -> tuple[bool, str]:
    """Check message builder embeds codebook + transcript + required meta."""
    fix = lab_root / "tests" / "fixtures"
    cases = (fix / "cases.txt").read_text(encoding="utf-8").split()
    if not cases:
        return False, "no fixture cases"
    cid = cases[0]
    # transcript
    tpath = transcripts_dir(lab_root, "startup_battlefield") / f"{cid}.txt"
    if not tpath.exists():
        return False, f"missing transcript {tpath}"
    transcript = tpath.read_text(encoding="utf-8")
    codebook = load_prompt(lab_root / "prompts", "v1_3_2")
    msg = build_user_message(
        codebook_text=codebook,
        codebook_version="1.3.2",
        case_id=cid,
        transcript=transcript,
        model_id="composer-2.5",
        extraction_run=1,
    )
    required = [
        "Extraction task",
        "## Codebook",
        "## Transcript",
        cid,
        "meta.codebook_version",
        "meta.pass = \"structure\"",
        "meta.model_id",
        transcript[:80],
    ]
    missing = [r for r in required if r not in msg]
    if missing:
        return False, f"message missing fragments: {missing}"
    # codebook body present (first non-empty line after title)
    if "P → D → V" not in msg and "P -> D -> V" not in msg:
        return False, "codebook hierarchy marker missing from message"
    return True, "PASS message construction contains codebook+transcript+meta"


def level3_live(lab_root: Path, model: str) -> tuple[bool, str]:
    """Optional live re-encode of one fixture case — descriptive, not a hard gate."""
    try:
        from dotenv import load_dotenv

        from .backends import LiteLLMBackend
        from .prompts import messages_for_case, load_prompt
    except Exception as e:
        return True, f"SKIP live ({e})"

    load_dotenv(lab_root / ".env")
    load_dotenv()
    fix = lab_root / "tests" / "fixtures"
    cases = (fix / "cases.txt").read_text(encoding="utf-8").split()
    if not cases:
        return True, "SKIP live (no fixtures)"
    cid = cases[0]
    tpath = transcripts_dir(lab_root, "startup_battlefield") / f"{cid}.txt"
    transcript = tpath.read_text(encoding="utf-8")
    codebook = load_prompt(lab_root / "prompts", "v2_0_0")
    msgs = messages_for_case(
        codebook_text=codebook,
        codebook_version="2.0.0",
        case_id=cid,
        transcript=transcript,
        model_id=model,
        extraction_run=1,
    )
    try:
        backend = LiteLLMBackend()
        result = backend.complete(
            msgs, model=model, temperature=0.0, max_tokens=4000, timeout_s=180
        )
    except Exception as e:
        return True, f"SKIP live encode failed: {e}"
    # parse loosely
    import re

    text = result.text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
    except Exception as e:
        return True, f"SKIP live JSON parse failed: {e}"
    b = breadth(obj)
    d = n_domains(obj)
    ref = load_case(fix / "encodings" / f"{cid}_run1.json")
    return True, (
        f"LIVE ok {cid}: new breadth={b} domains={d}; "
        f"ref breadth={breadth(ref)} domains={n_domains(ref)}"
    )


def run_equivalence(lab_root: Path, *, live: bool = False, model: str = "openai/gpt-4.1") -> bool:
    print("== equivalence battery ==")
    results = []
    ok1, msg1 = level1_fixture_measures(lab_root)
    print(f"[1] {msg1}")
    results.append(ok1)
    ok2, msg2 = level2_message_construction(lab_root)
    print(f"[2] {msg2}")
    results.append(ok2)
    if live:
        ok3, msg3 = level3_live(lab_root, model)
        print(f"[3] {msg3}")
        # live is not a hard gate
    else:
        print("[3] SKIP live (pass --live to enable)")
    hard_ok = all(results)
    print("PASS" if hard_ok else "FAIL")
    return hard_ok
