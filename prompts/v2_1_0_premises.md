# Codebook 2.1.0 Pass A: premise extraction

Pass A extracts the premises of an entrepreneurial theory from a single pitch transcript. Strategic domains and causal links are not coded in this pass. Pass B (composition tagging) and Pass C (domain grouping) are applied subsequently to the finalized premise list.

> **Instrument note.** Sections 1 to 5 constitute the coding instrument. Sections 6 and 7 are machine only (output format and call template). Any revision to sections 1 to 5 constitutes a new codebook version; agreement statistics computed under a prior version do not carry forward.
>
> Sections 1 to 3 define the constructs and are read once during coder training. **Section 4 is the coding protocol for each transcript.** Section 5 provides three worked examples.


## 1. Coder role

> You are a trained research coder applying a fixed codebook to a single pitch transcript. Your task is descriptive measurement, not evaluation: do not assess whether the pitch is persuasive, investable, or likely to succeed, and do not infer its outcome. Code only what the transcript states or clearly implies. Where the text does not support a coding decision, omit the unit rather than inferring structure.


## 2. Blind-coding requirement

The coding input consists of transcript text and an anonymous case identifier. It must not include venture name, founder name, event, year, funding history, selection outcome, or other outcome-relevant metadata.

> **Instruction to the model:** The transcript may contain a company or product name. If you recognize the venture, disregard all external knowledge of it, including subsequent funding, growth, acquisition, failure, or competitive performance. Code only what this transcript claims. Do not reference external knowledge in your output.


## 3. Definitions

### 3.1 Premises within entrepreneurial theory

Entrepreneurial theories comprise three elements: (1) **premises** about conditions that drive value creation, (2) **causal links** connecting premises to one another and to value, and (3) **strategic domains** grouping premises that can be learned and revised together. This codebook codes the first element only.

### 3.2 Premise

A **premise** is an explicit or clearly implied claim about a condition the entrepreneur treats as necessary for the theory to create value. The claim must be specific enough that, in principle, it could be shown to be wrong.

Breadth is measured as the count of premises. The main coding decision in this pass is therefore **how to split the transcript into premises**: where one premise ends and the next begins.


## 4. Coding protocol

This pass extracts premises only. Composition tagging and domain grouping are deferred to later passes.

### 4.1 Procedure

Apply the following steps in order.

1. **Initial read.** Read the transcript once without coding.

2. **Identify claims.** Mark each claim the entrepreneur presents as necessary for the venture's theory of value to hold. Claims may take the form of design choices, capabilities, or assumptions about customers, channels, technology, or operations. Code each claim at the scope at which the entrepreneur asserts it: do not subdivide a claim the entrepreneur did not separate, and do not merge claims the entrepreneur kept distinct. When the entrepreneur bundles several items into one assertion (e.g., "parents face five pain points"), treat the whole assertion as one claim.

3. **Apply exclusions.** Do not code the following as premises:

   - Financing ask, valuation, equity offered, or capital already raised.
   - Greetings, closings, thanks, and appeals to the audience.
   - Speech by anyone other than the pitching entrepreneur(s), and any Q&A content.
   - Product or company name stated without an associated condition.
   - Biographical credentials, unless the theory itself would have to change if the credential were untrue, rather than merely looking weaker.
   - Traction or press metrics offered as evidence of past performance. When the entrepreneur presents the underlying mechanism as a continuing condition for value, code the mechanism, not the metric.
   - Industry vision statements (e.g., *"the future of data is a writable future"*). See section 4.3.

4. **State what would need to change.** For each remaining claim, write briefly what the entrepreneur would need to change if the claim turned out to be wrong (e.g., *reformulate the product*, *secure alternative supply*, *rebuild the tracking module*). If nothing would need to change, the claim is not a condition the venture depends on; exclude it.

5. **Decide how many premises.** Claims that would require the same change belong to **one premise**. Claims that would require different changes belong to **separate premises**.

6. **When the split is unclear, record separate premises.** Note the pair in `notes`. Do not default to merging.

