# -*- coding: utf-8 -*-
"""Pass A extractions chunk 26 part B — remaining 7 cases."""
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


def case_1053(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Businesses run on messy reply-all email threads that waste time; the answer is not to abandon email but to make it more productive, collaborative, and social",
                    "status": "explicit",
                    "evidence_span": "Businesses almost all run on these kind of reply all threads. And it's totally stupid. But we don't think the answer is to throw email away",
                },
                {
                    "id": "P2",
                    "text": "A loop is a smart mailing list with a name and email address, used through ordinary email and backed by a SaaS app that adds search, sharing, and history",
                    "status": "explicit",
                    "evidence_span": "The loop is a smart mailing list easy to search, easy to share, easy to create",
                },
                {
                    "id": "P3",
                    "text": "Loops are created via email with no IT ticket, download, or new learning curve because interaction is just email",
                    "status": "explicit",
                    "evidence_span": "There was no IT help desk request. No one had to download anything. No one had to learn anything, because it's just email",
                },
                {
                    "id": "P4",
                    "text": "Freemium monetization: customers pay for customization, administration, and integrations, aided by intrinsic email-list virality",
                    "status": "explicit",
                    "evidence_span": "customers have told us they'll pay for customization",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Broken workplace email threads", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Email-native Loop product", "premise_ids": ["P2", "P3"]},
                {"id": "D3", "name": "Freemium and viral email lists", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Make workplace email more productive, collaborative, and social so people waste less time in it",
                    "status": "explicit",
                    "evidence_span": "make email more productive, so you waste less time in it, more collaborative, and more social",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "the email problem is so big",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "We don't ask for behavior changes, because it's just email",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "email lists are just intrinsically viral",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": True,
                "dependency_pass": True,
                "coder_confidence": 0.82,
            },
            "notes": "Transcript truncates mid-sentence at beta invite. Web search, digests, open loops, and footer sharing folded into the Loop product module (§4.1(5)). Price customization and integrations kept with freemium/virality as one commercial premise (§4.1(3)). Need/product/money triad justified: freemium packaging revisable without changing email-native creation, and reply-all waste is a separate market claim. Singleton D1 and D3 retained.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Reply-all email threads are how business runs but are a poor collaboration substrate",
                    "status": "explicit",
                    "evidence_span": "Businesses almost all run on these kind of reply all threads",
                },
                {
                    "id": "P2",
                    "text": "Loops are named email-addressed lists created and used through email, with a SaaS web layer for search, attachments, suggestions, and following",
                    "status": "explicit",
                    "evidence_span": "The way you interact with the loop is through email",
                },
                {
                    "id": "P3",
                    "text": "Adoption works because no behavior change, download, or initial account is required—users stay in email",
                    "status": "explicit",
                    "evidence_span": "We don't ask for anybody to download, install anything. They don't even have to create accounts at first, because it's just email",
                },
                {
                    "id": "P4",
                    "text": "Email-list virality supports a freemium model where paid tiers cover branding, admin, and integrations",
                    "status": "explicit",
                    "evidence_span": "the thing about virality is it makes the freemium model really easy, or easier",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Email collaboration problem", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Loop as email plus SaaS", "premise_ids": ["P2", "P3"]},
                {"id": "D3", "name": "Viral freemium monetization", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Meet users in email and make workplace email cool and usable again",
                    "status": "explicit",
                    "evidence_span": "we can meet the users where they are and where they want to work, which is out of their email",
                }
            ],
            "secondary_value": [
                {
                    "text": "Waste less time; more collaborative and social email",
                    "evidence_span": "make email more productive, so you waste less time in it, more collaborative, and more social",
                }
            ],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "It's totally stupid",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "nothing is simpler than email",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "freemium model, viral, great application",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": True,
                "dependency_pass": True,
                "coder_confidence": 0.8,
            },
            "notes": "Truncated transcript. Demo features folded into P2. 'Make email cool again' treated as value framing aligned with primary value rather than a separate vision premise (§4.1(4)).",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Email is the workplace default and should be enhanced rather than replaced",
                "status": "explicit",
                "evidence_span": "we don't think the answer is to throw email away. We don't think that works",
            },
            {
                "id": "P2",
                "text": "The Loop is an email-native smart list plus SaaS that is easy to create, search, share, and follow without changing user behavior",
                "status": "explicit",
                "evidence_span": "We don't ask for behavior changes, because it's just email",
            },
            {
                "id": "P3",
                "text": "Intrinsic email-list virality plus freemium paid customization, admin, and integrations",
                "status": "explicit",
                "evidence_span": "email lists are just intrinsically viral, which is part of what got us interested in the idea in the first place",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Enhance email not replace it", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "Viral freemium model", "premise_ids": ["P3"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "More productive, collaborative, social workplace email with high adoption",
                "status": "explicit",
                "evidence_span": "make email more productive, so you waste less time in it, more collaborative, and more social",
            }
        ],
        "secondary_value": [],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "leveraging email",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "user adoption and the virality",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": True,
            "dependency_pass": True,
            "coder_confidence": 0.81,
        },
        "notes": "Merged market and product into one email-native theory domain; commercial freemium kept separate. Truncation flagged.",
    }


