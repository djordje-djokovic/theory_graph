# -*- coding: utf-8 -*-
"""Pass A extractions chunk 26 part C — Alicanto, Pundit, Fortuit + write all B+C."""
import json
from pathlib import Path

# Reuse dump helpers from part B by inlining
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


def case_1002(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Alicanto recommends marketing ideas via data mining and machine learning tailored to the business, location, and preferences",
                    "status": "explicit",
                    "evidence_span": "My feeds are based on data mining and machine learning algorithms and are tailored to my business, location, and preferences",
                },
                {
                    "id": "P2",
                    "text": "Users can launch multi-channel campaigns from style-matched templates across email, postcards, text, and social",
                    "status": "explicit",
                    "evidence_span": "I can run it across multiple marketing channels, emails, postcards, text, and social media, to name a few",
                },
                {
                    "id": "P3",
                    "text": "Alliances let businesses run joint campaigns to reach each other's customers",
                    "status": "explicit",
                    "evidence_span": "Alliances allow businesses to run marketing campaigns together, reaching a huge number of new customers",
                },
                {
                    "id": "P4",
                    "text": "Freemium revenue with contextual sponsored suggestions; distribution is viral via the Alliance invite feature",
                    "status": "explicit",
                    "evidence_span": "Our revenue model is freemium, with contextual sponsored suggestions built in",
                },
            ],
            "domains": [
                {"id": "D1", "name": "ML marketing recommendations and campaigns", "premise_ids": ["P1", "P2"]},
                {"id": "D2", "name": "Business alliance campaigns", "premise_ids": ["P3"]},
                {"id": "D3", "name": "Freemium and viral distribution", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Drive key marketing KPIs—average purchase, new and returning clients, and total revenues—with a sophisticated marketing mix",
                    "status": "explicit",
                    "evidence_span": "This drives all key performance indicators rapidly off, average purchase, number of new clients, number of returning customers, and total revenues",
                }
            ],
            "secondary_value": [
                {
                    "text": "Handle all of a small business's marketing needs so owners can focus on the craft",
                    "evidence_span": "It handles all of your marketing needs",
                }
            ],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "they run very sophisticated marketing mix and many, many tasks",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "helping each other reach more customers, driving more traffic to our businesses",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "Our distribution model is highly viral, thanks to our Alliance feature",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.86,
            },
            "notes": "Calendar, ROI analytics, SEO/Google Places, and print signs folded into the recommendation/campaign offering (§4.1(5)). Alliance kept separate as an independently revisable growth module. Freemium+sponsored suggestions one commercial premise. Product/alliance/monetization partition; not a need triad.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "ML-powered virtual marketing manager suggests location- and industry-relevant campaigns and executes them across channels",
                    "status": "explicit",
                    "evidence_span": "This is how my virtual marketing manager gives me marketing ideas",
                },
                {
                    "id": "P2",
                    "text": "Alliance campaigns let merchants jointly message shared and new audiences",
                    "status": "explicit",
                    "evidence_span": "With just a few clicks, I can either create a new alliance campaign or join an existing one",
                },
                {
                    "id": "P3",
                    "text": "Also automates tasks like Google Places visibility and holiday customer messaging",
                    "status": "explicit",
                    "evidence_span": "Alicanto realized I'm not on Google Places. It will actually do it for me, increasing my visibility on the web",
                },
                {
                    "id": "P4",
                    "text": "Freemium with sponsored suggestions; viral invites through Alliances",
                    "status": "explicit",
                    "evidence_span": "Alliance feature that enables businesses to invite other businesses to our system",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Automated multi-channel marketing suite", "premise_ids": ["P1", "P3"]},
                {"id": "D2", "name": "Alliance co-marketing", "premise_ids": ["P2"]},
                {"id": "D3", "name": "Freemium viral model", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Rapidly improve retail marketing KPIs versus basic prior marketing",
                    "status": "explicit",
                    "evidence_span": "Before Alicanto, Ruti and our other beta customers ran very basic marketing",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "Now with Alicanto, they run very sophisticated marketing mix",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "reaching a huge number of new customers",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "revenue model is freemium",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.82,
            },
            "notes": "Borderline: SEO/Places kept as part of suite rather than vision. Templates folded into P1.",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Tailored ML feeds plus multi-channel templates and marketing calendar/analytics form an all-in-one SMB marketing system",
                "status": "explicit",
                "evidence_span": "Alicanto makes it easy. It handles all of your marketing needs",
            },
            {
                "id": "P2",
                "text": "Businesses co-market through Alliances to expand reach",
                "status": "explicit",
                "evidence_span": "Alliances allow businesses to run marketing campaigns together",
            },
            {
                "id": "P3",
                "text": "Freemium monetization with contextual sponsored suggestions and viral Alliance invites",
                "status": "explicit",
                "evidence_span": "Our revenue model is freemium, with contextual sponsored suggestions built in",
            },
        ],
        "domains": [
            {"id": "D1", "name": "All-in-one marketing automation", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Alliance growth loop", "premise_ids": ["P2"]},
            {"id": "D3", "name": "Freemium sponsored model", "premise_ids": ["P3"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Drive traffic, customers, and revenues for local businesses",
                "status": "explicit",
                "evidence_span": "driving more traffic to our businesses",
            }
        ],
        "secondary_value": [],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "drives all key performance indicators",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "reach over 8,000 potential customers",
            },
            {
                "from": "D3",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "distribution model is highly viral",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": False,
            "dependency_pass": True,
            "coder_confidence": 0.85,
        },
        "notes": "Calendar/SEO/print folded into all-in-one premise. Alliance singleton retained as separately revisable viral module.",
    }


