# Codebook 1.3.2 — entrepreneurial theory architecture extraction (P → D → V)

Output: JSON only, conforming to the schema below.

---

## 1. System / role instruction

> You are a trained research coder applying a fixed codebook to a single pitch transcript. Your task is descriptive measurement, not evaluation: you never judge whether the pitch is persuasive, investable, or likely to succeed, and you never predict its outcome. You code only what the transcript states or clearly implies. When the text does not support a coding decision, you omit the unit or mark it as inferred rather than inventing structure. You return JSON only.

---

## 2. Blind-coding requirement (mandatory)

The coding input is transcript text plus an anonymous identifier. It must **not** include the venture name, founder name, event, year, funding history, selection outcome, or any other outcome-relevant metadata.

> **Instruction to the model:** The transcript may contain a company or product name. If you recognize the venture, you must ignore all outside knowledge of it — including its later funding, growth, acquisition, failure, or competition results. Code only the propositional content of this transcript. Do not mention or use such knowledge anywhere in your output.


---

## 3. Theoretical definitions (apply exactly)

### 3.1 Constitutive elements

Entrepreneurial theories are composed of three constitutive elements: (1) **premises** held by the entrepreneur about what drives value, (2) the **causal relationships** that connect the premises to each other and to value, and (3) the **strategic domains** that group those parts of the theory that can be learned together. Together, these elements delineate what the entrepreneur deems critical for value creation, why the theory is expected to be valuable, and how the theory is internally organized.

### 3.2 Premises

Premises are the conditions underlying the theory that the entrepreneur claims to be **critical for value creation**. They encapsulate the conditions the entrepreneur treats as necessary for the theory to succeed and compress what the entrepreneur considers "salient and diagnostic" for the theory to become valuable. Premises are critical *preconditions* for the theory to have merit in the market; they concretize the theory and limit the search space.

### 3.3 Causal relationships

An entrepreneurial theory specifies how premises produce value. Causal relationships comprise two kinds of links: those **among premises**, and those running from premises **via strategic domains to value** — value being the market's assessment of the enacted product.

### 3.4 Strategic domains

Strategic domains are coherent modules into which a theory can be decomposed. Following near-decomposability, causal relationships **within** a domain are stronger than causal relationships **between** domains, so domains can be analyzed almost — albeit not perfectly — independently. Premises inside a domain are tightly affiliated toward illuminating a coherent part of the theory.

### 3.5 Hierarchy: P → D → V

At the top sit premises. Intermediate layers aggregate related premises into strategic domains. At the bottom sits the concrete instantiation of the theory as the market-facing offering whose value is assessed in the market. Denote this as **P → D → V**.

**Value is the criterion, not an element of the theory.** Value is what the market assesses about the enacted offering. Never code value as a premise, and never code "obtaining investment" as value.

---

## 4. Coding protocol (Pass A — structure)

Work in the order given: premises → domains → value → domain-value links, then the optional dependency step. Do not skip ahead; in particular, **do not decide how many domains there are before the premises are written out**.

### 4.1 Premise identification and atomicity (critical for reliability)

Code a premise when the speaker asserts a condition, design choice, capability, customer assumption, channel assumption, technological assumption, or operating assumption that is presented as **needing to hold for the venture's theory of value to work**.

**Atomicity rule.** One premise = one condition that could independently fail.

- Split coordinated claims when the components could fail separately.
  *"Our burger combines seaweed and mushrooms, and we source kelp from regenerative ocean farms"* → two premises: (a) the seaweed–mushroom combination is the right formulation; (b) kelp is sourced from regenerative ocean farming.
- Do **not** split a single condition restated for emphasis or expressed as a list of near-synonyms.
  *"It's delicious, it tastes great, people love the flavor"* → one premise about product taste.
- Do **not** split a bundle the speaker explicitly treats as one indivisible mechanism.
  *"A single 30-second phone scan replaces in-person measurement"* → one premise, even though it names several steps.
- Quantitative detail attached to a condition stays inside that premise; it does not create a second premise.
  *"24 inches tall, holds 26 ounces"* → one premise about the product form factor.
- **Granularity check (soft).** For a typical Startup Battlefield pitch, expect about **3–8 premises**. Fewer than 3 is fine when the theory is truly narrow. More than 8 is a warning that you are probably over-splitting: merge near-synonyms, feature lists, and restatements before finishing. Do **not** invent or drop premises merely to hit a count.