def case_565(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Proprietary Neotic algorithms analyze U.S. stock market data daily, cluster stocks, and classify winners versus losers with an adaptive everyday-learning model",
                    "status": "explicit",
                    "evidence_span": "The proprietary Neotech algorithms analyze daily all U.S. stocks' financial markets data, extract features and labels, group stocks into clusters, and classify them as winners or losers accordingly",
                },
                {
                    "id": "P2",
                    "text": "Neotic automates live orders through Collective2 connected to multiple brokers without requiring traders to write code",
                    "status": "explicit",
                    "evidence_span": "Neotic runs on Collective 2, which is a marketplace for trading strategies and is connected to five other brokers",
                },
                {
                    "id": "P3",
                    "text": "Customers are acquired via specialized forums, email, AdWords, articles, and broker referrals; free trial then ~$400 per user per year by backtests, forecasts, and automated traders",
                    "status": "explicit",
                    "evidence_span": "We charge per number of backtest, forecast, and automated traders average $400 per user per year",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Adaptive stock forecasting algorithms", "premise_ids": ["P1"]},
                {"id": "D2", "name": "No-code broker automation via Collective2", "premise_ids": ["P2"]},
                {"id": "D3", "name": "Acquisition and usage pricing", "premise_ids": ["P3"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Make good returns on invested money via automated winning-stock orders",
                    "status": "explicit",
                    "evidence_span": "start making some good returns on your money instead of keeping it under your belt",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "accelerated machine learning forecasting model, which is adaptive and everyday learning",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "start automated orders",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "Every user is entitled to a free trial",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": True,
                "dependency_pass": True,
                "coder_confidence": 0.75,
            },
            "notes": "Transcript begins mid-demo (truncated). Early-adopter counts and board bios excluded as traction/credentials. Quantopian contrast folded into no-code automation premise. Channel list and price kept one commercial premise (§4.1(3)). Product/automation/money partition; not a classic need triad. Singletons retained as independently revisable.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Neotic's ML pipeline forecasts U.S. equities as winners/losers and supports backtesting, live portfolio population, and automated broker orders",
                    "status": "explicit",
                    "evidence_span": "Neotic will start populating daily his portfolio. And he can track the live by sending orders of winning stocks",
                },
                {
                    "id": "P2",
                    "text": "Unlike coder-centric platforms, traders need not write code to use Neotic",
                    "status": "explicit",
                    "evidence_span": "they require traders to know how to write codes, while Neotic doesn't",
                },
                {
                    "id": "P3",
                    "text": "Live automation runs via Collective2 marketplace linked to multiple brokers",
                    "status": "explicit",
                    "evidence_span": "connected to five other brokers",
                },
                {
                    "id": "P4",
                    "text": "Monetization is free trial then charges averaging $400/user/year for backtests, forecasts, and automated traders",
                    "status": "explicit",
                    "evidence_span": "average $400 per user per year",
                },
            ],
            "domains": [
                {"id": "D1", "name": "No-code ML trading product", "premise_ids": ["P1", "P2"]},
                {"id": "D2", "name": "Collective2 broker connectivity", "premise_ids": ["P3"]},
                {"id": "D3", "name": "Usage-based subscription pricing", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Good investment returns instead of idle cash",
                    "status": "explicit",
                    "evidence_span": "making some good returns on your money",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "sending orders of winning stocks with certain parameters",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "track the live performance on his broker's account",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "Every user is entitled to a free trial",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": True,
                "dependency_pass": True,
                "coder_confidence": 0.74,
            },
            "notes": "Truncated opening. Acquisition channel laundry list folded into pricing/commercial context rather than separate premise. No-code differentiation split from broker automation.",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Adaptive ML classifies U.S. stocks as winners or losers from daily market features",
                "status": "explicit",
                "evidence_span": "classify them as winners or losers accordingly",
            },
            {
                "id": "P2",
                "text": "Automated trading without coding via Collective2 and connected brokers",
                "status": "explicit",
                "evidence_span": "enter them on Neotic, and start automated orders",
            },
            {
                "id": "P3",
                "text": "Free trial and roughly $400 per user per year pricing; customers reached through forums, ads, content, and broker referrals",
                "status": "explicit",
                "evidence_span": "We acquire our customers through specialized forums, email campaigns, Google AdWords, publishing articles, and referral by our connected brokers",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Forecasting and automated execution", "premise_ids": ["P1", "P2"]},
            {"id": "D2", "name": "Acquisition and pricing", "premise_ids": ["P3"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Automated equity returns for individual investors",
                "status": "explicit",
                "evidence_span": "start making some good returns on your money instead of keeping it under your belt",
            }
        ],
        "secondary_value": [],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "automated orders",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "log in to Neotic.ai today",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": True,
            "dependency_pass": True,
            "coder_confidence": 0.73,
        },
        "notes": "ML and automation merged as one product domain. Truncation flagged. Market-size claims not coded as premises.",
    }


