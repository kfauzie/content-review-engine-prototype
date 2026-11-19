"""pm-1 Initial review of the synthetic transcript test set. Every number in RUN.md comes from this script.

Reads only what a reviewer sees: the expert profile, the onboarding declaration and the transcript.
The answer keys are cut off before parsing and never read here; they are kept as a hidden test set for the build.

Run from the run folder: python3 notebooks/data_review.py
"""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "data" / "synthetic-expert-transcripts.md"
TURN = re.compile(r"^\[(\d\d):(\d\d)\] (EXPERT|INTERVIEWER|AI INTERVIEWER): (.*)$")
EMPLOYER = re.compile(r",\s*([A-Z][\w&]*(?: [A-Z][\w&]*)*)\s*\(")
COMPANY_WORDS = r"Grocers|Logistics|Freight|Haulage|Software|Payments|Invoicing|Biomedical|Analytics|Foods|Advisory|Insurance|Credit"

# Markers a reviewer reading line by line would stop at. Each is a plain pattern, so any count can be checked by hand.
MARKERS = {
    "precise figure or period": r"\d+(?:\.\d+)?%|\bQ[1-4]\b|£|\$|€",
    "timing not yet public": r"\b(?:next|last|this) (?:week|month|quarter)\b|\b(?:from|by|in) (?:January|February|March|April|May|June|July|August|September|October|November|December|spring|summer|autumn|winter|Q[1-4])\b|haven't been (?:told|announced)|not (?:yet )?(?:public|announced)|signed off|timing on the announcement",
    "insider source": r"told me|I still talk to|my contact|internally|people there",
    "named person": None,  # filled per transcript: capitalised first and last name that isn't a company
}
PUBLIC_SOURCE = r"investor day|public filings|annual results|earnings call|slides they published|the August call|in their filings"
HEDGE = r"probably shouldn't|not saying anything specific|let's just say|stay careful|stick to what's public|rather talk about capabilities"


def words(s):
    return len(s.split())


def parse(text):
    out = []
    for block in text.split("\n## Transcript ")[1:]:
        block = block.split("**Answer key**")[0]  # the answer key is never read
        head = block.splitlines()[0]
        profile = re.search(r"\*\*Expert profile:\*\* (.*)", block).group(1)
        declaration = re.search(r"\*\*Onboarding declaration:\*\* (.*)", block).group(1)
        turns = [TURN.match(l).groups() for l in block.splitlines() if TURN.match(l)]
        turns = [(int(m) * 60 + int(s), who, txt) for m, s, who, txt in turns]
        out.append(dict(num=int(head.split(":")[0]), profile=profile, declaration=declaration, turns=turns,
                        employers=sorted({e.split()[0] for e in EMPLOYER.findall(profile)}),
                        first_name=profile.split()[0],
                        current=declaration.startswith("Currently employed"),
                        ai_led=any(w == "AI INTERVIEWER" for _, w, _ in turns)))
    return out


