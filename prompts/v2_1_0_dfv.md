# Codebook 2.1.0 Pass B: composition tagging

Pass B assigns one composition tag to each premise from Pass A. The premise list is **fixed**. You may not add, remove, combine, split, rename, or reorder premises. Your only job is to tag each premise with exactly one of the four labels below.

> **Instrument note.** Sections 1 to 5 constitute the coding instrument. Sections 6 to 8 are machine only (input format, output schema, call template). Any revision to sections 1 to 5 constitutes a new codebook version; agreement statistics computed under a prior version do not carry forward.
>
> Sections 1 to 3 define the constructs and are read once during coder training. **Section 4 is the coding protocol for each premise list.** Section 5 provides three worked examples on the same hold-out cases as Pass A.


## 1. Coder role

> You are a trained research coder applying a fixed set of tags to a finished list of premises from one pitch transcript. Your task is descriptive measurement, not evaluation: do not assess whether the pitch is persuasive, investable, or likely to succeed, and do not infer its outcome. Do not reconsider how the premises were split. Give each premise exactly one tag.


## 2. Blind-coding requirement

The coding input consists of the finished premise list, transcript text for context, and an anonymous case identifier. It must not include venture name, founder name, event, year, funding history, selection outcome, or other outcome-relevant metadata.

> **Instruction to the model:** The transcript may contain a company or product name. If you recognize the venture, disregard all external knowledge of it, including subsequent funding, growth, acquisition, failure, or competitive performance. Tag only the premises as given. Do not reference external knowledge in your output.


## 3. Definitions

### 3.1 Composition tagging within entrepreneurial theory

Pass A extracts premises — conditions the entrepreneur treats as necessary for value. Pass B names the **kind of condition** each premise asserts: demand, deliverability, economics, or something outside those three.

### 3.2 The four tags

| Tag | When to use |
|---|---|
| `DESIRABILITY` | Customer need, target segment, demand, willingness to pay, problem salience, user experience, taste, adoption intent |
| `FEASIBILITY` | Technical capability, product mechanism, engineering, IP, manufacturing, operational process, supply chain, regulatory clearance |
| `VIABILITY` | Unit economics, pricing, margins, capital efficiency, revenue model, distribution economics, scalability of the business model |
| `OTHER` | Does not fit D/F/V cleanly. For example: team capability treated as a causal condition, regulatory or ecosystem conditions that are not technical feasibility, social impact conditions not framed as customer value |

The main coding decision in this pass is therefore **what kind of repair each premise requires if it turns out to be wrong**.


## 4. Coding protocol

This pass tags premises only. Do not add, remove, merge, split, or rename premises.

### 4.1 Procedure

Apply the following steps in order.

1. **Initial read.** Read the frozen premise list and transcript once without tagging.

2. **State what would fail.** For each premise, write briefly what would have turned out false if the premise were wrong (e.g., *customers do not want this*, *the product cannot be built or delivered*, *the economics do not work*).

3. **Assign one tag.** Match the failure you wrote to one tag:
   - demand or adoption fails → `DESIRABILITY`
   - build, delivery, operations, IP, or regulatory clearance fails → `FEASIBILITY`
   - pricing, margins, revenue model, or business-model economics fail → `VIABILITY`
   - none of the above cleanly → `OTHER`

   Tag the **failure**, not the nouns in the sentence. *"Customers will pay $50 a month"* fails as a claim about demand, so it is `DESIRABILITY`, even though it mentions a price.

4. **Resolve ties.** If two of `DESIRABILITY`, `FEASIBILITY`, and `VIABILITY` fit equally well, take the first in this order: `DESIRABILITY`, then `FEASIBILITY`, then `VIABILITY`. Record the tag you did not choose in `taxonomy_notes` as `alt:<TAG>`.

5. **Record each assignment.** Every `premise_id` in the input list must appear exactly once in `assignments`. If a premise seems misidentified, tag it as given and note the disagreement in `taxonomy_notes`.

