"""Validate session_04 extractions: provenance + evidence spans."""
import csv
import json
import re
from pathlib import Path

base = Path(__file__).resolve().parents[1]
tx_dir = base / "runs" / "_session_04_transcripts"
rows = list(csv.DictReader((base / "sessions" / "session_04.csv").open(encoding="utf-8")))


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def span_ok(span: str, transcript: str) -> bool:
    if not span:
        return False
    t, sp = norm(transcript), norm(span)
    if sp in t:
        return True
    # allow minor punctuation diffs by stripping non-alnum
    def alnum(x):
        return re.sub(r"[^a-z0-9]+", "", x)

    return alnum(sp) in alnum(t)


fail = 0
ok = 0
for i, row in enumerate(rows, 1):
    path = base / "runs" / f"run{row['run']}" / f"{row['case_id']}.json"
    tx_path = tx_dir / f"{row['case_id']}.txt"
    if not path.exists():
        print(f"MISSING {row['case_id']}")
        fail += 1
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    m = data["meta"]
    issues = []
    if m.get("model_id") != "composer-2.5":
        issues.append(f"model_id={m.get('model_id')}")
    if m.get("codebook_version") != "1.5.1":
        issues.append(f"codebook={m.get('codebook_version')}")
    if m.get("coder_session_id") != "session_04":
        issues.append("bad session")
    if m.get("session_case_index") != i:
        issues.append(f"index={m.get('session_case_index')} expected {i}")
    if m.get("extraction_run") != int(row["run"]):
        issues.append(f"run={m.get('extraction_run')}")
    if m.get("temperature_controlled") is not False or m.get("temperature") is not None:
        issues.append("temperature meta")
    if len(data.get("value", [])) != 1:
        issues.append("value count")
    pids = {p["id"] for p in data["premises"]}
    assigned = []
    for d in data["domains"]:
        assigned.extend(d["premise_ids"])
    if sorted(assigned) != sorted(pids):
        issues.append(f"partition {sorted(assigned)} vs {sorted(pids)}")
    dv = {c["from"] for c in data["causal_links"] if c["type"] == "domain-value"}
    dids = {d["id"] for d in data["domains"]}
    if dv != dids:
        issues.append(f"domain-value missing/extra: have={dv} need={dids}")
    tx = tx_path.read_text(encoding="utf-8")
    spans = []
    for p in data["premises"]:
        spans.append(("P", p["id"], p["evidence_span"]))
    for v in data["value"]:
        spans.append(("V", v["id"], v["evidence_span"]))
    for sv in data.get("secondary_value", []):
        spans.append(("SV", "", sv["evidence_span"]))
    for c in data["causal_links"]:
        spans.append(("L", f"{c['from']}->{c['to']}", c["evidence_span"]))
    bad_spans = []
    for kind, id_, sp in spans:
        if not span_ok(sp, tx):
            bad_spans.append(f"{kind}:{id_}:{sp[:80]}")
    if bad_spans:
        issues.append(f"{len(bad_spans)} bad spans")
        for b in bad_spans[:8]:
            issues.append("  " + b)
    if issues:
        fail += 1
        print(f"FAIL {row['case_id']} run{row['run']}")
        for x in issues:
            print(" ", x)
    else:
        ok += 1
        print(f"OK {row['case_id']} P={len(data['premises'])} D={len(data['domains'])}")

print(f"\n{ok} ok, {fail} fail, {len(rows)} total")
