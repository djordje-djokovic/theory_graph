import json
import re
from pathlib import Path

base = Path(
    r"c:\Projects\uni\sources\entrepreneurial_theories\data\theory_dags\corpus_v1_5\batches\03_full_v151_w08"
)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def transcript_from_prompt(case_id: str) -> str:
    p = base / "prompts" / f"{case_id}_session_02.md"
    content = p.read_text(encoding="utf-8")
    part = content.split("## Transcript\n", 1)[1]
    return part.split("\n## Output meta", 1)[0].strip()


csv = (base / "sessions" / "session_02.csv").read_text(encoding="utf-8").strip().splitlines()[1:]
issues = []
for i, line in enumerate(csv, 1):
    case_id, run = line.strip().split(",")
    data = json.loads((base / "runs" / f"run{run}" / f"{case_id}.json").read_text(encoding="utf-8"))
    nt = norm(transcript_from_prompt(case_id))
    pids = {p["id"] for p in data["premises"]}
    assigned = [pid for d in data["domains"] for pid in d["premise_ids"]]
    if sorted(assigned) != sorted(pids):
        issues.append(f"{case_id} partition")
    if len(data["value"]) != 1:
        issues.append(f"{case_id} value")
    dids = {d["id"] for d in data["domains"]}
    linked = {c["from"] for c in data["causal_links"] if c["type"] == "domain-value"}
    if linked != dids:
        issues.append(f"{case_id} domain-value")
    spans = [p["evidence_span"] for p in data["premises"]]
    spans += [v["evidence_span"] for v in data["value"]]
    spans += [s["evidence_span"] for s in data.get("secondary_value", [])]
    spans += [c["evidence_span"] for c in data["causal_links"]]
    for span in spans:
        if norm(span) not in nt:
            issues.append(f"{case_id} span: {span[:80]!r}")

print(f"issues={len(issues)}")
for x in issues:
    print(x)
