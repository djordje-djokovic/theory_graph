# Prompt registry

| Version | File | Status | Notes |
|---|---|---|---|
| v1.3.2 | `v1_3_2.md` | published (nested k=3) | Structure-only; allows descriptive `secondary_value` (unused in IVs) |
| v1.5.1 | `v1_5_1.md` | published (crossed k=3) | Same as v1.3.2 on value coding |
| v2.0.0 | `v2_0_0.md` | experimental base | Single pass, flat P→D→V graph. Exactly one value node, coding the value the speaker *asserts*; free-text domain names, no taxonomy; verbatim `evidence_span`. Premise-to-domain is membership only; `domain-value` is the sole link type. No dependency layer, `secondary_value`, `epistemic_markers`, or `quality` / `coder_confidence`. |
| v2.1.0 | `v2_1_0_premises.md` + `v2_1_0_dfv.md` + `v2_1_0_domains.md` | experimental multi-pass | **Pass A** (`premises`): premises-only extraction, no domains, no causal links, optional single value node for audit. Strengthened §4.1 atomicity with v1.5.1 enumeration rules. **Pass B** (`dfv`): premise-level DFV+OTHER tagging on frozen Pass A premises — exploratory composition. **Pass C** (`domains`): free-text strategic-domain grouping on frozen Pass A premises — exploratory modularity. |

From v2.0.0 on the validator accepts `domain-value` edges only; `premise-premise`, `premise-domain`, and `domain-domain` links stay valid for v1.3.2 and v1.5.1 runs. Dependency-derived measures (`within_domain_share`, `cross_domain_link_rate`, `n_dep_*`) are therefore empty or zero for v2.0.0 runs, and modularity rests on the partition (`n_domains`, `balance`, `granularity`).

**v2.1.0 drops domains and causal links from Pass A.** The confirmatory IV is breadth (`|premises|`). Pass B (`dfv`) adds composition variables (`breadth_D`, `breadth_F`, `breadth_V`, `breadth_O`, `concentration`, `balance_DFV`) as exploratory descriptives. Pass C (`domains`) adds modularity variables (`n_domains`, `balance`, `granularity`) as exploratory descriptives. Neither Pass B nor Pass C is confirmatory; modularity and permeability are theoretical constructs not tested in this design.

**Prompt design (v2.1.0): one instrument for human and model coders.** The v2.1.0 prompt files are written as a single coding instrument administered to both human and model coders, so that human–model agreement measures coder reliability rather than a difference between two documents. Each file marks an **instrument note** dividing it into two parts:

- **Coding instrument** — role, blind-coding requirement, definitions, coding protocol, few-shot cases (Pass A/B/C §§1–5). Human and model coders receive this text **verbatim and identical**.
- **Machine mechanics** — input format, JSON output schema, user message template (Pass A §§6–7; Pass B §§6–8; Pass C §§6–8). These specify serialization, not coding decisions. Human coders record the same fields on a coding sheet, so omitting them cannot shift a coding judgment.

`theory_graph.prompts.task_header` and `build_user_message` add the provenance and model-lock instructions at call time, so the codebook file itself stays the human-facing document.

Two classes of content are excluded from the instrument for both coder types:

- **Numeric bands.** v1.3.2 stated an expected range ("about 3–8 premises") and coders clustered at 7–8. A stated range biases human coders for the same reason it biases models, and it never helps decide a specific case, so no band appears in either instrument — only the atomicity rules and the statement that narrow and broad theories are equally legitimate. v1.5.1's later prohibition ("do not aim for any band, including 3–8") named the numbers in order to forbid them; v2.1.0 drops the numbers entirely rather than relying on negation.
- **Analysis framing.** Which variables are confirmatory versus exploratory is recorded in this registry, not in the prompts. A coder told that a pass is exploratory may apply it less carefully, and the framing affects no coding decision.

The Pass C **anti-template rule** is retained as a coding rule (§4.6) because dropping it would change domain counts, but it is rewritten so it no longer names the standard three-bucket pitch outline it guards against. It now tests the partition against presentation order and generic business-plan structure, and requires either evidence of separate revisability in `notes` or a merge.

**One test across all three passes (the repair test).** v2.1.0 states the atomicity, taxonomy, and grouping criteria as three applications of a single operational question — what would a disconfirmation oblige the entrepreneur to change?

- **Pass A** individuates premises: different repairs → different premises; one fix for both → one premise.
- **Pass B** tags premises: the tag names the *kind* of thing that would need repair (demand, delivery, economics).
- **Pass C** groups premises: a repair that spills over from one premise to another → same domain.

This replaces an earlier structure in which Pass A carried eight "boundary clarifications," each of which ended in the same escape clause ("unless the speaker treats it as separately revisable"). Those eight were not eight rules; they were one judgment restated eight times, with the cognitive cost of a large rule set and the reliability of a single vague test, plus an ordering dependency ("apply these before the tie-break") and a live conflict between the clarification covering listed features and the one covering capability enumerations. They are now **grain precedents** — worked applications of the test, split into a "one premise" list and a "separate premises" list, carrying no independent authority — and the conflict is resolved on the face of the lists: a list of items is one premise when they share a fix and separate premises when each has its own.

**§4 is the working instrument for both coder types.** Pass A §4 is written as the sheet a coder actually works from: a seven-step procedure with the exclusion list inline at step 3 (so no step sends the coder to a section defined later), followed by the common cases as a scannable two-list lookup. The grain decision is split into "write down what would have to change" and "group claims by what you wrote," which replaces a two-branch counterfactual comparison with an artifact the coder produces and then matches — the more reliable operation. Rationale moved up into §3, which is read once during training.