def case_441(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Many couples need relationship help that fits everyday life; a substantial share find therapy ineffective and there has been no digital health-tracking solution",
                    "status": "explicit",
                    "evidence_span": "11 to 18 percent of people that go to therapy find it to be not effective. There is no digital solution",
                },
                {
                    "id": "P2",
                    "text": "LifeCouple uses a metric onboarding questionnaire and proprietary algorithm across communication, trust, intimacy, and conflict, then check-ins, alerts, and AI to close satisfaction gaps",
                    "status": "explicit",
                    "evidence_span": "through a proprietary algorithm, four key areas of the relationship have now been filled. Communication, trust, intimacy and conflict",
                },
                {
                    "id": "P3",
                    "text": "The platform complements therapy and EAPs rather than replacing them, giving therapists measurable activities between sessions",
                    "status": "explicit",
                    "evidence_span": "we complement therapy. We do not say that therapy is going to be replaced by technology",
                },
                {
                    "id": "P4",
                    "text": "Unlike competitors, LifeCouple tracks and monitors relationship health continuously",
                    "status": "explicit",
                    "evidence_span": "no one tracks and no one monitors the health of one's relationship",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Therapy gap and everyday relationship need", "premise_ids": ["P1"]},
                {"id": "D2", "name": "Metric relationship health platform", "premise_ids": ["P2", "P4"]},
                {"id": "D3", "name": "Therapy and EAP complement channel", "premise_ids": ["P3"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Keep relationships healthy—a Fitbit for your heart",
                    "status": "explicit",
                    "evidence_span": "LifeCouple is a Fitbit for your heart",
                }
            ],
            "secondary_value": [
                {
                    "text": "Reduce unproductivity from divorce and unhappy marriages in EAP contexts",
                    "evidence_span": "13 billion dollars is lost of unproductivity because of people divorced or in an unhappy marriage",
                }
            ],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "address relationship challenges in a way that's suitable for their everyday life",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "This platform was built to keep a relationship healthy",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "This is a treatment plan",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.83,
            },
            "notes": "Icebreakers, digital gifts, love languages folded into platform premise (§4.1(5)). CAC/user traction excluded. 'Future of relationship health' treated as vision framing not premise (§4.1(4)). Need/product/channel triad justified: therapy-complement GTM revisable without changing the algorithm, and therapy-ineffectiveness is a separate market claim.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Couples need a relationship tool that fits entrepreneurial everyday life when therapy alone is not working",
                    "status": "explicit",
                    "evidence_span": "We needed to come up with something that worked in my entrepreneurial lifestyle",
                },
                {
                    "id": "P2",
                    "text": "Onboarding metrics plus AI/ML check-ins and icebreakers guide couples from current satisfaction toward healthier levels across four vital areas",
                    "status": "explicit",
                    "evidence_span": "through alerts and AI and machine learning, the couple is now offered ways to bring the gap between where they're at in their satisfaction level to be one",
                },
                {
                    "id": "P3",
                    "text": "Therapists can use LifeCouple as an iPad-era treatment plan with between-session phone activities they can see on return",
                    "status": "explicit",
                    "evidence_span": "When you walk in to day one of a therapist's office, that therapist is going to take an iPad out",
                },
                {
                    "id": "P4",
                    "text": "Go-to-market partners with organizations historically closed to technology because the product complements therapy",
                    "status": "explicit",
                    "evidence_span": "we've broken grounds with some of the biggest organizations that have blocked technology from day one, and we have built a partnership because we complement therapy",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Everyday relationship support need", "premise_ids": ["P1"]},
                {"id": "D2", "name": "AI relationship vitals platform", "premise_ids": ["P2"]},
                {"id": "D3", "name": "Therapist and enterprise partnerships", "premise_ids": ["P3", "P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Propelling healthy relationships people can monitor daily",
                    "status": "explicit",
                    "evidence_span": "built to keep a relationship healthy",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "without a good relationship, our lives could somewhat be meaningless",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "Fitbit for your heart",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "we complement therapy",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.8,
            },
            "notes": "Competitor non-tracking claim folded into product differentiation within P2 rather than separate premise. Traction and advisor names excluded.",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Therapy often fails a meaningful minority and lacks continuous digital relationship-health tracking",
                "status": "explicit",
                "evidence_span": "11 to 18 percent of people that go to therapy find it to be not effective. There is no digital solution. And now there is",
            },
            {
                "id": "P2",
                "text": "LifeCouple is a metric-driven AI platform that monitors communication, trust, intimacy, and conflict and coaches couples through check-ins and activities",
                "status": "explicit",
                "evidence_span": "LifeCouple is a platform that allows couples to address relationship challenges in a way that's suitable for their everyday life",
            },
            {
                "id": "P3",
                "text": "Positioned to complement therapy and EAP channels rather than replace clinicians",
                "status": "explicit",
                "evidence_span": "we complement therapy. We do not say that therapy is going to be replaced by technology",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Relationship therapy gap", "premise_ids": ["P1"]},
            {"id": "D2", "name": "LifeCouple monitoring platform", "premise_ids": ["P2"]},
            {"id": "D3", "name": "Complement-not-replace GTM", "premise_ids": ["P3"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Keep couples together with measurable relationship health",
                "status": "explicit",
                "evidence_span": "This platform will keep us together",
            }
        ],
        "secondary_value": [],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "There is no digital solution",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "LifeCouple is a Fitbit for your heart",
            },
            {
                "from": "D3",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "This is a treatment plan",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": False,
            "dependency_pass": True,
            "coder_confidence": 0.84,
        },
        "notes": "Feature list folded into P2. Vision closing line excluded (§4.1(4)). Need/product/channel triad justified by separate revisability.",
    }


