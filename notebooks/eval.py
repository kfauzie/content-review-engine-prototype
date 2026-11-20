"""Eval: score an engine's flags against the human verdict, as a funnel per issue type.
Run from the run folder: python3 notebooks/eval.py

Runs:
  1. Blind AI reviewer: data/eval/ai_verdicts_blind.json, written by a subagent that saw only
     data/eval/blind_input.md (no answer keys, no transcript titles).
  2. Rules baseline: flags every answer that names a company. Made up, to show what misses look like; not a
     model of Dialectica's tool.

Human verdict: the test set's answer key (8 synthetic transcripts). Some "misses" in real data will be the human
over-redacting; the drill-down lets a reviewer mark those.

Funnel per issue type X, over every passage with a human verdict:
  AI flagged as X -> human acted on it (rightly flagged) | human cleared it (false alarm)
  Missed by AI: the human acted on it as X, and the AI didn't flag the passage at all.
  Flagged under another type: the human acted on it as X, and the AI flagged it as a different type.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_review import SRC, parse  # noqa: E402
from synthesis import companies  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TYPES = ["MNPI", "Current employer confidential", "Declaration conflict", "Source disclosure", "Confidentiality breach", "PII"]


def aid(t, ts):
    return f"T{t['num']}-{ts // 60:02d}:{ts % 60:02d}"


def load():
    text = SRC.read_text()
    T = parse(text)
    keys = {int(re.match(r"\d+", b).group()): json.loads(re.search(r"```json\n(.*?)\n```", b, re.S).group(1))
            for b in text.split("\n## Transcript ")[1:]}
    A = [(t, ts, txt) for t in T for ts, who, txt in t["turns"] if who == "EXPERT"]
    human = {aid(t, ts): None for t, ts, _ in A}
    for n, k in keys.items():
        for i in k["issues"]:
            human[f"T{n}-{i['timestamp']}"] = {"type": i["category"], "action": i["expected_action"]}
    return T, A, human


def runs(T, A):
    blind = json.loads((ROOT / "data/eval/ai_verdicts_blind.json").read_text())["verdicts"]
    ai = {k: ({"type": v["type"], "action": v["action"]} if v["verdict"] == "flag" else None) for k, v in blind.items()}
    C = companies(T)
    rules = {aid(t, ts): ({"type": None, "action": None} if any(re.search(rf"\b{c}\b", txt) for c in C) else None)
             for t, ts, txt in A}
    return {"Blind AI reviewer": ai, "Rules baseline (flags company names)": rules}


def funnel(engine, human):
    rows = {}
    for x in TYPES:
        flagged = [a for a, v in engine.items() if v and v["type"] == x]
        rows[x] = dict(flagged=flagged,
                       acted=[a for a in flagged if human[a]],
                       cleared=[a for a in flagged if not human[a]],
                       missed=[a for a, h in human.items() if h and h["type"] == x and not engine[a]],
                       other=[a for a, h in human.items() if h and h["type"] == x and engine[a] and engine[a]["type"] != x],
                       human=[a for a, h in human.items() if h and h["type"] == x])
    allflags = [a for a, v in engine.items() if v]
    return rows, dict(reviewed=len(human), flagged=allflags,
                      acted=[a for a in allflags if human[a]], cleared=[a for a in allflags if not human[a]],
                      missed=[a for a, h in human.items() if h and not engine[a]],
                      human=[a for a, h in human.items() if h])


def main():
    T, A, human = load()
    blind = json.loads((ROOT / "data/eval/ai_verdicts_blind.json").read_text())["verdicts"]
    for name, engine in runs(T, A).items():
        assert set(engine) == set(human), f"{name}: every answer needs a verdict"
        rows, tot = funnel(engine, human)
        print(f"\n== {name}")
        print(f"passages reviewed by a human: {tot['reviewed']}; human acted on: {len(tot['human'])}")
        print(f"AI flagged {len(tot['flagged'])} -> human acted on {len(tot['acted'])} (rightly flagged), "
              f"cleared {len(tot['cleared'])} (false alarm)")
        print(f"missed by AI: {len(tot['missed'])} of {len(tot['human'])} the human acted on {tot['missed']}")
        print(f"false alarms: {tot['cleared']}")
        print("  by issue type: AI flagged -> acted / cleared | missed by AI | flagged under another type")
        for x, r in rows.items():
            print(f"    {x}: {len(r['flagged'])} -> {len(r['acted'])} / {len(r['cleared'])} | {len(r['missed'])} | {len(r['other'])}")
        typed = [a for a in tot["acted"] if engine[a]["type"]]
        if typed:
            same = [a for a in typed if engine[a]["action"] == human[a]["action"]]
            diff = {a: f"AI {engine[a]['action']} / human {human[a]['action']}" for a in typed if a not in same}
            print(f"same action as the human: {len(same)} of {len(typed)}; differs: {diff}")
            print(f"other types the AI listed: { {a: blind[a].get('other_types') for a in typed if blind[a].get('other_types')} }")


if __name__ == "__main__":
    main()