**Rules that apply throughout:**

- **One tag per premise.** No multi-label.
- **`OTHER` is not a tie-break.** Use it only when a premise falls outside D/F/V, not when the choice between D, F, and V is hard.
- **When still unsure after step 4, keep the precedence default** and record `alt:<TAG>`. Never leave a premise untagged.

### 4.2 Worked examples: which tag fits

The following cases apply steps 2 and 3 to recurring premise patterns. They illustrate the protocol; they do not add rules. When a case is not listed, apply steps 2 and 3 directly.

**`DESIRABILITY`** (demand or adoption would fail):

- Problem or pain the customer faces: *"parents face five major pain points."*
- Target segment or use case: *"sports fans are the target buyers."*
- Willingness to pay framed as demand: *"customers will pay $50 a month."*
- User experience or taste: *"people love the flavor."*

**`FEASIBILITY`** (build, delivery, operations, IP, or clearance would fail):

- Product mechanism or technical capability: *"a single 30-second phone scan replaces in-person measurement."*
- Patent, license, or regulatory clearance: *"we have a patent," "FCC compliant."*
- Operational process or integration: *"all grower data syncs into one platform."*
- Feature or module the venture must deliver: *"task manager tracks harvest and seeding."*

**`VIABILITY`** (economics or business model would fail):

- Margins, pricing, or unit economics: *"over 50% gross margins."*
- Revenue model or channel economics: *"sell through stadium concession stands."*
- Scalability of the business model: *"OEM licensing extends the platform."*
- Cost savings counted as business payoff: *"save $50,000 annually on electricity."*

**`OTHER`** (outside D/F/V):

- Founder team treated as a causal condition rather than credibility garnish.
- Ecosystem or policy conditions not framed as customer value or technical delivery.

When a premise mentions both a mechanism and its economic payoff, tag the failure that would matter first. A recommendation engine that fails to save money is primarily a `FEASIBILITY` failure (the mechanism does not work); record `alt:VIABILITY` when economics are also central.


## 5. Worked examples

Three hold-out cases using the **frozen premise lists from Pass A §5**. These cases are reserved for training and agreement calibration and are **excluded from the confirmatory analysis sample** (see `prompts/registry.md` and `data/corpora/startup_battlefield/samples/calibration_holdouts.csv`).

### 5.1 AgriList (`pilot-773`)

**Frozen premises:** P1–P8 from Pass A §5.1.

**Tags:**

| Premise id | Tag | Rationale |
|---|---|---|
| P1 | `FEASIBILITY` | Current disconnected records cannot support operational decisions |
| P2 | `FEASIBILITY` | Unified data platform must deliver operational clarity |
| P3 | `FEASIBILITY` | Ingestion from sensors, uploads, and manual entry must work |
| P4 | `FEASIBILITY` | Task-management module must track daily grower workflows |
| P5 | `FEASIBILITY` | Yield-problem detection must work early enough to act |
| P6 | `FEASIBILITY` | Growth-cycle adjustment must recover from yield problems |
| P7 | `VIABILITY` | Time-varying electricity rates must create usable savings opportunities |
| P8 | `FEASIBILITY` | Recommendation engine must produce the claimed energy savings; `alt:VIABILITY` |

**Notes:** P7 is tagged `VIABILITY` because the failure is that rate structures do not create arbitrage value. P8 is primarily a delivery failure (recommendations do not save money); economics are secondary.

### 5.2 Pi Charging (`pilot-620`)

**Frozen premises:** P1–P6 from Pass A §5.2.

**Tags:**

