"""Release gate for the review agent (synthetic data). Run from the run folder: python3 notebooks/release_gate.py
(build_data.py runs it too and embeds the result in the page).

Three versions of the agent. Their outputs on the 8 test-set transcripts are pre-generated and labelled simulated:
  v1.0  current production. The rule "flag any answer that names a company", run on the masked text (a Company ID).
  v1.1  candidate. The blind AI reviewer's verdicts (data/eval/ai_verdicts_blind.json), reasons masked.
  v1.2  candidate. v1.1 on a cheaper, faster model: the same verdicts, except it clears the hedged MNPI hint (T5-01:24).
The scoring is real: eval.funnel compares each version's flags with the answer key, on the masked test set.

Gate rule: zero misses in MNPI, current-employer confidential and declaration conflict, and no more misses in the
other types than current production (v1.0).
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
HIGH = ["MNPI", "Current employer confidential", "Declaration conflict"]
BASELINE = "v1.0"
# how each answer-key type reads on the page and in a gate message
LABELS = {"MNPI": ("Material non-public information", "MNPI"),
          "Current employer confidential": ("Current-employer confidential", "current-employer confidential"),
          "Declaration conflict": ("Declaration conflict", "a declaration conflict"),
          "Source disclosure": ("Source disclosure", "a source disclosure"),
          "Confidentiality breach": ("Former-client confidential", "former-client confidential"),
          "PII": ("Personal data", "personal data")}
# one short description per answer-key issue, for gate messages and the comparison table
ISSUE_NOTES = {"T2-01:39": "unannounced acquisition at the expert's listed employer",
               "T3-01:34": "unreleased pricing at the expert's current employer",
               "T5-01:24": "hedged hint about a listed company",
               "T6-01:06": "still in touch with former colleagues, against the declaration",
               "T6-01:34": "names a current insider as the source",
               "T8-00:53": "a former client's confidential details",
               "T8-01:24": "a named person's health information"}
VERSIONS = [
    {"id": "v1.0", "status": "Current production",
     "description": "Flags any answer that names a company. Too many false alarms, and misses passages that don't name a company.",
     "model": "Small, fast model", "prompt": "Flag every expert answer that names a company.",
     "settings": "Reads the answer only. No declaration, no question."},
    {"id": "v1.1", "status": "Candidate",
     "description": "Also reads the expert's declaration to work out “we”, “us” and “their”. Fewer false alarms, no misses in the high-priority types.",
     "model": "Large model", "prompt": "Review each answer with the question before it and the expert's declaration. Work out who “we”, “us” and “their” refer to, using the masked IDs and their tags. Flag by issue type and suggest an action.",
     "settings": "Reads the question, the answer and the declaration. Temperature 0."},
    {"id": "v1.2", "status": "Candidate",
     "description": "v1.1 on a cheaper, faster model. Misses one hedged MNPI hint.",
     "model": "Small, fast model", "prompt": "Same as v1.1.",
     "settings": "Reads the question, the answer and the declaration. Temperature 0."},
]
LOG = [{"at": "2026-09-08T10:14", "version": "v1.0", "result": "Released",
        "reason": "First release, before the gate existed. Now the baseline that candidates are compared with.", "by": "Staff 0004"}]


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
    v12 = json.loads(json.dumps(v11))
    v12["T5-01:24"] = {"flag": False, "type": None, "action": None,
                       "reason": "General advice to watch results; no company named and no specific figure."}
    return {"v1.0": v10, "v1.1": v11, "v1.2": v12}


def engine(out):
    return {k: ({"type": v["type"], "action": v["action"]} if v["flag"] else None) for k, v in out.items()}


def score(out, human):
    rows, tot = funnel(engine(out), human)
    return {"flags": len(tot["flagged"]), "right": len(tot["acted"]), "false_alarms": tot["cleared"],
            "missed": {x: rows[x]["missed"] for x in TYPES}, "issues": len(tot["human"])}


def gate(vid, s, base):
    high = sorted((a, x) for x in HIGH for a in s["missed"][x])
    other = sum(len(s["missed"][x]) for x in TYPES if x not in HIGH)
    base_other = sum(len(base["missed"][x]) for x in TYPES if x not in HIGH)
    if high:
        parts = [f"{LABELS[x][1]} in transcript {a[1]} ({ISSUE_NOTES[a]})" for a, x in high]
        return {"passed": False, "message": f"Release gate: blocked. {vid} missed {' and '.join(parts)}.",
                "reason": f"Missed {' and '.join(parts)}.", "links": [a for a, _ in high]}
    if other > base_other:
        miss = sorted(a for x in TYPES if x not in HIGH for a in s["missed"][x])
        return {"passed": False, "message": f"Release gate: blocked. {vid} missed {other} issues in the other types; current production misses {base_other}.",
                "reason": f"Missed {other} issues in the other types; current production misses {base_other}.", "links": miss}
    return {"passed": True, "message": f"Release gate: passed. {vid} can go to shadow mode.",
            "reason": f"No misses in the high-priority types; {other} in the other types (current production: {base_other}).", "links": []}


def run(M):
    T, A, human = load(MASKED_TEST_SET.read_text())
    outs = outputs(M, T, A)
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    for vid, o in outs.items():
        assert set(o) == set(human), vid
        (VERSIONS_DIR / f"{vid}.json").write_text(json.dumps({"version": vid, "note": "SIMULATED outputs on the masked synthetic test set.",
                                                               "outputs": o}, indent=1, ensure_ascii=False) + "\n")
    scores = {vid: score(o, human) for vid, o in outs.items()}
    result = {vid: {**scores[vid], "gate": gate(vid, scores[vid], scores[BASELINE])} for vid in outs}
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return T, A, human, outs, result


def release_data(M, tset, listed, topics):
    from mask import tags_for
    T, A, human, outs, result = run(M)
    transcripts = {}
    for n, t in sorted(tset.items()):
        transcripts[str(n)] = {"num": n, "topic": topics[n], "profile": t["profile"], "declaration": t["declaration"],
                               "turns": [{"ts": f"{s // 60:02d}:{s % 60:02d}", "speaker": w, "text": x} for s, w, x in t["turns"]],
                               "entities": tags_for(t["profile"], t["declaration"], " ".join(x for _, _, x in t["turns"]), listed)}
    return {"note": "Agent outputs are SIMULATED (pre-generated on the masked synthetic test set). The scoring runs on the page.",
            "baseline": BASELINE, "high": HIGH, "types": [{"id": x, "label": LABELS[x][0], "short": LABELS[x][1], "high": x in HIGH} for x in TYPES],
            "issue_notes": ISSUE_NOTES, "answer_key": {k: v for k, v in human.items() if v}, "answers": sorted(human),
            "versions": [{**v, "outputs": outs[v["id"]]} for v in VERSIONS], "log": LOG, "transcripts": transcripts}


if __name__ == "__main__":
    from mask import Masker, VAULT_PATH
    *_, result = run(Masker(json.loads(VAULT_PATH.read_text())))
    for vid, r in result.items():
        miss = {x: m for x, m in r["missed"].items() if m}
        print(f"{vid}: flags {r['flags']}, right {r['right']}, false alarms {len(r['false_alarms'])}, missed {miss}\n  {r['gate']['message']}")
