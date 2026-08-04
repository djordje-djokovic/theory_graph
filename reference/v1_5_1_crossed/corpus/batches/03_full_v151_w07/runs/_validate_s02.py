"""Validate session_02 extractions only (composer-2.5 / 1.5.1)."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

BATCH = Path(__file__).resolve().parents[1]
ROOT = BATCH.parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_theory_dag import span_matches  # noqa: E402

SESS = BATCH / "sessions" / "session_02.csv"
PROMPTS = BATCH / "prompts"
RUNS = BATCH / "runs"


def extract_transcript(case_id: str) -> str:
    text = (PROMPTS / f"{case_id}_session_02.md").read_text(encoding="utf-8")
    m = re.search(r"## Transcript\r?\n\r?\n(.+?)\r?\n\r?\n## Output meta", text, re.S)
    if not m:
        raise SystemExit(f"no transcript for {case_id}")
    return m.group(1).strip()


def collect_spans(obj: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for p in obj.get("premises", []):
        out.append((f"premise:{p.get('id')}", p.get("evidence_span", "")))
    for v in obj.get("value", []):
        out.append((f"value:{v.get('id')}", v.get("evidence_span", "")))
    for i, s in enumerate(obj.get("secondary_value", [])):
        out.append((f"secondary:{i}", s.get("evidence_span", "")))
    for i, c in enumerate(obj.get("causal_links", [])):
        out.append((f"link:{i}:{c.get('from')}->{c.get('to')}", c.get("evidence_span", "")))
    return out


def structural_checks(obj: dict, case_id: str, run: int, idx: int) -> list[str]:
    issues: list[str] = []
    m = obj.get("meta", {})
    if m.get("codebook_version") != "1.5.1":
        issues.append(f"codebook={m.get('codebook_version')}")
    if m.get("model_id") != "composer-2.5":
        issues.append(f"model_id={m.get('model_id')}")
    if m.get("model_provider") != "cursor-agent":
        issues.append(f"provider={m.get('model_provider')}")
    if m.get("temperature") is not None:
        issues.append(f"temperature={m.get('temperature')}")
    if m.get("temperature_controlled") is not False:
        issues.append(f"temperature_controlled={m.get('temperature_controlled')}")
    if m.get("pass") != "structure":
        issues.append(f"pass={m.get('pass')}")
    if m.get("coder_session_id") != "session_02":
        issues.append(f"session={m.get('coder_session_id')}")
    if m.get("extraction_run") != int(run):
        issues.append(f"extraction_run={m.get('extraction_run')} expected {run}")
    if m.get("session_case_index") != idx:
        issues.append(f"session_case_index={m.get('session_case_index')} expected {idx}")
    if m.get("case_id") != case_id:
        issues.append(f"case_id={m.get('case_id')}")
    if m.get("unit") != "pitch_transcript":
        issues.append(f"unit={m.get('unit')}")
    if m.get("hierarchy") != "P->D->V":
        issues.append(f"hierarchy={m.get('hierarchy')}")

    premises = obj.get("premises", [])
    domains = obj.get("domains", [])
    value = obj.get("value", [])
    if len(value) != 1:
        issues.append(f"value_count={len(value)}")
    pids = [p["id"] for p in premises]
    if len(pids) != len(set(pids)):
        issues.append("duplicate premise ids")
    assigned: list[str] = []
    for d in domains:
        assigned.extend(d.get("premise_ids", []))
    if sorted(assigned) != sorted(pids):
        issues.append(f"partition mismatch assigned={assigned} premises={pids}")
    dv = {c["from"] for c in obj.get("causal_links", []) if c.get("type") == "domain-value"}
    for d in domains:
        if d["id"] not in dv:
            issues.append(f"missing domain-value for {d['id']}")
    return issues


def main() -> None:
    rows = list(csv.DictReader(SESS.open(encoding="utf-8")))
    fail = 0
    ok = 0
    for idx, row in enumerate(rows, 1):
        cid = row["case_id"]
        run = int(row["run"])
        path = RUNS / f"run{run}" / f"{cid}.json"
        if not path.exists():
            print(f"MISSING {path}")
            fail += 1
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        issues = structural_checks(obj, cid, run, idx)
        tr = extract_transcript(cid)
        for label, span in collect_spans(obj):
            if not span or not span_matches(span, tr):
                issues.append(f"SPAN_FAIL {label}: {span!r}")
        if issues:
            fail += 1
            print(f"FAIL {cid} run{run} idx{idx}")
            for i in issues:
                print(f"  - {i}")
        else:
            ok += 1
            print(
                f"OK   {cid} run{run} idx{idx} "
                f"breadth={len(obj['premises'])} domains={len(obj['domains'])}"
            )
    print(f"\nsummary: ok={ok} fail={fail} total={len(rows)}")


if __name__ == "__main__":
    main()
