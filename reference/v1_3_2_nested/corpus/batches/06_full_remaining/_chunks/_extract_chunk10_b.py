# -*- coding: utf-8 -*-
"""Remaining cases + write/validate for chunk 10."""
import json
import pathlib
import sys

BASE = pathlib.Path(r"c:\Projects\uni\sources\entrepreneurial_theories\data\theory_dags\corpus_v1_3\batches\06_full_remaining")
TRANS = BASE / "transcripts"
RUNS = BASE / "runs"
sys.path.insert(0, str(pathlib.Path(r"c:\Projects\uni\sources\entrepreneurial_theories\scripts")))
from validate_theory_dag import span_matches, validate  # type: ignore

from _extract_chunk10_a import DATA, meta, wrap, load_t  # noqa: E402


# ===================== pilot-232 BetterData =====================
DATA["pilot-232"] = [
    {
        "premises": [
            {"id": "P1", "text": "Privacy regulation and internal privacy/legal/security processes make data access slow for AI and data teams", "status": "explicit", "evidence_span": "It takes a long time to get access to data. Data is either locked away, or they have to go through a long process, including privacy engineering, legal, and security"},
            {"id": "P2", "text": "Private real data can be converted into 100% anonymized synthetic data with the same properties", "status": "explicit", "evidence_span": "We convert private real data into 100% anonymized synthetic data that has the same properties as the real data"},
            {"id": "P3", "text": "Confidential computing lets computation run on encrypted data so BetterData cannot see the data", "status": "explicit", "evidence_span": "We introduced confidential computing, where you can compute on encrypted data, so companies don't have to trust us with data because we can't even see it"},
            {"id": "P4", "text": "Data tokenization keeps ownership with the company via tamper-proof locks", "status": "explicit", "evidence_span": "data tokenization. Companies own their data fully, and we have tamper-proof locks for that as well"},
            {"id": "P5", "text": "Encrypted multi-party collaboration can combine datasets and return shared synthetic data without revealing raw data", "status": "explicit", "evidence_span": "safely collaborate with others, all while their customer data remains encrypted to all parties involved"},
            {"id": "P6", "text": "Licensing and support business with on-prem, private, and public cloud plus API or web interface", "status": "explicit", "evidence_span": "We have a licensing and support business model, and we support on-premise, private, and public cloud"},
        ],
        "domains": [
            {"id": "D1", "name": "Privacy-constrained data access", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Synthetic data and confidential compute", "premise_ids": ["P2", "P3", "P4", "P5"]},
            {"id": "D3", "name": "Licensing deployment model", "premise_ids": ["P6"]},
        ],
        "value": [{"id": "V1", "text": "Companies innovate on data in days while protecting customer privacy", "status": "explicit", "evidence_span": "allows you to innovate on data in days and not months"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "This slows down innovation a lot"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "innovate on data in days and not months"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "You can either use our APIs integrated directly into your data science pipelines or the web interface"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.85},
        "notes": "Vision that most AI models will train on synthetic data excluded per v1.3.2 clarification 4. Pilot counts and grants treated as traction/credentials. QA report and ML parity folded into synthetic-data mechanism.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Privacy laws and compliance make sharing and accessing data the biggest bottleneck for building AI software", "status": "explicit", "evidence_span": "data privacy to be the biggest challenge for companies to build AI software today"},
            {"id": "P2", "text": "BetterData produces anonymized synthetic data usable like real data for analytics and ML", "status": "explicit", "evidence_span": "synthetic data can be used just like the real data for your analytics, for your machine learning"},
            {"id": "P3", "text": "Confidential computing and tokenization keep raw customer data unread by BetterData and owned by the company", "status": "explicit", "evidence_span": "at no point in time does better data access to read or download the data set itself"},
            {"id": "P4", "text": "Parties can collaborate on encrypted datasets to produce combined synthetic customer profiles", "status": "explicit", "evidence_span": "companies can collaborate on data sets together and understand more about their combined and common customers"},
            {"id": "P5", "text": "Sold as licensing/support across on-prem and cloud with API or web access", "status": "explicit", "evidence_span": "licensing and support business model"},
        ],
        "domains": [
            {"id": "D1", "name": "Data access delay problem", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Privacy-preserving synthetic platform", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "Licensing GTM", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Faster data access and safe collaboration without exposing private data", "status": "explicit", "evidence_span": "access data in days and not months, retain full ownership over their data, and safely collaborate with others"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "don't let data slow you down"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "customer data remains encrypted to all parties involved"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "APIs integrated directly into your data science pipelines"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.8},
        "notes": "Confidential computing and tokenization merged into one ownership/privacy mechanism this run. Market-size and pilot traction excluded.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Getting usable data requires long privacy engineering, legal, and security processes that slow innovation", "status": "explicit", "evidence_span": "This slows down innovation a lot"},
            {"id": "P2", "text": "Synthetic data generation preserves statistical properties while anonymizing private data", "status": "explicit", "evidence_span": "100% anonymized synthetic data that has the same properties as the real data"},
            {"id": "P3", "text": "Encrypted confidential computing means the vendor cannot see customer data during jobs", "status": "explicit", "evidence_span": "companies don't have to trust us with data because we can't even see it"},
            {"id": "P4", "text": "Tokenized data assets remain company-owned with tamper-proof locks", "status": "explicit", "evidence_span": "That token belongs to the company. So only the company can read or download their customer data"},
            {"id": "P5", "text": "Cross-organization encrypted collaboration yields joint synthetic datasets", "status": "explicit", "evidence_span": "the encrypted data from both banks will go into the confidential computing environment, combined together, and a synthetic data will be produced"},
            {"id": "P6", "text": "Deployable via licensing/support on-prem or cloud through APIs or a web UI", "status": "explicit", "evidence_span": "we support on-premise, private, and public cloud"},
        ],
        "domains": [
            {"id": "D1", "name": "Access friction under privacy rules", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Synthetic data stack", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "Multi-party collaboration", "premise_ids": ["P5"]},
            {"id": "D4", "name": "Licensing and deployment", "premise_ids": ["P6"]},
        ],
        "value": [{"id": "V1", "text": "Innovate on private data quickly without compromising privacy or ownership", "status": "explicit", "evidence_span": "innovate on data while protecting their customers' privacy"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "It takes a long time to get access to data"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "innovate on data in days and not months"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "safely collaborate with others"},
            {"from": "D4", "to": "V1", "type": "domain-value", "evidence_span": "licensing and support business model"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.82},
        "notes": "Collaboration split as its own module this run because the bank demo presents it as a distinct path to value. Future market-ownership claim not coded.",
    },
]

# ===================== pilot-1153 Schwope =====================
DATA["pilot-1153"] = [
    {
        "premises": [
            {"id": "P1", "text": "Vendors unilaterally collect and leverage tracking data while consumers lack equivalent leverage", "status": "explicit", "evidence_span": "Those with the vendors are the only ones that can be amassing and leveraging and tracking the data that's out there"},
            {"id": "P2", "text": "Forwarding order confirmations captures purchase history into the consumer's Schwope account", "status": "explicit", "evidence_span": "all I need to do is forward my order confirmations in my inbox to wowat12.com"},
            {"id": "P3", "text": "Consumers augment purchase records with why/need context for mindful shopping and taste signaling", "status": "explicit", "evidence_span": "augmenting the basic purchase data, the stuff that's like the what, the how much sort of thing, with the why"},
            {"id": "P4", "text": "A Shopify application makes the product data-compatible with tens of thousands of stores", "status": "explicit", "evidence_span": "application with Shopify stores that makes us instantly data compatible with tens of thousands of stores"},
            {"id": "P5", "text": "Consumers can port selected shopping history outbound as a personal RFP for personalized deals and loyalty value", "status": "explicit", "evidence_span": "the customer can take all that they've amassed and leverage it back for something of value in return, better deals, loyalty points, VIP programs"},
        ],
        "domains": [
            {"id": "D1", "name": "Consumer data asymmetry", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Purchase capture and enrichment", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "Data-out personal RFP", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Consumers make shopping data meaningful and regain leverage over vendors", "status": "explicit", "evidence_span": "building tools for consumers to help them make their shopping data more meaningful"}],
        "secondary_value": [{"text": "Opt-in data portability yields personalized merchant offers", "evidence_span": "It's all opt-in and transparent"}],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "what if the consumers had as much leverage with the data as the vendors do"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "make their shopping data more meaningful"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "leverage it back for something of value in return"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.75},
        "notes": "Data-out / personal RFP coded as a premise because the speaker frames it as the disruptive value path, not mere aspiration. Social sharing roadmap folded into enrichment/GTM rather than split. ASR names (Schwab/Schwelp) left in spans.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Consumer shopping data is one-sided today in favor of vendors", "status": "explicit", "evidence_span": "we think that it's one-sided"},
            {"id": "P2", "text": "Email-forwarded receipts and store plugins feed purchases into a consumer-owned history", "status": "explicit", "evidence_span": "forward my order confirmations in my inbox"},
            {"id": "P3", "text": "Annotating purchases with needs and stories enables taste signaling and mindful shopping", "status": "explicit", "evidence_span": "What we're doing here as we're posting what we're buying and what we talk about when we're buying is taste signaling"},
            {"id": "P4", "text": "Shopify compatibility connects tens of thousands of merchant stores", "status": "explicit", "evidence_span": "instantly data compatible with tens of thousands of stores"},
            {"id": "P5", "text": "Selective sharing of history with chosen brands returns personalized results and deals", "status": "explicit", "evidence_span": "I can choose what part of my data, how far back in my data that I'm sharing. with the stores in order for them to give me really cool personalized results"},
        ],
        "domains": [
            {"id": "D1", "name": "One-sided data problem", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Ingest and annotate purchases", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "Personal RFP outbound", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Consumers gain vendor-like leverage from their own shopping data", "status": "explicit", "evidence_span": "consumers had as much leverage with the data as the vendors do"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "There's definitely something wrong with this picture"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "make their shopping data more meaningful"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "personalized results"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.72},
        "notes": "Analytics mashup (weather) treated as planned feature of enrichment, not a separate premise. Retailer 'powered by' interest treated as GTM evidence not a premise.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Consumers forget purchases and lack tools to amass shopping data the way vendors do", "status": "explicit", "evidence_span": "as consumers, well, we kind of forget the last couple of things that we purchase most of the time"},
            {"id": "P2", "text": "Order-confirmation forwarding populates a consumer shopping account automatically", "status": "explicit", "evidence_span": "forward my order confirmations in my inbox to wowat12.com"},
            {"id": "P3", "text": "Editing purchases with why/need metadata makes history sliceable and meaningful", "status": "explicit", "evidence_span": "I can start to slice it by when, where, what time, also by what I needed at the time"},
            {"id": "P4", "text": "Shopify plugin enables automatic capture from many merchant stores", "status": "explicit", "evidence_span": "because it has the application installed, it should automatically appear"},
            {"id": "P5", "text": "Portable opt-in sharing of selected data drives personalized merchant responses", "status": "explicit", "evidence_span": "data portability exemplified"},
        ],
        "domains": [
            {"id": "D1", "name": "Consumer data tools gap", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Data-in capture product", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "Data-out portability", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Meaningful consumer-controlled shopping data that can be leveraged for value back", "status": "explicit", "evidence_span": "make their shopping data more meaningful"}],
        "secondary_value": [{"text": "Better deals, loyalty, VIP, and search from leveraged data out", "evidence_span": "better deals, loyalty points, VIP programs, and even better search results"}],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "what if the consumers had as much leverage with the data as the vendors do"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "I've shown you a lot of the data in to Schwab"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "the real disruptive part of Schwab. And that is data out"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.7},
        "notes": "Speaker explicitly elevates data-out as the disruptive module, so it is retained separately from data-in. Twitter/Facebook sharing roadmap not split.",
    },
]

