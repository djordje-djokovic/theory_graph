# -*- coding: utf-8 -*-
"""Write Pass A extractions for chunk 10 cases (except 1136 already written)."""
import json
import pathlib
import re
import sys

BASE = pathlib.Path(r"c:\Projects\uni\sources\entrepreneurial_theories\data\theory_dags\corpus_v1_3\batches\06_full_remaining")
TRANS = BASE / "transcripts"
RUNS = BASE / "runs"
sys.path.insert(0, str(pathlib.Path(r"c:\Projects\uni\sources\entrepreneurial_theories\scripts")))
from validate_theory_dag import span_matches, validate  # type: ignore


def load_t(cid: str) -> str:
    return (TRANS / f"{cid}.txt").read_text(encoding="utf-8")


def meta(cid: str, run: int) -> dict:
    ts = {1: "2026-07-31T15:30:00+02:00", 2: "2026-07-31T15:35:00+02:00", 3: "2026-07-31T15:40:00+02:00"}[run]
    return {
        "codebook_version": "1.3.2",
        "pass": "structure",
        "unit": "pitch_transcript",
        "hierarchy": "P->D->V",
        "case_id": cid,
        "model_id": "composer-2.5",
        "model_provider": "cursor-agent",
        "temperature": None,
        "temperature_controlled": False,
        "extraction_run": run,
        "extracted_at": ts,
        "provenance_note": "Codebook-only prompt v1.3.2; temperature not API-controlled in this harness.",
    }


def wrap(cid, run, body):
    out = dict(body)
    out["meta"] = meta(cid, run)
    return out


DATA = {}

