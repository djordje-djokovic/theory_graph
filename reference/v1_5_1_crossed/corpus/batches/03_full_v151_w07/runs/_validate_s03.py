"""Validate session_03 extractions only (composer-2.5 / 1.5.1)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BATCH = Path(__file__).resolve().parents[1]
ROOT = BATCH.parents[4]  # entrepreneurial_theories
sys.path.insert(0, str(ROOT / "scripts"))
from validate_theory_dag import span_matches  # noqa: E402

ASSIGN = [
    ("pilot-961", 3, 1),
    ("pilot-969", 3, 2),
    ("pilot-998", 3, 3),
    ("pilot-1009", 3, 4),
    ("pilot-1015", 3, 5),
    ("pilot-1023", 3, 6),
    ("pilot-1030", 3, 7),
    ("pilot-1053", 3, 8),
    ("pilot-962", 2, 9),
    ("pilot-976", 2, 10),
    ("pilot-1002", 2, 11),
    ("pilot-1010", 2, 12),
    ("pilot-1016", 2, 13),
    ("pilot-1024", 2, 14),
    ("pilot-1031", 2, 15),
    ("pilot-1054", 2, 16),
    ("pilot-963", 1, 17),
    ("pilot-979", 1, 18),
    ("pilot-1003", 1, 19),
    ("pilot-1011", 1, 20),
    ("pilot-1017", 1, 21),
    ("pilot-1026", 1, 22),
    ("pilot-1049", 1, 23),
    ("pilot-1056", 1, 24),
]


def transcript_for(case_id: str) -> str:
    text = (BATCH / "prompts" / f"{case_id}_session_03.md").read_text(encoding="utf-8")
    m = re.search(r"## Transcript\r?\n\r?\n(.+?)\r?\n\r?\n## Output meta", text, re.S)
    if not m:
        raise SystemExit(f"no transcript for {case_id}")
    return m.group(1).strip()


def main() -> int:
    ok = fail = 0
    issues: list[str] = []
    for cid, run, idx in ASSIGN:
        jp = BATCH / f"runs/run{run}/{cid}.json"
        if not jp.exists():
            issues.append(f"MISSING {jp}")
            fail += 1
            continue
        data = json.loads(jp.read_text(encoding="utf-8"))
        m = data["meta"]
        errs: list[str] = []
        if m.get("codebook_version") != "1.5.1":
            errs.append("codebook")
        if m.get("model_id") != "composer-2.5":
            errs.append(f"model={m.get('model_id')}")
        if m.get("model_provider") != "cursor-agent":
            errs.append("provider")
        if m.get("temperature") is not None:
            errs.append("temp")
        if m.get("temperature_controlled") is not False:
            errs.append("temp_ctrl")
        if m.get("pass") != "structure":
            errs.append("pass")
        if m.get("extraction_run") != run:
            errs.append(f"run={m.get('extraction_run')}")
        if m.get("session_case_index") != idx:
            errs.append(f"idx={m.get('session_case_index')}")
        if m.get("coder_session_id") != "session_03":
            errs.append("session")
        if len(data.get("value", [])) != 1:
            errs.append("value_count")
        pids = {p["id"] for p in data["premises"]}
        seen: set[str] = set()
        for d in data["domains"]:
            for pid in d["premise_ids"]:
                if pid in seen:
                    errs.append(f"dup {pid}")
                seen.add(pid)
                if pid not in pids:
                    errs.append(f"bad {pid}")
        if seen != pids:
            errs.append(f"partition {pids - seen}|{seen - pids}")
        dvids = {c["from"] for c in data["causal_links"] if c["type"] == "domain-value"}
        for d in data["domains"]:
            if d["id"] not in dvids:
                errs.append(f"no DV {d['id']}")
        t = transcript_for(cid)
        spans: list[tuple[str, str, str]] = []
        for p in data["premises"]:
            spans.append(("P", p["id"], p["evidence_span"]))
        for v in data["value"]:
            spans.append(("V", v["id"], v["evidence_span"]))
        for s in data.get("secondary_value", []):
            spans.append(("SV", "", s["evidence_span"]))
        for c in data["causal_links"]:
            spans.append(("L", f"{c['from']}->{c['to']}", c["evidence_span"]))
        for kind, i, sp in spans:
            if not span_matches(sp, t):
                errs.append(f"span {kind}{i}: {sp[:90]!r}")
        if errs:
            fail += 1
            issues.append(f"{cid}: " + "; ".join(errs[:12]))
        else:
            ok += 1
    print(f"OK={ok} FAIL={fail}")
    for line in issues:
        print(line)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
