"""Eval dry run: compare engine flags with the answer key, per expert answer and by issue type.
Run from the run folder: python3 notebooks/eval.py

Engines compared:
  1. Current tool (stand-in): flags every expert answer that names a company. Built from the role-play
     description ("it flags every company mention"), not from the real tool.
  2. Declaration-aware AI reviewer: data/eval/ai_reviewer_verdicts.json. NOT BLIND (see its caveat).

Truth: the answer key. In a real eval the truth is reviewers' verdicts, with disagreements adjudicated by a senior
reviewer or Legal, which adds a fourth outcome (the human missed it). The answer key has no separate human verdict,
so that column can't be filled here.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_review import SRC, parse  # noqa: E402
from synthesis import companies  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HIGH = ["MNPI", "Current employer confidential", "Declaration conflict"]
TYPES = HIGH + ["Source disclosure", "Confidentiality breach", "PII"]
RANK = ["publish", "publish with redactions", "escalate", "reject"]
ACTION_TO_DECISION = {"redact": "publish with redactions", "escalate to human": "escalate", "reject whole transcript": "reject"}


def aid(t, ts):
    return f"T{t['num']}-{ts // 60:02d}:{ts % 60:02d}"


def main():
    text = SRC.read_text()
    T = parse(text)
    keys = {int(re.match(r"\d+", b).group()): json.loads(re.search(r"```json\n(.*?)\n```", b, re.S).group(1))
            for b in text.split("\n## Transcript ")[1:]}
    A = [(t, ts, txt) for t in T for ts, who, txt in t["turns"] if who == "EXPERT"]
    truth = {f"T{n}-{i['timestamp']}": i for n, k in keys.items() for i in k["issues"]}
    C = companies(T)

    current = {aid(t, ts): any(re.search(rf"\b{c}\b", txt) for c in C) for t, ts, txt in A}
    R = json.loads((ROOT / "data/eval/ai_reviewer_verdicts.json").read_text())["verdicts"]
    reviewer = {k: v["verdict"] == "flag" for k, v in R.items()}
    assert set(reviewer) == set(current), "every expert answer needs a verdict"

    print(f"expert answers: {len(A)}; answers with an issue in the answer key: {len(truth)}")
    results = {}
    for name, flags in [("Current tool (stand-in)", current), ("Declaration-aware reviewer (not blind)", reviewer)]:
        tp = [a for a in flags if flags[a] and a in truth]
        fp = [a for a in flags if flags[a] and a not in truth]
        fn = [a for a in flags if not flags[a] and a in truth]
        results[name] = dict(tp=tp, fp=fp, fn=fn)
        print(f"\n== {name}")
        print(f"flagged {len(tp) + len(fp)} of {len(A)}: rightly flagged {len(tp)}, false alarms {len(fp)}, missed {len(fn)}")
        print(f"  false alarms: {fp}")
        print(f"  missed: {fn}")
        print("  by issue type (rightly flagged / missed):")
        for ty in TYPES:
            ids = [a for a, i in truth.items() if i["category"] == ty]
            got = [a for a in ids if flags[a]]
            print(f"    {ty}: {len(got)} / {len(ids) - len(got)} {'(zero-miss type)' if ty in HIGH else ''}")
        hm = [a for a in fn if truth[a]["category"] in HIGH]
        print(f"  misses in the three zero-miss types: {len(hm)} {hm}")

    print("\n== Reviewer: issue type labels and transcript decisions")
    label_ok = [a for a, i in truth.items() if R[a]["verdict"] == "flag" and i["category"] in R[a]["types"]]
    print(f"right issue type on flagged issues: {len(label_ok)} of {len(truth)}")
    extra = {a: [x for x in R[a].get('types', []) if x != truth.get(a, {}).get('category')] for a in R if R[a]["verdict"] == "flag"}
    print(f"extra labels on rightly flagged answers: { {a: x for a, x in extra.items() if x} }")
    dec_ok = 0
    for n, k in keys.items():
        acts = [ACTION_TO_DECISION[R[a]["action"]] for a in R if a.startswith(f"T{n}-") and R[a]["verdict"] == "flag"]
        d = max(acts, key=RANK.index) if acts else "publish"
        dec_ok += d == k["overall_decision"]
        if d != k["overall_decision"]:
            print(f"  T{n}: reviewer {d}, answer key {k['overall_decision']}")
    print(f"transcript decisions matching the answer key: {dec_ok} of {len(keys)}")

    print("\n== Failure analysis: current tool (stand-in)")
    cur = results["Current tool (stand-in)"]
    by_ts = {aid(t, ts): (t, txt) for t, ts, txt in A}
    for a in cur["fn"]:
        t, txt = by_ts[a]
        voice = re.findall(r"\b(us|we|our|their|there)\b", txt, re.I)
        print(f"  missed {a} [{truth[a]['category']}]: names no company; points at it with {sorted(set(w.lower() for w in voice))}")
    cause_fp = Counter()
    for a in cur["fp"]:
        t, txt = by_ts[a]
        own = any(re.search(rf"\b{e}\b", txt) for e in t["employers"])
        public = bool(re.search(r"investor day|filings|annual results|earnings call|Publicly|reports in", txt))
        cause = ("own former employer, public source cited" if own and public else
                 "own former employer, expert declines to go further" if own else
                 "another company, framed as public talk" if public else "another company")
        cause_fp[cause] += 1
        print(f"  false alarm {a}: {cause}")
    print(f"false alarms by cause: {dict(cause_fp)}")

    print("\n== Sizing the live test: zero misses in n real issues of a type bounds the miss rate below 3/n (95% confidence)")
    for rate in (0.05, 0.02, 0.01):
        print(f"  to show a miss rate below {rate:.0%}: at least {int(3 / rate)} issues of that type, all caught")


if __name__ == "__main__":
    main()