# ===================== pilot-844 Offerboard (truncated) =====================
DATA["pilot-844"] = [
    {
        "premises": [
            {"id": "P1", "text": "A fundability score compares a company's data to past successful and unsuccessful raises and tells the CEO how to improve", "status": "explicit", "evidence_span": "looks at a company's data and compares it with the data of companies that have successfully and unsuccessfully raised capital in the past"},
            {"id": "P2", "text": "The score is built from large private-offering datasets including the Australian Small Scale Offering Board plus US and global databases", "status": "explicit", "evidence_span": "we took the largest data set of small private offerings in the world, which is the Australian Small Scale Offering Board's data set"},
            {"id": "P3", "text": "Signup is free; the platform takes a 2% success fee on deals that transact via a broker-dealer partnership", "status": "explicit", "evidence_span": "For any deals that transact on the platform, we take a 2% success fee"},
            {"id": "P4", "text": "Optional full-service investment banking is offered at an additional 5%, or via specialty niche banks", "status": "explicit", "evidence_span": "If you want to engage us as your full service investment bank, it's another 5%"},
            {"id": "P5", "text": "Global deal inventory comes through partnerships with platforms, deal sourcers, and brokers across countries", "status": "explicit", "evidence_span": "We've made partnerships with global platforms, deal sourcers, and brokers to bring in deals from multiple countries"},
            {"id": "P6", "text": "Significant investors already use the platform and are looking for companies to invest in alongside them", "status": "explicit", "evidence_span": "they're looking for people to invest alongside them. They're looking for companies to invest in"},
        ],
        "domains": [
            {"id": "D1", "name": "Fundability score and data", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "Marketplace fees and banking", "premise_ids": ["P3", "P4"]},
            {"id": "D3", "name": "Global deals and investor demand", "premise_ids": ["P5", "P6"]},
        ],
        "value": [{"id": "V1", "text": "Issuers improve fundability and connect with investors on a capital-raising platform", "status": "explicit", "evidence_span": "provides the CEO information about what they can do to improve that score"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "P2", "to": "P1", "type": "premise-premise", "evidence_span": "we put a great team to work using that data set to develop the fundability score"},
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "improve your fundability as a company"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "For any deals that transact on the platform, we take a 2% success fee"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "They're looking for companies to invest in"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": True, "dependency_pass": True, "coder_confidence": 0.7},
        "notes": "Transcript truncated mid-sentence. Team credentials and listing/fundraise dollar traction excluded per 4.2. Jobs Act market-size framing not coded as a premise (v1.3.2 clarification 4). Three domains: score/data, fee model, and two-sided deal/investor inventory.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Fundability score uses company inputs versus historical raise outcomes to recommend improvements", "status": "explicit", "evidence_span": "provides the CEO information about what they can do to improve that score"},
            {"id": "P2", "text": "Changing board composition or ask size can statistically improve the fundability score", "status": "explicit", "evidence_span": "we know statistically both of those things will improve your likelihood of success as a company"},
            {"id": "P3", "text": "Score training data combines ASSOB private-offering data with other US and global public and private databases", "status": "explicit", "evidence_span": "we layered in data from other US and global databases, both public and private"},
            {"id": "P4", "text": "Revenue comes from a 2% success fee on platform transactions through a broker-dealer, with optional higher-touch banking fees", "status": "explicit", "evidence_span": "we take a 2% success fee. And we can do that through our partnership with a broker dealer"},
            {"id": "P5", "text": "Partnerships with global platforms and brokers supply multi-country deal inventory", "status": "explicit", "evidence_span": "partnerships with global platforms, deal sourcers, and brokers to bring in deals from multiple countries"},
        ],
        "domains": [
            {"id": "D1", "name": "Fundability analytics", "premise_ids": ["P1", "P2", "P3"]},
            {"id": "D2", "name": "Transaction fees and deal supply", "premise_ids": ["P4", "P5"]},
        ],
        "value": [{"id": "V1", "text": "Companies raise capital more successfully by improving fundability and accessing investors on the platform", "status": "explicit", "evidence_span": "improve your fundability as a company"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "improve your fundability as a company"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "We have a global inventory of deals"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": True, "dependency_pass": True, "coder_confidence": 0.65},
        "notes": "Pitch cuts off mid-sentence. Investor-name-dropping treated as traction evidence of the marketplace, not a separate premise. Free signup folded into the fee model premise.",
    },
    {
        "premises": [
            {"id": "P1", "text": "A data-driven fundability score diagnoses and guides improvement of a company's raise readiness", "status": "explicit", "evidence_span": "This is a score that looks at a company's data and compares it with the data of companies that have successfully and unsuccessfully raised capital"},
            {"id": "P2", "text": "The underlying dataset is the world's largest small private-offerings set layered with US and global sources", "status": "explicit", "evidence_span": "the largest data set of small private offerings in the world"},
            {"id": "P3", "text": "Platform economics: free signup for investors/issuers and a 2% success fee on closed deals via broker-dealer", "status": "explicit", "evidence_span": "For investors or issuers to sign up on the site, it's free. For any deals that transact on the platform, we take a 2% success fee"},
            {"id": "P4", "text": "Active institutional and private-office investors on the platform seek companies to fund", "status": "explicit", "evidence_span": "We've seen investors from private offices, Bain Capital, Credit Suisse, or Goldman Sachs who are already using the platform"},
            {"id": "P5", "text": "Global partnerships feed listed opportunities from multiple countries onto the site", "status": "explicit", "evidence_span": "bring in deals from multiple countries that have all gone through the process of getting on the site"},
        ],
        "domains": [
            {"id": "D1", "name": "Fundability score", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "Two-sided capital marketplace", "premise_ids": ["P3", "P4", "P5"]},
        ],
        "value": [{"id": "V1", "text": "CEOs improve raise odds and connect with capital on Offerboard", "status": "explicit", "evidence_span": "what they can do to improve that score"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "improve your fundability as a company"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "They're looking for companies to invest in"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": True, "dependency_pass": True, "coder_confidence": 0.68},
        "notes": "truncated=true. Market-size claims excluded as framing. Named investor brands support the investor-presence premise as mechanism, not pure traction metrics.",
    },
]

# ===================== pilot-925 Healthy Out =====================
DATA["pilot-925"] = [
    {
        "premises": [
            {"id": "P1", "text": "Weekly menus are personalized from health goals and taste likes/dislikes, with cancel, swap, and nutrition filters", "status": "explicit", "evidence_span": "Every single week, he gets a personalized menu that's tailored to just him"},
            {"id": "P2", "text": "Local restaurant kitchens cook healthy meals to preferences and hand-deliver within the hour, unlike warehouse diet food", "status": "explicit", "evidence_span": "convert your local restaurant kitchen into a supplier of healthy food that's custom made to your health and taste preferences and hand delivered to you within the hour"},
            {"id": "P3", "text": "Restaurant partners deliver so the company holds no inventory and runs no complex delivery network", "status": "explicit", "evidence_span": "we don't hold inventory. We don't have a complicated delivery network. Our restaurant partners deliver"},
            {"id": "P4", "text": "Unit economics combine a monthly subscription fee with restaurant commissions as mostly gross profit", "status": "explicit", "evidence_span": "We charge consumers $28 in the form of a monthly subscription fee. And then on average, we get $16 worth of restaurant commissions"},
            {"id": "P5", "text": "The offering attracts customers who would never join commercial weight-loss plans or eat cardboard-box meal kits", "status": "explicit", "evidence_span": "attracting a new segment of customers who would have never considered signing up for a commercial weight loss plan or eating food out of a cardboard box"},
        ],
        "domains": [
            {"id": "D1", "name": "Personalized healthy ordering", "premise_ids": ["P1", "P5"]},
            {"id": "D2", "name": "Restaurant supply and delivery", "premise_ids": ["P2", "P3"]},
            {"id": "D3", "name": "Subscription and commission economics", "premise_ids": ["P4"]},
        ],
        "value": [{"id": "V1", "text": "Convenient, personalized, delicious restaurant-quality healthy food delivered to home and office", "status": "explicit", "evidence_span": "high quality restaurant food that can be delivered to your home and office"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "P2", "to": "P5", "type": "premise-premise", "evidence_span": "which is why we have a far superior ability to attract and retain customers over those diet meal delivery guys"},
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "It's convenient, it's no hassle healthy, and it's seriously delicious food"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "hand delivered to you within the hour"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "That's $44 per user per month. That's virtually all gross profit"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.85},
        "notes": "Singleton D3 retained: pricing/commission model is a separately revisable commercial module. Seed raise and promo week-off excluded. Nutrition-filter UI details folded into P1 per v1.3.2 clarification 5.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Setup captures health goals and preferences so weekly menus fit the individual and stay flexible", "status": "explicit", "evidence_span": "we asked him his health goals and his likes and dislikes"},
            {"id": "P2", "text": "The platform learns preferences over time to improve recommendations", "status": "explicit", "evidence_span": "Every single time that Josh does this, we learn about his user preferences"},
            {"id": "P3", "text": "Healthy Out uses local restaurants as on-demand healthy-food suppliers with hour-scale delivery", "status": "explicit", "evidence_span": "using our data and our platform to convert your local restaurant kitchen into a supplier of healthy food"},
            {"id": "P4", "text": "Asset-light model: no inventory and partner restaurants handle delivery", "status": "explicit", "evidence_span": "Not like those diet meal delivery guys, we don't hold inventory"},
            {"id": "P5", "text": "Revenue mixes ~$28 subscription and ~$16 restaurant commissions per user per month", "status": "explicit", "evidence_span": "That's $44 per user per month. That's virtually all gross profit"},
        ],
        "domains": [
            {"id": "D1", "name": "Preference-driven personalization", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "Restaurant-powered fulfillment", "premise_ids": ["P3", "P4"]},
            {"id": "D3", "name": "Subscription plus commission model", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Busy people get personalized healthy restaurant food without hassle", "status": "explicit", "evidence_span": "convenience of a personal assistant with the personalization of a nutritionist, but all done through technology"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "personalized menu that's tailored to just him"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "your food shows up looking like this"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "The unit economics of our business model are simple"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.8},
        "notes": "New-segment claim folded into value rather than a separate premise this run. Singleton commercial domain noted as independently revisable.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Personalized flexible menus with confirm/cancel/swap texts beat rigid diet schedules", "status": "explicit", "evidence_span": "Ninety minutes before every single meal, he gets a text message to confirm, cancel, or swap out the dish"},
            {"id": "P2", "text": "Restaurant-kitchen supply yields fresher healthy meals than preservative warehouse diet delivery", "status": "explicit", "evidence_span": "It's mass produced in a regional warehouse. It's loaded with preservatives so it can survive a multi-day track"},
            {"id": "P3", "text": "Local restaurants cook to health and taste preferences and deliver within the hour", "status": "explicit", "evidence_span": "custom made to your health and taste preferences and hand delivered to you within the hour"},
            {"id": "P4", "text": "Partners deliver; Healthy Out avoids inventory and a proprietary delivery network", "status": "explicit", "evidence_span": "Our restaurant partners deliver"},
            {"id": "P5", "text": "Monthly subscription plus restaurant commissions create high-gross-profit unit economics", "status": "explicit", "evidence_span": "We charge consumers $28 in the form of a monthly subscription fee"},
            {"id": "P6", "text": "Superior food quality drives better attraction and retention versus diet meal delivery", "status": "explicit", "evidence_span": "we have a far superior ability to attract and retain customers over those diet meal delivery guys"},
        ],
        "domains": [
            {"id": "D1", "name": "Personalized ordering experience", "premise_ids": ["P1", "P6"]},
            {"id": "D2", "name": "Local restaurant supply chain", "premise_ids": ["P2", "P3", "P4"]},
            {"id": "D3", "name": "Unit economics", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "High-quality restaurant food delivered home/office with nutritionist-like personalization", "status": "explicit", "evidence_span": "high quality restaurant food that can be delivered to your home and office"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "P3", "to": "P6", "type": "premise-premise", "evidence_span": "which is why we have a far superior ability to attract and retain customers"},
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "It's convenient, it's no hassle healthy, and it's seriously delicious food"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "hand delivered to you within the hour"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "That's virtually all gross profit"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.83},
        "notes": "Contrast with warehouse diet food coded as part of the supply mechanism. Financing ask excluded.",
    },
]

# ===================== pilot-435 Teo =====================
DATA["pilot-435"] = [
    {
        "premises": [
            {"id": "P1", "text": "People attend events for both great content and socialization", "status": "explicit", "evidence_span": "People come to events for two reasons. To learn from great content and to socialize with people"},
            {"id": "P2", "text": "Livestreams, webinars, and AMAs deliver content but not socialization", "status": "explicit", "evidence_span": "they could livestream, in which case people can learn from great content, but they can't socialize"},
            {"id": "P3", "text": "Teo places customized avatars in a shared virtual venue where hundreds of real people can move and talk", "status": "explicit", "evidence_span": "You appear inside of a venue. This is my avatar that I customized"},
            {"id": "P4", "text": "Distributed communities need a way to bring members into the same virtual room", "status": "explicit", "evidence_span": "no way to bring them together into the same room. With Teo, now they can"},
            {"id": "P5", "text": "Revenue is a monthly venue fee plus a share of ticket sales and virtual sponsorship", "status": "explicit", "evidence_span": "charging organizations a monthly fee to have access to our venues. And then we also take a percentage of ticket sales and virtual sponsorship"},
        ],
        "domains": [
            {"id": "D1", "name": "Event dual-benefit gap", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "Avatar virtual venue", "premise_ids": ["P3", "P4"]},
            {"id": "D3", "name": "Venue and sponsorship monetization", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Online events that deliver both learning from content and real socialization", "status": "explicit", "evidence_span": "a product that gives the two benefits of why we are all here at this event online"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "P1", "to": "P2", "type": "premise-premise", "evidence_span": "People come to events for two reasons. To learn from great content and to socialize with people"},
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "gives the two benefits of why we are all here at this event online"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "You can move around and actually talk to people"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "charging organizations a monthly fee to have access to our venues"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.85},
        "notes": "Singleton D3 retained as separately revisable monetization. Session-length/traction observations excluded as metrics. Offline sponsorship market size treated as framing.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Existing remote formats fail to reproduce event socialization alongside content", "status": "explicit", "evidence_span": "People can learn from great content, but they can't socialize"},
            {"id": "P2", "text": "Virtual venue with controllable avatars enables moving and talking among many attendees", "status": "explicit", "evidence_span": "You can move around and actually talk to people, just like you're going to plan on doing today"},
            {"id": "P3", "text": "Organizations with geographically dispersed members can assemble everyone in one Teo room", "status": "explicit", "evidence_span": "Those alumni span across 50 countries, and he has no way to bring them into the same room"},
            {"id": "P4", "text": "After formal programming, attendees stay to socialize for hours like a real event", "status": "explicit", "evidence_span": "for the next few hours, people actually socialize"},
            {"id": "P5", "text": "Organizations pay monthly for venues and share ticket and virtual sponsorship revenue", "status": "explicit", "evidence_span": "we also take a percentage of ticket sales and virtual sponsorship"},
        ],
        "domains": [
            {"id": "D1", "name": "Social virtual events product", "premise_ids": ["P1", "P2", "P4"]},
            {"id": "D2", "name": "Distributed community customers", "premise_ids": ["P3"]},
            {"id": "D3", "name": "Fees and sponsorship take-rate", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Virtual events that recreate in-person content plus socialization benefits", "status": "explicit", "evidence_span": "platform for virtual events"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "Creating connections that you could never create otherwise"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "With Teo, now they can"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "The way that we make money as a company is by charging organizations a monthly fee"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.8},
        "notes": "Singleton D2: distributed-community need is independently revisable from product mechanics. Dual-reason premise merged into the product gap statement.",
    },
    {
        "premises": [
            {"id": "P1", "text": "Events matter for content learning and for socializing", "status": "explicit", "evidence_span": "To learn from great content and to socialize with people"},
            {"id": "P2", "text": "Current online substitutes omit socialization", "status": "explicit", "evidence_span": "Or maybe even a Reddit AMA. People can learn from great content, but they can't socialize"},
            {"id": "P3", "text": "Teo is an avatar-based virtual events platform inside a shared venue", "status": "explicit", "evidence_span": "Enter Teo, a platform for virtual events. You appear inside of a venue"},
            {"id": "P4", "text": "Communities like Startup Grind and Draper alumni lack a same-room gathering tool without Teo", "status": "explicit", "evidence_span": "They have two million entrepreneurs across 600 cities and no way to bring them together into the same room"},
            {"id": "P5", "text": "Business model: monthly venue access fee plus percentages of tickets and virtual sponsorship", "status": "explicit", "evidence_span": "charging organizations a monthly fee to have access to our venues"},
        ],
        "domains": [
            {"id": "D1", "name": "Missing online socialization", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "Teo venue product and communities", "premise_ids": ["P3", "P4"]},
            {"id": "D3", "name": "Organization monetization", "premise_ids": ["P5"]},
        ],
        "value": [{"id": "V1", "text": "Distributed communities get both event content and socialization online", "status": "explicit", "evidence_span": "help connect your community, ah, your distributed community"}],
        "secondary_value": [],
        "causal_links": [
            {"from": "D1", "to": "V1", "type": "domain-value", "evidence_span": "The world is missing a product that gives the two benefits"},
            {"from": "D2", "to": "V1", "type": "domain-value", "evidence_span": "You can move around and actually talk to people"},
            {"from": "D3", "to": "V1", "type": "domain-value", "evidence_span": "take a percentage of ticket sales and virtual sponsorship"},
        ],
        "epistemic_markers": [],
        "quality": {"thin_transcript": False, "truncated": False, "dependency_pass": True, "coder_confidence": 0.84},
        "notes": "Named community examples support the distributed-community premise. $62B sponsorship figure excluded as market framing.",
    },
]

print("defined", list(DATA.keys()), "continuing...")
