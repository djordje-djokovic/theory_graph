# Prompt registry

| Version | File | Status | Notes |
|---|---|---|---|
| v1.3.2 | `v1_3_2.md` | published (nested k=3) | Structure-only; allows descriptive `secondary_value` (unused in IVs) |
| v1.5.1 | `v1_5_1.md` | published (crossed k=3) | Same as v1.3.2 on value coding |
| v2.0.0 | `v2_0_0.md` | experimental base | Single pass, flat P→D→V graph. Exactly one value node, coding the value the speaker *asserts*; free-text domain names, no taxonomy; verbatim `evidence_span`. Premise-to-domain is membership only; `domain-value` is the sole link type. No dependency layer, `secondary_value`, `epistemic_markers`, or `quality` / `coder_confidence`. |
| v2.1.1 | `v2_1_1_premises.md` + `v2_1_0_dfv.md` + `v2_1_0_domains.md` | experimental, Pass A revision | Pass A §4 only; Pass B and Pass C files unchanged. Constrains the **scale** of the change named in §4.1 step 4, gates the step 6 tie-break behind steps 4–5, and adds a balanced pair of demonstration precedents to §4.2. Terminal defaults, exclusions, the value criterion, and §§6–7 are unchanged. See § Pass A revision v2.1.1 below. |
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

**Codebook files are the audit record for a version.** Only the config was frozen into an experiment folder; codebook text was read live from `prompts/`, so editing a file in place silently detached completed runs from the text that produced them. `theory-graph init` (and any later pass registration) now copies each pass's codebook file into `<run>/prompts/`, and encoding reads that frozen copy when it exists. v2.1.0 is therefore left exactly as the `battle_n20_k3_qwen3_32b` runs encoded it, and every revision below is a new file. Runs created before snapshots existed fall back to the shared `prompts/` tree, so their reproducibility still rests on v2.1.0 not being edited.

**Computational environment.** Model name and temperature do not identify a locally served model: quantization changes token selection and the serving version changes defaults, so two runs of `qwen3:32b` at temperature 0 are not necessarily the same instrument. Each encoding session therefore captures its environment to `<run>/environment.jsonl` — inference settings, Ollama version, quantization level, parameter size, weight format, model digest, native context length, Python and platform, and versions of the packages that touch the numbers. A record is appended only when it differs from the previous one, so the file also documents environment drift across resumed sessions. A compact identity subset — `num_ctx`, `max_tokens`, Ollama version, quantization level, parameter size, digest — is stamped into every encoding's `meta.environment`, so a single JSON file remains self-describing.

Probing is best-effort and never fails a run; when the server cannot be reached the record states that instead of omitting the field. For the pilot battery the instrument is `qwen3:32b` at **Q4_K_M** (4-bit, 32.8B parameters, GGUF) served by Ollama 0.32.5 with `num_ctx` 16384 against a native context length of 40960, which must be reported as such rather than as `qwen3:32b`. Both pilot batteries predate this capture and their records are marked `captured_retroactively` with the reason; the digest identifies the same weights, while the machine fields were not observed at encode time.

`meta.temperature` and `meta.temperature_controlled` are now written by the harness, which knows what it sent, rather than accepted from the model's own account of its sampling. Encodings made before this change carry the model's self-report and one file failed provenance validation as a result.

**Level of measurement for count agreement.** Breadth and `n_domains` are counts with a true zero, and this section prescribes ratio-level alpha for breadth, so `theory_graph.reliability` computes alpha at `ratio`. Because alpha on a count is depressed by between-case range restriction — breadths in the pilot cluster near the grand mean — the **mean absolute difference** between runs is reported alongside alpha as prescribed, and the interval-level alpha is disclosed as a sensitivity check in every generated report. The choice is not directional: on the same pilot data the ratio figure is higher for breadth (0.565 vs 0.397) and lower for `n_domains` (0.717 vs 0.759).