**Boundary clarifications.** Apply the bullets above; these notes resolve recurring ties without adding a new premise type:

1. **IP / patents / comparative sensitivity** attached to a named product mechanism stay inside that mechanism's premise, unless the speaker treats intellectual property itself as a separately revisable go-to-market or licensing condition.
2. **Speaker-enumerated uses of the same mechanism** ("First… Two… Three…") are one premise when they are benefits or applications of one capability. Split only when each use is claimed as an independently learnable module with its own path to value.
3. **Price amount and partner/channel structure for the same offer** stay one commercial premise when both describe how that offer is sold. Split only when the speaker presents a distinct partner-economics or channel module that could fail while the price point still stood.

**Boundary clarifications.** Two further recurring ties:

4. **Vision / "future of X" / market-ownership claims** are **not** premises by default. Code them only when the speaker presents the vision as a *condition that must hold for the value theory to work* (e.g., a market-acceptance or platform-adoption condition), not as aspiration or framing. When the same claim works as a value statement, prefer the value node; do not also make it a premise.
5. **Speaker-listed product features, UI elements, patents, or platform extensions** ("the sharing panel…", "there are nine patents…", "we're opening a developer platform…") stay inside the core capability premise when the speaker presents them as parts of one offering. Split only when the speaker explicitly frames the item as a separately revisable module with its own path to value (e.g., "the developer platform is our second product and could stand alone if the app failed").

Worked examples (from diagnostic pitches; do not copy their domain structure):

- *"We have patents registered for this technology"* stated immediately after naming the Secure IoT stack → **one** product-protection premise (patents are IP detail on the stack), not a second premise.
- *"First, we do active warning… Two, the data is usable for logistics… And three, your building has a Carfax"* about one sensor network → **one** monitoring-value premise (three uses of the same mechanism), unless the speaker later treats logistics or the lasting record as a separately sold module.
- *"The future of data is a writable future"* → **not** a premise (vision framing); record in `secondary_value` if it states an additional criterion, or leave uncoded.
- *"There's nine patents that cover the core IP"* and *"we're opening up our developer platform early next year"* alongside the anticipatory engine → **fold into** the engine/platform premise; do not add separate premises for the patent count or the developer-platform roadmap item unless the speaker claims each could fail independently of the core engine.

Write each premise as a short declarative claim in the entrepreneur's own terms, lightly normalized for grammar.

### 4.2 Exclusions

Do not code as premises:

1. The financing ask, valuation, equity offered, instrument type, or amount already raised.
2. Biographical credentials, unless the speaker makes the credential a causal condition for the theory working.
3. Traction or press metrics offered as evidence of past performance (revenue to date, store counts as achievements, view counts, awards) — **unless** the speaker treats the underlying mechanism as a continuing condition for value. Code the mechanism, not the number.
4. Greetings, motivational closings, thanks, and audience appeals.
5. Content spoken by anyone other than the pitching entrepreneur(s), and any Q&A content, if present.
6. The product or company name alone, without an associated condition.

### 4.3 Value — one primary node, secondary criteria recorded

Extract **exactly one** primary value criterion as the single `value` node: for whom the offering is valuable and/or the valued outcome the market is claimed to receive (problem solved, performance benefit, economic or social outcome tied to the offering). Prefer the speaker's stated priority ("most important," hero benefit). Financing is never value.

If the speaker clearly advances **additional, non-redundant value criteria** (for example a social or environmental outcome alongside a product benefit), record each as a string in `secondary_value` with its own evidence span. `secondary_value` is descriptive: it is not a graph node, receives no edges, and does not enter breadth or modularity. It exists so that multi-criterion theories are visible in the data rather than collapsed without trace.

### 4.4 Premise dependencies (optional, exploratory)

The paper defines causal relationships as including links among premises, and near-decomposability implies those links are denser within domains than between them. Pitch talk, however, rarely asserts dependence explicitly, so **dependency coding is optional and exploratory**: it never carries a confirmatory test, and omitting it does not make a case incomplete.

Code a `premise-premise` link **only** where the speaker plainly asserts that one premise is a prerequisite for another — that the second only works, or only matters, if the first holds.