def people(txt, t):
    names = re.findall(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", txt)
    return [n for n in names if not re.search(COMPANY_WORDS, n) and n.split()[0] not in t["employers"]
            and not re.search(r"\b(North|South|East|West)\b", n)
            and not re.match(r"(The|In|At|On|For|My|Our|Let|Look|Most|Several|Machine|Electric|Contract|Default|Volume)\b", n)]


def markers(txt, t):
    hits = [k for k, p in MARKERS.items() if p and re.search(p, txt)]
    if people(txt, t):
        hits.append("named person")
    return hits


def main():
    T = parse(SRC.read_text())
    A = [(t, ts, txt) for t in T for ts, who, txt in t["turns"] if who == "EXPERT"]
    Q = [(t, ts, txt) for t in T for ts, who, txt in t["turns"] if who != "EXPERT"]

    print("== 1. The data")
    print(f"transcripts: {len(T)} (AI-led: {sum(t['ai_led'] for t in T)}); expert answers: {len(A)}; "
          f"interviewer questions: {len(Q)}; expert words: {sum(words(a[2]) for a in A)}")
    print("first five expert answers (transcript, time, words, start):")
    for t, ts, txt in A[:5]:
        print(f"  T{t['num']} {ts // 60:02d}:{ts % 60:02d} {words(txt):>3}w  {txt[:70]}...")
    lens = [max(ts for ts, _, _ in t["turns"]) for t in T]
    print(f"call length (last timestamp): {min(lens) // 60}:{min(lens) % 60:02d} to {max(lens) // 60}:{max(lens) % 60:02d}")

    print("\n== Data quality")
    print(f"every transcript has a profile and a declaration: {all(t['profile'] and t['declaration'] for t in T)}")
    print(f"timestamps increase in every transcript: {all([a for a, _, _ in t['turns']] == sorted(a for a, _, _ in t['turns']) for t in T)}")
    self_dated = [t["num"] for t in T if "per declaration" in t["profile"]]
    print(f"profiles whose dates come from the expert's own declaration: {len(self_dated)} {self_dated}")

    print("\n== F1. What's concentrated: answers with any marker a reviewer would stop at")
    marked = [(t["num"], ts, markers(txt, t)) for t, ts, txt in A if markers(txt, t)]
    print(f"answers with at least one marker: {len(marked)} of {len(A)} ({len(marked) / len(A):.1%})")
    print(f"answers with none: {len(A) - len(marked)} ({1 - len(marked) / len(A):.1%})")
    for k in MARKERS:
        n = [(m[0], f"{m[1] // 60:02d}:{m[1] % 60:02d}") for m in marked if k in m[2]]
        print(f"  {k}: {len(n)} {n}")
    w_marked = sum(words(txt) for t, ts, txt in A if markers(txt, t))
    print(f"words in marked answers: {w_marked} of {sum(words(a[2]) for a in A)}")

    print("\n== F2. What's concentrated: the expert's own employer")
    print(f"experts currently employed (per declaration): {sum(t['current'] for t in T)} of {len(T)} "
          f"{[t['num'] for t in T if t['current']]}")
    q_emp = [(t["num"], txt) for t, ts, txt in Q if any(e in txt for e in t["employers"])]
    a_emp = [(t["num"], ts) for t, ts, txt in A if any(e in txt for e in t["employers"])]
    calls_q = sorted({n for n, _ in q_emp})
    print(f"interviewer questions that name the expert's own employer: {len(q_emp)}, in {len(calls_q)} of {len(T)} calls {calls_q}")
    for n, txt in q_emp:
        print(f"  T{n}: \"{txt}\"")
    print(f"expert answers that name their own employer: {len(a_emp)}, in {len({n for n, _ in a_emp})} calls "
          f"{[(n, f'{ts // 60:02d}:{ts % 60:02d}') for n, ts in a_emp]}")
    we = [(t["num"], ts) for t, ts, txt in A if t["current"] and re.search(r"\b(we|our|us)\b", txt, re.I)]
    print(f"answers by currently employed experts that say we/our/us: {len(we)}")

    print("\n== F3. What's odd: answers that look sensitive but name a public source")
    pub = [(t["num"], f"{ts // 60:02d}:{ts % 60:02d}", markers(txt, t), any(e in txt for e in t["employers"]))
           for t, ts, txt in A if re.search(PUBLIC_SOURCE, txt)]
    print(f"answers that cite a public source: {len(pub)} {pub}")
    risky_pub = [p for p in pub if p[2] or p[3]]
    print(f"of those, with a precise figure or the expert's employer named: {len(risky_pub)}")
    pub_calls = sorted({p[0] for p in pub})
    print(f"calls with a public-source answer: {pub_calls}")

    print("\n== F4. What's missing from the text: who the expert is talking about, and how they know")
    for t, ts, txt in A:
        ps, src = people(txt, t), re.search(MARKERS["insider source"], txt)
        if ps or src:
            print(f"  T{t['num']} {ts // 60:02d}:{ts % 60:02d} people={ps} source={'yes' if src else 'no'}")
    named = sum(1 for t, ts, txt in A if people(txt, t))
    src = sum(1 for t, ts, txt in A if re.search(MARKERS["insider source"], txt))
    print(f"answers naming a private person: {named}; answers citing a personal or insider source: {src}")

    print("\n== Looked at")
    hedges = [(t["num"], f"{ts // 60:02d}:{ts % 60:02d}") for t, ts, txt in A if re.search(HEDGE, txt, re.I)]
    print(f"answers where the expert hedges or limits what they'll say: {len(hedges)} {hedges}")
    ai = [t for t in T if t["ai_led"]]
    print(f"AI-led calls: {[t['num'] for t in ai]}; their marked answers: "
          f"{[(m[0], m[1]) for m in marked if m[0] in [t['num'] for t in ai]]}")


if __name__ == "__main__":
    main()