**Aggregation and attenuation.** The analysed IV is not a single run: `aggregate.py` records `breadth` as the **median of the k runs**, keeps per-case dispersion in `breadth_run_sd`, and `_consensus_premises` freezes the run nearest the median breadth as the premise list Passes B and C receive. Single-run alpha therefore understates the reliability of the variable actually regressed, and every reliability report now states both. On `battle_n20_k3_v211_qwen3_32b` the single run is α = 0.619 (ratio) while the median of three is **0.830** by Spearman-Brown, or 0.550 and 0.786 at interval level.

Spearman-Brown is exact for the mean of k and the pipeline aggregates by median, so the aggregate figures are approximations to be read as upper bounds, the median of three being slightly noisier than their mean. Median is retained deliberately: it is what stops one runaway run — `pilot-828` at 15 premises under v2.1.0 — from moving a case. Single-run alpha is reported as the conservative floor.

Because error in an independent variable biases coefficients toward zero, breadth effects from this data are attenuated rather than inflated: an observed association is a lower bound, and a null is weaker evidence of absence than it would be under perfect measurement. The implied ceiling on an observed correlation is sqrt of the aggregate reliability, 0.911 under v2.1.1, and reports state it so a coefficient can be disattenuated. Aggregation removes random error only; systematic over- or under-splitting is shared across runs of one model and survives the median, which is what human–model agreement is required to detect.

**Span verification.** `validate.normalise` folds typographic quote and dash variants before comparison, because §4.1 step 7 already allows spacing and capitalisation to differ so long as the words match, and a curly apostrophe is not a different word. Span failures are now logged as either an ellipsis splice or a span absent from the transcript; both were invalid before and remain invalid, so no run's validity changes. The split matters because it identifies the failure: on `battle_n20_k3_qwen3_32b` (60 premises files, v2.1.0), **42 of the 45 invalid files fail on ellipsis splicing and 3 on a span genuinely absent from the transcript**. The dominant validity failure is quotation mechanics, not fabricated or paraphrased evidence.

Report reliability as three quantities, not one:

1. **Within-model**, across the k=3 runs on an identical prompt. Isolates instrument ambiguity as the model experiences it and is already produced by the pipeline.
2. **Within-human**, from two independent coders on a pilot subsample.
3. **Human–model**, the statistic of interest.

