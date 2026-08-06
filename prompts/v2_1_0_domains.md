# Codebook 2.1.0 Pass C: strategic domain grouping

Pass C sorts the premises from Pass A into groups called strategic domains. The premise list is **fixed**. You may not add, remove, combine, split, rename, or reorder premises. Your only job is to put every premise into exactly one group and give each group a name.

> **Instrument note.** Sections 1 to 5 constitute the coding instrument. Sections 6 to 8 are machine only (input format, output schema, call template). Any revision to sections 1 to 5 constitutes a new codebook version; agreement statistics computed under a prior version do not carry forward.
>
> Sections 1 to 3 define the constructs and are read once during coder training. **Section 4 is the coding protocol for each premise list.** Section 5 provides three worked examples on the same hold-out cases as Pass A.


## 1. Coder role

> You are a trained research coder applying a fixed codebook to a finished list of premises from one pitch transcript. Your task is descriptive measurement, not evaluation: do not assess whether the pitch is persuasive, investable, or likely to succeed, and do not infer its outcome. Do not reconsider how the premises were split. Sort premises into groups.


## 2. Blind-coding requirement

The coding input consists of the finished premise list, transcript text for context, and an anonymous case identifier. It must not include venture name, founder name, event, year, funding history, selection outcome, or other outcome-relevant metadata.

> **Instruction to the model:** The transcript may contain a company or product name. If you recognize the venture, disregard all external knowledge of it, including subsequent funding, growth, acquisition, failure, or competitive performance. Group only the premises as given. Do not reference external knowledge in your output.


## 3. Definitions

### 3.1 Strategic domains within entrepreneurial theory

Entrepreneurial theories comprise premises that can be learned and revised together. A **strategic domain** is a set of premises that the entrepreneur would change as a bundle: fixing one would oblige a change to the others in the same group.

Premises that could be tested or revised on their own belong in **different** domains. Modularity is measured from the resulting partition.

The main coding decision in this pass is therefore **which premises would have to change together** if the theory were revised.


## 4. Coding protocol

This pass groups premises only. Do not add, remove, merge, split, or rename premises.

### 4.1 Procedure

Apply the following steps in order.

1. **Initial read.** Read the frozen premise list and transcript once without grouping.

2. **Compare premise pairs.** For each pair of premises, ask:

   > *If one of these turned out to be wrong, would fixing it force a change to the other as well?*

   Say what the change would actually be before you decide. If fixing one drags the other along, they belong in the **same** domain. If each could change while the other stayed as it is, they belong in **different** domains.

   Where the speaker links one claim to another ("because," "that's why," "this lets us," "so"), that is evidence the two would co-revise. Use these links to decide grouping only. Do not record them in your output.

3. **Form domains.** Collect premises that co-revise into groups. Assign every premise to exactly one domain. No premise is left unassigned. No premise appears in two domains.

4. **Name each domain.** Give each group a short free-text `name` drawn from the speaker's own words. Do not use category or taxonomy labels.

5. **Check presentation order.** If your groups mirror the order the speaker presented things in, or a standard business-plan outline, write in `notes` the evidence that the groups would really change separately. If you cannot point to such evidence, combine them.

6. **When the grouping is still unclear, merge.** Put the two premises in the same domain and write one line in `notes` naming the pair. Never leave a pair undecided.

**No target domain count.** Group only by the co-revision test in step 2. A domain with only one premise is fine when no other premise would have to change along with it; say why in `notes` whenever you keep one.

### 4.2 Worked examples: same domain or separate domains

The following cases apply steps 2 and 3 to recurring premise patterns. They illustrate the protocol; they do not add rules. When a case is not listed, apply steps 2 and 3 directly.

**Same domain** (one repair spills into the other):

- Problem state and the single mechanism offered to solve it when the speaker treats them as one revision: disconnected records and the unified-dashboard promise, when both would be rewritten together if the platform story failed.
- Features that share one integration path: BYOD activation, presence, and transcription from one switch platform.
- Rate opportunity and the recommendation engine that operationalizes it, when both depend on the same energy-optimization module.

**Separate domains** (each premise has its own repair):

- Product mechanism and patent protection: the technology could fail while the IP strategy stayed, or vice versa.
- Technical capability and unit economics: the product could work while margins failed.
- Yield detection and growth-cycle recovery: alerting could work while the agronomic playbook failed.
- Direct-to-consumer economics and OEM licensing: each channel could be revised independently.

