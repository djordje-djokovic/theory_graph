import json, re, pathlib

base = pathlib.Path(r"c:\Projects\uni\sources\entrepreneurial_theories\data\theory_dags\corpus_v1_5\batches\03_full_v151_w08")
assign = [
    ("pilot-1062", 1, 1), ("pilot-1068", 1, 2), ("pilot-1074", 1, 3), ("pilot-1133", 1, 4), ("pilot-1143", 1, 5),
    ("pilot-1150", 1, 6), ("pilot-1158", 1, 7), ("pilot-1066", 3, 8), ("pilot-1072", 3, 9), ("pilot-1078", 3, 10),
    ("pilot-1141", 3, 11), ("pilot-1148", 3, 12), ("pilot-1156", 3, 13), ("pilot-1067", 2, 14), ("pilot-1073", 2, 15),
    ("pilot-1118", 2, 16), ("pilot-1142", 2, 17), ("pilot-1149", 2, 18), ("pilot-1157", 2, 19),
]

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip().lower()

issues = []
for case, run, idx in assign:
    jf = base / f"runs/run{run}" / f"{case}.json"
    pf = base / "prompts" / f"{case}_session_01.md"
    data = json.loads(jf.read_text(encoding="utf-8"))
    md = pf.read_text(encoding="utf-8")
    trans = md.rsplit("## Transcript", 1)[1]
    if "## Output meta" in trans:
        trans = trans.split("## Output meta")[0]
    trans = trans.strip()
    nt = norm(trans)
    meta = data["meta"]
    checks = [
        (meta.get("codebook_version") == "1.5.1", "codebook"),
        (meta.get("model_id") == "composer-2.5", "model"),
        (meta.get("extraction_run") == run, "run"),
        (meta.get("session_case_index") == idx, "index"),
        (meta.get("coder_session_id") == "session_01", "session"),
        (len(data.get("value") or []) == 1, "value"),
    ]
    for ok, name in checks:
        if not ok:
            issues.append(f"{case}: bad {name}: {meta.get(name, meta)}")
    allp = {p["id"] for p in data["premises"]}
    assigned = set()
    for d in data["domains"]:
        for pid in d["premise_ids"]:
            if pid in assigned:
                issues.append(f"{case}: duplicate {pid}")
            assigned.add(pid)
    if assigned != allp:
        issues.append(f"{case}: partition mismatch {allp ^ assigned}")
    doms = {d["id"] for d in data["domains"]}
    dv = {c["from"] for c in data["causal_links"] if c["type"] == "domain-value"}
    if dv != doms:
        issues.append(f"{case}: domain-value missing {doms - dv} extra {dv - doms}")
    spans = []
    for p in data["premises"]:
        spans.append(("P", p["id"], p["evidence_span"]))
    for v in data["value"]:
        spans.append(("V", v["id"], v["evidence_span"]))
    for i, s in enumerate(data.get("secondary_value") or []):
        spans.append(("SV", str(i), s["evidence_span"]))
    for i, c in enumerate(data["causal_links"]):
        spans.append(("L", f"{c['from']}->{c['to']}", c["evidence_span"]))
    for kind, i, sp in spans:
        if norm(sp) not in nt:
            issues.append(f"{case}: FAIL {kind} {i}: {sp[:100]!r}")

print("ISSUES", len(issues))
for x in issues:
    print(x)
print("OK cases", len(assign) - len({x.split(':')[0] for x in issues}))