| Premise id | Tag | Rationale |
|---|---|---|
| P1 | `FEASIBILITY` | Multi-angle magnetic charging must work as claimed |
| P2 | `FEASIBILITY` | Patent must protect the wireless-power approach |
| P3 | `FEASIBILITY` | Product must meet FCC safety requirements |
| P4 | `VIABILITY` | Direct-to-consumer margins must sustain the business |
| P5 | `VIABILITY` | Multi-room adoption must extend customer lifetime value |
| P6 | `VIABILITY` | OEM licensing must work as a revenue path |

**Notes:** Product, IP, and regulatory premises are `FEASIBILITY`; go-to-market and licensing premises are `VIABILITY`. Pass A already separated these failure types into distinct premises.

### 5.3 Tango TV (`pilot-649`, truncated)

**Frozen premises:** P1–P2 from Pass A §5.3.

**Tags:**

| Premise id | Tag | Rationale |
|---|---|---|
| P1 | `DESIRABILITY` | Local audiences must want local movies, TV, and music |
| P2 | `FEASIBILITY` | Mobile and TV delivery endpoints must work |

**Notes:** Thin truncated pitch; tag only the premises given. Financing in the excerpt is excluded in Pass A and is not tagged here.


## 6. Input format (machine only)

You receive:

- The transcript (for context)
- The finished list of premises from Pass A, each with `id` and `text`

You do not receive Pass A's rules for splitting premises, and you do not need them.


## 7. Output schema (machine only)

Return exactly one JSON object. No prose outside the JSON.

**Worked example (Case 5.1 in JSON).** Tag assignments must match section 5; only the serialization format differs.

```json
{
  "meta": {"codebook_version": "2.1.0", "pass": "dfv", "unit": "pitch_transcript", "case_id": "BLIND_CASE_ID", "model_id": "MODEL_ID", "model_provider": "PROVIDER", "temperature": null, "temperature_controlled": false, "extraction_run": 1, "extracted_at": "ISO-8601"},
  "assignments": [
    {"premise_id": "P1", "tag": "FEASIBILITY"},
    {"premise_id": "P2", "tag": "FEASIBILITY"},
    {"premise_id": "P3", "tag": "FEASIBILITY"},
    {"premise_id": "P4", "tag": "FEASIBILITY"},
    {"premise_id": "P5", "tag": "FEASIBILITY"},
    {"premise_id": "P6", "tag": "FEASIBILITY"},
    {"premise_id": "P7", "tag": "VIABILITY"},
    {"premise_id": "P8", "tag": "FEASIBILITY"}
  ],
  "taxonomy_notes": "P8: alt:VIABILITY — savings claim is secondary to recommendation delivery."
}
```

**Schema template:**

```json
{
  "meta": {
    "codebook_version": "2.1.0",
    "pass": "dfv",
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
    {"premise_id": "P1", "tag": "DESIRABILITY|FEASIBILITY|VIABILITY|OTHER"}
  ],
  "taxonomy_notes": "string"
}
```

Validity conditions:

- Every `premise_id` from the input list appears exactly once in `assignments`
- `tag` is one of `DESIRABILITY`, `FEASIBILITY`, `VIABILITY`, `OTHER`
- no `premises`, `domains`, `causal_links`, `value`, or `quality` fields
- **provenance required:** same as Pass A


## 8. User message template (machine only)

```text
Tag each frozen premise below with exactly one composition tag (DESIRABILITY, FEASIBILITY, VIABILITY, OTHER) using codebook v2.1.0 Pass B. Return JSON only. Do not add, remove, merge, split, or rename premises.

Requirements: tag the kind of failure each premise asserts — demand, deliverability, economics, or other; one tag per premise; when two of D/F/V fit equally, use precedence DESIRABILITY then FEASIBILITY then VIABILITY and record alt:<TAG> in taxonomy_notes; never route a tie to OTHER.

CASE_ID: {{blind_case_id}}

FROZEN PREMISES:
{{frozen_premises_with_ids_and_texts}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```

`blind_case_id` is a random identifier held in a separate key file. Venture name, event, year, and all outcome variables are joined only after extraction is complete and locked.
