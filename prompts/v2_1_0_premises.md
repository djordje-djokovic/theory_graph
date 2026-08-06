# Codebook 2.1.0 Pass A: entrepreneurial theory premise extraction

Output: JSON only, conforming to the schema below.

Pass A identifies the critical premises of an entrepreneurial theory from a single pitch transcript. Domains and causal relationships are **not coded here**; they are conceptual context for the paper, not output of this pass. If premise composition tagging is desired, it runs as a separate Pass B on the frozen premise list produced here.


## 1. System / role instruction

> You are a trained research coder applying a fixed codebook to a single pitch transcript. Your task is descriptive measurement, not evaluation: you never judge whether the pitch is persuasive, investable, or likely to succeed, and you never predict its outcome. You code only what the transcript states or clearly implies. When the text does not support a coding decision, you omit the unit or mark it as inferred rather than inventing structure. You return JSON only.


## 2. Blind-coding requirement (mandatory)

The coding input is transcript text plus an anonymous identifier. It must **not** include the venture name, founder name, event, year, funding history, selection outcome, or any other outcome-relevant metadata.

> **Instruction to the model:** The transcript may contain a company or product name. If you recognize the venture, you must ignore all outside knowledge of it, including its later funding, growth, acquisition, failure, or competition results. Code only the propositional content of this transcript. Do not mention or use such knowledge anywhere in your output.


## 3. Theoretical definitions (apply exactly)

### 3.1 Constitutive elements

Entrepreneurial theories are composed of three constitutive elements: (1) **premises** held by the entrepreneur about what drives value, (2) the **causal relationships** that connect the premises to each other and to value, and (3) the **strategic domains** that group those parts of the theory that can be learned together. This codebook extracts the first element only.

### 3.2 Premises

A premise is an **explicit, testable claim about a critical condition the entrepreneur believes must hold for the theory to create value**. Premises are the **unit of architecture**: breadth counts them, strategic domains group them, and prediction errors are attributed to them. That is why they are individuated at the grain set out in §4.1.


## 4. Coding protocol

### 4.1 Premise identification and atomicity (critical for reliability)

Code a premise when the speaker asserts something presented as **needing to hold for the venture's theory of value to work** (§3.2). The claim may take any form: a design choice, a capability, a customer, channel, technological, or operating assumption. These are illustrations, not categories to be filled; the criterion is criticality for the claimed value.

**Atomicity rule.** One premise = one condition that could independently fail.

*Why this grain.* Breadth counts premises, and premises are what a prediction error gets attributed to. A premise stated too coarsely absorbs errors belonging to several distinct conditions, so feedback cannot be localized; one stated too finely splits a single condition into fragments that can only ever fail together. Individuate each premise at the level at which one disconfirming observation could implicate it and not its neighbours.

- Split coordinated claims when the components could fail separately.
  *"Our burger combines seaweed and mushrooms, and we source kelp from regenerative ocean farms"* → two premises.
- Do **not** split a single condition restated for emphasis or as near-synonyms.
  *"It's delicious, it tastes great, people love the flavor"* → one premise about taste.
- Do **not** split a bundle the speaker treats as one indivisible mechanism.
  *"A single 30-second phone scan replaces in-person measurement"* → one premise.
- Quantitative detail stays inside the premise it modifies.
  *"24 inches tall, holds 26 ounces"* → one premise about product form.

**No expected premise count.** Breadth is the measured construct. Do **not** aim for any band (including 3–8 or a habitual 7–8). Narrow theories with 1–2 premises and broad theories with 9–12+ premises are both legitimate when the atomicity rules support them. Never invent or drop premises to hit a count, never merge solely because the list is long, and never add filler premises because the count feels low.

**Enumeration atomicity.** When the speaker lists multiple features, pain points, capabilities, or channel/product items ("five pain points…", "we provide A, B, C, D, and E"):

1. **One premise** when the items are facets of a **single value mechanism** — one capability, one product surface, or one pain-bundle the speaker treats as solved together by the same offering. Near-synonym restatements of that mechanism stay inside it.
2. **Separate premises** when items map to **distinct value mechanisms** — separately failable conditions, distinct stakeholder jobs, or modules the speaker presents as independently revisable paths to value.
3. **Tie-break (symmetric, mandatory).** If after applying (1)–(2) you are still unsure whether two items could fail independently, **split them into separate premises**. Do not default to merging. Record residual doubt in `notes`.

**Boundary clarifications.** Apply these before the tie-break; they resolve recurring ties without adding a premise type:

