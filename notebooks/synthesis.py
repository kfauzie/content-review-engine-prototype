"""pm-1 Step 2 (Answer): test the claims from the discovery call, one at a time, and compute every number the
solution concept quotes. Run from the run folder: python3 notebooks/synthesis.py

Sources: the 8 transcripts (profiles, declarations, transcripts; answer keys cut off). The claims come from a
role-play call and are tested as hypotheses. The answer keys are read only in the last section, for the test cases.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_review import SRC, MARKERS, markers, parse, people, words  # noqa: E402

NOT_COMPANIES = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                 "November", "December", "Europe", "Scotland", "North", "West", "UK", "EU", "US"}


def companies(T):
    """Company names: the expert's employers from each profile, plus capitalised words used mid-sentence in an
    expert answer that are not months, places or people's names."""
    names = {e for t in T for e in t["employers"]}
    for t in T:
        for _, who, txt in t["turns"]:
            if who != "EXPERT":
                continue
            ppl = {w for p in people(txt, t) for w in p.split()}
            for s in re.split(r"(?<=[.!?])\s+", txt):
                for w in s.split()[1:]:
                    w = w.strip(",.?!'\":;")
                    if re.fullmatch(r"[A-Z][a-z]+", w) and w not in NOT_COMPANIES and w not in ppl and w not in ("Freight", "Credit"):
                        names.add(w)
    return sorted(names)


def main():
    T = parse(SRC.read_text())
    A = [(t, ts, txt) for t in T for ts, who, txt in t["turns"] if who == "EXPERT"]
    C = companies(T)
    print(f"company names found: {C}")

    print("\n== Claim 1: 'Most of any transcript is harmless, but we don't know which 10% matters until we've read it.'")
    marked = [(t, ts, txt) for t, ts, txt in A if markers(txt, t)]
    mw, aw = sum(words(x[2]) for x in marked), sum(words(x[2]) for x in A)
    print(f"answers with a marker: {len(marked)} of {len(A)} ({len(marked) / len(A):.1%}); words: {mw} of {aw} ({mw / aw:.1%})")

    print("\n== Claim 2: 'Whenever an expert mentions a company, the reviewer has to stop ... Sometimes 5 or 6 times in one call.'")
    rows = []
    for t in T:
        ans = [(ts, txt) for ts, who, txt in t["turns"] if who == "EXPERT"]
        co = [ts for ts, txt in ans if any(re.search(rf"\b{c}\b", txt) for c in C)]
        own = [ts for ts, txt in ans if any(re.search(rf"\b{e}\b", txt) for e in t["employers"])]
        mins = max(ts for ts, _, _ in t["turns"]) / 60
        rows.append((t["num"], len(co), len(own), mins))
        print(f"  T{t['num']}: answers naming a company {len(co)}, naming the expert's own employer {len(own)}, call {mins:.1f} min")
    tot_co, tot_min = sum(r[1] for r in rows), sum(r[3] for r in rows)
    per_min = tot_co / tot_min
    print(f"answers naming a company: {tot_co} in {tot_min:.1f} minutes of calls = {per_min:.2f} a minute")
    print(f"calls with no company named by the expert: {sum(1 for r in rows if r[1] == 0)} of {len(T)}")
    insider = [(t["num"], f"{ts // 60:02d}:{ts % 60:02d}") for t, ts, txt in A
               if t["current"] and re.search(r"\b(we|our|us)\b", txt, re.I) and not any(re.search(rf"\b{c}\b", txt) for c in C)]
    print(f"answers where a currently employed expert says we/our/us without naming a company: {len(insider)} {insider}")


    print("\n== Claim 3: 'PII matters too, but that's usually a simple redaction.'")
    for t, ts, txt in A:
        if people(txt, t):
            print(f"  T{t['num']} {ts // 60:02d}:{ts % 60:02d} person={people(txt, t)} "
                  f"insider source={'yes' if re.search(MARKERS['insider source'], txt) else 'no'}")

    print("\n== Claim 4: 'The flagging tool ... flags every company mention, and reviewers learn to ignore it.'")
    print("not testable: no output from the current tool in the data. Needed: a month of its flags with reviewers' decisions.")


    print("\n== Test cases from the answer key (hidden test set)")
    keys = [json.loads(re.search(r"```json\n(.*?)\n```", b, re.S).group(1)) for b in SRC.read_text().split("\n## Transcript ")[1:]]
    from collections import Counter
    print(f"decisions: {dict(Counter(k['overall_decision'] for k in keys))}")
    iss = [i for k in keys for i in k["issues"]]
    print(f"issues: {len(iss)}; by category: {dict(Counter(i['category'] for i in iss))}")
    hi_cat = {"MNPI", "Current employer confidential", "Declaration conflict"}
    print(f"issues in the three zero-miss types (role-play hypothesis): {sum(i['category'] in hi_cat for i in iss)}")
    print(f"transcripts that must publish untouched (over-flag tests): {[k['transcript'] for k in keys if k['overall_decision'] == 'publish']}")


if __name__ == "__main__":
    main()