- Code from the text only. Plausible-sounding logical dependencies that the speaker does not assert are **not** coded.
- Acceptable warrants are explicit: "because," "that's why," "this lets us," "once we have X we can Y," or a mechanism stated as enabling another. Absent such a marker, code nothing.
- **When in doubt, omit.** A false dependency is more damaging than a missing one, because it moves the integration statistics without textual warrant.
- Zero dependencies is a normal and complete result. Set `quality.dependency_pass = true` only if you considered the question; the field is informational and no longer required for validity.
- Do not code a dependency merely because two premises concern the same topic; topical similarity is captured by domain membership, not by a link.
- Dependencies must not form a cycle. If mutual dependence is implied, code the direction with the stronger textual warrant and record the ambiguity in `notes`.

### 4.5 Domains: coherence and separate revisability

Group premises into strategic domains such that premises that must be learned and revised **together** sit in the same domain, and premises that can be tested or revised **independently** sit in different domains. Where the speaker does assert a dependency (§4.4), it is evidence that the two premises belong together, but the partition does not require dependency links to be coded.

1. Assign **every** retained premise to exactly one **primary** domain (`domains[].premise_ids`). This partition defines the decomposition measures.
2. Give each domain a short free-text `name` drawn from the transcript's own vocabulary. **Pass A has no taxonomy field.** Do not classify, and do not consult any category list; classification happens later and must not shape the partition.
3. **No domain count is a target.** A theory that supports one coherent bundle receives one domain. A theory with five independently learnable parts receives five.
4. **Singleton rule.** A single-premise domain is legitimate only when that premise is an independently learnable mechanism with its own claimed contribution to value (for example a standalone pricing model). If the premise is instead a detail of another bundle, merge it into that bundle. State the reason in `notes` whenever a singleton domain is retained.
5. **Anti-template rule.** Do not impose a habitual pitch template. If your partition happens to be exactly three domains corresponding to customer need, product/technology, and money/channel, add one sentence to `notes` citing the transcript evidence that these are three separately revisable modules. If you cannot, merge.
6. Because domains are only *near*-decomposable, dependencies that cross the partition may be recorded when explicitly stated, as exploratory evidence:
   - `premise-premise` links whose endpoints sit in different primary domains (§4.4);
   - `premise-domain` links where a premise contributes to a domain other than its primary one;
   - `domain-domain` links where one domain's functioning is claimed to depend on another's.

### 4.6 Causal relationships (keep the graph flat and readable)

The confirmatory graph is **P → D → V**: membership edges plus `domain-value` links. Premise-level dependencies and cross-domain links form an optional exploratory layer on top of it. Do **not** build multilevel premise hierarchies.

Primary domain membership is implied by `domains[].premise_ids` and must **not** be repeated in `causal_links`.

| Type | When to code | Role in measurement |
|---|---|---|
| `domain-value` | **Required** for each domain that clearly contributes to the primary value | Confirmatory |
| `premise-premise` | **Optional** (§4.4): only where the speaker plainly asserts a prerequisite | Exploratory |
| `premise-domain` | **Optional**: only for a clear **cross-domain** contribution (not primary membership) | Exploratory |
| `domain-domain` | **Optional**: only if one domain is explicitly said to depend on another | Exploratory |

### 4.7 DAG constraints (enforced)

The graph must be a directed acyclic graph over three layers, premises → domains → value:

1. No edge may point upward: no `value → domain`, no `domain → premise`, no `value → premise`.
2. Value is a sink; it has no outgoing edges.
3. `premise-premise` and `domain-domain` edges must be directed and must not create a cycle.
4. Every id referenced in `causal_links` and in `domains[].premise_ids` must exist.

### 4.8 Transcript artifacts

- **Automatic-speech-recognition noise.** Correct obvious transcription errors silently in the premise `text` when the intended claim is unambiguous (`Vreshna` / `Breshna`, spaced numerals such as `$300 000`). The `evidence_span` must still be copied **verbatim from the transcript**, including its errors. If a passage is unintelligible, do not code it; note it.
- **Truncation.** If the transcript ends mid-sentence or the pitch is evidently cut off, set `quality.truncated = true` and code only what is present. Do not complete the argument.
- **Multiple presenters.** Pool the premises of all co-founders presenting the same venture; do not duplicate a premise because two speakers state it.

### 4.9 Evidence spans are verbatim and verified

