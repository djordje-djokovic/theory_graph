"""Validate extracted theory-architecture JSON and derive architecture measures.

Production path: codebook v1.3 Pass A (`meta.pass` = structure). Enforces
P -> D -> V DAG constraints, verifies evidence spans, writes measures.

Also accepts experiment-only pass kinds (premises / pairs) from the closed
v1.4 frozen-grouping archive under data/theory_dags/experiments/.

Usage:
    python validate_theory_dag.py EXTRACTION_DIR --out measures.csv
    python validate_theory_dag.py EXTRACTION_DIR --transcripts DIR --out measures.csv
    python validate_theory_dag.py EXTRACTION_DIR --frozen FROZEN_DIR --out measures.csv
    python validate_theory_dag.py --self-test

With --transcripts, every evidence_span must appear in the case transcript as a
verbatim substring (whitespace and case normalised, fuzzy tolerance for ASR
noise). Transcript files are matched by case id: <case_id>.txt.

With --frozen, Pass A2 pair files are checked against the frozen premise set
for that case_id.

Measures produced per case (see docs/methods/measurement_and_analysis_plan.md):
    breadth                  number of premises
    breadth_explicit         premises coded as explicit
    n_domains                number of strategic domains
    balance                  1 - sum(share_k^2) over premises per domain
    granularity              n_domains / breadth
    n_domains_merged         domain count after merging single-premise domains
    balance_merged           balance recomputed on the merged partition
    within_domain_share      share of premise dependencies inside one domain
    n_dep_within             premise dependencies inside one domain
    n_dep_between            premise dependencies crossing the partition
    cross_domain_link_rate   (cross premise-domain + domain-domain) / breadth
    n_value, n_secondary_value, n_links, n_premise_premise_links
    truncated, thin_transcript, dependency_pass, coder_confidence
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

SPAN_FUZZ_THRESHOLD = 0.92

TAXONOMY = {
    "DESIRABILITY",
    "FEASIBILITY",
    "VIABILITY",
    "OPERATIONS_SUPPLY",
    "GTM_DISTRIBUTION",
    "ORGANIZATION_TEAM",
    "INSTITUTIONAL_REGULATORY",
    "IMPACT_EXTERNALITY",
}

LINK_TYPES = {"premise-premise", "premise-domain", "domain-domain", "domain-value"}

LAYER = {"P": 0, "D": 1, "V": 2}

# Codebooks from 2.0.0 on code a flat P->D->V graph: premise-to-domain is membership
# and domain-value is the only edge type. Published v1.3.2 and v1.5.1 still carry the
# exploratory dependency layer, so their runs keep validating unchanged.
FLAT_GRAPH_FROM = (2, 0, 0)


def flat_graph_codebook(version: str | None) -> bool:
    """True when `version` is a codebook that codes domain-value links only."""
    if not version:
        return False
    parts = str(version).lstrip("vV").split(".")
    try:
        return tuple(int(p) for p in parts[:3]) >= FLAT_GRAPH_FROM
    except ValueError:
        return False


def layer_of(node_id: str) -> int | None:
    if not node_id:
        return None
    return LAYER.get(node_id[0].upper())


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def span_matches(span: str, transcript: str) -> bool:
    """True if span appears in transcript verbatim, allowing ASR-level noise."""
    needle, haystack = normalise(span), normalise(transcript)
    if not needle:
        return False
    if needle in haystack:
        return True
    window = len(needle)
    if window > len(haystack):
        return False
    matcher = SequenceMatcher(autojunk=False)
    matcher.set_seq2(needle)
    step = max(1, window // 8)
    for start in range(0, len(haystack) - window + 1, step):
        matcher.set_seq1(haystack[start : start + window])
        if matcher.quick_ratio() < SPAN_FUZZ_THRESHOLD:
            continue
        if matcher.ratio() >= SPAN_FUZZ_THRESHOLD:
            return True
    return False


def spans_of(case: dict) -> list[tuple[str, str]]:
    """(label, span) pairs for every evidence span in the case."""
    out: list[tuple[str, str]] = []
    for p in case.get("premises") or []:
        out.append((str(p.get("id")), p.get("evidence_span") or ""))
    for v in case.get("value") or []:
        out.append((str(v.get("id")), v.get("evidence_span") or ""))
    for i, s in enumerate(case.get("secondary_value") or []):
        out.append((f"secondary_value[{i}]", s.get("evidence_span") or ""))
    for i, link in enumerate(case.get("causal_links") or []):
        span = link.get("evidence_span")
        if span:
            out.append((f"link[{i}] {link.get('from')}->{link.get('to')}", span))
    return out


# Production confirmatory extracts must use this exact slug (not fast/lite).
ALLOWED_PRODUCTION_MODEL = "composer-2.5"
FORBIDDEN_MODEL_SUFFIXES = ("-fast", "-lite")


def validate_provenance(case: dict, require_model: str | None = None) -> list[str]:
    """Require an honest record of which model produced the extraction.

    `temperature` may only be recorded as a number when sampling was actually
    pinned; runs made through an agent harness that does not expose the
    parameter must declare `temperature_controlled: false` and leave the value
    null rather than implying a control that was not exercised.

    When `require_model` is set (e.g. "composer-2.5"), `meta.model_id` must
    match exactly. Fast/lite variants are always rejected under that lock.
    """
    errors: list[str] = []
    meta = case.get("meta")
    if not isinstance(meta, dict):
        errors.append("meta: missing object")
        return errors
    model_id = meta.get("model_id")
    if not isinstance(model_id, str) or not model_id.strip():
        errors.append("meta.model_id: required non-empty string")
    else:
        mid = model_id.strip()
        if require_model is not None and mid != require_model:
            errors.append(
                f"meta.model_id: required {require_model!r}, got {mid!r}"
            )
        elif require_model is not None and any(
            mid.endswith(suf) for suf in FORBIDDEN_MODEL_SUFFIXES
        ):
            errors.append(
                f"meta.model_id: forbidden fast/lite variant {mid!r}; "
                f"use {require_model!r}"
            )

    controlled = meta.get("temperature_controlled")
    if not isinstance(controlled, bool):
        errors.append("meta.temperature_controlled: required boolean")
        return errors

    temp = meta.get("temperature")
    if controlled:
        if not isinstance(temp, (int, float)) or isinstance(temp, bool):
            errors.append("meta.temperature: required number when controlled")
    elif temp is not None:
        errors.append("meta.temperature: must be null when not controlled")
    return errors


def validate_pairs(case: dict, frozen: dict | None = None) -> list[str]:
    """Validate a v1.4 Pass A2 pairwise co-revisability JSON."""
    errors: list[str] = []
    errors.extend(validate_provenance(case))
    meta = case.get("meta") or {}
    if meta.get("pass") not in {None, "pairs"}:
        errors.append(f"meta.pass: expected 'pairs', got {meta.get('pass')!r}")
    wording = meta.get("wording")
    if wording not in {"revise_if_false", "learn_together"}:
        errors.append("meta.wording: must be revise_if_false or learn_together")

    pairs = case.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        errors.append("pairs: required non-empty list")
        return errors

    frozen_ids: set[str] | None = None
    if frozen is not None:
        frozen_ids = {p.get("id") for p in (frozen.get("premises") or []) if p.get("id")}
        if not frozen_ids:
            errors.append("frozen premises: empty")

    seen: set[tuple[str, str]] = set()
    for i, pair in enumerate(pairs):
        tag = f"pairs[{i}]"
        a, b = pair.get("premise_a"), pair.get("premise_b")
        if not isinstance(a, str) or not isinstance(b, str):
            errors.append(f"{tag}: premise_a/premise_b required strings")
            continue
        if a == b:
            errors.append(f"{tag}: self-pair not allowed")
        if a >= b:
            errors.append(f"{tag}: require premise_a < premise_b lexicographically")
        if (a, b) in seen:
            errors.append(f"{tag}: duplicate pair")
        seen.add((a, b))
        if not isinstance(pair.get("co_revise"), bool):
            errors.append(f"{tag}: co_revise must be boolean")
        if frozen_ids is not None:
            if a not in frozen_ids:
                errors.append(f"{tag}: unknown premise_a {a}")
            if b not in frozen_ids:
                errors.append(f"{tag}: unknown premise_b {b}")

    if frozen_ids is not None and len(frozen_ids) >= 2:
        expected = {(a, b) for a, b in combinations(sorted(frozen_ids), 2)}
        missing = expected - seen
        extra = seen - expected
        if missing:
            errors.append(f"pairs: missing {len(missing)} expected unordered pair(s)")
        if extra:
            errors.append(f"pairs: {len(extra)} pair(s) not in frozen set")

    conf = (case.get("quality") or {}).get("coder_confidence")
    if conf is not None and (
        not isinstance(conf, (int, float)) or not 0.0 <= float(conf) <= 1.0
    ):
        errors.append("quality.coder_confidence must be in [0, 1]")
    return errors


def validate_premises_pass(case: dict, transcript: str | None = None) -> list[str]:
    """Validate a premises-only JSON (no domains, no causal_links).

    Accepts both the v1.4 experiment shape (optional value, optional
    premise-premise links) and the v2.1.0 Pass A shape (optional value, no
    links at all).
    """
    errors: list[str] = []
    errors.extend(validate_provenance(case))
    if case.get("domains"):
        errors.append("pass=premises must not include domains")

    premises = case.get("premises") or []
    values = case.get("value") or []
    links = case.get("causal_links") or []
    premise_ids = [p.get("id") for p in premises]
    value_ids = [v.get("id") for v in values]

    if not premises:
        errors.append("no premises coded")
    if len(values) > 1:
        errors.append(f"value must have at most one item (got {len(values)})")

    all_ids = premise_ids + value_ids
    if len(all_ids) != len(set(all_ids)):
        errors.append("duplicate node ids")
    for pid in premise_ids:
        if layer_of(pid) != 0:
            errors.append(f"premise id must start with P: {pid}")
    for vid in value_ids:
        if layer_of(vid) != 2:
            errors.append(f"value id must start with V: {vid}")

    for p in premises:
        if p.get("status") not in {"explicit", "inferred"}:
            errors.append(f"{p.get('id')}: status must be explicit or inferred")
        if not (p.get("evidence_span") or "").strip():
            errors.append(f"{p.get('id')}: missing evidence_span")

    for i, link in enumerate(links):
        src, dst, ltype = link.get("from"), link.get("to"), link.get("type")
        tag = f"link[{i}] {src}->{dst}"
        if ltype != "premise-premise":
            errors.append(f"{tag}: premises pass allows only premise-premise links")
            continue
        if src not in premise_ids or dst not in premise_ids:
            errors.append(f"{tag}: unresolved premise id")
        if src == dst:
            errors.append(f"{tag}: self-loop")

    quality = case.get("quality") or {}
    conf = quality.get("coder_confidence")
    if conf is not None and (
        not isinstance(conf, (int, float)) or not 0.0 <= float(conf) <= 1.0
    ):
        errors.append("quality.coder_confidence must be in [0, 1]")
    if transcript is not None:
        for label, span in spans_of(case):
            if span and not span_matches(span, transcript):
                errors.append(f"{label}: evidence_span not found in transcript")
    return errors


DOMAIN_TAGS = {"DESIRABILITY", "FEASIBILITY", "VIABILITY", "OTHER"}


def validate_domains_pass(case: dict, frozen_premise_ids: list[str] | None = None) -> list[str]:
    """Validate a v2.1.0 Pass B premise-DFV tagging JSON."""
    errors: list[str] = []
    errors.extend(validate_provenance(case))

    for forbidden in ("premises", "domains", "causal_links", "value", "quality"):
        if case.get(forbidden):
            errors.append(f"pass=dfv must not include {forbidden}")

    assignments = case.get("assignments") or []
    if not assignments:
        errors.append("no assignments coded")
        return errors

    seen: set[str] = set()
    for i, a in enumerate(assignments):
        pid = a.get("premise_id")
        tag = a.get("tag")
        if not pid:
            errors.append(f"assignments[{i}]: missing premise_id")
            continue
        if pid in seen:
            errors.append(f"{pid}: tagged more than once")
        seen.add(pid)
        if tag not in DOMAIN_TAGS:
            errors.append(f"{pid}: invalid tag {tag!r}")

    if frozen_premise_ids is not None:
        expected = set(frozen_premise_ids)
        got = {a.get("premise_id") for a in assignments if a.get("premise_id")}
        missing = expected - got
        extra = got - expected
        if missing:
            errors.append(f"untagged premises: {sorted(missing)}")
        if extra:
            errors.append(f"unknown premise_ids: {sorted(extra)}")

    return errors


def validate_strategic_pass(case: dict, frozen_premise_ids: list[str] | None = None) -> list[str]:
    """Validate a v2.1.0 Pass C strategic-domain grouping JSON."""
    errors: list[str] = []
    errors.extend(validate_provenance(case))

    for forbidden in ("premises", "causal_links", "value", "assignments", "quality"):
        if case.get(forbidden):
            errors.append(f"pass=strategic_domains must not include {forbidden}")

    domains = case.get("domains") or []
    if not domains:
        errors.append("no domains coded")
        return errors

    domain_ids = [d.get("id") for d in domains]
    if len(domain_ids) != len(set(domain_ids)):
        errors.append("duplicate domain ids")
    for did in domain_ids:
        if not str(did).startswith("D"):
            errors.append(f"domain id must start with D: {did}")

    membership: dict[str, str] = {}
    for d in domains:
        if not (d.get("name") or "").strip():
            errors.append(f"{d.get('id')}: missing name")
        for pid in d.get("premise_ids") or []:
            if pid in membership:
                errors.append(f"{pid}: assigned to multiple domains")
            else:
                membership[pid] = d["id"]

    if frozen_premise_ids is not None:
        expected = set(frozen_premise_ids)
        got = set(membership.keys())
        missing = expected - got
        extra = got - expected
        if missing:
            errors.append(f"unassigned premises: {sorted(missing)}")
        if extra:
            errors.append(f"unknown premise_ids: {sorted(extra)}")

    return errors


def validate(
    case: dict,
    transcript: str | None = None,
    frozen: dict | None = None,
    require_model: str | None = None,
) -> list[str]:
    """Return a list of validation errors; empty list means the case passes."""
    pass_kind = (case.get("meta") or {}).get("pass")
    if pass_kind == "pairs":
        return validate_pairs(case, frozen)
    if pass_kind == "premises":
        return validate_premises_pass(case, transcript)
    if pass_kind == "dfv":
        frozen_ids = None
        if frozen and "premises" in frozen:
            frozen_ids = [p.get("id") for p in frozen["premises"] if p.get("id")]
        return validate_domains_pass(case, frozen_premise_ids=frozen_ids)
    if pass_kind == "domains":
        frozen_ids = None
        if frozen and "premises" in frozen:
            frozen_ids = [p.get("id") for p in frozen["premises"] if p.get("id")]
        return validate_strategic_pass(case, frozen_premise_ids=frozen_ids)
    if pass_kind == "taxonomy":
        return validate_provenance(case, require_model=require_model)

    errors: list[str] = []
    errors.extend(validate_provenance(case, require_model=require_model))

    premises = case.get("premises") or []
    domains = case.get("domains") or []
    values = case.get("value") or []
    links = case.get("causal_links") or []

    premise_ids = [p.get("id") for p in premises]
    domain_ids = [d.get("id") for d in domains]
    value_ids = [v.get("id") for v in values]

    if not premises:
        errors.append("no premises coded")
    if not domains:
        errors.append("no domains coded")
    if len(values) != 1:
        errors.append(f"value must have exactly one item (got {len(values)})")

    all_ids = premise_ids + domain_ids + value_ids
    if len(all_ids) != len(set(all_ids)):
        errors.append("duplicate node ids")

    for pid in premise_ids:
        if layer_of(pid) != 0:
            errors.append(f"premise id must start with P: {pid}")
    for did in domain_ids:
        if layer_of(did) != 1:
            errors.append(f"domain id must start with D: {did}")
    for vid in value_ids:
        if layer_of(vid) != 2:
            errors.append(f"value id must start with V: {vid}")

    for p in premises:
        if p.get("status") not in {"explicit", "inferred"}:
            errors.append(f"{p.get('id')}: status must be explicit or inferred")
        if not (p.get("evidence_span") or "").strip():
            errors.append(f"{p.get('id')}: missing evidence_span")

    for i, sec in enumerate(case.get("secondary_value") or []):
        if not (sec.get("text") or "").strip():
            errors.append(f"secondary_value[{i}]: missing text")
        if not (sec.get("evidence_span") or "").strip():
            errors.append(f"secondary_value[{i}]: missing evidence_span")

    # Membership: every premise in exactly one domain. Taxonomy is assigned in
    # Pass B, so it is optional here but must be valid when present.
    membership: dict[str, str] = {}
    for d in domains:
        if "taxonomy" in d and d.get("taxonomy") not in TAXONOMY:
            errors.append(f"{d.get('id')}: invalid taxonomy {d.get('taxonomy')!r}")
        for pid in d.get("premise_ids") or []:
            if pid not in premise_ids:
                errors.append(f"{d.get('id')}: unknown premise {pid}")
            elif pid in membership:
                errors.append(f"{pid}: assigned to multiple domains")
            else:
                membership[pid] = d["id"]
    for pid in premise_ids:
        if pid not in membership:
            errors.append(f"{pid}: not assigned to any domain")

    # Coded links.
    flat_graph = flat_graph_codebook((case.get("meta") or {}).get("codebook_version"))
    edges: list[tuple[str, str]] = []
    for i, link in enumerate(links):
        src, dst, ltype = link.get("from"), link.get("to"), link.get("type")
        tag = f"link[{i}] {src}->{dst}"
        if ltype not in LINK_TYPES:
            errors.append(f"{tag}: invalid type {ltype!r}")
            continue
        if flat_graph and ltype != "domain-value":
            errors.append(f"{tag}: codebook codes domain-value links only, got {ltype}")
            continue
        if src not in all_ids or dst not in all_ids:
            errors.append(f"{tag}: unresolved node id")
            continue
        ls, ld = layer_of(src), layer_of(dst)
        expected = {
            "premise-premise": (0, 0),
            "premise-domain": (0, 1),
            "domain-domain": (1, 1),
            "domain-value": (1, 2),
        }[ltype]
        if (ls, ld) != expected:
            errors.append(f"{tag}: layers do not match type {ltype}")
            continue
        if ld < ls:
            errors.append(f"{tag}: upward edge is not permitted")
        if ltype == "premise-domain" and membership.get(src) == dst:
            errors.append(f"{tag}: primary membership must not be restated as a link")
        if src == dst:
            errors.append(f"{tag}: self-loop")
        edges.append((src, dst))

    # Membership edges complete the graph.
    edges.extend((pid, did) for pid, did in membership.items())

    # Value nodes must be sinks.
    for src, _ in edges:
        if layer_of(src) == 2:
            errors.append(f"{src}: value nodes must not have outgoing edges")

    if _has_cycle(all_ids, edges):
        errors.append("graph contains a cycle")

    quality = case.get("quality") or {}
    conf = quality.get("coder_confidence")
    if conf is not None and (
        not isinstance(conf, (int, float)) or not 0.0 <= float(conf) <= 1.0
    ):
        errors.append("quality.coder_confidence must be in [0, 1]")
    if transcript is not None:
        for label, span in spans_of(case):
            if span and not span_matches(span, transcript):
                errors.append(f"{label}: evidence_span not found in transcript")

    return errors


def _has_cycle(nodes: list[str], edges: list[tuple[str, str]]) -> bool:
    indeg: dict[str, int] = {n: 0 for n in nodes}
    adj: dict[str, list[str]] = defaultdict(list)
    for src, dst in edges:
        if src in indeg and dst in indeg:
            adj[src].append(dst)
            indeg[dst] += 1
    queue = [n for n, d in indeg.items() if d == 0]
    seen = 0
    while queue:
        node = queue.pop()
        seen += 1
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    return seen != len(nodes)


_TERMINAL_PUNCT = ".!?\"')]"


def transcript_truncated(transcript: str | None) -> bool | None:
    """Deterministic truncation flag: does the transcript stop mid-utterance?

    Derived from the text rather than coded by the model, so the control does not
    inherit coder error and is reproducible without an extraction run. Returns None
    when no transcript is available.
    """
    if transcript is None:
        return None
    text = transcript.strip()
    if not text:
        return True
    if text.endswith(("...", "\u2026", "-", "\u2013", "\u2014")):
        return True
    return text[-1] not in _TERMINAL_PUNCT


def measures(case: dict, transcript: str | None = None) -> dict:
    premises = case.get("premises") or []
    domains = case.get("domains") or []
    values = case.get("value") or []
    links = case.get("causal_links") or []
    quality = case.get("quality") or {}

    membership = {
        pid: d["id"] for d in domains for pid in (d.get("premise_ids") or [])
    }
    breadth = len(premises)
    n_domains = len(domains)

    sizes = [len(d.get("premise_ids") or []) for d in domains]
    balance = (
        1.0 - sum((s / breadth) ** 2 for s in sizes) if breadth and n_domains else None
    )

    n_singletons = sum(1 for s in sizes if s == 1)
    n_domains_merged = max(n_domains - n_singletons, 1) if n_domains else 0
    sizes_merged = sorted((s for s in sizes if s > 1), reverse=True)
    if n_singletons and sizes_merged:
        sizes_merged[0] += n_singletons
    elif n_singletons:
        sizes_merged = [n_singletons]
    balance_merged = (
        1.0 - sum((s / breadth) ** 2 for s in sizes_merged) if breadth and sizes_merged else None
    )

    pp_links = [l for l in links if l.get("type") == "premise-premise"]
    within = [
        l
        for l in pp_links
        if membership.get(l.get("from")) == membership.get(l.get("to"))
    ]
    within_share = len(within) / len(pp_links) if pp_links else None

    cross = [
        l
        for l in links
        if l.get("type") == "domain-domain"
        or (
            l.get("type") == "premise-domain"
            and membership.get(l.get("from")) != l.get("to")
        )
    ]
    cross_rate = len(cross) / breadth if breadth else None

    return {
        "breadth": breadth,
        "breadth_explicit": sum(1 for p in premises if p.get("status") == "explicit"),
        "n_domains": n_domains,
        "balance": None if balance is None else round(balance, 4),
        "granularity": round(n_domains / breadth, 4) if breadth else None,
        "n_domains_merged": n_domains_merged,
        "balance_merged": None if balance_merged is None else round(balance_merged, 4),
        "within_domain_share": None if within_share is None else round(within_share, 4),
        "n_dep_within": len(within),
        "n_dep_between": len(pp_links) - len(within),
        "cross_domain_link_rate": None if cross_rate is None else round(cross_rate, 4),
        "n_value": len(values),
        "n_secondary_value": len(case.get("secondary_value") or []),
        "n_links": len(links),
        "n_premise_premise_links": len(pp_links),
        "domain_taxonomies": "|".join(sorted({d.get("taxonomy", "") for d in domains if d.get("taxonomy")})),
        "thin_transcript": bool(quality.get("thin_transcript")),
        "truncated": bool(quality.get("truncated")),
        "truncated_derived": transcript_truncated(transcript),
        "dependency_pass": bool(quality.get("dependency_pass")),
        "coder_confidence": quality.get("coder_confidence"),
    }


FIELDS = [
    "case_id",
    "valid",
    "n_errors",
    "errors",
    "spans_checked",
    "breadth",
    "breadth_explicit",
    "n_domains",
    "balance",
    "granularity",
    "n_domains_merged",
    "balance_merged",
    "within_domain_share",
    "n_dep_within",
    "n_dep_between",
    "cross_domain_link_rate",
    "n_value",
    "n_secondary_value",
    "n_links",
    "n_premise_premise_links",
    "domain_taxonomies",
    "thin_transcript",
    "truncated",
    "truncated_derived",
    "dependency_pass",
    "coder_confidence",
]


def load_transcript(transcripts: Path | None, case_id: str) -> str | None:
    if transcripts is None:
        return None
    candidates = [f"{case_id}.txt"]
    if case_id.startswith("pilot-"):
        candidates.append(f"pitch_{case_id.removeprefix('pilot-')}.txt")
    for name in candidates:
        path = transcripts / name
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


def load_frozen(frozen_dir: Path | None, case_id: str) -> dict | None:
    if frozen_dir is None:
        return None
    path = frozen_dir / f"{case_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def process_dir(
    src: Path,
    out: Path,
    transcripts: Path | None = None,
    frozen_dir: Path | None = None,
    require_model: str | None = None,
) -> int:
    rows = []
    failures = 0
    span_checked = 0
    span_failures = 0
    for path in sorted(src.glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        case_id = case.get("meta", {}).get("case_id") or path.stem
        transcript = load_transcript(transcripts, case_id)
        frozen = load_frozen(frozen_dir, case_id)
        errors = validate(case, transcript, frozen, require_model=require_model)
        failures += bool(errors)
        if transcript is not None and (case.get("meta") or {}).get("pass") != "pairs":
            span_checked += 1
            span_failures += any("evidence_span not found" in e for e in errors)
        row = {
            "case_id": case_id,
            "valid": not errors,
            "n_errors": len(errors),
            "errors": "; ".join(errors),
            "spans_checked": transcript is not None,
        }
        if (case.get("meta") or {}).get("pass") in {"pairs", "premises", "taxonomy"}:
            # Pair / A1 passes do not carry a full domain partition.
            row.update(
                {
                    "breadth": len(case.get("premises") or [])
                    if (case.get("meta") or {}).get("pass") == "premises"
                    else (
                        len((frozen or {}).get("premises") or [])
                        if frozen
                        else ""
                    ),
                    "breadth_explicit": "",
                    "n_domains": "",
                    "balance": "",
                    "granularity": "",
                    "n_domains_merged": "",
                    "balance_merged": "",
                    "within_domain_share": "",
                    "n_dep_within": "",
                    "n_dep_between": "",
                    "cross_domain_link_rate": "",
                    "n_value": len(case.get("value") or []),
                    "n_secondary_value": len(case.get("secondary_value") or []),
                    "n_links": len(case.get("causal_links") or []),
                    "n_premise_premise_links": "",
                    "domain_taxonomies": "",
                    "thin_transcript": bool((case.get("quality") or {}).get("thin_transcript")),
                    "truncated": bool((case.get("quality") or {}).get("truncated")),
                    "truncated_derived": transcript_truncated(transcript),
                    "dependency_pass": bool((case.get("quality") or {}).get("dependency_pass")),
                    "coder_confidence": (case.get("quality") or {}).get("coder_confidence"),
                }
            )
        else:
            row.update(measures(case, transcript))
        rows.append(row)

    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"cases: {len(rows)}  failing validation: {failures}")
    if span_checked:
        rate = 100.0 * (span_checked - span_failures) / span_checked
        print(f"span verification: {span_checked - span_failures}/{span_checked} cases clean ({rate:.1f}%)")
    elif transcripts is not None:
        print("span verification: no matching transcripts found")
    print(f"wrote {out}")
    return failures


_GOOD_CASE = {
    "meta": {
        "codebook_version": "1.3",
        "pass": "structure",
        "case_id": "selftest-good",
        "model_id": "selftest-model",
        "model_provider": "selftest",
        "temperature": 0.0,
        "temperature_controlled": True,
        "extraction_run": 1,
    },
    "premises": [
        {"id": "P1", "text": "a", "status": "explicit", "evidence_span": "alpha claim"},
        {"id": "P2", "text": "b", "status": "explicit", "evidence_span": "beta claim"},
        {"id": "P3", "text": "c", "status": "inferred", "evidence_span": "gamma claim"},
    ],
    "domains": [
        {"id": "D1", "name": "product", "premise_ids": ["P1", "P2"]},
        {"id": "D2", "name": "channels", "premise_ids": ["P3"]},
    ],
    "value": [{"id": "V1", "text": "v", "status": "explicit", "evidence_span": "value claim"}],
    "secondary_value": [],
    "causal_links": [
        {"from": "P1", "to": "P2", "type": "premise-premise", "evidence_span": "alpha claim"},
        {"from": "P1", "to": "D2", "type": "premise-domain", "evidence_span": "gamma claim"},
        {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "value claim"},
        {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "value claim"},
    ],
    "quality": {
        "thin_transcript": False,
        "truncated": False,
        "dependency_pass": True,
        "coder_confidence": 0.9,
    },
}

_TRANSCRIPT = (
    "We make an alpha claim, and then a beta claim about the product. "
    "Our gamma claim covers channels. The value claim is what the market gets."
)

_BAD_CASES = {
    "upward edge": {"from": "V1", "to": "D1", "type": "domain-value"},
    "membership restated": {"from": "P1", "to": "D1", "type": "premise-domain"},
    "unresolved id": {"from": "P9", "to": "D1", "type": "premise-domain"},
}


def self_test() -> int:
    failed = 0

    errors = validate(_GOOD_CASE)
    if errors:
        print(f"FAIL good case rejected: {errors}")
        failed += 1
    else:
        print("ok: valid case accepted")

    m = measures(_GOOD_CASE)
    expected = {
        "breadth": 3,
        "breadth_explicit": 2,
        "n_domains": 2,
        "balance": round(1 - ((2 / 3) ** 2 + (1 / 3) ** 2), 4),
        "granularity": round(2 / 3, 4),
        "n_domains_merged": 1,
        "balance_merged": 0.0,
        "within_domain_share": 1.0,
        "n_dep_within": 1,
        "n_dep_between": 0,
        "cross_domain_link_rate": round(1 / 3, 4),
    }
    for key, want in expected.items():
        if m[key] != want:
            print(f"FAIL measure {key}: got {m[key]!r} want {want!r}")
            failed += 1
    if not failed:
        print("ok: measures correct")

    for label, bad_link in _BAD_CASES.items():
        case = json.loads(json.dumps(_GOOD_CASE))
        case["causal_links"].append(bad_link)
        if not validate(case):
            print(f"FAIL '{label}' was not caught")
            failed += 1
        else:
            print(f"ok: caught {label}")

    # cycle among premises
    case = json.loads(json.dumps(_GOOD_CASE))
    case["causal_links"].append({"from": "P2", "to": "P1", "type": "premise-premise"})
    if "graph contains a cycle" not in validate(case):
        print("FAIL cycle was not caught")
        failed += 1
    else:
        print("ok: caught cycle")

    # premise in two domains
    case = json.loads(json.dumps(_GOOD_CASE))
    case["domains"][1]["premise_ids"] = ["P2", "P3"]
    if not any("multiple domains" in e for e in validate(case)):
        print("FAIL multi-domain premise was not caught")
        failed += 1
    else:
        print("ok: caught premise in multiple domains")

    # two value nodes (the defect in codebook v1.2 few-shot Case A)
    case = json.loads(json.dumps(_GOOD_CASE))
    case["value"].append({"id": "V2", "text": "w", "status": "explicit", "evidence_span": "value claim"})
    if not any("exactly one item" in e for e in validate(case)):
        print("FAIL second value node was not caught")
        failed += 1
    else:
        print("ok: caught second value node")

    # dependency links are optional (codebook v1.3 4.4)
    case = json.loads(json.dumps(_GOOD_CASE))
    case["causal_links"] = [l for l in case["causal_links"] if l["type"] != "premise-premise"]
    case["quality"].pop("dependency_pass", None)
    if validate(case):
        print(f"FAIL case without dependency links rejected: {validate(case)}")
        failed += 1
    else:
        print("ok: case without dependency links accepted")

    # codebook 2.0.0 codes a flat P->D->V graph: domain-value edges only
    case = json.loads(json.dumps(_GOOD_CASE))
    case["meta"]["codebook_version"] = "2.0.0"
    if not any("domain-value links only" in e for e in validate(case)):
        print("FAIL dependency link under codebook 2.0.0 was not caught")
        failed += 1
    else:
        print("ok: caught dependency link under codebook 2.0.0")

    case["causal_links"] = [
        l for l in case["causal_links"] if l["type"] == "domain-value"
    ]
    if validate(case):
        print(f"FAIL flat 2.0.0 case rejected: {validate(case)}")
        failed += 1
    else:
        print("ok: flat 2.0.0 case accepted")

    # taxonomy optional in Pass A, validated when present
    case = json.loads(json.dumps(_GOOD_CASE))
    case["domains"][0]["taxonomy"] = "NOT_A_CODE"
    if not any("invalid taxonomy" in e for e in validate(case)):
        print("FAIL invalid taxonomy was not caught")
        failed += 1
    else:
        print("ok: caught invalid taxonomy")

    # span verification against a transcript
    if validate(_GOOD_CASE, _TRANSCRIPT):
        print(f"FAIL verbatim spans rejected: {validate(_GOOD_CASE, _TRANSCRIPT)}")
        failed += 1
    else:
        print("ok: verbatim spans accepted")

    case = json.loads(json.dumps(_GOOD_CASE))
    case["premises"][0]["evidence_span"] = "a claim never spoken in this pitch"
    if not any("not found in transcript" in e for e in validate(case, _TRANSCRIPT)):
        print("FAIL fabricated span was not caught")
        failed += 1
    else:
        print("ok: caught fabricated span")

    case = json.loads(json.dumps(_GOOD_CASE))
    case["premises"][0]["evidence_span"] = "an  ALPHA   claim"
    if any("not found in transcript" in e for e in validate(case, _TRANSCRIPT)):
        print("FAIL whitespace/case normalisation rejected a real span")
        failed += 1
    else:
        print("ok: span matching tolerates whitespace and case")

    case = json.loads(json.dumps(_GOOD_CASE))
    del case["meta"]["model_id"]
    if not any("meta.model_id" in e for e in validate(case)):
        print("FAIL missing model_id was not caught")
        failed += 1
    else:
        print("ok: caught missing model_id")

    case = json.loads(json.dumps(_GOOD_CASE))
    case["meta"]["temperature_controlled"] = False
    if not any("must be null when not controlled" in e for e in validate(case)):
        print("FAIL uncontrolled temperature claiming a value was not caught")
        failed += 1
    else:
        print("ok: caught uncontrolled temperature claiming a value")

    case = json.loads(json.dumps(_GOOD_CASE))
    case["meta"]["temperature_controlled"] = False
    case["meta"]["temperature"] = None
    if validate(case):
        print(f"FAIL honest uncontrolled temperature rejected: {validate(case)}")
        failed += 1
    else:
        print("ok: honest uncontrolled temperature accepted")

    return failed


def self_test_v14() -> int:
    """Additional tests for Pass A1 / A2 introduced in codebook v1.4."""
    failed = 0

    def check(cond: bool, label: str) -> None:
        nonlocal failed
        if cond:
            print(f"ok: {label}")
        else:
            print(f"FAIL {label}")
            failed += 1

    frozen = {
        "meta": {
            "pass": "premises",
            "model_id": "selftest",
            "temperature_controlled": False,
            "temperature": None,
        },
        "premises": [
            {"id": "P1", "text": "a", "status": "explicit", "evidence_span": "alpha claim"},
            {"id": "P2", "text": "b", "status": "explicit", "evidence_span": "beta claim"},
            {"id": "P3", "text": "c", "status": "explicit", "evidence_span": "gamma claim"},
        ],
        "value": [{"id": "V1", "text": "v", "status": "explicit", "evidence_span": "value claim"}],
        "causal_links": [],
        "quality": {"coder_confidence": 0.8},
    }
    check(not validate(frozen, _TRANSCRIPT), "Pass A1 premises accepted")

    bad = json.loads(json.dumps(frozen))
    bad["domains"] = [{"id": "D1", "name": "x", "premise_ids": ["P1"]}]
    check(any("must not include domains" in e for e in validate(bad)), "A1 rejects domains")

    pairs = {
        "meta": {
            "pass": "pairs",
            "wording": "revise_if_false",
            "model_id": "selftest",
            "temperature_controlled": False,
            "temperature": None,
        },
        "pairs": [
            {"premise_a": "P1", "premise_b": "P2", "co_revise": True, "rationale": "t"},
            {"premise_a": "P1", "premise_b": "P3", "co_revise": False, "rationale": "t"},
            {"premise_a": "P2", "premise_b": "P3", "co_revise": False, "rationale": "t"},
        ],
        "quality": {"coder_confidence": 0.7},
    }
    check(not validate(pairs, frozen=frozen), "Pass A2 pairs accepted")

    bad_pairs = json.loads(json.dumps(pairs))
    bad_pairs["pairs"][0]["premise_a"] = "P2"
    bad_pairs["pairs"][0]["premise_b"] = "P1"
    check(
        any("lexicographically" in e for e in validate(bad_pairs, frozen=frozen)),
        "A2 rejects unsorted pair",
    )

    bad_pairs = json.loads(json.dumps(pairs))
    bad_pairs["pairs"] = bad_pairs["pairs"][:2]
    check(
        any("missing" in e for e in validate(bad_pairs, frozen=frozen)),
        "A2 rejects incomplete pair set",
    )

    return failed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", nargs="?", help="directory of extraction JSON files")
    parser.add_argument("--out", default="theory_architecture_measures.csv")
    parser.add_argument("--transcripts", type=Path, help="directory of <case_id>.txt transcripts")
    parser.add_argument(
        "--frozen",
        type=Path,
        help="directory of frozen premise JSONs (required to fully validate Pass A2)",
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--require-model",
        default=None,
        metavar="MODEL_ID",
        help=(
            "reject any JSON whose meta.model_id is not exactly MODEL_ID "
            f"(production lock: {ALLOWED_PRODUCTION_MODEL})"
        ),
    )
    args = parser.parse_args()

    if args.self_test:
        failed = self_test()
        failed += self_test_v14()
        # Model-lock unit check (does not affect default validate path).
        bad_fast = {
            "meta": {
                "model_id": "composer-2.5-fast",
                "temperature_controlled": False,
                "temperature": None,
                "pass": "structure",
            },
            "premises": [],
            "domains": [],
            "value": [{"id": "V1", "text": "x", "status": "explicit", "evidence_span": "x"}],
            "secondary_value": [],
            "causal_links": [],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.5,
            },
            "notes": "",
        }
        lock_errs = validate_provenance(bad_fast, require_model=ALLOWED_PRODUCTION_MODEL)
        if not any("required" in e for e in lock_errs):
            print("FAIL model lock did not reject composer-2.5-fast")
            failed += 1
        else:
            print("ok: model lock rejects composer-2.5-fast")
        print("SELF-TEST PASSED" if not failed else f"SELF-TEST FAILED ({failed})")
        return 1 if failed else 0
    if not args.src:
        parser.error("provide an extraction directory or --self-test")
    return 1 if process_dir(
        Path(args.src),
        Path(args.out),
        args.transcripts,
        args.frozen,
        require_model=args.require_model,
    ) else 0


if __name__ == "__main__":
    sys.exit(main())
