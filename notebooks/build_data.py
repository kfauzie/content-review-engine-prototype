"""Assemble data/benchmark.json for the prototype and embed it in build/mvp.html.
Run from the run folder: python3 notebooks/build_data.py

Sources (all ILLUSTRATIVE):
  counts         made up for a 1,000-transcript sample (Kevin's call), defined below
  examples       data/examples_illustrative.json (missed issues and false alarms; 7 quote the test set, the rest written)
  transcripts    5 from data/synthetic-expert-transcripts.md (test set), 13 from data/transcripts_illustrative.json (written)
Clickable cards: every card in the top two categories, plus the fix examples from other categories.
Masking: every person and company is replaced by a stable ID (notebooks/mask.py) before anything is written. The vault
(name -> ID) goes to data/private/vault.json, gitignored; the masked test set goes to data/eval/test_set_masked.md.
A clickable card's timestamp is taken from its transcript's passage, so the two always agree.
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_review import SRC, parse  # noqa: E402
from mask import Masker, build_vault, listed_status, save_vault, tags_for  # noqa: E402
from release_gate import MASKED_TEST_SET, release_data  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = 1000
TOP = ["Material non-public information", "Current-employer confidential"]
# name, priority, description, found by human reviewers, missed by AI, false alarms -- made up
CATEGORIES = [
    ("Material non-public information", "high", "Non-public facts that could move a listed company's share price", 38, 5, 60),
    ("Current-employer confidential", "high", "Non-public information about the expert's current employer", 52, 4, 30),
    ("Declaration conflict", "high", "Contradicts what the expert declared", 14, 0, 9),
    ("Source disclosure", "lower", "Names an insider as the source", 29, 4, 8),
    ("Former-client confidential", "lower", "Confidential details from a former client or employer", 33, 3, 20),
    ("Personal data", "lower", "Names or sensitive details of private individuals", 96, 7, 60),
]
# reviewer comments and root causes for the 5 test-set transcripts (the 13 written ones carry their own)
TEST_SET_NOTES = {
    "T5-01:24": ("Hedged, but points to a possible undisclosed product quality issue at a listed former employer, sourced from current "
                 "contacts there. Too uncertain for AI to clear or reject; needs a compliance reviewer.",
                 "The AI looks for named companies, and none is named: the expert says \u201ctheir\u201d. Linking it to Northwind, a listed "
                 "company he left in March 2026, needs the question before it and his declaration."),
    "T3-01:34": ("Non-public pricing decision at the expert's current employer, not yet told to customers, in breach of her declaration. "
                 "Redacted; the expert gets a reminder of her restrictions.",
                 "The AI only checks passages that name a company. This one says \u201cfor us\u201d, and linking that to Teallight, her "
                 "current employer, needs her declaration, which the AI didn't read."),
    "T2-01:19": ("Naming Corvane as a commonly mentioned target is public speculation, and Corvane isn't the expert's employer. Cleared.",
                 "The AI flags any passage that names a company. It matched \u201cCorvane Freight\u201d and didn't weigh that the expert "
                 "framed it as public talk."),
    "T4-00:26": ("The expert left Quillon in 2021 and everything here is from the public investor day and filings. Cleared.",
                 "It matched \u201cQuillon\u201d, the expert's former employer, without checking that he left in 2021 or that he cites "
                 "the public investor day."),
    "T6-01:34": ("Names a current insider as the source of non-public vendor decisions, which also contradicts her declared lack of "
                 "professional contact with Marrow. Transcript rejected; the expert is referred to the vetting team.",
                 "The AI checks for company names, and this answer names none: \u201cthere\u201d points back to Marrow. It didn't treat "
                 "\u201cmy contact Jamie Holt \u2026 told me\u201d as an insider source, so nothing was flagged."),
    "T8-01:24": ("Names a private individual alongside private health information. Redacted.",
                 "The AI looks for company information only. A private person's name and health details aren't on its list, so the "
                 "answer went through."),
    "T7-00:36": ("Precise figures, but all from the public Q2 earnings call and slides, which the expert confirms at 01:11. He left "
                 "Ardent in 2022. Cleared.",
                 "It matched \u201cArdent\u201d next to precise margin figures and flagged them, without checking the source the expert "
                 "gave: the public Q2 earnings call."),
}


# made-up reviewers (Athens compliance team and Legal), assigned in turn; possible MNPI goes to Legal
REVIEWERS = {"Material non-public information": ["Sophie Laurent, Legal Counsel", "Nikos Andreou, Senior Compliance Manager"],
             "other": ["Eleni Papadaki, Compliance Analyst", "Dimitris Vlachos, Compliance Analyst", "Katerina Ioannou, Compliance Analyst"]}
REVIEW_TIMES = ["09:42", "11:17", "14:05", "16:38", "10:26", "12:51", "15:09"]  # made up
# the three fixes, from the reviewers' comments and the agents' root-cause analysis (Kevin's judgement in tagging)
FIXES = [
    {"id": "declaration", "title": "Read each answer in context", "cause_label": "Why the AI missed it",
     "root_cause": "The AI read each answer in isolation. When an expert said \u201cwe\u201d, \u201ctheir\u201d or \u201cthe board\u201d, it didn't know "
                   "which company they meant, so it couldn't tell that the expert was talking about their own employer, a client or a former employer.",
     "examples": [{"name": "Priya Natarajan", "highlight": "For us specifically"}, {"name": "Henrik Lindqvist", "highlight": "The board approved the sale"},
                  {"name": "Olivia Grant", "highlight": "the regulator's decision on their diabetes drug"}],
     "how": ["Give the AI the expert's declaration and the question asked alongside every answer.",
             "Work out which company \u201cwe\u201d, \u201cour\u201d or \u201ctheir\u201d refers to before judging the answer.",
             "Check what was said against the expert's restrictions and the date they left each company."]},
    {"id": "people", "title": "Check for people and sources, not just companies", "cause_label": "Why the AI missed it",
     "root_cause": "The AI only looked for information about companies. It didn't catch private individuals being named, or experts naming "
                   "insiders as their source.",
     "examples": [{"name": "Elena Vasquez", "highlight": "My contact Jamie Holt, who runs procurement there now, told me"},
                  {"name": "Hannah Booth", "highlight": "Mark Ellison"}],
     "how": ["Flag any named private individual mentioned alongside health, family or legal details.",
             "Flag phrases that point to an inside source, such as \u201cmy contact\u201d, \u201ctold me\u201d and \u201cI still speak to\u201d.",
             "Send both to a reviewer, with the name highlighted."]},
    {"id": "sources", "title": "Check the expert's cited source before flagging", "cause_label": "Why the AI raised a false alarm",
     "root_cause": "Most false alarms were statements the expert attributed to a public source, such as an earnings call, a press release or an "
                   "annual report. The AI flagged them without checking whether the information really was public.",
     "examples": [{"name": "Ibrahim Yusuf", "highlight": "Our prices are on the website"}, {"name": "Laura Bennett", "highlight": "As their annual report says"},
                  {"name": "Robert Chen", "highlight": "On their Q2 earnings call in August"},
                  {"name": "Chloe Martin", "highlight": "We announced the Leeds office in a press release"}],
     "how": ["Spot when an expert cites a source.",
             "Check that source: filings, press releases or the company's website.",
             "Clear the statement if the information is there. Keep it flagged if it isn't."]},
]
# the telling phrase in each card's quote (fix examples reuse the same phrase); checked to appear word for word
HIGHLIGHT = {
    "Sanjay Mehta": "watch their Q3 numbers closely", "Olivia Grant": "the regulator's decision on their diabetes drug",
    "Henrik Lindqvist": "The board approved the sale", "Nadia Rahimi": "Their biggest customer has given notice on the five-year supply deal",
    "Benjamin Cole": "The October order book I saw was down about 15%",
    "Priya Natarajan": "For us specifically", "Grace Liu": "We're closing the Manchester plant in March",
    "Mateo Alvarez": "Our roadmap has the analytics module launching in Q2", "Siobhan Kelly": "We're about to lose our second-largest customer",
    "Elena Vasquez": "My contact Jamie Holt, who runs procurement there now, told me", "Owen Prendergast": "Their head of logistics, Carla, told me",
    "Mei Lin Tan": "I still speak to the plant manager at Ostrava", "Farid Haddad": "Someone on their pricing committee sent me the new rate card",
    "Thomas Achebe": "the stranded costs came out at nearly twice what management told the board",
    "Ingrid Solberg": "had its core banking migration fail twice", "Ravi Chandran": "the real number was well above what they show investors",
    "Hannah Booth": "Mark Ellison", "Marcus Webb": "Tom Reyes, has been going through a difficult divorce",
    "Sofia Marchetti": "I've got his personal mobile", "Kwame Mensah": "Aisha Rahman, went on long-term sick leave after surgery",
    "Lena Hoffmann": "Pieter van Dam, was let go after a drink-driving conviction", "Daniel Osei": "Rachel Lim, is on maternity leave",
    "Aoife Brennan": "The founder's son is only nineteen",
    "Daniel Reyes": "Publicly, people talk about", "Tom Fairley": "at their 2024 investor day", "Robert Chen": "On their Q2 earnings call in August",
    "Laura Bennett": "As their annual report says", "Arjun Mehra": "said on the results call",
    "Chloe Martin": "We announced the Leeds office in a press release", "Ibrahim Yusuf": "Our prices are on the website",
    "Ruth Okonkwo": "what's in our published sustainability report", "Marco Rossi": "showed the new product on stage at the trade show",
    "Isabel Moreno": "My own estimate",
    "Kenji Watanabe": "Nobody told me this, but my view is",
    "Fatima Al-Sayed": "that's only my opinion",
    "George Whitfield": "When I was at Harlow Foods in 2015",
    "Ana Costa": "I left Brennick Steel in 2017",
    "Patrick Doyle": "back in 2014",
    "Leila Nasser": "has said at two conferences",
    "Tomasz Nowak": "that's just the chatter going round",
    "Rebecca Stone": "According to the financial press",
}
# false alarms grouped by why the AI raised them; counts made up (they sum to 187), examples tagged by Kevin's judgement
FALSE_ALARM_TYPES = [
    {"id": "public-source", "name": "Public source cited", "description": "The expert attributed it to a filing, earnings call, press release or website", "count": 98},
    {"id": "own-view", "name": "The expert's own opinion or estimate", "description": "A personal view or estimate, not based on inside information", "count": 41},
    {"id": "former-employer", "name": "Former employer, left long ago", "description": "About a company the expert left years ago, with nothing current", "count": 27},
    {"id": "market-talk", "name": "Public market talk", "description": "Speculation already circulating in the market", "count": 21},
]
FALSE_ALARM_TYPE_OF = {"Robert Chen": "public-source", "Laura Bennett": "public-source", "Arjun Mehra": "public-source", "Chloe Martin": "public-source",
                       "Ibrahim Yusuf": "public-source", "Ruth Okonkwo": "public-source", "Marco Rossi": "public-source",
                       "Tom Fairley": "former-employer", "Daniel Reyes": "market-talk",
                       "Isabel Moreno": "own-view",
                       "Kenji Watanabe": "own-view",
                       "Fatima Al-Sayed": "own-view",
                       "George Whitfield": "former-employer",
                       "Ana Costa": "former-employer",
                       "Patrick Doyle": "former-employer",
                       "Leila Nasser": "market-talk",
                       "Tomasz Nowak": "market-talk",
                       "Rebecca Stone": "market-talk",
                       }
FIX_EXAMPLE_NAMES = {x["name"] for f in FIXES for x in f["examples"]}
FIX_OF = {  # card name -> fix id; cards not listed are not addressed by any of the three
    "Sanjay Mehta": "declaration", "Olivia Grant": "declaration", "Henrik Lindqvist": "declaration", "Nadia Rahimi": "declaration",
    "Benjamin Cole": "declaration", "Priya Natarajan": "declaration", "Grace Liu": "declaration",
    "Thomas Achebe": "declaration", "Ingrid Solberg": "declaration", "Ravi Chandran": "declaration", "Tom Fairley": "declaration",
    "Elena Vasquez": "people", "Owen Prendergast": "people", "Mei Lin Tan": "people", "Farid Haddad": "people",
    "Hannah Booth": "people", "Marcus Webb": "people", "Sofia Marchetti": "people", "Kwame Mensah": "people",
    "Lena Hoffmann": "people", "Daniel Osei": "people", "Aoife Brennan": "people",
    "Daniel Reyes": "sources", "Robert Chen": "sources", "Laura Bennett": "sources", "Arjun Mehra": "sources",
    "Chloe Martin": "sources", "Ibrahim Yusuf": "sources", "Ruth Okonkwo": "sources", "Marco Rossi": "sources",
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def ts(s):
    return f"{s // 60:02d}:{s % 60:02d}"


def role_of(profile):
    return re.sub(r"^[^.]+\.\s*", "", profile).rsplit(" Industry:", 1)[0]


def blocks(src):
    """The test set split per transcript, so each block can be masked with its own people in context."""
    parts = src.split("\n## Transcript ")
    return parts[0], parts[1:]


def main():
    ex = json.loads((ROOT / "data/examples_illustrative.json").read_text())
    written_raw = {t["name"]: t for t in json.loads((ROOT / "data/transcripts_illustrative.json").read_text())["transcripts"]}
    src = SRC.read_text()
    topics = {int(n): tp.strip() for n, tp in re.findall(r"^\| (\d) \| ([^|]+?) \|", src, re.M)}

    # masking: one vault for every person and company; the masked data is all that leaves this step
    experts = [e["name"] for e in ex["examples"] + ex["false_alarms"]] + [t["profile"].split(".")[0] for t in parse(src)]
    reviewers = [r.split(",")[0] for pool in REVIEWERS.values() for r in pool]
    vault = build_vault(experts, reviewers)
    save_vault(vault)
    M = Masker(vault)
    head, raw_blocks = blocks(src)
    block_ctx = {int(re.match(r"\d+", b).group()): M.context(b) for b in raw_blocks}
    masked_src = M.text(head) + "".join("\n## Transcript " + M.text(b, block_ctx[int(re.match(r"\d+", b).group())]) for b in raw_blocks)
    MASKED_TEST_SET.write_text(masked_src)
    tset = {t["num"]: t for t in parse(masked_src)}
    ctx_of = {}
    for e in ex["examples"] + ex["false_alarms"]:
        c = M.context(e, written_raw.get(e["name"]))
        m = re.match(r"test set T(\d)", e["source"])
        ctx_of[e["name"]] = c | (block_ctx[int(m.group(1))] if m else set())
    written = {n: M.obj(w, ctx_of.get(n, M.context(w))) for n, w in written_raw.items()}
    listed = listed_status(masked_src, *[w["profile"] + " " + w["declaration"] for w in written.values()])

    transcripts, cards, by_raw = {}, [], {}
    for kind, items in (("missed", ex["examples"]), ("false_alarm", ex["false_alarms"])):
        for e in items:
            raw, ctx = e["name"], ctx_of[e["name"]]
            me = M.obj(e, ctx)
            name = M.name(raw)
            card = {"id": slug(f"{kind}-{name}"), "kind": kind, "category": e["category"], "name": name,
                    "date": e["date"], "ts": e["ts"], "quote": me["quote"], "source": e["source"],
                    "cleared": me.get("cleared"), "transcript": None, "fix": FIX_OF.get(raw), "highlight": M.text(HIGHLIGHT[raw], ctx),
                    "fa_type": FALSE_ALARM_TYPE_OF.get(raw) if kind == "false_alarm" else None}
            assert card["highlight"] in card["quote"], raw
            if e["category"] in TOP or raw in FIX_EXAMPLE_NAMES:
                tid = card["id"]
                if e["source"].startswith("test set"):
                    n, pts = re.match(r"test set T(\d)-(\d\d:\d\d)", e["source"]).groups()
                    t = tset[int(n)]
                    rc, why = (M.text(x, ctx) for x in TEST_SET_NOTES[f"T{n}-{pts}"])
                    tr = {"topic": topics[int(n)], "profile": t["profile"], "declaration": t["declaration"],
                          "turns": [{"ts": ts(s), "speaker": w, "text": x} for s, w, x in t["turns"]],
                          "passage_ts": pts, "reviewer_comment": rc, "root_cause": why, "source": f"test set, transcript {n}"}
                else:
                    w = written[raw]
                    assert (w["kind"], w["category"], w["date"]) == (kind, e["category"], e["date"]), raw
                    tr = {k: w[k] for k in ("topic", "profile", "declaration", "turns", "passage_ts", "reviewer_comment", "root_cause")}
                    tr["source"] = "written for the prototype"
                pool = REVIEWERS.get(e["category"], REVIEWERS["other"]) if kind == "missed" else REVIEWERS["other"]
                n = len(transcripts)  # made-up review time: one or two days after the call, during Athens office hours
                reviewed = date.fromisoformat(e["date"]) + timedelta(days=1 + n % 2)
                tr.update({"id": tid, "kind": kind, "category": e["category"], "name": name, "date": e["date"],
                           "role": role_of(tr["profile"]), "reviewer": M.text(pool[n % len(pool)]),
                           "reviewed_at": f"{reviewed.isoformat()}T{REVIEW_TIMES[n % len(REVIEW_TIMES)]}",
                           "entities": tags_for(tr["profile"], tr["declaration"], " ".join(u["text"] for u in tr["turns"]), listed)})
                transcripts[tid] = tr
                card["transcript"] = tid
                card["ts"] = tr["passage_ts"]
            cards.append(card)
            by_raw[raw] = card

    assert sum(t["count"] for t in FALSE_ALARM_TYPES) == sum(c[5] for c in CATEGORIES) == 187
    assert all(c["fa_type"] for c in cards if c["kind"] == "false_alarm")
    for f in FIXES:
        for x in f["examples"]:
            c = by_raw[x["name"]]
            assert x["highlight"] == HIGHLIGHT[x["name"]] and c["fix"] == f["id"], x
    data = {"note": "ILLUSTRATIVE. Made-up counts for a 1,000-transcript sample; examples and transcripts are synthetic.",
            "sample": SAMPLE, "top": TOP,
            "categories": [{"name": n, "priority": p, "description": d, "found": f, "missed": m, "false_alarms": fa}
                           for n, p, d, f, m, fa in CATEGORIES],
            "false_alarm_types": FALSE_ALARM_TYPES,
            "fixes": [{**f, "examples": [{**x, **{k: by_raw[x["name"]][k] for k in ("name", "highlight", "quote", "date", "ts", "kind", "category", "transcript")}}
                                         for x in f["examples"]]} for f in FIXES], "cards": cards, "transcripts": transcripts}
    data = M.obj(data)  # safety pass over every remaining string (descriptions, fix copy)
    data["release"] = release_data(M, tset, listed, topics)
    leaks = M.leaks(json.dumps(data, ensure_ascii=False))
    assert not leaks, f"real names left after masking: {leaks}"
    out = ROOT / "data/benchmark.json"
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")

    html_path = ROOT / "build/mvp.html"
    html = html_path.read_text()
    embedded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = re.sub(r'(<script id="data" type="application/json">).*?(</script>)', lambda m: m.group(1) + embedded + m.group(2),
                  html, count=1, flags=re.S)
    html_path.write_text(html)
    print(f"cards {len(cards)}, clickable {sum(1 for c in cards if c['transcript'])}, transcripts {len(transcripts)}")


if __name__ == "__main__":
    main()