The instrument sections are written in plain language throughout, on the view that a term a coder has to decode is a term two coders can decode differently. Words such as *atomicity*, *individuate*, *unit of architecture*, *co-revisability*, *taxonomy*, and *tie-break* appear in this registry but nowhere a coder has to act on them. Pass B's tags are no longer called "domain tags," which collided with Pass C's strategic domains. The precedents are deliberately *not* split into a separate human-facing summary: most of them resolve toward "one premise," so giving them to one coder type and not the other would shift the mean of measured breadth rather than merely add scatter, biasing the agreement statistic instead of widening it. One document, both coders.

The test is chosen to make coders *produce* something (a named repair) rather than *judge* something, which is the more reliable operation, and it matches the construct directly, since the paper treats premises as the units to which prediction errors are attributed.

**Terminal tie-breaks (no undecided cases).** Each pass ends in a mandatory default, so no coding decision is left open:

| Pass | Default when still unsure | Rationale |
|---|---|---|
| A (premises) | **Split** | Protects breadth from under-counting distinct failure points |
| B (dfv) | Fixed precedence `DESIRABILITY` → `FEASIBILITY` → `VIABILITY`, runner-up recorded as `alt:<TAG>` in `taxonomy_notes` | Deterministic, disclosed, and re-testable |
| C (domains) | **Merge** | Prevents an uncertain judgment from manufacturing modularity the transcript does not support |

The A/C asymmetry is deliberate and should be reported as such. The Pass B `alt:` convention exists so ambiguous tags can be flipped in a sensitivity analysis; report composition results under both assignments.

**Prompt design excludes two classes of content** for both coder types. Numeric bands: v1.3.2 stated an expected range ("about 3–8 premises") and coders clustered at 7–8. A stated range biases human coders for the same reason it biases models and never helps decide a specific case, so no band appears in either instrument — only the procedure and the statement that narrow and broad theories are equally legitimate. v1.5.1's later prohibition ("do not aim for any band, including 3–8") named the numbers in order to forbid them; v2.1.0 drops them entirely rather than relying on negation. Analysis framing: which variables are confirmatory versus exploratory is recorded here, not in the prompts, because a coder told a pass is exploratory may apply it less carefully while the framing affects no coding decision.

The Pass C **anti-template rule** is retained as a coding rule because dropping it would change domain counts, but it no longer names the standard three-bucket pitch outline it guards against; it tests the partition against presentation order and generic business-plan structure instead.

**Agreement protocol.** Record the prompt version the human coders worked from alongside every agreement statistic. Because the instrument sections are the shared document, any edit to them is a new codebook version, and agreement computed under the previous version does not carry over to the new one.

Report reliability as three quantities, not one:

1. **Within-model**, across the k=3 runs on an identical prompt. Isolates instrument ambiguity as the model experiences it and is already produced by the pipeline.
2. **Within-human**, from two independent coders on a pilot subsample.
3. **Human–model**, the statistic of interest.

Human–model agreement is bounded above by roughly `sqrt(r_hh * r_ll)`, so reporting all three distinguishes an attenuation ceiling from a model failure. For breadth — a count, and the confirmatory IV — report count-level agreement (ICC or Krippendorff's alpha for ratio data, plus mean absolute difference), which avoids the premise-alignment problem entirely. Code independently, reconcile, report pre-reconciliation agreement, and compare the model against the adjudicated standard. Train human coders on the precedent table and few-shot cases using a practice set held out of the analysis sample.

**Calibration hold-outs (Pass A/B/C §5).** The three worked examples in each v2.1.0 prompt file §5 use the same hold-out cases, the same verbatim transcripts, and the same frozen premise lists. Each pass is self-contained for training and agreement calibration: Pass A §5 adds evidence spans and value; Pass B §5 adds composition tags; Pass C §5 adds domain groupings. Transcripts are from corpus files, not composite teaching text. All three are complete pitches (`truncated=0`). They serve the same pedagogical roles as earlier codebook versions (broad multi-premise, narrow product-and-IP, thin complete pitch) but are anchored to real cases:

| §5 case | Corpus `case_id` | Venture | Teaching profile |
|---|---|---|---|
| 5.1 | `pilot-65` | ByteKnight (ByteNite) | Broad theory: distributed compute, supply-side incentives, sustainability (~286 words) |
| 5.2 | `pilot-620` | Pi Charging | Narrow theory: product form, IP/regulatory protection, go-to-market (excerpt) |
| 5.3 | `pilot-11` | Akowe | Thin complete pitch: credential fraud, issuance, verification, mobile wallet (~218 words) |

Listed in `data/corpora/startup_battlefield/samples/calibration_holdouts.csv`. Exclude these `case_id`s from confirmatory analysis samples and from any model encoding run whose results feed confirmatory IVs. Human–model agreement on §5 may use the reference keys in the prompt; agreement on the analysis sample must not include these cases.

Because v2.0.0 drops the model-coded `quality.truncated` flag, the `truncated` control is derived from the transcript instead (`theory_graph.validate.transcript_truncated`). Runs from v1.3.2 and v1.5.1 keep using their coded flag, which is why the reference outputs still reproduce exactly.

An earlier draft also labeled v2.0.0 (with `secondary_value` and quality fields) existed briefly in git before the rewrite; it was never a published baseline.

To try a change: copy a file (`copy prompts\v2_1_0_premises.md prompts\v2_1_1_premises.md`), edit it, set `experiment.prompt_version: v2_1_1_premises` and `experiment.run_id` in your config, and run `theory-graph init`.