Every `evidence_span` must be an **exact substring of the transcript** (whitespace and letter case may differ; nothing else). Do not paraphrase, do not stitch distant fragments with ellipses, and do not quote text that is not present. Spans are checked automatically against the transcript by `scripts/validate_theory_dag.py`; a case whose spans do not verify is re-extracted, and the verification rate is reported as a data-quality statistic.

If a claim genuinely spans two separated sentences, quote the single most diagnostic contiguous fragment.

### 4.10 Confidence rubric (anchored)

Set `quality.coder_confidence` using these anchors:

| Value | Condition |
|---|---|
| 0.9–1.0 | Nearly all premises explicit; domain assignment unambiguous; value clearly stated |
| 0.7–0.8 | Mostly explicit; one or two domain assignments required judgment |
| 0.4–0.6 | Several inferred premises, or the domain partition is genuinely ambiguous |
| 0.1–0.3 | Truncated, largely unintelligible, or almost no causal content |

### 4.11 Out of scope for this pass

Do not score theory **breadth**, **modularity**, or **permeability** inside the JSON; these are computed downstream. Do not infer prediction errors, pivots, or revision history. Do not estimate outcomes (including `GotSelected`).

**Permeability (Props 3a–3c) is out of scope** for single-pitch coding.

**Optional exploratory field.** If the speaker explicitly states what evidence would change their approach, record it in `epistemic_markers` (not a permeability measure).

---

## 5. Pass B — domain taxonomy (separate call, frozen partition)

Pass B runs as a **second call** whose input is the transcript plus the *frozen* Pass A domains (id, name, member premise texts). It returns one taxonomy code per domain and nothing else.

> **Instruction to the model:** The domains below are fixed. Assign each one category code. You may not merge, split, rename, add, or remove domains, and you may not revisit premise membership. If a domain fits no category well, choose the closest and say so in `taxonomy_notes`.

| Code | Scope |
|---|---|
| `DESIRABILITY` | customer need, target segment, demand, willingness to pay, problem salience |
| `FEASIBILITY` | technology, science, product design, engineering, intellectual property |
| `VIABILITY` | unit economics, pricing, margins, capital efficiency, revenue model |
| `OPERATIONS_SUPPLY` | manufacturing, sourcing, supply chain, logistics, capacity |
| `GTM_DISTRIBUTION` | channels, retail and platform access, marketing, partnerships, sales motion |
| `ORGANIZATION_TEAM` | team capability or structure invoked as a condition for the theory working |
| `INSTITUTIONAL_REGULATORY` | regulation, certification, standards, licensing, policy |
| `IMPACT_EXTERNALITY` | environmental or social outcomes the venture claims to produce as value drivers |

The eight codes are an unordered set; none is more expected than another. When taxonomy categories are shown, present them in a random order.

Rules: one code per domain; two domains in the same case may share a code when the transcript separates them as distinct modules (record the reason in `taxonomy_notes`).

Pass B output:

```json
{
  "meta": {"codebook_version": "1.3", "pass": "taxonomy", "case_id": "string", "taxonomy_order_seed": 0},
  "assignments": [{"domain_id": "D1", "taxonomy": "FEASIBILITY"}],
  "taxonomy_notes": "string"
}
```

---

## 6. Few-shot cases (Pass A)

Four cases with deliberately different architectures. Domain counts are 4, 2, 2, and 1. None is a desirability/feasibility/viability triad. Note the varying premise and domain counts: **no shape is a target.**

### 6.1 Case A — broad, multi-domain, two value criteria

**Input (abridged).** "We're creating a regenerative plant-based food company. Our hero product, the kelp burger, combines two superfoods, seaweed and mushrooms. We source our kelp from regenerative ocean farming supply chains. Our kelp burger is packed with protein and umami flavor, and it's sold in over 1,000 grocery stores, in 40 restaurants and nationwide online. Our kelp farming supply chain helps beat climate change by taking CO2 out of the ocean and creates new jobs in coastal communities. But the most important part: our products taste delicious."

**Output.**

