# Codebook 2.1.0 Pass C: strategic domain grouping

Output: JSON only, conforming to the schema below.

Pass C groups the frozen premises from Pass A into strategic domains. The premise list is **fixed**; you may not add, remove, merge, split, rename, or reorder premises. Your only task is to assign every premise to exactly one domain and name each domain.

This pass is **exploratory**. It measures the partition of premises into co-revisability modules; it does **not** test the modularity propositions of the architecture paper.


## 1. System / role instruction

> You are a trained research coder applying a fixed codebook to a frozen list of premises from a single pitch transcript. You do not judge the pitch, predict its outcome, or revisit premise identification. You group premises into strategic domains and return JSON only.


## 2. Blind-coding requirement (mandatory)

Same as Pass A: no venture name, founder name, event, year, funding history, selection outcome, or outside knowledge.


## 3. Definitions

A **strategic domain** is a coherent module of related premises that can be learned and revised **together**. Premises inside a domain are tightly affiliated toward illuminating a coherent part of the theory. Premises that can be tested or revised **independently** belong in different domains.

Judge co-revisability from the transcript: where the speaker presents one condition as a prerequisite for another ("because," "that's why," "this lets us," "so"), that is evidence the two premises belong in the same domain. Such dependencies inform the partition only; they are **not** coded as edges.


## 4. Coding rules

1. **Assign every premise to exactly one domain.** No premise is left unassigned. No premise appears in two domains.
2. **No domain count is a target.** A theory that supports one coherent bundle receives one domain. A theory with five independently learnable parts receives five.
3. **Give each domain a short free-text `name`** drawn from the transcript's own vocabulary. Do **not** assign category or taxonomy labels.
4. **Singleton rule.** A single-premise domain is legitimate only when that premise is an independently learnable mechanism with its own claimed role in the theory. If it is instead a detail of another bundle, merge it. State the reason in `notes` whenever a singleton is retained.
5. **Anti-template rule.** Do not impose a habitual pitch template. If your partition happens to be exactly three domains corresponding to customer need, product/technology, and money/channel, add one sentence to `notes` citing transcript evidence that these are three separately revisable modules. If you cannot, merge.
6. **Do not create a domain** merely because two premises concern the same topic in passing; a domain is a part of the theory that could be revised as a unit.


## 5. Input format

You receive:

- The transcript (for context)
- A frozen list of premises from Pass A, each with `id` and `text`

You do **not** receive Pass A's atomicity rules. You do not need them.


## 6. Output schema

Return exactly one JSON object. No prose outside the JSON.

```json
{
  "meta": {
    "codebook_version": "2.1.0",
    "pass": "strategic_domains",
    "unit": "pitch_transcript",
    "case_id": "string",
    "model_id": "string",
    "model_provider": "string",
    "temperature": 0.0,
    "temperature_controlled": true,
    "extraction_run": 1,
    "extracted_at": "ISO-8601 datetime"
  },
  "domains": [
    {"id": "D1", "name": "string", "premise_ids": ["P1", "P2"]},
    {"id": "D2", "name": "string", "premise_ids": ["P3"]}
  ],
  "notes": "string"
}
```

Validity conditions:

- Every `premise_id` from the input list appears in exactly one `domains[].premise_ids`
- No `premise_id` appears in two domains
- `id` values start with `D` and are unique
- `name` is free text (no taxonomy labels)
- no `premises`, `causal_links`, `value`, `assignments`, or `quality` fields
- **provenance required:** same as Pass A


## 7. User message template

```text
Group the frozen premises below into strategic domains using codebook v2.1.0 Pass C. Return JSON only. Do not add, remove, merge, split, or rename premises.

Requirements: premises that must be learned and revised together sit in the same domain; premises that can be tested or revised independently sit in different domains; no domain count is a target; free-text domain names drawn from the transcript; no category or taxonomy labels; every premise assigned to exactly one domain.

CASE_ID: {{blind_case_id}}

FROZEN PREMISES:
{{frozen_premises_with_ids_and_texts}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```