1. **IP / patents** attached to a named mechanism stay inside that mechanism's premise, unless the speaker treats intellectual property itself as a separately revisable licensing or go-to-market condition.
2. **Speaker-enumerated uses of one mechanism** ("First… Two… Three…") are one premise when they are applications of a single capability. Split only when each use is claimed as an independently learnable module with its own path to value.
3. **Price and channel structure for the same offer** stay one commercial premise. Split only when the speaker presents a distinct partner-economics or channel module that could fail while the price point still stood.
4. **Vision / "future of X" claims** are **not** premises by default. Code them only when presented as a condition that must hold for the value theory to work. When the claim works as a value statement, prefer the value node and do not also make it a premise.
5. **Listed features, UI elements, or platform extensions** stay inside the core capability premise when presented as parts of one offering. Split only when the speaker explicitly frames the item as separately revisable with its own path to value.
6. **Problem/pain enumerations vs product capability enumerations.** When the speaker lists several pains/needs as **one problem set** that a single product will solve, that list is **one** premise. Do **not** emit one premise per pain label. When the speaker then lists **product capabilities** that are distinct jobs-to-be-done, those capabilities are **separate** premises under rule 2.
7. **Feature cascade of one mechanism.** Features that are consequences or UI/config facets of one claimed mechanism stay **inside that mechanism's premise** unless the speaker frames an item as a separately sold or independently revisable module.
8. **Process + performance package.** Speed, cost, water use, emissions, and grade of **the same extraction/manufacturing process** are quantitative detail of that process premise, not separate premises.

**Worked examples** (from diagnostic pitches; do not copy their structure):

- *"We have patents registered for this technology"* stated immediately after naming a product stack → **one** product-protection premise, not a second premise.
- *"First, we do active warning… Two, the data is usable for logistics… And three, your building has a Carfax"* about one sensor network → **one** monitoring-value premise, unless the speaker later treats logistics or the lasting record as a separately sold module.
- *"The future of data is a writable future"* → **not** a premise (vision framing).
- *"Parents face five major pain points: communication, safety, progress reports, fee payments, and daily needs. School Bridge provides two-way communication; instant report cards; GPS tracking; online fee payment; and e-commerce delivery."* → **1** pain-bundle premise + **5** capability premises = **6** total, not 11 with split pains.
- *"Mobile is integrated into the switch, which enables BYOD activation, presence, non-GPS location, seamless transfer, real-time transcription, cheaper IP international calls, and native voice-channel quality"* → **one** mobile-integration premise.
- *"Our extraction process is faster, cheaper, uses less water, and emits less CO2 than incumbents"* → **one** process premise.

Write each premise as a short declarative claim in the entrepreneur's own terms, lightly normalized for grammar.

### 4.2 Exclusions

Do not code as premises:

1. The financing ask, valuation, equity offered, instrument type, or amount already raised.
2. Biographical credentials, unless the speaker makes the credential a causal condition for the theory working.
3. Traction or press metrics offered as evidence of past performance, **unless** the speaker treats the underlying mechanism as a continuing condition for value. Code the mechanism, not the number.
4. Greetings, motivational closings, thanks, and audience appeals.
5. Content spoken by anyone other than the pitching entrepreneur(s), and any Q&A content.
6. The product or company name alone, without an associated condition.

### 4.3 Value: exactly one node (optional, for audit)

Extract **exactly one** value criterion as the single `value` node: for whom the offering is valuable and/or the valued outcome the market is claimed to receive. Prefer the speaker's stated priority ("most important," hero benefit). Financing is never value.

The value node is **not an independent variable** and receives no edges. It exists so that what counts as "critical for the theory" is anchored and auditable. If no value criterion is asserted, omit the `value` array.

### 4.4 Evidence spans and transcript artifacts

Every `evidence_span` must be an **exact substring of the transcript** (whitespace and letter case may differ; nothing else). Do not paraphrase, do not stitch distant fragments with ellipses, and do not quote text that is not present. Spans are checked automatically; a case whose spans do not verify is re-extracted. If a claim genuinely spans two separated sentences, quote the single most diagnostic contiguous fragment.

- **Automatic-speech-recognition noise.** Correct obvious transcription errors silently in the premise `text` when the intended claim is unambiguous. The `evidence_span` must still be copied verbatim, including its errors. If a passage is unintelligible, do not code it; note it.
- **Truncation.** If the transcript ends mid-sentence or the pitch is evidently cut off, code only what is present. Do not complete the argument.
- **Multiple presenters.** Pool the premises of all co-founders presenting the same venture; do not duplicate a premise because two speakers state it.