```json
{
  "meta": {"codebook_version": "1.3", "pass": "structure", "unit": "pitch_transcript", "hierarchy": "P->D->V"},
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
  "domains": [
    {"id": "D1", "name": "Product formulation and taste", "premise_ids": ["P1", "P2", "P3"]},
    {"id": "D2", "name": "Regenerative kelp supply chain", "premise_ids": ["P4"]},
    {"id": "D3", "name": "Retail and online distribution", "premise_ids": ["P5", "P6"]},
    {"id": "D4", "name": "Climate and community impact", "premise_ids": ["P7", "P8"]}
  ],
  "value": [
    {"id": "V1", "text": "Plant-based food that consumers buy for health and taste", "status": "explicit", "evidence_span": "regenerative plant-based food company"}
  ],
  "secondary_value": [
    {"text": "Climate and coastal-livelihood benefits valued alongside the product", "evidence_span": "helps beat climate change by taking CO2 out of the ocean and creates new jobs in coastal communities"}
  ],
  "causal_links": [
    {"from": "P1", "to": "P2", "type": "premise-premise", "evidence_span": "combines two superfoods, seaweed and mushrooms"},
    {"from": "P4", "to": "P7", "type": "premise-premise", "evidence_span": "Our kelp farming supply chain helps beat climate change by taking CO2 out of the ocean"},
    {"from": "P4", "to": "P8", "type": "premise-premise", "evidence_span": "creates new jobs in coastal communities"},
    {"from": "P4", "to": "D4", "type": "premise-domain", "evidence_span": "Our kelp farming supply chain helps beat climate change"},
    {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "the most important part: our products taste delicious"},
    {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "sold in over 1,000 grocery stores"},
    {"from": "D4", "to": "V1", "type": "domain-value", "evidence_span": "creates new jobs in coastal communities"}
  ],
  "epistemic_markers": [],
  "quality": {"thin_transcript": false, "truncated": false, "dependency_pass": true, "coder_confidence": 0.9},
  "notes": "Singleton D2 retained: the supply chain is presented as an independently learnable mechanism that drives the impact domain (cross-domain link P4->D4). Impact is coded as a secondary value criterion, not a second value node."
}
```

### 6.2 Case B — narrow, two domains, traction-heavy

**Input (abridged).** "We are selling the beer bat to fanatics who can buy it online, and they can get it at stadium beer concession stands. We have a patent for the beer bat. We also have an MLB license. It's 24 inches tall and holds 26 ounces of beer. We can't make them fast enough. That's why we're here today. We are presenting a $250,000 SAFE note for 5% equity to buy a mold and increase inventory. Our sales were a million dollars."

**Output.**

```json
{
  "meta": {"codebook_version": "1.3", "pass": "structure", "unit": "pitch_transcript", "hierarchy": "P->D->V"},
  "premises": [
    {"id": "P1", "text": "A 24-inch novelty container holding 26 ounces is the right product form", "status": "explicit", "evidence_span": "24 inches tall and holds 26 ounces of beer"},
    {"id": "P2", "text": "A patent protects the product", "status": "explicit", "evidence_span": "We have a patent for the beer bat"},
    {"id": "P3", "text": "An MLB license grants access to the relevant venues and fan base", "status": "explicit", "evidence_span": "We also have an MLB license"},
    {"id": "P4", "text": "Sports fans are the target buyers", "status": "explicit", "evidence_span": "selling the beer bat to fanatics"},
    {"id": "P5", "text": "Online sales and stadium concession stands are the channels", "status": "explicit", "evidence_span": "buy it online, and they can get it at stadium beer concession stands"},
    {"id": "P6", "text": "Production capacity must expand to meet demand", "status": "explicit", "evidence_span": "We can't make them fast enough"}
  ],
  "domains": [
    {"id": "D1", "name": "Licensed novelty product", "premise_ids": ["P1", "P2", "P3"]},
    {"id": "D2", "name": "Fan channels and supply", "premise_ids": ["P4", "P5", "P6"]}
  ],
  "value": [
    {"id": "V1", "text": "A novelty drinking product sports fans buy at games and online", "status": "explicit", "evidence_span": "selling the beer bat to fanatics"}
  ],
  "secondary_value": [],
  "causal_links": [
    {"from": "P3", "to": "P5", "type": "premise-premise", "evidence_span": "We also have an MLB license"},
    {"from": "P3", "to": "D2", "type": "premise-domain", "evidence_span": "they can get it at stadium beer concession stands"},
    {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "We have a patent for the beer bat"},
    {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "buy it online, and they can get it at stadium beer concession stands"}
  ],
  "epistemic_markers": [],
  "quality": {"thin_transcript": false, "truncated": false, "dependency_pass": true, "coder_confidence": 0.8},
  "notes": "Financing ask ($250,000 SAFE, 5%) and cumulative sales excluded per 4.2. P6 coded as an operating condition, not as a traction boast, because the speaker treats capacity as binding. The licence is coded as a prerequisite for the stadium channel (P3->P5), which crosses the partition."
}
```

