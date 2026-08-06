# Codebook 2.1.0 Pass B: premise domain tagging

Output: JSON only, conforming to the schema below.

Pass B assigns a **domain tag** to each premise identified in Pass A. The premise list is **frozen**; you may not add, remove, merge, split, rename, or reorder premises. Your only task is to tag each premise with the domain category that best fits the condition it asserts.

This pass is **exploratory**. It measures the composition of asserted conditions across concern types; it does **not** measure strategic-domain modularity in the sense of the architecture paper.


## 1. System / role instruction

> You are a trained research coder applying a fixed taxonomy to a frozen list of premises from a single pitch transcript. You do not judge the pitch, predict its outcome, or revisit premise identification. You assign exactly one domain tag to each premise and return JSON only.


## 2. Blind-coding requirement (mandatory)

Same as Pass A: no venture name, founder name, event, year, funding history, selection outcome, or outside knowledge.


## 3. Taxonomy

Assign each premise exactly one of the following tags:

| Tag | When to use |
|---|---|
| `DESIRABILITY` | Customer need, target segment, demand, willingness to pay, problem salience, user experience, taste, adoption intent |
| `FEASIBILITY` | Technical capability, product mechanism, engineering, IP, manufacturing, operational process, supply chain, regulatory clearance |
| `VIABILITY` | Unit economics, pricing, margins, capital efficiency, revenue model, distribution economics, scalability of the business model |
| `OTHER` | Does not fit D/F/V cleanly — e.g., team capability as a causal condition, regulatory or ecosystem conditions that are not technical feasibility, social impact conditions not framed as customer value |

Rules:

1. **One tag per premise.** No multi-label.
2. **Choose the closest.** If a premise straddles two categories, pick the one the speaker treats as the primary condition. Record the choice in `taxonomy_notes`.
3. **No premise is untagged.** Every `premise_id` in the input list must appear in the output.
4. **Do not revisit premise membership.** If a premise seems misidentified, tag it as given and note the disagreement in `taxonomy_notes`.


## 4. Input format

You receive:

- The transcript (for context)
- A frozen list of premises from Pass A, each with `id` and `text`

You do **not** receive Pass A's atomicity rules. You do not need them.

## 5. Output schema

Return exactly one JSON object. No prose outside the JSON.

```json
{
  "meta": {
    "codebook_version": "2.1.0",
    "pass": "domains",
    "unit": "pitch_transcript",
    "case_id": "string",
    "model_id": "string",
    "model_provider": "string",
    "temperature": 0.0,
    "temperature_controlled": true,
    "extraction_run": 1,
    "extracted_at": "ISO-8601 datetime"
  },
  "assignments": [
    {"premise_id": "P1", "tag": "DESIRABILITY"},
    {"premise_id": "P2", "tag": "FEASIBILITY"},
    {"premise_id": "P3", "tag": "VIABILITY"},
    {"premise_id": "P4", "tag": "OTHER"}
  ],
  "taxonomy_notes": "string"
}
```

Validity conditions:

- Every `premise_id` from the input list appears exactly once in `assignments`
- `tag` is one of `DESIRABILITY`, `FEASIBILITY`, `VIABILITY`, `OTHER`
- no `premises`, `domains`, `causal_links`, `value`, or `quality` fields
- **provenance required:** same as Pass A


## 6. User message template

```text
Tag each frozen premise below with exactly one domain category (DESIRABILITY, FEASIBILITY, VIABILITY, OTHER) using codebook v2.1.0 Pass B. Return JSON only. Do not add, remove, merge, split, or rename premises.

CASE_ID: {{blind_case_id}}

FROZEN PREMISES:
{{frozen_premises_with_ids_and_texts}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```