def case_692(run):
    if run == 1:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Hiring fails often because candidates and employers decide on the wrong data: hidden jobs, soft-skill mismatch, and resumes that only show hard skills",
                    "status": "explicit",
                    "evidence_span": "everyone, both candidates and employers, are making decisions based on the wrong data",
                },
                {
                    "id": "P2",
                    "text": "Cognitive assessments of soft skills are the most accurate job-performance predictors but are long, expensive, and slow, so almost no one uses them",
                    "status": "explicit",
                    "evidence_span": "these tests are long and grueling, they're expensive, and they can take days or weeks to administer and get results",
                },
                {
                    "id": "P3",
                    "text": "Scoutable's 20-minute science-based mobile games quantify soft skills into a cognitive fingerprint and match candidates to top-performer profiles",
                    "status": "explicit",
                    "evidence_span": "In just 20 minutes, our science-based mobile games measure and quantify soft skills to match perfect fit candidates to top jobs",
                },
                {
                    "id": "P4",
                    "text": "Companies pay a setup fee for a top-performer predictive model plus subscription filtering or sourcing fees; games are free for candidates",
                    "status": "explicit",
                    "evidence_span": "Companies like Cloud Co pay us a one-time setup fee for creating the predictive model based on their top performers, and then a subscription for filtering inbound candidates against that model, or a sourcing fee",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Wrong-data hiring failure", "premise_ids": ["P1", "P2"]},
                {"id": "D2", "name": "Game-based soft-skill matching", "premise_ids": ["P3"]},
                {"id": "D3", "name": "Setup fee plus subscription/sourcing", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Help companies build world-class teams by matching perfect-fit soft-skill talent",
                    "status": "explicit",
                    "evidence_span": "how we help companies build world-class teams",
                }
            ],
            "secondary_value": [
                {
                    "text": "Candidates learn about their own unique talents",
                    "evidence_span": "free for anyone to download and play to learn more about themselves and their own unique talents",
                }
            ],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "46% of hires fail",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "match perfect fit candidates to top jobs",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "Moneyball for hiring",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.89,
            },
            "notes": "Mini-game examples and hustle/social/bandwidth score labels folded into the game-matching premise (§4.1(5)). Diversity-for-predictors framing folded into matching. Harvard bio excluded. Need/product/money triad justified: pricing pack revisable without changing game science; soft-skill measurement gap is separately revisable from general wrong-data claim but kept with P1 as one market domain. Singleton D2 and D3 retained.",
        }
    if run == 2:
        return {
            "premises": [
                {
                    "id": "P1",
                    "text": "Soft-skill mismatch drives most turnover while resumes only list measurable hard skills",
                    "status": "explicit",
                    "evidence_span": "89% of turnover is actually due to soft skill mismatch, not hard skills",
                },
                {
                    "id": "P2",
                    "text": "Cognitive soft-skill tests predict performance best but are unused because they are long, costly, and slow",
                    "status": "explicit",
                    "evidence_span": "cognitive assessments, are the single most accurate predictors of job performance across the board",
                },
                {
                    "id": "P3",
                    "text": "Mobile games in ~20 minutes produce a cognitive fingerprint used to model top performers and source lookalike talent while ignoring irrelevant resume signals",
                    "status": "explicit",
                    "evidence_span": "we gate out all of the irrelevant signals, such as gender, education, race, et cetera, to focus only on the demonstrated predictors of job success",
                },
                {
                    "id": "P4",
                    "text": "B2B setup fee plus subscription or sourcing; free play for individuals",
                    "status": "explicit",
                    "evidence_span": "Scoutable's games are free for anyone to download and play",
                },
            ],
            "domains": [
                {"id": "D1", "name": "Soft-skill measurement gap", "premise_ids": ["P1", "P2"]},
                {"id": "D2", "name": "Cognitive fingerprint matching", "premise_ids": ["P3"]},
                {"id": "D3", "name": "Freemium hiring monetization", "premise_ids": ["P4"]},
            ],
            "value": [
                {
                    "id": "V1",
                    "text": "Build world-class teams using demonstrated predictors of job success",
                    "status": "explicit",
                    "evidence_span": "Focusing on the right data maximizes a company's potential to build a world-class team",
                }
            ],
            "secondary_value": [],
            "causal_links": [
                {
                    "from": "D1",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "yet no one is using them",
                },
                {
                    "from": "D2",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "identified the talent that is most likely to perform like Aiden on the job",
                },
                {
                    "from": "D3",
                    "to": "V1",
                    "type": "domain-value",
                    "evidence_span": "one-time setup fee for creating the predictive model",
                },
            ],
            "epistemic_markers": [],
            "quality": {
                "thin_transcript": False,
                "truncated": False,
                "dependency_pass": True,
                "coder_confidence": 0.87,
            },
            "notes": "Hidden-jobs statistic folded into soft-skill/wrong-data market domain via P1 context. Game vignettes folded into P3.",
        }
    return {
        "premises": [
            {
                "id": "P1",
                "text": "Wrong hiring data—unadvertised jobs and soft-skill blind spots—causes widespread hire failure",
                "status": "explicit",
                "evidence_span": "In the US, 46% of hires fail",
            },
            {
                "id": "P2",
                "text": "Scoutable games measure soft skills in 20 minutes and match people to roles via top-performer predictive models",
                "status": "explicit",
                "evidence_span": "our science-based mobile games measure and quantify soft skills to match perfect fit candidates to top jobs",
            },
            {
                "id": "P3",
                "text": "Revenue from employer setup fees, subscriptions, and sourcing while candidates play free",
                "status": "explicit",
                "evidence_span": "a subscription for filtering inbound candidates against that model, or a sourcing fee for bringing undiscovered talent",
            },
        ],
        "domains": [
            {"id": "D1", "name": "Talent misallocation problem", "premise_ids": ["P1"]},
            {"id": "D2", "name": "Game-based matching product", "premise_ids": ["P2"]},
            {"id": "D3", "name": "Employer fees and free play", "premise_ids": ["P3"]},
        ],
        "value": [
            {
                "id": "V1",
                "text": "Unlock better human potential by building world-class teams",
                "status": "explicit",
                "evidence_span": "unlock the next wave of human potential",
            }
        ],
        "secondary_value": [
            {
                "text": "Match perfect-fit candidates to top jobs",
                "evidence_span": "match perfect fit candidates to top jobs",
            }
        ],
        "causal_links": [
            {
                "from": "D1",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "human talent misallocation",
            },
            {
                "from": "D2",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "Moneyball for hiring",
            },
            {
                "from": "D3",
                "to": "V1",
                "type": "domain-value",
                "evidence_span": "Companies like Cloud Co pay us",
            },
        ],
        "epistemic_markers": [],
        "quality": {
            "thin_transcript": False,
            "truncated": False,
            "dependency_pass": True,
            "coder_confidence": 0.85,
        },
        "notes": "Cognitive-assessment unused-because-friction claim folded into product necessity within market+product rather than separate premise. Need/product/money triad justified.",
    }