### 6.3 Case C — thin and truncated

**Input (abridged).** "Before Brave, only accredited investors could invest in private equity, which has outperformed public stocks. The Brave platform is the only way everyday investors will get exposure to the $10 trillion alternative assets market. We are pre-revenue, but we've made meaningful traction in development of our product for advisors and consumers, both web and mobile. We've signed LOIs with multiple private equity feeder funds. We are raising $100,000 out of —"

**Output.**

```json
{
  "meta": {"codebook_version": "1.3", "pass": "structure", "unit": "pitch_transcript", "hierarchy": "P->D->V"},
  "premises": [
    {"id": "P1", "text": "Non-accredited retail investors are excluded from private-market returns", "status": "explicit", "evidence_span": "only accredited investors could invest in private equity"},
    {"id": "P2", "text": "Private equity outperforms public equities", "status": "explicit", "evidence_span": "which has outperformed public stocks"},
    {"id": "P3", "text": "A web and mobile platform can serve both advisors and consumers", "status": "explicit", "evidence_span": "product for advisors and consumers, both web and mobile"},
    {"id": "P4", "text": "Feeder-fund partnerships supply access to private-market assets", "status": "explicit", "evidence_span": "signed LOIs with multiple private equity feeder funds"}
  ],
  "domains": [
    {"id": "D1", "name": "Retail exclusion from private markets", "premise_ids": ["P1", "P2"]},
    {"id": "D2", "name": "Platform and fund access", "premise_ids": ["P3", "P4"]}
  ],
  "value": [
    {"id": "V1", "text": "Everyday investors gain exposure to alternative assets", "status": "explicit", "evidence_span": "everyday investors will get exposure to the $10 trillion alternative assets market"}
  ],
  "secondary_value": [],
  "causal_links": [
    {"from": "P2", "to": "P1", "type": "premise-premise", "evidence_span": "only accredited investors could invest in private equity, which has outperformed public stocks"},
    {"from": "P4", "to": "D1", "type": "premise-domain", "evidence_span": "signed LOIs with multiple private equity feeder funds"},
    {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "the only way everyday investors will get exposure"},
    {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "product for advisors and consumers"}
  ],
  "epistemic_markers": [],
  "quality": {"thin_transcript": true, "truncated": true, "dependency_pass": true, "coder_confidence": 0.4},
  "notes": "Pitch cut off mid-sentence during the financing ask; no viability or operations content available. Pre-revenue status and LOI count excluded as traction per 4.2, except P4 which states the access mechanism. Outperformance is the reason exclusion matters, coded P2->P1."
}
```

### 6.4 Case D — monolithic (one domain)

**Input (abridged).** "Concrete is the second most used material on earth and making it emits a tenth of global CO2. We inject captured CO2 into the concrete while it cures. The CO2 mineralizes, so the concrete gets stronger, which means producers use less cement for the same strength. It bolts onto the existing batch plant, so producers change nothing about how they work."

**Output.**