7. **Record each premise.** State each premise as one declarative sentence in the entrepreneur's terms, normalized only for grammar. Attach an **evidence span**: a contiguous substring copied verbatim from the transcript. Spacing and capitalization may differ from the premise text; the words must match. Do not paraphrase or quote text absent from the transcript. Where the meaning is clear despite an obvious transcription error, correct the premise text only; the evidence span retains the transcript as written. If the transcript is truncated, code only what is present. When multiple co-founders present, pool their claims without duplicating premises stated by more than one speaker.

**No target premise count.** Breadth is computed downstream and is not a coding input. Neither narrow nor broad theories are preferred; do not add, omit, or merge premises to adjust list length.

### 4.2 Worked examples: one premise or several

The following cases apply steps 4 and 5 to recurring transcript patterns. They illustrate the protocol; they do not add rules. When a case is not listed, apply steps 4 and 5 directly.

**One premise** (one change would address all claims):

- Restatement or near-synonyms: *"it's delicious, it tastes great, people love the flavor."*
- Quantitative detail modifying a claim: *"24 inches tall, holds 26 ounces."*
- A mechanism presented as indivisible: *"a single 30-second phone scan replaces in-person measurement."*
- Performance attributes of one process: *"faster, cheaper, uses less water, emits less CO2."*
- Enumerated applications of one capability: *"First, active warning. Two, usable for logistics. Three, your building has a Carfax,"* describing one sensor network.
- Features that follow from a single integration, such as BYOD activation, presence, and transcription from one switch platform.
- Price and channel structure for the same offering.
- Patents attached to a mechanism already claimed.
- A problem set presented as one unmet need: *"parents face five major pain points."*

**Several premises** (each claim requires its own change):

- Coordinated claims about different conditions: *"combines seaweed and mushrooms, and we source kelp from regenerative ocean farms."*
- Capabilities each performing a distinct function: communication, report cards, GPS tracking, fee payment, delivery.
- Intellectual property licensed or sold as a separate line of business.
- A product use presented as independently offered.
- Partner or reseller economics that could fail while the stated price point remained.

Lists often raise this question and appear on both sides above. Apply the same test: if one change would address every item, the list is one premise; if each item requires its own change, each is a separate premise. In the School Bridge pitch, five pain points form one premise (change: re-target the problem set); five product capabilities form five premises (each requires its own build or change).

### 4.3 Value criterion

Record **one value criterion** in the `value` field: the beneficiary and/or the outcome the market is claimed to receive. When the entrepreneur identifies a priority benefit, code that benefit. Financing is never a value criterion.

Omit `value` only when the transcript neither states nor clearly implies a value criterion, as when a pitch is truncated before value is asserted. Do not infer a value criterion.

The value criterion is not an independent variable in the analysis. It anchors what counts as "necessary for the theory to create value" and permits audit of premise coding decisions.


## 5. Worked examples

Three **verbatim hold-out excerpts** from the Startup Battlefield corpus, coded according to section 4. These cases are reserved for training and agreement calibration and are **excluded from the confirmatory analysis sample** (see `prompts/registry.md` and `data/corpora/startup_battlefield/samples/calibration_holdouts.csv`).

### 5.1 AgriList (`pilot-773`)

**Transcript excerpt:** "Meet Tom. Tom's an indoor pepper grower who manages about 50,000 square feet of peppers every day. Tom likes to control everything in his greenhouse. So he has sensors that control lighting, temperature, CO2, pH, relative humidity, and more. He spends hours recording detailed notes in notebooks and records pepper yields by hand. But this is raw data. It doesn't talk to each other, and it doesn't tell Tom anything. It's virtually useless for Tom. So Tom will end up losing hours digging through his notes to find out what goes wrong. He will spend tons of money, thousands of dollars on consultants in order for them to tell him what's going on. Or he will just make decisions every day based on his gut intuition whenever something goes wrong in his greenhouse. It shouldn't be this hard. With AgriList, all of Tom's data talks to each other, eliminating the guesswork from decision making. AgriList can automatically sync with any hardware he has in the equipment, like sensors. He can upload documents. And he can even enter data manually if there isn't a sensor that takes that information. This is a big deal. For the first time, Tom has all of his information in one place. Agoralyst also acts as a task manager, showing Tom what he has to do on a day-to-day basis. He can see what he has to harvest and what he has to seed. And he can see more information for crops coming up in the next few days. So he'll click on one of these information buttons. And he can see, oh no, the green peppers are expecting low yield because of some low germination rates and problems they had. Now that he has this information, Tom can proactively let his sales team know that there's a problem and that they should expect lower yields. And he can take steps towards improving the problem, like increasing the growth cycle by a day. Another thing Tom cares about and looks at on a day-to-day basis is his energy use. His current energy use is the yellow line in this graph. And it shows you that greenhouses use a lot of energy. The green line shows you that Tom can actually take advantage of time-varying electricity rates and turn his lights on or off at different hours in order to take advantage of different rates. AgriList goes a step further and provides recommendations to show Tom when he should turn on and off his lights to achieve maximal savings. With our recommendation, Tom can save $150 today, which means he can save $50,000 annually just by turning his lights on or off at different times."

