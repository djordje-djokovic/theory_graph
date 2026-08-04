# -*- coding: utf-8 -*-
"""Pass A extractions for chunk 26 — write runs/run{1,2,3}/*.json"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RUNS = BASE / "runs"

META = dict(
    codebook_version="1.3.2",
    pass_="structure",
    unit="pitch_transcript",
    hierarchy="P->D->V",
    model_id="composer-2.5",
    model_provider="cursor-agent",
    temperature=None,
    temperature_controlled=False,
)


def meta(case_id, run, ts):
    m = {k if k != "pass_" else "pass": v for k, v in META.items()}
    m["case_id"] = case_id
    m["extraction_run"] = run
    m["extracted_at"] = ts
    return m


def dump(case_id, run, obj, ts):
    obj = dict(obj)
    obj["meta"] = meta(case_id, run, ts)
    path = RUNS / f"run{run}" / f"{case_id}.json"
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# pilot-1142 — Venmo Giphy
# ---------------------------------------------------------------------------
def case_1142(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Venmo makes it easy and fun to pay and charge friends by linking a credit card and bank account to the phone",
                    "status": "explicit",
                    "evidence_span": "Venmo is a service that makes it really easy and really fun to pay and charge your friends. You get to link a credit card and a bank account to your phone",
                },
                {
                    "id": "P2",
                    "text": "Giphy is an iPhone app that lets people hide real money at real-world locations for friends to find by checking in through Foursquare",
                    "status": "explicit",
                    "evidence_span": "Giphy is an iPhone application that lets people hide real money at real-world locations for their friends to find by checking in through Foursquare",
                },
                {
                    "id": "P3",
                    "text": "Friends do not need the Giphy app to receive a gift; Foursquare friendship plus Venmo delivery is enough",
                    "status": "explicit",
                    "evidence_span": "your friends don't need to have the application to receive a gift from you. So all they need to do is be Foursquare friends with you, and Venmo is going to handle the rest",
                },
                {
                    "id": "P4",
                    "text": "Venmo social transactions complement the location check-in interactions that take place on Foursquare",
                    "status": "explicit",
                    "evidence_span": "these social transactions that seem to fit really well and actually complement the types of interactions that take place on Foursquare",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Venmo social payments", "premise_ids": ["P1", "P4"]},
                {"id": "D2", "name": "Location money gifts via check-in", "premise_ids": ["P2", "P3"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Make someone feel special by leaving real money gifts at places for friends to find",
                    "status": "explicit",
                    "evidence_span": "It really does feel nice to make someone feel special",
                }
            ],
            "secondary_value": [
                {
                    "text": "Businesses and brands can use Giphy to show loyalty, service, and hospitality to customers and their friends",
                    "evidence_span": "What a great way for businesses to show their customers, and more importantly, their customers' friends, about how they think about loyalty, service, and hospitality",
                }
            ],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "makes it really easy and really fun to pay and charge your friends",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "hide real money at real-world locations for their friends to find by checking in",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.84,
            },
            "notes": "Demo UI steps (clues, notes, multi-recipient race) folded into the Giphy offering premise per v1.3.2 §4.1(5). Future Facebook Places support folded as platform extension. Beta launch game and App Store availability treated as traction/launch, not premises. Brand-loyalty future uses recorded as secondary_value rather than premises (§4.1(4)).",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Venmo lets users pay and charge friends from a phone-linked credit card and bank account",
                    "status": "explicit",
                    "evidence_span": "You get to link a credit card and a bank account to your phone, and that's where the money comes from",
                },
                {
                    "id": "P2",
                    "text": "Giphy hides real money at real-world locations for friends to discover by checking in on location services starting with Foursquare",
                    "status": "explicit",
                    "evidence_span": "Giphy is an iPhone application that lets people hide real money at real-world locations for their friends to find by checking in through Foursquare",
                },
                {
                    "id": "P3",
                    "text": "Recipients only need to be Foursquare friends; Venmo delivers the gift without requiring the Giphy app",
                    "status": "explicit",
                    "evidence_span": "all they need to do is be Foursquare friends with you, and Venmo is going to handle the rest",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Phone-linked peer payments", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Check-in money hunt app", "premise_ids": ["P2", "P3"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Fun social gifting of real money at places friends visit",
                    "status": "explicit",
                    "evidence_span": "You get to hide real money at real-world locations for your friends to find by checking in",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "Venmo is going to handle the rest",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "hide real money at real-world locations for their friends to find",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.82,
            },
            "notes": "Complement-Foursquare framing treated as pitch context rather than a separately revisable premise. Multi-recipient competition, clues, and notes folded into P2 (§4.1(5)). Business/brand loyalty pitch coded as aspiration not premise (§4.1(4)). Singleton D1 retained: payment rails could fail independently of the check-in gift mechanic.",
        }
    # run 3
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Venmo social payments from linked cards/banks fit and complement Foursquare-style real-world check-in interactions",
                "status": "explicit",
                "evidence_span": "these social transactions that seem to fit really well and actually complement the types of interactions that take place on Foursquare",
            },
            {
                "id": "P2",
                "text": "Giphy is an iPhone app that hides real money at locations for friends to find by checking in, with clues, notes, and optional multi-recipient races",
                "status": "explicit",
                "evidence_span": "Giphy is an iPhone application that lets people hide real money at real-world locations for their friends to find by checking in through Foursquare",
            },
            {
                "id": "P3",
                "text": "Friends need not install Giphy; Foursquare friendship and Venmo complete delivery",
                "status": "explicit",
                "evidence_span": "your friends don't need to have the application to receive a gift from you",
            },
            {
                "id": "P4",
                "text": "Businesses and major brands can leave complimentary offers at check-ins to demonstrate loyalty and hospitality",
                "status": "inferred",
                "evidence_span": "imagine how businesses and major brands can benefit from Giphy",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Social payment plus check-in gift product", "premise_ids": ["P1", "P2", "P3"]},
            {"id": "D2", "name": "Business and brand check-in offers", "premise_ids": ["P4"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Make friends feel special with meaningful real-money gifts tied to places",
                "status": "explicit",
                "evidence_span": "they get a meaningful message from you with real money out of the blue",
            }
        ],
        "secondary_value": [
            {
                "text": "Loyalty, service, and hospitality signaling for businesses",
                "evidence_span": "loyalty, service, and hospitality",
            }
        ],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "make someone feel special",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "thanking you for being a loyal customer",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": False,
            "dependency_pass": True,
            "coder_confidence": 0.78,
        },
        "notes": "Borderline call: business/brand use coded as a go-to-market condition (P4) because the speaker presents it as how brands benefit, not pure vision framing. If treated as aspiration only, P4 would drop. Singleton D2 retained as separately revisable B2B module. Demo feature list folded into P2.",
    }


# ---------------------------------------------------------------------------
# pilot-671 — Phoenix P2P streaming
# ---------------------------------------------------------------------------
def case_671(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "CDN/HLS large-audience streaming introduces substantial latency (on the order of a minute or two)",
                    "status": "explicit",
                    "evidence_span": "a content delivery network based solution that results in an awful lot of latency being introduced the minute or 2 minutes that we were talking about earlier",
                },
                {
                    "id": "P2",
                    "text": "Existing real-time streams (under half a second) do not scale to enough concurrent viewers",
                    "status": "explicit",
                    "evidence_span": "The challenge with these real time applications is that they don't scale to reach enough concurrent viewers",
                },
                {
                    "id": "P3",
                    "text": "Phoenix is a scalable real-time video platform streaming to millions of concurrent viewers under half a second of latency via proprietary algorithms including an interactive transport protocol",
                    "status": "explicit",
                    "evidence_span": "we can stream to millions of concurrent viewers with under half a second of latency",
                },
                {
                    "id": "P4",
                    "text": "The product is licensed through APIs and SDKs to Android, iOS, web, and desktop, with quick customer integration",
                    "status": "explicit",
                    "evidence_span": "we license our product to our customers through our API's and SDK's that reach devices like Android iOS as well as web and desktop browsers",
                },
                {
                    "id": "P5",
                    "text": "Optional proximity multicast peer-to-peer algorithms further reduce cost, enable massive scale, and address bandwidth constraints",
                    "status": "explicit",
                    "evidence_span": "we give our customers the option to add in our proximity multicast, which is a series of peer-to-peer algorithms that help to further reduce cost deliver on an even massive scale and address the bandwidth constraints",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Latency versus scale streaming gap", "premise_ids": ["P1", "P2"]},
                {"id": "D2", "name": "Scalable real-time Phoenix platform", "premise_ids": ["P3", "P5"]},
                {"id": "D3", "name": "API and SDK licensing", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Reach very large audiences with low latency that enables interactivity and engagement",
                    "status": "explicit",
                    "evidence_span": "reach really large audiences and do so in a very innovative way with very low latency to drive interactive interaction and engagement with your users",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "latency that results from your video stream",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "stream to millions of concurrent viewers with under half a second of latency",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "license our product to our customers through our API's and SDK's",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.86,
            },
            "notes": "Founder bio and named customers/pilots excluded as credentials/traction. One-to-many, group chat, news, education, e-sports, AR/VR, OTT listed as uses of the same scalable real-time mechanism and folded per §4.1(2). Partition is need/product/channel triad; justified because API licensing is revisable without changing the transport stack, and the CDN latency vs real-time scale gap is a separate market assumption. Singleton D3 retained.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Large-audience CDN streaming adds about a minute or two of latency while true real-time streams fail to scale",
                    "status": "explicit",
                    "evidence_span": "they don't scale to reach enough concurrent viewers",
                },
                {
                    "id": "P2",
                    "text": "Phoenix streams the same video to huge audiences under half a second using a ground-up platform and proprietary algorithms including interactive transport",
                    "status": "explicit",
                    "evidence_span": "we've built it from the ground up to eliminate many of these, deliver the same video using several of our proprietary algorithms, including our interactive transport protocol",
                },
                {
                    "id": "P3",
                    "text": "Proximity multicast peer-to-peer option further cuts cost and scales under bandwidth constraints",
                    "status": "explicit",
                    "evidence_span": "proximity multicast, which is a series of peer-to-peer algorithms that help to further reduce cost deliver on an even massive scale",
                },
                {
                    "id": "P4",
                    "text": "Customers integrate via APIs/SDKs across mobile, web, and desktop browsers",
                    "status": "explicit",
                    "evidence_span": "through our API's and SDK's that reach devices like Android iOS as well as web and desktop browsers",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Real-time at scale problem", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Phoenix transport and multicast platform", "premise_ids": ["P2", "P3"]},
                {"id": "D3", "name": "API and SDK distribution", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Low-latency video at large concurrent scale for interactive engagement",
                    "status": "explicit",
                    "evidence_span": "very low latency to drive interactive interaction and engagement with your users",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "That is until now",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "under half a second of latency",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "customers have been able to integrate our solution with as little as 30 minutes of work",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.85,
            },
            "notes": "CDN latency and real-time scale limits merged into one market-gap premise. Bio and customer logos excluded. Use-case laundry list folded into platform capability (§4.1(2)). Need/product/channel triad justified: licensing channel separately revisable from transport algorithms.",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "CDN-based streaming creates high latency for large audiences",
                "status": "explicit",
                "evidence_span": "content delivery network based solution that results in an awful lot of latency",
            },
            {
                "id": "P2",
                "text": "Real-time under-half-second streaming historically cannot reach enough concurrent viewers",
                "status": "explicit",
                "evidence_span": "they don't scale to reach enough concurrent viewers",
            },
            {
                "id": "P3",
                "text": "Phoenix delivers scalable real-time streaming to millions under half a second via proprietary algorithms and optional proximity multicast",
                "status": "explicit",
                "evidence_span": "Phoenix is here is the world's only scalable real time video streaming platform we can stream to millions of concurrent viewers with under half a second of latency",
            },
            {
                "id": "P4",
                "text": "Licensed through APIs and SDKs for Android, iOS, web, and desktop with fast integration",
                "status": "explicit",
                "evidence_span": "we license our product to our customers through our API's and SDK's",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Streaming latency and scale problem", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "Phoenix platform and API licensing", "premise_ids": ["P3", "P4"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Reach large audiences innovatively with very low latency for interaction and engagement",
                "status": "explicit",
                "evidence_span": "reach really large audiences and do so in a very innovative way with very low latency",
            }
        ],
        "secondary_value": [],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "What you're experiencing is latency that results from your video stream",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "scalable real time video streaming platform",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": False,
            "dependency_pass": True,
            "coder_confidence": 0.83,
        },
        "notes": "Multicast folded into core platform premise (§4.1(5)). API licensing grouped with product as one learnable go-to-market+tech module rather than a singleton commercial domain. Traction and team credentials excluded.",
    }


# ---------------------------------------------------------------------------
# pilot-679 — Bark
# ---------------------------------------------------------------------------
def case_679(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Children socialize heavily on connected devices, and new technology creates new online risks such as harmful messages",
                    "status": "explicit",
                    "evidence_span": "new technology creates new risks",
                },
                {
                    "id": "P2",
                    "text": "Parents' only options today are manually scanning phones or spot-checking with saved passwords, which undermines independence and is daily friction",
                    "status": "explicit",
                    "evidence_span": "my only options are to pick up his phone, scan through his messages, or to save his passwords and randomly spot check his activity online",
                },
                {
                    "id": "P3",
                    "text": "Bark uses machine learning on social and message content to detect issues like cyberbullying, sexting, and depression/suicide signs, alerting parents with recommended actions without unfettered message access",
                    "status": "explicit",
                    "evidence_span": "we've developed machine learning-based algorithms to detect issues like cyberbullying, sexting, signs of depression or suicide",
                },
                {
                    "id": "P4",
                    "text": "Bark costs $9 per month per family for unlimited children and accounts, with an affiliate model for schools and nonprofits",
                    "status": "explicit",
                    "evidence_span": "BARC is just $9 per month per family, unlimited children, unlimited connected accounts",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Online child safety monitoring gap", "premise_ids": ["P1", "P2"]},
                {"id": "D2", "name": "ML issue detection and parent alerts", "premise_ids": ["P3"]},
                {"id": "D3", "name": "Family subscription and school affiliates", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Keep children safe online while preserving privacy and building family trust",
                    "status": "explicit",
                    "evidence_span": "keep children safe online while allowing them privacy and helping their families build trust in that process",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "parents need a smarter solution to help keep their children safe online",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "If we detect an issue, we send an alert to the parent along with recommended actions",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "working directly with schools and nonprofits to provide them affiliate revenue",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.88,
            },
            "notes": "Message volume and school-commit counts excluded as traction. UI setup steps and psychologist advisors folded into the detection/alert offering (§4.1(5)). Price and school/nonprofit affiliate channel kept as one commercial premise (§4.1(3)). Need/product/money triad justified: subscription/affiliate economics revisable without changing ML detection, and the manual-monitoring parent problem is a separate assumption. Singleton D2 and D3 retained.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Manual parental phone scanning and password spot-checks create daily friction and conflict with kids' independence",
                    "status": "explicit",
                    "evidence_span": "This manual process is a daily friction point",
                },
                {
                    "id": "P2",
                    "text": "ML algorithms detect cyberbullying, sexting, and depression/suicide signs from social content and user messages, then alert parents with recommended actions while withholding full message access",
                    "status": "explicit",
                    "evidence_span": "BART does not provide a parent unfettered access to a child's messages, only potential problems",
                },
                {
                    "id": "P3",
                    "text": "Parents can configure issue notifications by child age/context across many connected social accounts",
                    "status": "explicit",
                    "evidence_span": "We give the parents the ability to configure the type of notifications they want to receive",
                },
                {
                    "id": "P4",
                    "text": "$9 per family per month unlimited, plus school and nonprofit affiliate revenue partnerships",
                    "status": "explicit",
                    "evidence_span": "We have a unique approach working directly with schools and nonprofits to provide them affiliate revenue",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Manual monitoring friction", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Detection alerts and parental controls", "premise_ids": ["P2", "P3"]},
                {"id": "D3", "name": "Pricing and school affiliates", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Smarter online child safety with privacy and family trust",
                    "status": "explicit",
                    "evidence_span": "Our goal is to provide trust and communication around online safety",
                }
            ],
            "secondary_value": [
                {
                    "text": "Mission to keep children safe online",
                    "evidence_span": "Our mission is to keep children safe online",
                }
            ],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "both of those options suck",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "machine learning-based algorithms to detect issues",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "keeping their student population safe online",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.84,
            },
            "notes": "Age-configurable notifications split as a product-control premise that could fail while detection still worked. Traction metrics excluded. Price+affiliate kept one commercial premise (§4.1(3)).",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Parents need a smarter alternative to manual phone scanning because they want kids to socialize independently without hours of scrolling",
                "status": "explicit",
                "evidence_span": "I want my son to feel like he can socialize independently of me",
            },
            {
                "id": "P2",
                "text": "Bark continuously monitors connected social accounts with ML to flag issues and text parents only potential problems plus recommended actions",
                "status": "explicit",
                "evidence_span": "Bark is continuously monitoring the connected accounts in the background",
            },
            {
                "id": "P3",
                "text": "Sold at $9/month per family unlimited, distributed via school and nonprofit affiliates that earn fundraising revenue",
                "status": "explicit",
                "evidence_span": "BARC is just $9 per month per family, unlimited children, unlimited connected accounts",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Parent monitoring need", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Background ML monitoring product", "premise_ids": ["P2"]},
            {"id": "D3", "name": "Family pricing and affiliates", "premise_ids": ["P3"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Keep children safe online with privacy and family trust",
                "status": "explicit",
                "evidence_span": "keep children safe online while allowing them privacy and helping their families build trust",
            }
        ],
        "secondary_value": [],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "parents need a smarter solution to help keep their children safe online",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "If there is an issue detected, you'll receive a text message",
            },
            {
                "from": "D3",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "offering their families value, and keeping their student population safe online",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": False,
            "dependency_pass": True,
            "coder_confidence": 0.86,
        },
        "notes": "Tighter atomicity: detection features, privacy constraint, and psychologist recommendations folded into one product premise. Need/product/money triad justified by separate revisability of affiliate pricing vs monitoring tech vs parent-friction assumption.",
    }


# Remaining cases imported from companion module when present; stub main for part A.
CASES_A = {
    "pilot-1142": case_1142,
    "pilot-671": case_671,
    "pilot-679": case_679,
}


if __name__ == "__main__":
    ts = {
        1: "2026-07-31T15:40:00+02:00",
        2: "2026-07-31T15:48:00+02:00",
        3: "2026-07-31T15:56:00+02:00",
    }
    written = []
    for cid, fn in CASES_A.items():
        for run in (1, 2, 3):
            written.append(str(dump(cid, run, fn(run), ts[run])))
    print(f"wrote {len(written)} files (part A)")