```json
{
  "meta": {"codebook_version": "1.3", "pass": "structure", "unit": "pitch_transcript", "hierarchy": "P->D->V"},
  "premises": [
    {"id": "P1", "text": "Cement production is a very large source of global CO2 emissions", "status": "explicit", "evidence_span": "making it emits a tenth of global CO2"},
    {"id": "P2", "text": "Captured CO2 can be injected into concrete during curing", "status": "explicit", "evidence_span": "We inject captured CO2 into the concrete while it cures"},
    {"id": "P3", "text": "The injected CO2 mineralizes and strengthens the concrete", "status": "explicit", "evidence_span": "The CO2 mineralizes, so the concrete gets stronger"},
    {"id": "P4", "text": "Stronger concrete lets producers use less cement per unit of strength", "status": "explicit", "evidence_span": "producers use less cement for the same strength"},
    {"id": "P5", "text": "The system retrofits existing batch plants without changing producer workflow", "status": "explicit", "evidence_span": "It bolts onto the existing batch plant, so producers change nothing"}
  ],
  "domains": [
    {"id": "D1", "name": "CO2 mineralization in concrete curing", "premise_ids": ["P1", "P2", "P3", "P4", "P5"]}
  ],
  "value": [
    {"id": "V1", "text": "Lower-emission, stronger concrete that producers can adopt without changing operations", "status": "explicit", "evidence_span": "the concrete gets stronger, which means producers use less cement for the same strength"}
  ],
  "secondary_value": [],
  "causal_links": [
    {"from": "P2", "to": "P3", "type": "premise-premise", "evidence_span": "We inject captured CO2 into the concrete while it cures"},
    {"from": "P3", "to": "P4", "type": "premise-premise", "evidence_span": "The CO2 mineralizes, so the concrete gets stronger, which means producers use less cement"},
    {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "producers use less cement for the same strength"}
  ],
  "epistemic_markers": [],
  "quality": {"thin_transcript": false, "truncated": false, "dependency_pass": true, "coder_confidence": 0.85},
  "notes": "One domain: every premise is part of a single tightly chained mechanism (inject -> mineralize -> strength -> less cement) that cannot be revised in separable parts. No separate market, channel, or pricing module is asserted, so none is invented."
}
```

---

## 7. Output schema (Pass A)

Return exactly one JSON object. No prose outside the JSON.

```json
{
  "meta": {
    "codebook_version": "1.3",
    "pass": "structure",
    "unit": "pitch_transcript",
    "hierarchy": "P->D->V",
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
  "domains": [
    {"id": "D1", "name": "string", "premise_ids": ["P1"]}
  ],
  "value": [
    {"id": "V1", "text": "string", "status": "explicit|inferred", "evidence_span": "verbatim transcript substring"}
  ],
  "secondary_value": [
    {"text": "string", "evidence_span": "verbatim transcript substring"}
  ],
  "causal_links": [
    {"from": "P1", "to": "P2", "type": "premise-premise|premise-domain|domain-domain|domain-value", "evidence_span": "verbatim transcript substring"}
  ],
  "epistemic_markers": [],
  "quality": {"thin_transcript": false, "truncated": false, "dependency_pass": true, "coder_confidence": 0.0},
  "notes": "string"
}
```

Validity conditions (checked by `scripts/validate_theory_dag.py`):

- `value` has **exactly one** item; `secondary_value` may be empty
- no `taxonomy` field in Pass A output; taxonomy is merged from Pass B
- ids unique; `P*` premises, `D*` domains, `V*` value
- every premise appears in exactly one `domains[].premise_ids`
- every id in `causal_links` resolves; no primary-membership edge restated
- no upward edges; value is a sink; graph is acyclic
- every `evidence_span` verifies as a verbatim transcript substring
- `coder_confidence` ∈ [0, 1]; `quality.dependency_pass` is informational and not required
- **provenance required:** `meta.model_id` (non-empty string) and `meta.temperature_controlled` (boolean). `meta.temperature` carries a number only when sampling was actually pinned; when the extraction ran through a harness that does not expose the parameter, set `temperature_controlled: false` and `temperature: null` rather than recording an intended value as though it had been enforced. Record `model_provider`, `extraction_run`, and `extracted_at` whenever available.

---

## 8. User message templates

**Pass A — structure.**

```text
Extract the entrepreneurial theory architecture (P -> D -> V) from the transcript below using codebook v1.3, Pass A. Return JSON only. Do not use any outside knowledge about this venture.

Requirements: one primary value node; a flat premise layer; a domain-value link for each domain; domains grouped by what must be learned and revised together and named in the speaker's own words; no category or taxonomy labels; every evidence_span copied verbatim from the transcript. Premise dependencies are optional: code one only where the speaker plainly asserts that one premise is a prerequisite for another, and omit when in doubt.

CASE_ID: {{blind_case_id}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```

**Pass B — taxonomy.**

```text
Assign one category code to each frozen domain below using codebook v1.3, Pass B. You may not merge, split, rename, add, or remove domains, and you may not revisit premise membership. Return JSON only.

CATEGORIES (unordered):
{{taxonomy_table_shuffled}}

CASE_ID: {{blind_case_id}}

DOMAINS:
{{frozen_domains_with_member_premise_texts}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```

`blind_case_id` is a random identifier held in a separate key file. Venture name, event, year, and all outcome variables are joined only after extraction is complete and locked.

---