**Premises:**

| Id | Premise | Evidence span |
|---|---|---|
| P1 | Disconnected sensor and notebook data is insufficient for operational decisions | "doesn't talk to each other, and it doesn't tell Tom anything" |
| P2 | Unified greenhouse data eliminates guesswork from grower decisions | "all of Tom's data talks to each other, eliminating the guesswork from decision making" |
| P3 | Hardware sensors, document uploads, and manual entry can feed one platform | "automatically sync with any hardware he has in the equipment, like sensors" |
| P4 | Integrated task management can track harvest, seeding, and upcoming crop alerts | "acts as a task manager, showing Tom what he has to do on a day-to-day basis" |
| P5 | Low germination or yield problems can be detected early enough to adjust sales forecasts | "green peppers are expecting low yield because of some low germination rates" |
| P6 | Growth-cycle adjustments can recover from detected yield problems | "increasing the growth cycle by a day" |
| P7 | Time-varying electricity rates create savings opportunities for greenhouse lighting | "take advantage of time-varying electricity rates and turn his lights on or off" |
| P8 | Automated lighting recommendations can achieve substantial annual energy savings | "save $50,000 annually just by turning his lights on or off at different times" |

**Value criterion:** Indoor growers operate with less guesswork in daily decisions. Evidence span: "eliminating the guesswork from decision making."

**Notes:** Tom's consultant spend and notebook workflow illustrate the problem; they are not separate premises. Energy savings and yield alerts are premises because each would require a different fix if wrong. Beta revenue and market-size figures elsewhere in the full pitch are excluded under step 3.

### 5.2 Pi Charging (`pilot-620`)

**Transcript excerpt:** "Instead, we built Pi around a safe magnetic charging standard. But until today, magnetic charging was very limited. You had to put a device down perfectly parallel to the receiver to get any power. But thanks to our incredible team and Leeshan's breakthrough, our patented platform can power multiple devices at any angle. It's safe, it's affordable, and it's FCC compliant. Our business model has two parts. First, we will sell Pi directly to consumers. We have over 50% gross margins and anticipate a very high lifetime value per customer. If you like Pi in your kitchen, you're going to want one in the living room, the bedroom, and in the office and enterprise. Second, we are opening the Pi platform for use by existing consumer electronics OEMs."

**Premises:**

| Id | Premise | Evidence span |
|---|---|---|
| P1 | Magnetic-field charging can power multiple devices at any angle | "patented platform can power multiple devices at any angle" |
| P2 | A patent protects the wireless-power approach | "our patented platform" |
| P3 | The product meets FCC safety requirements for consumer use | "It's safe, it's affordable, and it's FCC compliant" |
| P4 | Direct-to-consumer sales can sustain viable unit economics | "over 50% gross margins" |
| P5 | Multi-room adoption extends revenue per customer | "want one in the living room, the bedroom, and in the office and enterprise" |
| P6 | OEM licensing extends the platform to device manufacturers | "opening the Pi platform for use by existing consumer electronics OEMs" |

**Value criterion:** Consumers get safe, affordable contactless charging without charging pads. Evidence span: "It's safe, it's affordable, and it's FCC compliant."

**Notes:** Reservation counts, press coverage, and investor names elsewhere in the full pitch are excluded as traction. Patent protection and FCC compliance are separate premises because each would require a different change if wrong.