def case_711(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Talk media (podcasts, radio) remain long, non-interactive, and poorly suited to mobile-first ADD audiences while photos and video have been reinvented",
                    "status": "explicit",
                    "evidence_span": "All these talk media have the same problem. They're long. They're not interactive. They don't really cater to the ADD generation, the mobile-first content creators",
                },
                {
                    "id": "P2",
                    "text": "Pundit is a social network for bite-sized talk shows where users create short audio posts, converse in max-30-second replies, with auto noise reduction, voice filters, and music",
                    "status": "explicit",
                    "evidence_span": "It's a social network for voice experiences, where users can start bite-sized talk shows about their favorite topics and invite their friends or followers to participate",
                },
                {
                    "id": "P3",
                    "text": "Creators can share and embed talks across social platforms and the web; fans can join from the web without the app; brands and media partners can distribute audio content",
                    "status": "explicit",
                    "evidence_span": "creators can share their Pundit talks on other social platforms and natively embed them on any website",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Stale talk-media format", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Bite-sized social voice product", "premise_ids": ["P2"]},
                {"id": "D3", "name": "Creator and brand distribution", "premise_ids": ["P3"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Make talk lightweight, interactive, and fun like Snapchat did for photos",
                    "status": "explicit",
                    "evidence_span": "making talk more lightweight, interactive, and fun",
                }
            ],
            "secondary_value": [
                {
                    "text": "Empower users to unleash their inner Oprah via voice experiences",
                    "evidence_span": "empowers you to unleash your inner Oprah",
                }
            ],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "music, photos, and videos have all been reinvented for the mobile and social age. But what about talk",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "every piece of content on Pundit is short and sweet",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "new world of possibilities for brands and top-notch creators to create and distribute awesome audio content",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.84,
            },
            "notes": "Voice box disappearing DMs folded into the core social voice offering (§4.1(5)). 'Newest wave of social media' vision excluded (§4.1(4)). Engagement metrics and Disney pilot treated as traction. Need/product/distribution triad justified: creator/brand distribution revisable without changing the 30-second talk format.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Voice talk has not been reinvented for mobile social the way photos and video have",
                    "status": "explicit",
                    "evidence_span": "music, photos, and videos have all been reinvented for the mobile and social age. But what about talk, the voice, the podcast, the radio? You know, it's still behind",
                },
                {
                    "id": "P2",
                    "text": "Pundit talks are short conversational audio with engineering polish plus private disappearing voice messages",
                    "status": "explicit",
                    "evidence_span": "Pundit will automatically reduce the background noise and engineer your voice to make you sound your best",
                },
                {
                    "id": "P3",
                    "text": "Growth via creator embedding/sharing and brand partnerships; web listening without installing the app",
                    "status": "explicit",
                    "evidence_span": "Those fans could join the Pundit talks from anywhere on the web, whether or not they had the app",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Voice media lag", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Short social voice experiences", "premise_ids": ["P2"]},
                {"id": "D3", "name": "Creator and brand go-to-market", "premise_ids": ["P3"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Turn the voice into fun, interactive social media",
                    "status": "explicit",
                    "evidence_span": "turn the voice into the newest wave of social media",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "They're long. They're not interactive",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "make voice fun again",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "it's all about the creators",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.8,
            },
            "notes": "Primary value takes the 'newest wave' line as the valued outcome rather than a premise (§4.1(4)). Voice box kept inside P2 as part of one offering.",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Long non-interactive talk formats fail mobile-first creators who prefer short social play",
                "status": "explicit",
                "evidence_span": "I, for one, don't really enjoy listening to podcasts as much as playing on Snapchat",
            },
            {
                "id": "P2",
                "text": "Bite-sized Pundit talks with 30-second replies, filters, and music make public and private voice exchanges fun",
                "status": "explicit",
                "evidence_span": "you can create short, insanely fun audio content",
            },
            {
                "id": "P3",
                "text": "Onboarding YouTubers and brand partners plus cross-posting/embeds drives engagement",
                "status": "explicit",
                "evidence_span": "we have onboarded thousands of YouTubers and similar creators to the platform",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Podcast boredom problem", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Fun short-form voice network", "premise_ids": ["P2", "P3"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Lightweight interactive fun talk in your pocket",
                "status": "explicit",
                "evidence_span": "making talk more lightweight, interactive, and fun",
            }
        ],
        "secondary_value": [],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "apparently, I'm not alone",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "as if we're in a talk show together, but in your pocket",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": False,
            "dependency_pass": True,
            "coder_confidence": 0.79,
        },
        "notes": "Creator traction sentence used as distribution mechanism evidence; absolute user counts still excluded as pure traction. Product and creator GTM merged into one learnable module.",
    }