Lists often raise this question. Apply the same test: if one change would address every item, the list is one domain; if each item requires its own change, split into separate domains or into single-premise domains.


## 5. Worked examples

Three hold-out cases using the **frozen premise lists from Pass A §5**. These cases are reserved for training and agreement calibration and are **excluded from the confirmatory analysis sample** (see `prompts/registry.md` and `data/corpora/startup_battlefield/samples/calibration_holdouts.csv`).

### 5.1 AgriList (`pilot-773`)

**Frozen premises:** P1–P8 from Pass A §5.1.

**Domains:**

| Domain id | Name | Premise ids |
|---|---|---|
| D1 | Fragmented grower records | P1 |
| D2 | Unified data platform | P2, P3 |
| D3 | Daily grower workflows | P4 |
| D4 | Yield detection and recovery | P5, P6 |
| D5 | Greenhouse energy management | P7, P8 |

**Notes:** P1 stays alone: reframing the problem does not force a change to the platform build. P2 and P3 co-revise because unification and ingestion fail together in practice. P4 is a separate workflow module. P5 and P6 co-revise in the yield-alert loop. P7 and P8 co-revise because rate arbitrage and lighting recommendations share one energy module.

### 5.2 Pi Charging (`pilot-620`)

**Frozen premises:** P1–P6 from Pass A §5.2.

**Domains:**

| Domain id | Name | Premise ids |
|---|---|---|
| D1 | Multi-angle wireless charging | P1 |
| D2 | Patent protection | P2 |
| D3 | FCC-compliant consumer product | P3 |
| D4 | Direct-to-consumer economics | P4, P5 |
| D5 | OEM platform licensing | P6 |

**Notes:** Technology, IP, and regulatory clearance are independently revisable. P4 and P5 co-revise because margin structure and multi-room adoption are the same consumer GTM story. OEM licensing is a separate commercial path.

### 5.3 Tango TV (`pilot-649`, truncated)

**Frozen premises:** P1–P2 from Pass A §5.3.

**Domains:**

| Domain id | Name | Premise ids |
|---|---|---|
| D1 | Local content streaming | P1, P2 |

**Notes:** Thin truncated pitch with only two premises. Local content demand and delivery endpoints co-revise in this fragment because both would change together if the streaming offer failed. A single domain is appropriate here.


## 6. Input format (machine only)

You receive:

- The transcript (for context)
- The finished list of premises from Pass A, each with `id` and `text`

You do not receive Pass A's rules for splitting premises, and you do not need them.


## 7. Output schema (machine only)

Return exactly one JSON object. No prose outside the JSON.

**Worked example (Case 5.1 in JSON).** Domain groupings must match section 5; only the serialization format differs.

```json
{
  "meta": {"codebook_version": "2.1.0", "pass": "strategic_domains", "unit": "pitch_transcript", "case_id": "BLIND_CASE_ID", "model_id": "MODEL_ID", "model_provider": "PROVIDER", "temperature": null, "temperature_controlled": false, "extraction_run": 1, "extracted_at": "ISO-8601"},
  "domains": [
    {"id": "D1", "name": "Fragmented grower records", "premise_ids": ["P1"]},
    {"id": "D2", "name": "Unified data platform", "premise_ids": ["P2", "P3"]},
    {"id": "D3", "name": "Daily grower workflows", "premise_ids": ["P4"]},
    {"id": "D4", "name": "Yield detection and recovery", "premise_ids": ["P5", "P6"]},
    {"id": "D5", "name": "Greenhouse energy management", "premise_ids": ["P7", "P8"]}
  ],
  "notes": "P2+P3 and P5+P6 and P7+P8 co-revise; P1 and P4 stand alone."
}
```

**Schema template:**

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


## 8. User message template (machine only)

```text
Group the frozen premises below into strategic domains using codebook v2.1.0 Pass C. Return JSON only. Do not add, remove, merge, split, or rename premises.

Requirements: premises that must be learned and revised together sit in the same domain; premises that can be tested or revised independently sit in different domains; no domain count is a target; free-text domain names drawn from the transcript; no category or taxonomy labels; every premise assigned to exactly one domain; when still unsure, merge and note the pair.

CASE_ID: {{blind_case_id}}

FROZEN PREMISES:
{{frozen_premises_with_ids_and_texts}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```

`blind_case_id` is a random identifier held in a separate key file. Venture name, event, year, and all outcome variables are joined only after extraction is complete and locked.