### 4.5 Out of scope

Do not code **domains**, **causal links**, or **taxonomy tags** in this pass. Do not score theory **breadth** or **modularity** inside the JSON; these are computed downstream. Do not infer prediction errors, pivots, or revision history. Do not estimate outcomes.


## 5. Few-shot cases

Three cases with deliberately different premise counts: 8, 5, and 2. Note the varying counts: **no shape is a target.**

The provenance values in `meta` are placeholders (`MODEL_ID`, `PROVIDER`, `ISO-8601`); copy the key set, but fill the values from the task header of your own run.

### 5.1 Case A: broad (8 premises)

**Input (abridged).** "We're creating a regenerative plant-based food company. Our hero product, the kelp burger, combines two superfoods, seaweed and mushrooms. We source our kelp from regenerative ocean farming supply chains. Our kelp burger is packed with protein and umami flavor, and it's sold in over 1,000 grocery stores, in 40 restaurants and nationwide online. Our kelp farming supply chain helps beat climate change by taking CO2 out of the ocean and creates new jobs in coastal communities. But the most important part: our products taste delicious."

**Output.**

```json
{
  "meta": {"codebook_version": "2.1.0", "pass": "premises", "unit": "pitch_transcript", "case_id": "BLIND_CASE_ID", "model_id": "MODEL_ID", "model_provider": "PROVIDER", "temperature": null, "temperature_controlled": false, "extraction_run": 1, "extracted_at": "ISO-8601"},
  "premises": [
    {"id": "P1", "text": "A seaweed-and-mushroom combination is the right product formulation", "status": "explicit", "evidence_span": "combines two superfoods, seaweed and mushrooms"},
    {"id": "P2", "text": "The product delivers high protein and umami flavor", "status": "explicit", "evidence_span": "packed with protein and umami flavor"},
    {"id": "P3", "text": "The product tastes good enough for repeat consumption", "status": "explicit", "evidence_span": "our products taste delicious"},
    {"id": "P4", "text": "Kelp can be sourced through regenerative ocean farming supply chains", "status": "explicit", "evidence_span": "source our kelp from regenerative ocean farming supply chains"},
    {"id": "P5", "text": "Grocery retail distribution is available at scale", "status": "explicit", "evidence_span": "sold in over 1,000 grocery stores"},
    {"id": "P6", "text": "Restaurant and direct online channels extend reach", "status": "explicit", "evidence_span": "in 40 restaurants and nationwide online"},
    {"id": "P7", "text": "Kelp farming sequesters CO2 from the ocean", "status": "explicit", "evidence_span": "beat climate change by taking CO2 out of the ocean"},
    {"id": "P8", "text": "Kelp farming creates jobs in coastal communities", "status": "explicit", "evidence_span": "creates new jobs in coastal communities"}
  ],
  "value": [
    {"id": "V1", "text": "Consumers get plant-based food that tastes delicious", "status": "explicit", "evidence_span": "our products taste delicious"}
  ],
  "notes": "Taste is the stated priority, so V1 anchors the consumer taste criterion. Climate and jobs claims are premises (conditions the speaker presents as needing to hold) but not part of the coded value."
}
```

### 5.2 Case B: narrow, traction-heavy (5 premises)

**Input (abridged).** "We are selling the beer bat to fanatics who can buy it online, and they can get it at stadium beer concession stands. We have a patent for the beer bat. We also have an MLB license. It's 24 inches tall and holds 26 ounces of beer. We can't make them fast enough. That's why we're here today. We are presenting a $250,000 SAFE note for 5% equity to buy a mold and increase inventory. Our sales were a million dollars."

**Output.**

