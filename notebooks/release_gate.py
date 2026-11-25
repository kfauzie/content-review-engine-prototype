"""Compare a new version of the review AI with current production, on the same 1,000 reviewed transcripts as the
benchmark (synthetic data). Run from the run folder: python3 notebooks/release_gate.py (build_data.py runs it too and
embeds the result in the page).

The reviewed set: every issue the human reviewers found (262) and every false alarm production raised (187), each in
its own transcript (IDs 0001 to 1000, deterministic). Items with an example in the benchmark (a card) or in the
8-transcript test set point to that transcript; the rest are counts only, as on the benchmark page.

Version outputs are SIMULATED, item by item, by stated rules:
  v1.0  current production: exactly the benchmark (it misses the 23 example misses, raises the 187 false alarms).
  v1.1  reads the expert's declaration and the question.
        On test-set answers: the blind AI reviewer's verdicts (data/eval/ai_verdicts_blind.json), plus two
        over-cautious flags (T5-01:03, T7-00:36).
        Elsewhere: it catches what production caught, and production's misses that depend on context (the declaration,
        "we", "their"). It adds no check for named people, so it still misses production's misses under the
        "named people" fix outside the test set. It clears false alarms about long-ago employers and public market talk
        (the declaration and the question settle them), and keeps those about public sources and the expert's own view.
  v1.2  v1.1 on a cheaper, faster model: the same, except it misses the hedged MNPI hint (T5-01:24).
The scoring is real: eval.funnel compares each version's flags with the human verdicts, item by item.

Ready: zero misses in the high-priority types, and no more misses in the other types than current production.
"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval import TYPES, funnel  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MASKED_TEST_SET = ROOT / "data/eval/test_set_masked.md"
OUT = ROOT / "data/eval/release_gate.json"
VERSIONS_DIR = ROOT / "data/eval/versions"
BASELINE = "v1.0"
N_TRANSCRIPTS = 1000
# benchmark category -> answer-key type (eval.TYPES)
TYPE_OF = {"Material non-public information": "MNPI", "Current-employer confidential": "Current employer confidential",
           "Declaration conflict": "Declaration conflict", "Source disclosure": "Source disclosure",
           "Former-client confidential": "Confidentiality breach", "Personal data": "PII"}
# test-set answers that sit in the reviewed set without a card: (category or false alarm type, benchmark card source of the transcript)
TEST_SET_EXTRA = {"T2-01:39": ("issue", "Material non-public information", "test set T2-01:19"),
                  "T6-01:06": ("issue", "Declaration conflict", "test set T6-01:34"),
                  "T8-00:53": ("issue", "Former-client confidential", "test set T8-01:24"),
                  "T4-02:03": ("false_alarm", "public-source", "test set T4-00:26"),
                  "T5-01:03": ("false_alarm", "own-view", "test set T5-01:24")}
NOTES = {"T2-01:39": "An unannounced acquisition by the expert's listed employer.",
         "T6-01:06": "Continuing contact with the former employer, contrary to the declaration.",
         "T8-00:53": "A former client's confidential information.",
         "T4-02:03": "Refers to figures the company publishes in its annual results.",
         "T5-01:03": "A general, favourable remark about a former employer. No specific or non-public fact."}
V11_EXTRA = {
    "T5-01:03": "Comment on Northwind Biomedical, a listed company the expert left in March 2026 and owes continuing confidentiality to. Flagged as a precaution.",
    "T7-00:36": "Precise margin figures and full-year guidance for Ardent Foods, the expert's listed former employer. The cited source was not verified.",
}
V12_MISS = {"T5-01:24": "General advice to watch the results. No company is named and no figure is given."}
RULE_REASON = {
    ("miss", "people"): "The answer names a person or a source, not company information, and this version does not check for named people.",
    ("fa", "public-source"): "Precise information about a company. The cited public source was not checked.",
    ("fa", "own-view"): "Comment about a named company, treated as possible inside information.",
}
READS_NEW = "Now reads the expert's declaration and the question, not just the answer"
VERSIONS = [
    {"id": "v1.0", "label": "Current production (v1.0)", "status": "Current production", "model": "Meridian Pro",
     "description": "The version in production. Its results are the ones on the Current AI performance page.", "changes": []},
    {"id": "v1.1", "label": "New version: reads the expert's declaration (v1.1)", "status": "New version", "model": "Meridian Pro",
     "description": "Also reads the question and the expert's declaration, so it can tell which company “we”, “us” and “their” refer to.",
     "changes": [["Model", "same (Meridian Pro)", False], ["Reads", READS_NEW, True],
                 ["Instructions", "Now works out which company “we”, “us” and “their” refer to", True],
                 ["Settings", "same", False]]},
    {"id": "v1.2", "label": "New version: cheaper model (v1.2)", "status": "New version", "model": "Meridian Swift",
     "description": "The same as v1.1, on a cheaper and faster model.",
     "changes": [["Model", "Meridian Pro → Meridian Swift", True], ["Reads", "same as v1.1: " + READS_NEW[0].lower() + READS_NEW[1:], True],
                 ["Instructions", "same as v1.1", True], ["Settings", "same", False]]},
]


def build_items(data):
    """One item per human-found issue and per production false alarm, each with a transcript ID."""
    cards = data["cards"]
    by_src = {c["source"]: c for c in cards if c["source"].startswith("test set")}
    ids = random.Random(2026).sample(range(1, N_TRANSCRIPTS + 1), N_TRANSCRIPTS)
    tid_of_key = {}

    def tid(key):
        if key not in tid_of_key:
            tid_of_key[key] = f"{ids[len(tid_of_key)]:04d}"
        return tid_of_key[key]

    for c in sorted(cards, key=lambda c: c["id"]):  # every card's transcript gets an ID first
        c["tid"] = tid(c["transcript"] or c["id"])
    items = []

    def add(kind, cat, prod_flag, key=None, ts=None, aid=None, card=None, fix=None, note=None):
        items.append({"id": f"i{len(items) + 1:03d}", "kind": kind, "cat": cat, "prod": prod_flag,
                      "tid": card["tid"] if card else (tid(key) if key else tid(f"count-{len(items)}")),
                      "key": key, "ts": ts, "aid": aid, "card": card["id"] if card else None, "fix": fix, "note": note})

    for c in data["categories"]:
        missed = [k for k in cards if k["kind"] == "missed" and k["category"] == c["name"]]
        assert len(missed) == c["missed"], c["name"]
        for k in missed:
            add("issue", c["name"], False, k["transcript"], k["ts"], k["source"].split()[-1] if k["source"].startswith("test set") else None, k, k["fix"])
        extra = [(a, v) for a, v in TEST_SET_EXTRA.items() if v[0] == "issue" and v[1] == c["name"]]
        for a, v in extra:
            host = by_src[v[2]]
            add("issue", c["name"], True, host["transcript"], a[3:], a, note=NOTES[a])
        for _ in range(c["found"] - c["missed"] - len(extra)):
            add("issue", c["name"], True)
    for t in data["false_alarm_types"]:
        fa = [k for k in cards if k["kind"] == "false_alarm" and k["fa_type"] == t["id"]]
        for k in fa:
            add("false_alarm", t["id"], True, k["transcript"], k["ts"], k["source"].split()[-1] if k["source"].startswith("test set") else None, k)
        extra = [(a, v) for a, v in TEST_SET_EXTRA.items() if v[0] == "false_alarm" and v[1] == t["id"]]
        for a, v in extra:
            host = by_src[v[2]]
            add("false_alarm", t["id"], True, host["transcript"], a[3:], a, note=NOTES[a])
        for _ in range(t["count"] - len(fa) - len(extra)):
            add("false_alarm", t["id"], True)
    for tr in data["transcripts"].values():
        tr["tid"] = tid_of_key[tr["id"]]
    for f in data["fixes"]:
        for x in f["examples"]:
            x["tid"] = tid_of_key[x["transcript"]]
    return items


def outputs(M, items):
    """SIMULATED outputs per version: item ID -> {flag, reason}."""
    blind = json.loads((ROOT / "data/eval/ai_verdicts_blind.json").read_text())["verdicts"]
    raw_src = (ROOT / "data/synthetic-expert-transcripts.md").read_text()
    ctx = {int(re.match(r"\d+", b).group()): M.context(b) for b in raw_src.split("\n## Transcript ")[1:]}
    v10, v11 = {}, {}
    for it in items:
        v10[it["id"]] = {"flag": it["prod"], "reason": "Flagged." if it["prod"] else "Not flagged."}
        if it["aid"]:
            b = blind[it["aid"]]
            flag = b["verdict"] == "flag" or it["aid"] in V11_EXTRA
            reason = M.text(V11_EXTRA[it["aid"]]) if it["aid"] in V11_EXTRA else M.text(b["reason"], ctx[int(it["aid"][1])])
        elif it["kind"] == "issue":
            flag = it["prod"] or it["fix"] != "people"
            reason = "Flagged." if flag else RULE_REASON[("miss", "people")]
        else:
            flag = it["cat"] in ("public-source", "own-view")
            reason = RULE_REASON[("fa", it["cat"])] if flag else "Not flagged."
        v11[it["id"]] = {"flag": flag, "reason": reason}
    v12 = json.loads(json.dumps(v11))
    for it in items:
        if it["aid"] in V12_MISS:
            v12[it["id"]] = {"flag": False, "reason": V12_MISS[it["aid"]]}
    return {"v1.0": v10, "v1.1": v11, "v1.2": v12}


def human(items):
    return {it["id"]: ({"type": TYPE_OF[it["cat"]], "action": None} if it["kind"] == "issue" else None) for it in items}


def score(out, items, fa_types):
    h = human(items)
    rows, tot = funnel({k: ({"type": None, "action": None} if v["flag"] else None) for k, v in out.items()}, h)
    missed = {x: rows[x]["missed"] for x in TYPES}
    high = [TYPE_OF[c] for c in TYPE_OF if c in HIGH_CATS]
    fa = tot["cleared"]
    cat = {it["id"]: it["cat"] for it in items}
    return {"flags": len(tot["flagged"]), "caught": len(tot["acted"]), "issues": len(tot["human"]), "missed": missed,
            "missed_total": sum(map(len, missed.values())), "missed_high": sum(len(missed[x]) for x in high),
            "false_alarms": fa, "false_alarms_by_type": {t: [a for a in fa if cat[a] == t] for t in fa_types}}


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}es" if word.endswith("s") else f"{n} {word}s"


def gate(s, base):
    other, base_other = s["missed_total"] - s["missed_high"], base["missed_total"] - base["missed_high"]
    if s["missed_high"]:
        return {"passed": False, "headline": "Not ready", "detail": plural(s["missed_high"], "high-priority miss")}
    if other > base_other:
        return {"passed": False, "headline": "Not ready", "detail": "0 high-priority misses, but more lower-priority misses than current production"}
    return {"passed": True, "headline": "Ready", "detail": "0 high-priority misses"}


HIGH_CATS = []


def release_data(M, data):
    HIGH_CATS[:] = [c["name"] for c in data["categories"] if c["priority"] == "high"]
    items = build_items(data)
    outs = outputs(M, items)
    fa_types = [t["id"] for t in data["false_alarm_types"]]
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    for vid, o in outs.items():
        (VERSIONS_DIR / f"{vid}.json").write_text(json.dumps({"version": vid, "note": "SIMULATED outputs on the 1,000 reviewed transcripts.",
                                                               "outputs": o}, indent=1, ensure_ascii=False) + "\n")
    scores = {vid: score(o, items, fa_types) for vid, o in outs.items()}
    base = scores[BASELINE]
    assert base["missed_total"] == sum(c["missed"] for c in data["categories"]) and base["issues"] == sum(c["found"] for c in data["categories"])
    assert {t["id"]: len(base["false_alarms_by_type"][t["id"]]) for t in data["false_alarm_types"]} == {t["id"]: t["count"] for t in data["false_alarm_types"]}
    result = {vid: {**scores[vid], "result": gate(scores[vid], base)} for vid in outs}
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return {"note": "Version outputs are SIMULATED, item by item, on the 1,000 reviewed transcripts. The scoring runs on the page.",
            "baseline": BASELINE, "transcripts": N_TRANSCRIPTS, "high": [TYPE_OF[c] for c in HIGH_CATS],
            "types": [{"id": TYPE_OF[c["name"]], "label": c["name"], "priority": c["priority"]} for c in data["categories"]],
            "fa_types": [{"id": t["id"], "label": t["name"]} for t in data["false_alarm_types"]],
            "items": items, "versions": [{**v, "outputs": outs[v["id"]]} for v in VERSIONS]}


if __name__ == "__main__":
    for vid, r in json.loads(OUT.read_text()).items():
        fa = {k: len(v) for k, v in r["false_alarms_by_type"].items()}
        print(f"{vid}: caught {r['caught']} of {r['issues']}, missed {r['missed_total']} ({r['missed_high']} high), false alarms {len(r['false_alarms'])} {fa} -> {r['result']['headline']}: {r['result']['detail']}")
