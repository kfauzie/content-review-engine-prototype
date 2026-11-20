"""Assemble data/benchmark.json for the prototype and embed it in build/mvp.html.
Run from the run folder: python3 notebooks/build_data.py

Sources (all ILLUSTRATIVE):
  counts         made up for a 1,000-transcript sample (Kevin's call), defined below
  examples       data/examples_illustrative.json (missed issues and false alarms; 7 quote the test set, the rest written)
  transcripts    5 from data/synthetic-expert-transcripts.md (test set), 13 from data/transcripts_illustrative.json (written)
Clickable cards: every card in the top two categories, plus the fix examples from other categories.
A clickable card's timestamp is taken from its transcript's passage, so the two always agree.
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_review import SRC, parse  # noqa: E402

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


def main():
    ex = json.loads((ROOT / "data/examples_illustrative.json").read_text())
    written = {t["name"]: t for t in json.loads((ROOT / "data/transcripts_illustrative.json").read_text())["transcripts"]}
    src = SRC.read_text()
    topics = {int(n): tp.strip() for n, tp in re.findall(r"^\| (\d) \| ([^|]+?) \|", src, re.M)}
    tset = {t["num"]: t for t in parse(src)}

    transcripts, cards = {}, []
    for kind, items in (("missed", ex["examples"]), ("false_alarm", ex["false_alarms"])):
        for e in items:
            card = {"id": slug(f"{kind}-{e['name']}"), "kind": kind, "category": e["category"], "name": e["name"],
                    "date": e["date"], "ts": e["ts"], "quote": e["quote"], "source": e["source"],
                    "cleared": e.get("cleared"), "transcript": None, "fix": FIX_OF.get(e["name"])}
            if e["category"] in TOP or e["name"] in FIX_EXAMPLE_NAMES:
                tid = card["id"]
                if e["source"].startswith("test set"):
                    n, pts = re.match(r"test set T(\d)-(\d\d:\d\d)", e["source"]).groups()
                    t = tset[int(n)]
                    rc, why = TEST_SET_NOTES[f"T{n}-{pts}"]
                    tr = {"topic": topics[int(n)], "profile": t["profile"], "declaration": t["declaration"],
                          "turns": [{"ts": ts(s), "speaker": w, "text": x} for s, w, x in t["turns"]],
                          "passage_ts": pts, "reviewer_comment": rc, "root_cause": why, "source": f"test set, transcript {n}"}
                else:
                    w = written[e["name"]]
                    assert (w["kind"], w["category"], w["date"]) == (kind, e["category"], e["date"]), e["name"]
                    tr = {k: w[k] for k in ("topic", "profile", "declaration", "turns", "passage_ts", "reviewer_comment", "root_cause")}
                    tr["source"] = "written for the prototype"
                pool = REVIEWERS.get(e["category"], REVIEWERS["other"]) if kind == "missed" else REVIEWERS["other"]
                n = len(transcripts)  # made-up review time: one or two days after the call, during Athens office hours
                reviewed = date.fromisoformat(e["date"]) + timedelta(days=1 + n % 2)
                tr.update({"id": tid, "kind": kind, "category": e["category"], "name": e["name"], "date": e["date"],
                           "role": role_of(tr["profile"]), "reviewer": pool[n % len(pool)],
                           "reviewed_at": f"{reviewed.isoformat()}T{REVIEW_TIMES[n % len(REVIEW_TIMES)]}"})
                transcripts[tid] = tr
                card["transcript"] = tid
                card["ts"] = tr["passage_ts"]
            cards.append(card)

    by_name = {c["name"]: c for c in cards}
    for f in FIXES:
        for x in f["examples"]:
            c = by_name[x["name"]]
            assert x["highlight"] in c["quote"] and c["fix"] == f["id"], x
    data = {"note": "ILLUSTRATIVE. Made-up counts for a 1,000-transcript sample; examples and transcripts are synthetic.",
            "sample": SAMPLE, "top": TOP,
            "categories": [{"name": n, "priority": p, "description": d, "found": f, "missed": m, "false_alarms": fa}
                           for n, p, d, f, m, fa in CATEGORIES],
            "fixes": [{**f, "examples": [{**x, **{k: by_name[x["name"]][k] for k in ("quote", "date", "ts", "kind", "category", "transcript")}}
                                         for x in f["examples"]]} for f in FIXES], "cards": cards, "transcripts": transcripts}
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