```json
{
  "meta": {"codebook_version": "2.1.0", "pass": "premises", "unit": "pitch_transcript", "case_id": "BLIND_CASE_ID", "model_id": "MODEL_ID", "model_provider": "PROVIDER", "temperature": null, "temperature_controlled": false, "extraction_run": 1, "extracted_at": "ISO-8601"},
  "premises": [
    {"id": "P1", "text": "A 24-inch novelty container holding 26 ounces is the right product form", "status": "explicit", "evidence_span": "24 inches tall and holds 26 ounces of beer"},
    {"id": "P2", "text": "A patent protects the product", "status": "explicit", "evidence_span": "We have a patent for the beer bat"},
    {"id": "P3", "text": "An MLB license grants access to the relevant venues and fan base", "status": "explicit", "evidence_span": "We also have an MLB license"},
    {"id": "P4", "text": "Sports fans are the target buyers", "status": "explicit", "evidence_span": "selling the beer bat to fanatics"},
    {"id": "P5", "text": "Online sales and stadium concession stands are the channels", "status": "explicit", "evidence_span": "buy it online, and they can get it at stadium beer concession stands"}
  ],
  "value": [
    {"id": "V1", "text": "A novelty drinking product sports fans buy at games and online", "status": "explicit", "evidence_span": "selling the beer bat to fanatics"}
  ],
  "notes": "Financing ask ($250,000 SAFE, 5%) and cumulative sales excluded per 4.2. 'Can't make them fast enough' is excluded: it is a traction statement, not a condition for value. Patent and MLB licence are separate premises because each could fail independently."
}
```

### 5.3 Case C: thin and truncated (2 premises)

**Input (abridged).** "Before Brave, only accredited investors could invest in private equity, which has outperformed public stocks. The Brave platform is the only way everyday investors will get exposure to the $10 trillion alternative assets market. We are pre-revenue, but we've made meaningful traction in development of our product for advisors and consumers, both web and mobile. We've signed LOIs with multiple private equity feeder funds. We are raising $100,000 out of —"

**Output.**

```json
{
  "meta": {"codebook_version": "2.1.0", "pass": "premises", "unit": "pitch_transcript", "case_id": "BLIND_CASE_ID", "model_id": "MODEL_ID", "model_provider": "PROVIDER", "temperature": null, "temperature_controlled": false, "extraction_run": 1, "extracted_at": "ISO-8601"},
  "premises": [
    {"id": "P1", "text": "Non-accredited retail investors are excluded from private-market returns", "status": "explicit", "evidence_span": "only accredited investors could invest in private equity"},
    {"id": "P2", "text": "A web and mobile platform can serve both advisors and consumers", "status": "explicit", "evidence_span": "product for advisors and consumers, both web and mobile"}
  ],
  "value": [
    {"id": "V1", "text": "Everyday investors gain exposure to alternative assets", "status": "explicit", "evidence_span": "everyday investors will get exposure to the $10 trillion alternative assets market"}
  ],
  "notes": "Pitch cut off mid-sentence during the financing ask. Pre-revenue status and LOI count excluded as traction per 4.2. Outperformance of private equity is framing for P1, not a separate condition."
}
```


## 6. Output schema

Return exactly one JSON object. No prose outside the JSON.

```json
{
  "meta": {
    "codebook_version": "2.1.0",
    "pass": "premises",
    "unit": "pitch_transcript",
    "case_id": "string",
    "model_id": "string",
    "model_provider": "string",
    "temperature": 0.0,
    "temperature_controlled": true,
    "extraction_run": 1,
    "extracted_at": "ISO-8601 datetime"
  },
  "premises": [
    {"id": "P1", "text": "string", "status": "explicit|inferred", "evidence_span": "verbatim transcript substring"}
  ],
  "value": [
    {"id": "V1", "text": "string", "status": "explicit|inferred", "evidence_span": "verbatim transcript substring"}
  ],
  "notes": "string"
}
```

Validity conditions:

- `premises` is non-empty
- `value` has **exactly one** item if present; do not include a `secondary_value` field
- no `domains`, `causal_links`, `taxonomy`, `epistemic_markers`, or `quality` fields
- ids unique; `P*` premises, `V*` value
- every `evidence_span` verifies as a verbatim transcript substring
- **provenance required:** `meta.model_id` (non-empty string) and `meta.temperature_controlled` (boolean). `meta.temperature` carries a number only when sampling was actually pinned; when the extraction ran through a harness that does not expose the parameter, set `temperature_controlled: false` and `temperature: null` rather than recording an intended value as though it had been enforced. Record `model_provider`, `extraction_run`, and `extracted_at` whenever available.


## 7. User message template

```text
Extract the critical premises of the entrepreneurial theory from the transcript below using codebook v2.1.0 Pass A. Return JSON only. Do not use any outside knowledge about this venture.

Requirements: premises are individuated at the grain where one disconfirming observation could implicate this condition and not its neighbours; no expected premise count; no domains or causal links in this pass; every evidence_span copied verbatim from the transcript. If a value criterion is asserted, extract exactly one value node to anchor what counts as critical.

CASE_ID: {{blind_case_id}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```

`blind_case_id` is a random identifier held in a separate key file. Venture name, event, year, and all outcome variables are joined only after extraction is complete and locked.