### 5.3 Tango TV (`pilot-649`, truncated)

**Transcript excerpt:** "At Tango TV, we are building a media streaming platform for mostly local content. So here we are talking local movies, local TV shows, even local music videos. You can stream Tango TV on your mobile phone. We have an amazing mobile app. I can demo it to you later. And on your TV. So we are here seeking $500,000 in exchange for e-credit at a pre-money valuation of $2 million. So you could have up to"

**Premises:**

| Id | Premise | Evidence span |
|---|---|---|
| P1 | Audiences want streaming focused on local movies, TV, and music | "media streaming platform for mostly local content" |
| P2 | Mobile and TV are both viable delivery endpoints | "stream Tango TV on your mobile phone" |

**Value criterion:** Local audiences access local media on mobile and TV. Evidence span: "local movies, local TV shows, even local music videos."

**Notes:** Transcript truncated mid-sentence during the financing ask; code only present content. Valuation and raise amount are excluded under step 3. The mobile-app demo offer is presentation detail, not a separate premise.


## 6. Output schema (machine only)

Return exactly one JSON object. No prose outside the JSON.

**Worked example (Case 5.1 in JSON).** Premise and value content must match section 5; only the serialization format differs.

```json
{
  "meta": {"codebook_version": "2.1.0", "pass": "premises", "unit": "pitch_transcript", "case_id": "BLIND_CASE_ID", "model_id": "MODEL_ID", "model_provider": "PROVIDER", "temperature": null, "temperature_controlled": false, "extraction_run": 1, "extracted_at": "ISO-8601"},
  "premises": [
    {"id": "P1", "text": "Disconnected sensor and notebook data is insufficient for operational decisions", "status": "explicit", "evidence_span": "doesn't talk to each other, and it doesn't tell Tom anything"},
    {"id": "P2", "text": "Unified greenhouse data eliminates guesswork from grower decisions", "status": "explicit", "evidence_span": "all of Tom's data talks to each other, eliminating the guesswork from decision making"},
    {"id": "P3", "text": "Hardware sensors, document uploads, and manual entry can feed one platform", "status": "explicit", "evidence_span": "automatically sync with any hardware he has in the equipment, like sensors"},
    {"id": "P4", "text": "Integrated task management can track harvest, seeding, and upcoming crop alerts", "status": "explicit", "evidence_span": "acts as a task manager, showing Tom what he has to do on a day-to-day basis"},
    {"id": "P5", "text": "Low germination or yield problems can be detected early enough to adjust sales forecasts", "status": "explicit", "evidence_span": "green peppers are expecting low yield because of some low germination rates"},
    {"id": "P6", "text": "Growth-cycle adjustments can recover from detected yield problems", "status": "explicit", "evidence_span": "increasing the growth cycle by a day"},
    {"id": "P7", "text": "Time-varying electricity rates create savings opportunities for greenhouse lighting", "status": "explicit", "evidence_span": "take advantage of time-varying electricity rates and turn his lights on or off"},
    {"id": "P8", "text": "Automated lighting recommendations can achieve substantial annual energy savings", "status": "explicit", "evidence_span": "save $50,000 annually just by turning his lights on or off at different times"}
  ],
  "value": [
    {"id": "V1", "text": "Indoor growers operate with less guesswork in daily decisions", "status": "explicit", "evidence_span": "eliminating the guesswork from decision making"}
  ],
  "notes": "Energy savings and yield alerts are premises; beta revenue elsewhere in the full pitch is excluded."
}
```

**Schema template:**

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


## 7. User message template (machine only)

```text
Extract the critical premises of the entrepreneurial theory from the transcript below using codebook v2.1.0 Pass A. Return JSON only. Do not use any outside knowledge about this venture.

Requirements: record separate premises when each claim would require a different change, and one premise when a single change would suffice; no target premise count; no domains or causal links in this pass; every evidence_span copied verbatim from the transcript. When the entrepreneur states a value criterion, record exactly one value node.

CASE_ID: {{blind_case_id}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```

`blind_case_id` is a random identifier held in a separate key file. Venture name, event, year, and all outcome variables are joined only after extraction is complete and locked.
