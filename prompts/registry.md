# Prompt registry

| Version | File | Status | Notes |
|---|---|---|---|
| v1.3.2 | `v1_3_2.md` | published (nested k=3) | Structure-only; allows descriptive `secondary_value` (unused in IVs) |
| v1.5.1 | `v1_5_1.md` | published (crossed k=3) | Same as v1.3.2 on value coding |
| v2.0.0 | `v2_0_0.md` | experimental base | Single pass, flat P→D→V graph. Exactly one value node, coding the value the speaker *asserts*; free-text domain names, no taxonomy; verbatim `evidence_span`. Premise-to-domain is membership only; `domain-value` is the sole link type. No dependency layer, `secondary_value`, `epistemic_markers`, or `quality` / `coder_confidence`. |
| v2.1.0 | `v2_1_0_premises.md` + `v2_1_0_dfv.md` + `v2_1_0_domains.md` | experimental multi-pass | **Pass A** (`premises`): premises-only extraction, no domains, no causal links, optional single value node for audit. Strengthened §4.1 atomicity with v1.5.1 enumeration rules. **Pass B** (`dfv`): premise-level DFV+OTHER tagging on frozen Pass A premises — exploratory composition. **Pass C** (`domains`): free-text strategic-domain grouping on frozen Pass A premises — exploratory modularity. |

From v2.0.0 on the validator accepts `domain-value` edges only; `premise-premise`, `premise-domain`, and `domain-domain` links stay valid for v1.3.2 and v1.5.1 runs. Dependency-derived measures (`within_domain_share`, `cross_domain_link_rate`, `n_dep_*`) are therefore empty or zero for v2.0.0 runs, and modularity rests on the partition (`n_domains`, `balance`, `granularity`).

**v2.1.0 drops domains and causal links from Pass A.** The confirmatory IV is breadth (`|premises|`). Pass B (`dfv`) adds composition variables (`breadth_D`, `breadth_F`, `breadth_V`, `breadth_O`, `concentration`, `balance_DFV`) as exploratory descriptives. Pass C (`domains`) adds modularity variables (`n_domains`, `balance`, `granularity`) as exploratory descriptives. Neither Pass B nor Pass C is confirmatory; modularity and permeability are theoretical constructs not tested in this design.

Because v2.0.0 drops the model-coded `quality.truncated` flag, the `truncated` control is derived from the transcript instead (`theory_graph.validate.transcript_truncated`). Runs from v1.3.2 and v1.5.1 keep using their coded flag, which is why the reference outputs still reproduce exactly.

An earlier draft also labeled v2.0.0 (with `secondary_value` and quality fields) existed briefly in git before the rewrite; it was never a published baseline.

To try a change: copy a file (`copy prompts\v2_1_0_premises.md prompts\v2_1_1_premises.md`), edit it, set `experiment.prompt_version: v2_1_1_premises` and `experiment.run_id` in your config, and run `theory-graph init`.
