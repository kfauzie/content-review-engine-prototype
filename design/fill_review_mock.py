"""Fill the transcript panel of design/1-review.html from the data, so every quote is verbatim.
Run from the run folder: python3 design/fill_review_mock.py"""
import html, json, re, sys
from pathlib import Path
sys.path.insert(0, "notebooks")
from eval import load, aid  # noqa: E402

NAMES = {"MNPI": "Material non-public information", "Current employer confidential": "Current-employer confidential",
         "Declaration conflict": "Declaration conflict", "Source disclosure": "Source disclosure",
         "Confidentiality breach": "Confidentiality breach", "PII": "Personal data"}
ACTS = {"redact": "Redact", "escalate to human": "Escalate", "reject whole transcript": "Reject whole transcript"}
N = 5


def main():
    T, A, human = load()
    ai = json.loads(Path("data/eval/ai_verdicts_blind.json").read_text())["verdicts"]
    text = Path("data/synthetic-expert-transcripts.md").read_text()
    key = json.loads(re.search(r"```json\n(.*?)\n```", text.split("\n## Transcript ")[N], re.S).group(1))
    notes = {f"T{N}-{i['timestamp']}": i["rationale"] for i in key["issues"]}
    t = next(x for x in T if x["num"] == N)
    out = []
    for ts, who, txt in t["turns"]:
        stamp = f"{ts // 60:02d}:{ts % 60:02d}"
        if who != "EXPERT":
            out.append(f'<div class="turn q"><span class="ts">{stamp}</span>Interviewer: {html.escape(txt)}</div>')
            continue
        a, v, h = aid(t, ts), ai[aid(t, ts)], human[aid(t, ts)]
        body = html.escape(txt)
        if v["verdict"] == "flag":
            for q in re.findall(r"'([^']+)'", v["reason"]):
                q = q.replace("...", "").strip()
                if html.escape(q) in body:
                    body = body.replace(html.escape(q), f'<mark class="q">{html.escape(q)}</mark>', 1)
            other = ", ".join(NAMES[o] for o in v.get("other_types", []))
            out.append(f'''<div class="turn a flagged"><div class="txt"><span class="ts">{stamp}</span>{body}</div>
    <div class="verd"><div class="col ai"><div class="who">AI flagged</div><div class="dec">{NAMES[v["type"]]} · {ACTS[v["action"]]}</div><div class="why">{html.escape(v["reason"])}</div>{f'<div class="also">Also listed: {other}</div>' if other else ''}</div>
    <div class="col human"><div class="who">Human verdict</div><div class="dec">{NAMES[h["type"]] + " · " + ACTS[h["action"]] if h else "Cleared"}</div>{f'<div class="why">{html.escape(notes[a])}</div>' if a in notes else ''}</div></div>
    <div class="outcome">{'<span class="pill agree">Rightly flagged</span>' if h else '<span class="pill alarm">False alarm</span>'}{f'<span class="pill note">Action differs: AI chose {ACTS[v["action"]].lower()}, human chose {ACTS[h["action"]].lower()}</span>' if h and h["action"] != v["action"] else ''}</div></div>''')
        else:
            badge = '<span class="pill miss">Missed by AI</span>' if h else '<span class="pill agree">Both cleared</span>'
            out.append(f'<div class="turn a"><div class="txt"><span class="ts">{stamp}</span>{body}</div><div class="clearline"><b>AI cleared</b><span>{html.escape(v["reason"])}</span>{badge}</div></div>')
    n_ans = sum(1 for _, w, _ in t["turns"] if w == "EXPERT")
    p = Path("design/1-review.html"); s = p.read_text()
    s = re.sub(r"<!--TURNS-->.*<!--/TURNS-->", "<!--TURNS-->\n" + "\n".join(out) + "\n<!--/TURNS-->", s, flags=re.S)
    s = re.sub(r"Transcript 5 · Sanjay Mehta · \d+ expert answers", f"Transcript 5 · Sanjay Mehta · {n_ans} expert answers", s)
    p.write_text(s)
    print(f"filled {len(out)} turns, {n_ans} expert answers")


if __name__ == "__main__":
    main()