Human–model agreement is bounded above by roughly `sqrt(r_hh * r_ll)`, so reporting all three distinguishes an attenuation ceiling from a model failure. For breadth — a count, and the confirmatory IV — report count-level agreement (ICC or Krippendorff's alpha for ratio data, plus mean absolute difference), which avoids the premise-alignment problem entirely. Code independently, reconcile, report pre-reconciliation agreement, and compare the model against the adjudicated standard. Train human coders on the precedent table and few-shot cases using a practice set held out of the analysis sample.

**Pass A revision v2.1.1.** Within-model reliability on `battle_n20_k3_qwen3_32b` (20 cases, k=3, `qwen3:32b`) put breadth at α = 0.565 (ratio) with a mean absolute difference of 1.67 premises between runs. Inspection of the per-case table located the disagreement in a specific place: 14 of 20 cases had all three runs within two premises, while the spread was carried by demonstration-heavy and list-heavy pitches — `pilot-828` at 6/6/15, `pilot-706` at 10/8/5, `pilot-928` at 13/8/8. In the 15-premise run of `pilot-828` each beat of a product walkthrough became its own premise; in the 6-premise runs the same walkthrough was coded as the capability being shown.

The diagnosis is that step 4 asked for a named change but set no scale for it, so the artifact steps 4 and 5 compare was itself produced at different grains by different runs. v2.1.1 therefore constrains the artifact rather than the judgment made from it:

| Change | Section | Rationale |
|---|---|---|
| The change must be stated as work the venture would carry out, at the scale the venture would carry it out; work completed *in the course of* a change already written is not a separate change; an item the pitch presents as separately built, or droppable while the rest stood, is work of its own | §4.1 step 4 | Extends the registry's existing reason for choosing the repair test — that coders should *produce* something rather than *judge* something — to the grain of what they produce. The added clauses are two-sided: one bounds subdivision, the other bounds merging. |
| The tie-break is reached only after the changes are written in step 4 and compared in step 5, and the undecided pair plus both changes are named in `notes` | §4.1 step 6 | The default direction is unchanged and remains **Split**. What changes is that the tie-break can no longer substitute for performing the test, and each invocation leaves an auditable record. Its trigger was previously self-assessed and unrecorded, which is what allowed it to fire at different rates across runs of the same pitch. |
| One demonstration precedent added to the "one premise" list and one to the "several premises" list; a closing paragraph applies the step 4 scale to walkthroughs | §4.2 | Deliberately balanced. This registry notes that the precedents mostly resolve toward "one premise" and that shifting that balance would move the mean of measured breadth rather than merely add scatter, so a merge-side precedent is not added without its separate-side counterpart. |

Two commitments are deliberately **not** revised. The Pass A terminal default stays **Split**, with its stated rationale of protecting breadth from under-counting distinct failure points, and the Pass A/Pass C asymmetry stays reportable as such. No numeric band, target count, or expected range is introduced, and §5 gains no additional worked example, so the anchoring that made v1.3.2 coders cluster at 7–8 is not reintroduced by a different route.

Because §§1–5 changed, agreement computed under v2.1.0 does not carry forward: v2.1.1 requires its own k=3 within-model run, and any human coding used for human–model agreement must be collected against the v2.1.1 text.

**Measured effect (`battle_n20_k3_v211_qwen3_32b`, same 20 cases, same model and sampling as the v2.1.0 battery, Pass A codebook the only difference).**

| | v2.1.0 | v2.1.1 |
|---|---|---|
| Krippendorff α, breadth, ratio | 0.565 | 0.619 |
| Krippendorff α, breadth, interval | 0.397 | 0.550 |
| Mean absolute difference, premises | 1.67 | 1.37 |
| Mean within-case range, premises | 2.50 | 2.05 |
| Content match share | 0.426 | 0.440 |
| **Mean breadth** | **6.70** | **6.55** |

Agreement improved while mean breadth moved 0.15 premises, so the revision tightened reliability without materially relocating the confirmatory IV — the outcome the two-sided formulation of the step 4 clauses was intended to produce. The gain is larger at interval level (+0.153) than at ratio (+0.054) because interval penalises large absolute deviations and the revision removed the extreme case: `pilot-828` went from 6/6/15 to 10/5/8 and `pilot-928` from 13/8/8 to 10/7/9, with no run producing a runaway feature enumeration. Two cases became unanimous. Against that, cases with a range of two or fewer fell from 14 to 13, so the revision traded extreme outliers for slightly more mid-range scatter, and breadth α remains below the 0.667 tentative threshold. The three §4 changes were introduced together and their contributions are not separately identified.

**Null result on evidence-span quotation (not carried into v2.1.1).** An earlier draft of v2.1.1 added an explicit prohibition on ellipsis-spliced spans to §§6–7, restating the contiguity requirement §4.1 step 7 already imposes. It had no effect: ellipsis-spliced spans went from 114/462 (24.7%) under v2.1.0 to 127/453 (28.0%) under the draft, files with no spliced span stayed at 18/60, and premises validity stayed at 25%. The instruction was therefore removed and §§6–7 left identical to v2.1.0, so v2.1.1 is a single-purpose revision of the §4 grain rules. The k=3 run above was encoded while that instruction was still present; the text actually sent is preserved in `experiments/battle_n20_k3_v211_qwen3_32b/prompts/`. Because a rule that is merely restated more prominently should respond to the restatement if the failure were one of instrument clarity, the null result indicates the failure is one of model compliance instead, and it is recorded as a limitation of `qwen3:32b` rather than of the codebook. Splicing is a validity defect confined to the audit trail: spans are not inputs to breadth, to Pass B tags, or to Pass C groupings, and ellipsis rate does not track breadth disagreement across cases.

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