# ===================== pilot-727 JewelBots =====================
DATA["pilot-727"] = [
    {
        "premises": [
            {"id": "P1", "text": "Girls want friendship and communication in toys, not low-tech dolls like Baby Alive", "status": "explicit", "evidence_span": "we've heard from them friendship, they're friends, and communication"},
            {"id": "P2", "text": "Patent-pending mesh networking lets wearables communicate device-to-device without a phone", "status": "explicit", "evidence_span": "Jewelbots is the first wearable device to communicate from device to device. That means girls don't need a mobile phone"},
            {"id": "P3", "text": "Friendship color groups, proximity glow, and customizable secret light/vibration messages are the social product experience", "status": "explicit", "evidence_span": "Jewelbots can be used to send messages, so girls can send each other secret messages in their own languages"},
            {"id": "P4", "text": "Open-source Arduino programming lets girls add custom effects and interactions", "status": "explicit", "evidence_span": "Jewelbots are completely open source. So girls can code them to do whatever they imagine"},
            {"id": "P5", "text": "COPPA compliance enables safe girl-to-girl communication", "status": "explicit", "evidence_span": "Jewelbots are also COPPA compliant, so the girls can communicate with each other completely safely"},
            {"id": "P6", "text": "Sold online in packs with interchangeable charms/bands and licensing partnerships that extend the brand", "status": "explicit", "evidence_span": "JewelBots are sold online for $69 for one, $99 for the two-pack, and $139 for the Bestie three-pack"},
        ],
        "domains": [
            {"id": "D1", "name": "Girl friendship toy need", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Mesh wearable and coding", "premise_ids": ["P2", "P3", "P4", "P5"]},
            {"id": "D3", "name": "Pack pricing and licensing", "premise_ids": ["P6"]},
        ],
        "value": [{"id": "V1", "text": "High-tech friendship wearables that empower girls toward engineering", "status": "explicit", "evidence_span": "every girl feels empowered to become an engineer"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "Girls are just as smart and they deserve a lot better"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "girls can code them to do whatever they imagine"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "JewelBots are sold online for $69 for one"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.85},
        "notes": "Friendship pairing/glow uses folded into P3 per v1.3.2 clarification 5. Sales dollars excluded as traction; price packs kept as commercial condition. Founder bio excluded.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Girl toys today lack real high-tech capability compared with toys made for boys", "status": "explicit", "evidence_span": "awesome, high-tech toys like this built for boys and stuff like this made for girls"},
            {"id": "P2", "text": "Mesh-network bracelets communicate peer-to-peer without requiring a mobile phone", "status": "explicit", "evidence_span": "girls don't need a mobile phone in order to use and program their Jewelbots"},
            {"id": "P3", "text": "Users pair friendship color groups and send secret coded messages via lights and vibrations", "status": "explicit", "evidence_span": "Using either their device or phone, users can set their friendships"},
            {"id": "P4", "text": "Arduino open-source coding enables custom weather and other interactions", "status": "explicit", "evidence_span": "You plug it in with a micro USB. This is just one of the ideas"},
            {"id": "P5", "text": "COPPA-compliant design keeps communication safe for girls", "status": "explicit", "evidence_span": "COPPA compliant, so the girls can communicate with each other completely safely"},
            {"id": "P6", "text": "Online pack pricing plus charms/bands and licensed characters (e.g., Powerpuff Girls) monetize the product", "status": "explicit", "evidence_span": "Jewelbots come with interchangeable charms and bands sold separately"},
        ],
        "domains": [
            {"id": "D1", "name": "Tech gap in girls' toys", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Programmable mesh friendship wearable", "premise_ids": ["P2", "P3", "P4", "P5"]},
            {"id": "D3", "name": "Retail packs and collectibles", "premise_ids": ["P6"]},
        ],
        "value": [{"id": "V1", "text": "Girls get better high-tech toys that teach coding through friendship play", "status": "explicit", "evidence_span": "that's why we made JewelBots"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "This is awful and unfair"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "The best part is that Jewelbots are completely open source"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "Girls can collect and trade their favorite limited edition designs"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.82},
        "notes": "Licensing announcements folded into commercial premise with charms. Patent pending kept inside mesh premise (v1.3.1 clarification 1).",
    },
    {
        "premises": [
            {"id": "P1", "text": "Research with girls shows friendship and communication are the desired toy attributes", "status": "explicit", "evidence_span": "We've talked to over 200 girls around the nation and asked them, what is important to you"},
            {"id": "P2", "text": "Device-to-device mesh wearables work without phones", "status": "explicit", "evidence_span": "patent pending mesh network means Jewelbots is the first wearable device to communicate from device to device"},
            {"id": "P3", "text": "Social features include friendship colors, proximity brightness, party animations, and secret messages", "status": "explicit", "evidence_span": "When girls are together, their bracelets match"},
            {"id": "P4", "text": "Open-source Arduino coding is the core learning path", "status": "explicit", "evidence_span": "You code a Jewelbot just like you would an Arduino"},
            {"id": "P5", "text": "Safety via COPPA compliance", "status": "explicit", "evidence_span": "Jewelbots are also COPPA compliant"},
            {"id": "P6", "text": "Multi-pack online pricing with Bestie three-pack as top seller", "status": "explicit", "evidence_span": "$139 for the Bestie three-pack, which is by far our biggest seller"},
            {"id": "P7", "text": "Licensing with Cartoon Network and Google Made with Code extends distribution and brand", "status": "explicit", "evidence_span": "our first Jewelbots licensing agreements. First, with the Cartoon Network"},
        ],
        "domains": [
            {"id": "D1", "name": "Girl research insight", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Mesh social wearable platform", "premise_ids": ["P2", "P3", "P4", "P5"]},
            {"id": "D3", "name": "Pricing and licensing GTM", "premise_ids": ["P6", "P7"]},
        ],
        "value": [{"id": "V1", "text": "Empower girls with friendship tech that leads into engineering", "status": "explicit", "evidence_span": "inspire as many women as possible to join this field"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "P1", "to": "P3", "type": "premise-premise", "evidence_span": "JewelBots are made from the stuff girls ask for"},
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "Girls are just as smart and they deserve a lot better"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "girls can code them to do whatever they imagine"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "make JewelBots into a massive business and brand"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.8},
        "notes": "Licensing split from pack pricing this run as separately revisable brand/channel module. Sales cumulative dollars excluded.",
    },
]

# ===================== pilot-889 HealthSync =====================
DATA["pilot-889"] = [
    {
        "premises": [
            {"id": "P1", "text": "Diabetes care is inadequate because manual logging is tedious, digital tools are incompatible, and no support-network platform exists", "status": "explicit", "evidence_span": "proper care for diabetes is inadequate and in many countries broken due to the following usability and technical problems"},
            {"id": "P2", "text": "A smart audio-jack cable connects the majority of existing glucometers to smart devices without buying new meters", "status": "explicit", "evidence_span": "this smart cable is compatible with majority of the glucometers in the market, even those in emerging markets"},
            {"id": "P3", "text": "App workflow color-codes readings, tags meals/meds, and logs contextual factors for interpretable graphs and doctor sharing", "status": "explicit", "evidence_span": "the app color codes some of the readings purple or orange if certain numbers are out of range"},
            {"id": "P4", "text": "Partner function lets remote family view stats, send encouragement, and set alerts for missed syncs or out-of-range numbers", "status": "explicit", "evidence_span": "I from Taiwan can use any one of my smart devices and view her stats"},
            {"id": "P5", "text": "Patient-centric platform enables third-party interactions such as insurers and pharmacies", "status": "explicit", "evidence_span": "enabling new forms of interaction with third parties to the patient"},
        ],
        "domains": [
            {"id": "D1", "name": "Broken diabetes tooling", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Legacy meter smart cable and app", "premise_ids": ["P2", "P3"]},
            {"id": "D3", "name": "Support network and third parties", "premise_ids": ["P4", "P5"]},
        ],
        "value": [{"id": "V1", "text": "Patients regain control of glucose management with usable connected tools", "status": "explicit", "evidence_span": "Health to Sync aggregates glucose data, ultimately giving control back to you"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "proper care for diabetes is inadequate"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "taking legacy devices, bringing them to the digital age, and making them smarter"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "data availability to the support network"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.85},
        "notes": "Three problem bullets folded into one broken-care premise. App UI details folded into P3. Family bio motivates but is not coded as a team premise. Indiegogo ask excluded.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Paper logbooks make sharing and analyzing blood sugar data difficult", "status": "explicit", "evidence_span": "a logbook, is the typical tool that records blood sugar levels, which actually makes sharing and analyzing data difficult"},
            {"id": "P2", "text": "Smart cable bridges legacy glucometers to phones/tablets via audio jack across most devices including emerging markets", "status": "explicit", "evidence_span": "connecting glucometers to the smart devices via the audio jack"},
            {"id": "P3", "text": "Software reduces data tedium and preserves transfer integrity with graphs and secure upload", "status": "explicit", "evidence_span": "solved three issues. One, data tedium. Two, data transferability integrity"},
            {"id": "P4", "text": "Remote partners/family can monitor and receive proactive notifications", "status": "explicit", "evidence_span": "I can pre-set notifications that would alert me should grandma forget to sync to test herself"},
            {"id": "P5", "text": "Platform opens future third-party service models including insurers and pharmacies", "status": "explicit", "evidence_span": "insurance companies, and offering flexible insurance premiums"},
        ],
        "domains": [
            {"id": "D1", "name": "Manual logging failure", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Hardware-software sync product", "premise_ids": ["P2", "P3"]},
            {"id": "D3", "name": "Care network platform", "premise_ids": ["P4", "P5"]},
        ],
        "value": [{"id": "V1", "text": "Usable digital diabetes care connecting patients to support networks", "status": "explicit", "evidence_span": "a platform connecting the patients to the support network doesn't exist"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "manually recording is considered tedious"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "making them smarter"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "data availability to the support network"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.8},
        "notes": "Value evidence uses the stated missing platform as the desired outcome criterion. Geographic launch list treated as roadmap traction, not a premise.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Usability failures: tedious manual recording, incompatible hardware/software, missing support-network platform", "status": "explicit", "evidence_span": "One, manually recording is considered tedious. Two, while digital tools exist, hardware and software are often incompatible"},
            {"id": "P2", "text": "Smart cable makes existing glucometers work with smart devices so users need not replace meters", "status": "explicit", "evidence_span": "users don't have to go out and buy new ones"},
            {"id": "P3", "text": "App tagging, medication flags, and contextual logs produce shareable graphs for patients and doctors", "status": "explicit", "evidence_span": "she can email or send it to the doctor in advance, or use it with a doctor the next time she visits"},
            {"id": "P4", "text": "Secure cloud plus partner view enables remote caregiving across devices", "status": "explicit", "evidence_span": "The data is also uploaded into a secure data center, where I, as part of the partner function, am one of her partners"},
            {"id": "P5", "text": "Third-party ecosystem (insurers, pharmacies, APIs) extends the patient-centric platform", "status": "explicit", "evidence_span": "this platform also enables us to get into new service business models in the future, API strategy partnerships"},
        ],
        "domains": [
            {"id": "D1", "name": "Care inadequacy diagnosis", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Cable and patient app", "premise_ids": ["P2", "P3"]},
            {"id": "D3", "name": "Partner network and ecosystem", "premise_ids": ["P4", "P5"]},
        ],
        "value": [{"id": "V1", "text": "Control glucose by aggregating and sharing usable patient data", "status": "explicit", "evidence_span": "To control diabetes is about controlling glucose"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "P2", "to": "P3", "type": "premise-premise", "evidence_span": "This smart solution, along with the software that we're offering, basically solved three issues"},
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "proper care for diabetes is inadequate"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "bringing them to the digital age"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "giving control back to you"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.83},
        "notes": "Prevalence statistic treated as problem framing, not a premise. Explicit 'smart solution along with software solved three issues' warrants P2->P3.",
    },
]

# ===================== pilot-605 Bridgefy =====================
DATA["pilot-605"] = [
    {
        "premises": [
            {"id": "P1", "text": "Many smartphone users lack internet access, creating life-critical and development connectivity gaps", "status": "explicit", "evidence_span": "66% of the world has a smartphone in their hands, but 53% of the population does not have access to internet"},
            {"id": "P2", "text": "An SDK lets existing apps work offline instead of building a new consumer app", "status": "explicit", "evidence_span": "Ridgefire is an SDK that apps integrate onto their own code so they can work offline"},
            {"id": "P3", "text": "Bluetooth mesh networking hops messages across devices to extend range beyond a single 330-foot link", "status": "explicit", "evidence_span": "it creates mesh networks, which means that information can hop on devices found in the middle, so the range is increased"},
            {"id": "P4", "text": "Smart mesh algorithm limits flooding, message lifetime, and battery drain; stack is encrypted, patented, and Android-iOS", "status": "explicit", "evidence_span": "We are the only ones in the market with Android to iOS integration. We are encrypted, and we're patented"},
            {"id": "P5", "text": "B2B go-to-market sells to developers who already have user density", "status": "explicit", "evidence_span": "we're working on a B2B model. We cater to developers that already have this user density"},
            {"id": "P6", "text": "Pricing charges on monthly active users that use the app thanks to Bridgefy technology", "status": "explicit", "evidence_span": "We charge based on monthly active users that use your app thanks to our technology each month"},
        ],
        "domains": [
            {"id": "D1", "name": "Offline connectivity need", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Bluetooth mesh SDK", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "Developer B2B monetization", "premise_ids": ["P5", "P6"]},
        ],
        "value": [{"id": "V1", "text": "Apps keep working and connecting people without internet, including emergencies", "status": "explicit", "evidence_span": "imagine being able to use WhatsApp or Uber or Snapchat when you don't have access to internet"}],
        "secondary_value": [{"text": "Emergency and community connectivity that can save lives", "evidence_span": "improve and save people's lives and hopefully connect full communities and cities"}],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "It can be the difference between life and death"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "apps integrate onto their own code so they can work offline"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "when developers make this revenue, we also make it"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.85},
        "notes": "Vision of becoming the offline-comms standard excluded per v1.3.2 clarification 4. Fundraising and user-count traction excluded. ASR Ridgefire/BridgeFlight left in spans. Encryption/patent folded into mesh stack premise.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Current efforts to connect the offline world via big-tech internet buildout or offline apps are not scalable soon enough", "status": "explicit", "evidence_span": "we don't feel that this is scalable. We don't feel that this is going to actually get to a lot of people real soon"},
            {"id": "P2", "text": "Bridgefy SDK makes third-party apps function offline over Bluetooth mesh", "status": "explicit", "evidence_span": "The way BridgeFi works is that it connects phones directly using their Bluetooth antennas"},
            {"id": "P3", "text": "Mesh hopping plus an algorithm keeps networks from flooding and controls battery use", "status": "explicit", "evidence_span": "the network is not going to be flooded, the messages are not going to live forever, and battery consumption is not going to be a problem"},
            {"id": "P4", "text": "Cross-platform Android-iOS support with encryption and patents", "status": "explicit", "evidence_span": "Android to iOS integration"},
            {"id": "P5", "text": "Sell to developers (B2B) rather than replacing WhatsApp-scale consumer apps", "status": "explicit", "evidence_span": "we don't think that we would be ever able to create an app that hundreds of millions of people would use instead of the ones that they use every day"},
            {"id": "P6", "text": "Usage-based fees on MAUs enabled by the technology", "status": "explicit", "evidence_span": "If they don't use it with our technology, we don't charge"},
        ],
        "domains": [
            {"id": "D1", "name": "Scalable offline gap", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Mesh offline SDK", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "Developer revenue share", "premise_ids": ["P5", "P6"]},
        ],
        "value": [{"id": "V1", "text": "Offline-capable apps open and expand markets for developers and users", "status": "explicit", "evidence_span": "You open up new markets. You open and you blow up existing ones"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "P5", "to": "P6", "type": "premise-premise", "evidence_span": "that's how when developers make this revenue, we also make it"},
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "53% of the population does not have access to internet"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "so they can work offline"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "that translates into revenue"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.82},
        "notes": "Team composition excluded as bio. Red Cross/earthquake app mentions treated as traction examples.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Lack of internet on smartphones is a large problem spanning emergencies and economic growth", "status": "explicit", "evidence_span": "it can also promote social and economical growth"},
            {"id": "P2", "text": "SDK integration brings offline mode to apps people already use", "status": "explicit", "evidence_span": "an SDK that apps integrate onto their own code so they can work offline"},
            {"id": "P3", "text": "Bluetooth mesh with hopping extends effective range via intermediate devices", "status": "explicit", "evidence_span": "information can hop on devices found in the middle, so the range is increased"},
            {"id": "P4", "text": "Algorithm manages flooding, TTL, and battery; product is encrypted and patented with Android-iOS support", "status": "explicit", "evidence_span": "The mesh network is powered by our really smart algorithm"},
            {"id": "P5", "text": "B2B developer distribution plus MAU-based pricing captures value when offline tech is used", "status": "explicit", "evidence_span": "We charge based on monthly active users that use your app thanks to our technology each month"},
        ],
        "domains": [
            {"id": "D1", "name": "Offline internet gap", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Bridgefy mesh technology", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "B2B MAU pricing", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "People stay connected through familiar apps without internet access", "status": "explicit", "evidence_span": "being able to connect with rescue corps or being able to connect with their teachers"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "difference between life and death"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "work offline"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "when developers make this revenue, we also make it"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.8},
        "notes": "GTM and pricing merged into one commercial premise this run. Standard-for-offline-comms aspiration not coded.",
    },
]

# ===================== pilot-848 Siddiqui =====================
DATA["pilot-848"] = [
    {
        "premises": [
            {"id": "P1", "text": "Online merchants must verify shopper identity and keep personal information safe", "status": "explicit", "evidence_span": "They need to know that Emily is who she says she is, and once they've confirmed that she is who she says she is, they need to keep her information safe"},
            {"id": "P2", "text": "Patented software confirms two parties hold the same information without exchanging that information", "status": "explicit", "evidence_span": "patented software that allows two parties to confirm that the information that they have is the same without ever exchanging the information"},
            {"id": "P3", "text": "An identity exchange lets organizations publish verified attributes in Siddiqui format for merchants who have never identified the person before", "status": "explicit", "evidence_span": "merchants who've never identified somebody before can leverage the information that others have previously done before them"},
            {"id": "P4", "text": "Transactional fees per verification with 30% shared back to the information provider", "status": "explicit", "evidence_span": "Every verification we do, we charge a fee for. But the interesting thing is we give 30% of that back to the provider of the information"},
            {"id": "P5", "text": "Target use cases include real-time fraud monitoring of card transactions and faster identity verification", "status": "explicit", "evidence_span": "We're looking to compete in two specific areas, the prevention of fraud, which is real-time monitoring of credit card transactions, and the identity verification area"},
        ],
        "domains": [
            {"id": "D1", "name": "Merchant identity and safety need", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Zero-exchange verification tech", "premise_ids": ["P2", "P3"]},
            {"id": "D3", "name": "Transactional fees and use cases", "premise_ids": ["P4", "P5"]},
        ],
        "value": [{"id": "V1", "text": "Businesses prove identity and keep information safe without moving PII", "status": "explicit", "evidence_span": "help businesses prove that you are who you say you are and keep your information safe"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "This creates a number of problems for merchants"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "no information left my browser, no information left the server in the bank"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "make it fast and accurate"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.85},
        "notes": "Hash/graph micro-component demo folded into P2 per v1.3.2 clarification 5. BT selection treated as traction. KYC/sharing-economy examples support value/use-case framing inside P5.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Shift to online commerce creates merchant problems of identity proof and information security", "status": "explicit", "evidence_span": "She's moved from buying at bricks and mortar stores to buying online. This creates a number of problems for merchants"},
            {"id": "P2", "text": "Siddiqui matching compares hashed graph micro-components so raw attributes never leave either side", "status": "explicit", "evidence_span": "instead of exchanging the graphs, we break it down into its micro-components, and we compare the micro-components"},
            {"id": "P3", "text": "Identity exchange converts holders of verified attributes into reusable Siddiqui-format sources", "status": "explicit", "evidence_span": "get organizations that hold lots of verified identity attributes on us to convert that information into the SIDICI format"},
            {"id": "P4", "text": "Per-verification fee with 30% revenue share to attribute providers who need not reveal data", "status": "explicit", "evidence_span": "they don't have to give any information because it's all in the Siddiqui form"},
            {"id": "P5", "text": "Product focuses on reducing false-positive fraud alerts and slow offline identity checks by making verification fast and accurate", "status": "explicit", "evidence_span": "There's a lot of false positives. In the identity verification area, it's slow, it's offline"},
        ],
        "domains": [
            {"id": "D1", "name": "Online identity problems", "premise_ids": ["P1", "P5"]},
            {"id": "D2", "name": "Non-exchange matching and exchange", "premise_ids": ["P2", "P3"]},
            {"id": "D3", "name": "Verification fee model", "premise_ids": ["P4"]},
        ],
        "value": [{"id": "V1", "text": "Identity verification that is fast, accurate, and privacy-preserving for merchants", "status": "explicit", "evidence_span": "bring those two things together and make it fast and accurate"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "worried about fraud, or you're worried about keeping your information secure"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "The information is integral"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "Our model's really simple. It's transactional"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.8},
        "notes": "Evidence span for value uses speaker's 'bring those two things together' claim; wording lightly normalized in premise text only. Singleton fee domain retained as separately revisable.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Merchants need identity proof and data protection for digital shoppers", "status": "explicit", "evidence_span": "help businesses prove that you are who you say you are and keep your information safe"},
            {"id": "P2", "text": "Zero-knowledge-style confirmation that two parties share the same attribute without exchanging it", "status": "explicit", "evidence_span": "confirm that the information that they have is the same without ever exchanging the information"},
            {"id": "P3", "text": "Identity exchange network makes prior verifications reusable across merchants", "status": "explicit", "evidence_span": "access it through an identity exchange"},
            {"id": "P4", "text": "Banks, payment companies, sharing-economy platforms, and age checks all need identity assurance", "status": "explicit", "evidence_span": "Banks need it to do KYC. Payment companies need to do it to make sure that they get paid and not ripped off"},
            {"id": "P5", "text": "Transactional pricing with 30% to information providers", "status": "explicit", "evidence_span": "we give 30% of that back to the provider of the information"},
            {"id": "P6", "text": "Compete by unifying real-time fraud monitoring and identity verification into one fast accurate flow", "status": "explicit", "evidence_span": "We want to bring those two things together and make it fast and accurate"},
        ],
        "domains": [
            {"id": "D1", "name": "Broad identity demand", "premise_ids": ["P1", "P4"]},
            {"id": "D2", "name": "Siddiqui matching and exchange", "premise_ids": ["P2", "P3", "P6"]},
            {"id": "D3", "name": "Fee and provider share", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Prove who someone is and keep data safe without handing over personal information", "status": "explicit", "evidence_span": "no information left my browser, no information left the server in the bank"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "Identity is enormous. It underlies every commercial transaction"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "without ever exchanging the information"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "Every verification we do, we charge a fee for"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.82},
        "notes": "BT UK identity exchange announcement excluded as traction. Fraud/IDV unification kept as product positioning premise tied to the tech domain.",
    },
]


def check_spans(cid, body):
    t = load_t(cid)
    bad = []
    for p in body["premises"]:
        if not span_matches(p["evidence_span"], t):
            bad.append(("P", p["id"], p["evidence_span"]))
    for v in body["value"]:
        if not span_matches(v["evidence_span"], t):
            bad.append(("V", v["id"], v["evidence_span"]))
    for i, s in enumerate(body.get("secondary_value") or []):
        if not span_matches(s["evidence_span"], t):
            bad.append(("S", i, s["evidence_span"]))
    for link in body.get("causal_links") or []:
        if not span_matches(link["evidence_span"], t):
            bad.append(("L", f"{link['from']}->{link['to']}", link["evidence_span"]))
    return bad


def main():
    # also validate already-written 1136
    written = []
    errors = []

    # import 1136 from disk into validation only
    for cid, runs in DATA.items():
        assert len(runs) == 3, cid
        for i, body in enumerate(runs, 1):
            bad = check_spans(cid, body)
            if bad:
                errors.append((cid, i, bad))
                continue
            case = wrap(cid, i, body)
            verr = validate(case, transcript=load_t(cid))
            if verr:
                errors.append((cid, i, verr))
                continue
            path = RUNS / f"run{i}" / f"{cid}.json"
            path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            written.append(str(path))

    # validate 1136 files
    for i in (1, 2, 3):
        path = RUNS / f"run{i}" / "pilot-1136.json"
        case = json.loads(path.read_text(encoding="utf-8"))
        verr = validate(case, transcript=load_t("pilot-1136"))
        if verr:
            errors.append(("pilot-1136", i, verr))
        else:
            written.append(str(path) + " (validated)")

    print("WRITTEN", len(written))
    for w in written:
        print(w)
    if errors:
        print("ERRORS", len(errors))
        for e in errors:
            print(e)
        sys.exit(1)
    print("ALL_OK")


if __name__ == "__main__":
    main()
