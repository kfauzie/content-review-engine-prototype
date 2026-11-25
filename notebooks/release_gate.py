"""Test a new version of the review AI against current production (synthetic data).
Run from the run folder: python3 notebooks/release_gate.py (build_data.py runs it too and embeds the result in the page).

Three versions. Their outputs on the 8 test-set transcripts are pre-generated and labelled simulated:
  v1.0  current production. The rule "flag any answer that names a company", run on the masked text (a Company ID).
  v1.1  reads the expert's declaration. The blind AI reviewer's verdicts (data/eval/ai_verdicts_blind.json), plus two
        over-cautious flags on clean answers, so the simulation reflects a realistic run rather than a perfect one.
  v1.2  v1.1 on a cheaper, faster model: the same outputs, except it clears the hedged MNPI hint (T5-01:24).
The scoring is real: eval.funnel compares each version's flags with the answer key, on the masked test set. False
alarms are grouped by why the answer was clean, from data/eval/clean_answers.json (a reviewer note per clean answer
that any version flags; the scoring fails if one is missing).

Rule for moving forward: zero misses in the high-priority types, and no more misses in the other types than
current production (v1.0).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval import TYPES, funnel, load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MASKED_TEST_SET = ROOT / "data/eval/test_set_masked.md"
OUT = ROOT / "data/eval/release_gate.json"
VERSIONS_DIR = ROOT / "data/eval/versions"
CLEAN = ROOT / "data/eval/clean_answers.json"
BASELINE = "v1.0"
# answer-key type -> page label, short form for a result line, priority (matches the benchmark's categories)
TYPE_INFO = {"MNPI": ("Material non-public information", "MNPI", "high"),
             "Current employer confidential": ("Current-employer confidential", "current-employer confidential", "high"),
             "Declaration conflict": ("Declaration conflict", "a declaration conflict", "high"),
             "Source disclosure": ("Source disclosure", "a source disclosure", "medium"),
             "Confidentiality breach": ("Former-client confidential", "former-client confidential", "low"),
             "PII": ("Personal data", "personal data", "medium")}
HIGH = [x for x in TYPES if TYPE_INFO[x][2] == "high"]
# one short description per answer-key issue, for result lines and the log
ISSUE_NOTES = {"T2-01:39": "an unannounced acquisition by the expert's listed employer",
               "T3-01:34": "unannounced pricing at the expert's current employer",
               "T5-01:24": "a hedged hint about a listed company",
               "T6-01:06": "continuing contact with the former employer, contrary to the declaration",
               "T6-01:34": "a current insider named as the source",
               "T8-00:53": "a former client's confidential information",
               "T8-01:24": "a named individual's health information"}
# model names are fictional
MODELS_NOTE = ("Meridian Pro: more careful with subtle cases, slower and costs more. "
               "Meridian Swift: faster and cheaper, more likely to miss subtle hints.")
READS_NEW = "Now reads the expert's declaration and the question, not just the answer"
VERSIONS = [
    {"id": "v1.0", "label": "Current production (v1.0)", "status": "Current production", "model": "Meridian Pro",
     "description": "Flags every answer that names a company. It raises many false alarms, and misses answers that refer to a company without naming it.",
     "changes": []},
    {"id": "v1.1", "label": "New version: reads the expert's declaration (v1.1)", "status": "New version", "model": "Meridian Pro",
     "description": "Also reads the question and the expert's declaration, so it can tell which company \u201cwe\u201d, \u201cus\u201d and \u201ctheir\u201d refer to.",
     "changes": [["Model", "same (Meridian Pro)", False], ["Reads", READS_NEW, True],
                 ["Instructions", "Now works out which company \u201cwe\u201d, \u201cus\u201d and \u201ctheir\u201d refer to, and flags by issue type", True],
                 ["Settings", "same", False]]},
    {"id": "v1.2", "label": "New version: cheaper model (v1.2)", "status": "New version", "model": "Meridian Swift",
     "description": "The same instructions as v1.1, on a cheaper and faster model.",
     "changes": [["Model", "Meridian Pro \u2192 Meridian Swift", True], ["Reads", READS_NEW, True],
                 ["Instructions", "as v1.1: works out which company \u201cwe\u201d, \u201cus\u201d and \u201ctheir\u201d refer to, and flags by issue type", True],
                 ["Settings", "same", False]]},
]
# simulated over-cautious flags by v1.1 (and so v1.2) on answers the answer key treats as clean
V11_EXTRA = {
    "T5-01:03": {"type": "Confidentiality breach", "action": "escalate to human",
                 "reason": "Comment on Northwind Biomedical, a listed company the expert left in March 2026 and owes continuing confidentiality to. Flagged as a precaution."},
    "T7-00:36": {"type": "MNPI", "action": "escalate to human",
                 "reason": "Precise margin figures and full-year guidance for Ardent Foods, the expert's listed former employer. The cited source was not verified."},
}


def outputs(M, T, A):
    """Pre-generated (simulated) outputs per version: answer ID -> {flag, type, action, reason}."""
    aid = lambda t, s: f"T{t['num']}-{s // 60:02d}:{s % 60:02d}"  # noqa: E731
    v10 = {}
    for t, s, txt in A:
        hit = re.findall(r"Company \d{4}", txt)
        v10[aid(t, s)] = ({"flag": True, "type": None, "action": "escalate to human", "reason": f"Names {hit[0]}."} if hit
                          else {"flag": False, "type": None, "action": None, "reason": "No company named."})
    blind = json.loads((ROOT / "data/eval/ai_verdicts_blind.json").read_text())["verdicts"]
    raw_src = (ROOT / "data/synthetic-expert-transcripts.md").read_text()
    ctx = {int(re.match(r"\d+", b).group()): M.context(b) for b in raw_src.split("\n## Transcript ")[1:]}
    v11 = {k: {"flag": v["verdict"] == "flag", "type": v["type"] if v["verdict"] == "flag" else None,
               "action": v["action"] if v["verdict"] == "flag" else None,
               "reason": M.text(v["reason"], ctx[int(k[1])])} for k, v in blind.items()}
    for k, v in V11_EXTRA.items():
        assert not v11[k]["flag"], k
        v11[k] = {"flag": True, **v, "reason": M.text(v["reason"])}
    v12 = json.loads(json.dumps(v11))
    v12["T5-01:24"] = {"flag": False, "type": None, "action": None,
                       "reason": "General advice to watch the results. No company is named and no figure is given."}
    return {"v1.0": v10, "v1.1": v11, "v1.2": v12}


def engine(out):
    return {k: ({"type": v["type"], "action": v["action"]} if v["flag"] else None) for k, v in out.items()}


def score(out, human, clean):
    rows, tot = funnel(engine(out), human)
    missed = {x: rows[x]["missed"] for x in TYPES}
    fa = tot["cleared"]
    missing = [a for a in fa if a not in clean["answers"]]
    assert not missing, f"flagged clean answers without a reviewer note: {missing}"
    return {"flags": len(tot["flagged"]), "caught": len(tot["acted"]), "issues": len(tot["human"]), "missed": missed,
            "missed_total": sum(map(len, missed.values())), "missed_high": sum(len(missed[x]) for x in HIGH),
            "false_alarms": fa, "false_alarms_by_type": {t["id"]: [a for a in fa if clean["answers"][a]["type"] == t["id"]] for t in clean["types"]}}


def gate(s, base):
    high = sorted((a, x) for x in HIGH for a in s["missed"][x])
    other, base_other = s["missed_total"] - s["missed_high"], base["missed_total"] - base["missed_high"]
    if high:
        short = " and ".join(f"{TYPE_INFO[x][1]} in transcript {a[1]}" for a, x in high)
        detail = " and ".join(f"{TYPE_INFO[x][1]} in transcript {a[1]} ({ISSUE_NOTES[a]})" for a, x in high)
        return {"passed": False, "headline": f"Not ready: missed {short}", "reason": f"Missed {detail}.", "links": [a for a, _ in high]}
    if other > base_other:
        miss = sorted(a for x in TYPES if x not in HIGH for a in s["missed"][x])
        line = f"missed {other} medium- or low-priority issues; current production missed {base_other}"
        return {"passed": False, "headline": f"Not ready: {line}", "reason": line[0].upper() + line[1:] + ".", "links": miss}
    return {"passed": True, "headline": "Ready for shadow testing",
            "reason": f"Missed nothing high priority; missed {other} other issues (current production missed {base_other}).", "links": []}


def run(M):
    T, A, human = load(MASKED_TEST_SET.read_text())
    clean = json.loads(CLEAN.read_text())
    outs = outputs(M, T, A)
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    for vid, o in outs.items():
        assert set(o) == set(human), vid
        (VERSIONS_DIR / f"{vid}.json").write_text(json.dumps({"version": vid, "note": "SIMULATED outputs on the masked synthetic test set.",
                                                               "outputs": o}, indent=1, ensure_ascii=False) + "\n")
    scores = {vid: score(o, human, clean) for vid, o in outs.items()}
    result = {vid: {**scores[vid], "result": gate(scores[vid], scores[BASELINE])} for vid in outs}
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return T, A, human, outs, result, clean


def release_data(M, tset, listed, topics):
    from mask import tags_for
    T, A, human, outs, result, clean = run(M)
    transcripts = {}
    for n, t in sorted(tset.items()):
        transcripts[str(n)] = {"num": n, "topic": topics[n], "profile": t["profile"], "declaration": t["declaration"],
                               "turns": [{"ts": f"{s // 60:02d}:{s % 60:02d}", "speaker": w, "text": x} for s, w, x in t["turns"]],
                               "entities": tags_for(t["profile"], t["declaration"], " ".join(x for _, _, x in t["turns"]), listed)}
    return {"note": "Version outputs are SIMULATED (pre-generated on the masked synthetic test set). The scoring runs on the page.",
            "baseline": BASELINE, "high": HIGH,
            "types": [{"id": x, "label": TYPE_INFO[x][0], "short": TYPE_INFO[x][1], "priority": TYPE_INFO[x][2], "high": x in HIGH} for x in TYPES],
            "issue_notes": ISSUE_NOTES, "answer_key": {k: v for k, v in human.items() if v}, "answers": sorted(human),
            "clean": clean, "models_note": MODELS_NOTE, "versions": [{**v, "outputs": outs[v["id"]]} for v in VERSIONS], "transcripts": transcripts}


if __name__ == "__main__":
    from mask import Masker, VAULT_PATH
    *_, result, _ = run(Masker(json.loads(VAULT_PATH.read_text())))
    for vid, r in result.items():
        fa = {k: len(v) for k, v in r["false_alarms_by_type"].items()}
        print(f"{vid}: caught {r['caught']} of {r['issues']}, missed {r['missed_total']} ({r['missed_high']} high), false alarms {len(r['false_alarms'])} {fa}\n  {r['result']['headline']}")