def case_1059(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "CRM yields garbage-in/garbage-out because sales reps skip data entry or let it go stale, leaving management without real pipeline transparency",
                    "status": "explicit",
                    "evidence_span": "it's garbage in, neatly packaged garbage out",
                },
                {
                    "id": "P2",
                    "text": "Fortuit's plugin automatically captures emails, IMs, contacts, and activities and combines them with the pipeline into a predictive model of how the rep sells",
                    "status": "explicit",
                    "evidence_span": "it was taking all of the unstructured data, all of my emails, activities, IMs, contacts, putting that information, combining it with my sales pipeline to build a predictive model about the way I sell",
                },
                {
                    "id": "P3",
                    "text": "The engine flags at-risk deals with reasons (e.g., legal not engaged) and a communication timeline so reps can triage and repair the pipe",
                    "status": "explicit",
                    "evidence_span": "What it's telling me is why this deal might not close",
                },
                {
                    "id": "P4",
                    "text": "Free Fortuit beta for sales reps installs without IT involvement in minutes",
                    "status": "explicit",
                    "evidence_span": "I downloaded the Fortuit plug-in, let it run, and within five minutes, I was up and running. No IT involvement",
                },
            ],
            "domains": [
                {"id": "D1", "name": "CRM compliance and transparency failure", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Predictive pipeline triage engine", "premise_ids": ["P2", "P3"]},
                {"id": "D3", "name": "IT-free free plugin distribution", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Answer whether the rep or team will make the quarter and show managers the rep is in control",
                    "status": "explicit",
                    "evidence_span": "will I make my quarter?",
                }
            ],
            "secondary_value": [
                {
                    "text": "Give management transparency and control over front-office sales operations",
                    "evidence_span": "the lack of transparency into front office operations, particularly sales",
                }
            ],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "If you don't know what's going on, you can't manage it",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "go all the way from, you know, I've got a problem with my pipeline, I'm not going to meet my quarter, to know exactly why",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "Available free on fortuit.com",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": True,
                "dependency_pass": True,
                "coder_confidence": 0.85,
            },
            "notes": "Transcript opens mid-argument (truncated). 89% predictive accuracy treated as traction evidence of the engine, not a separate premise. Repair-tool laundry list folded into triage premise (§4.1(5)). Need/product/distribution triad justified: free no-IT install revisable without changing the predictive engine.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Sales reps will not keep CRM current, so managers cannot reliably run the pipe",
                    "status": "explicit",
                    "evidence_span": "Sales reps don't comply with the corporate policy to put the data in the application",
                },
                {
                    "id": "P2",
                    "text": "Fortuit auto-ingests unstructured communication with pipeline data to predict deal success or failure",
                    "status": "explicit",
                    "evidence_span": "tells me whether I'm gonna succeed or whether I'm gonna fail on certain deals",
                },
                {
                    "id": "P3",
                    "text": "Visual pipeline and timeline explain why deals are at risk so the rep can self-triage before management review",
                    "status": "explicit",
                    "evidence_span": "The sales rep was able to triage his own pipe, come up with his own solution, and in a very clear manner, visual, show the manager he's in control",
                },
            ],
            "domains": [
                {"id": "D1", "name": "CRM data chore problem", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Fortuit predictive sales app", "premise_ids": ["P2", "P3"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Know if you will make the quarter and why deals will or will not close",
                    "status": "explicit",
                    "evidence_span": "will I make my quarter? Doesn't matter if you're a rep or management, you want to know the answer to that question",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "garbage in, neatly packaged garbage out",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "our engine is incredibly predictive",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": True,
                "dependency_pass": True,
                "coder_confidence": 0.83,
            },
            "notes": "Free/no-IT install folded into product adoption detail within D2 rather than singleton commercial domain. Truncation flagged.",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Front-office sales lack transparency because CRM data is incomplete and stale",
                "status": "explicit",
                "evidence_span": "if they do put the data in, they don't keep the information current",
            },
            {
                "id": "P2",
                "text": "Fortuit passively builds a predictive selling model from email/IM/contact activity plus pipeline and surfaces at-risk deals with root-cause timelines",
                "status": "explicit",
                "evidence_span": "Fortuita's telling me is at risk",
            },
            {
                "id": "P3",
                "text": "Free plug-in for reps with no IT involvement answers the shared 'will I make my quarter?' question for reps and managers",
                "status": "explicit",
                "evidence_span": "Available free on fortuit.com",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Opaque sales pipeline", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Passive predictive Fortuit", "premise_ids": ["P2"]},
            {"id": "D3", "name": "Free rep-first distribution", "premise_ids": ["P3"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Reps and managers know quarter outcome and can control the pipe",
                "status": "explicit",
                "evidence_span": "show the manager he's in control",
            }
        ],
        "secondary_value": [
            {
                "text": "Empower front office engagement while restoring management control",
                "evidence_span": "empower the front office to engage with customers as well as give management some semblance of control",
            }
        ],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "If you don't know what's going on, you can't manage it",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "know exactly why",
            },
            {
                "from": "D3",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "within five minutes, I was up and running",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": True,
            "dependency_pass": True,
            "coder_confidence": 0.84,
        },
        "notes": "ASR 'Fortuita's' left as verbatim evidence. Need/product/distribution triad justified. Truncation at start flagged.",
    }


# Import part B cases
import importlib.util

_B = Path(__file__).with_name("_extract_chunk26b.py")
spec = importlib.util.spec_from_file_location("chunk26b", _B)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CASES = {
    "pilot-1053": mod.case_1053,
    "pilot-565": mod.case_565,
    "pilot-441": mod.case_441,
    "pilot-692": mod.case_692,
    "pilot-1002": case_1002,
    "pilot-711": case_711,
    "pilot-1059": case_1059,
}


if __name__ == "__main__":
    ts = {
        1: "2026-07-31T15:40:00+02:00",
        2: "2026-07-31T15:48:00+02:00",
        3: "2026-07-31T15:56:00+02:00",
    }
    written = []
    for cid, fn in CASES.items():
        for run in (1, 2, 3):
            written.append(str(dump(cid, run, fn(run), ts[run])))
    print(f"wrote {len(written)} files (part B+C)")
