"""Write the scorecard mockups from the eval code, so every number and quote matches the data.
  design/2-scorecard.html: blind AI reviewer run, drill-down on Material non-public information, AI flagged
  design/3-scorecard-misses.html: rules baseline run (made up), drill-down on missed by AI, with root cause
Run from the run folder: python3 design/fill_scorecard_mock.py"""
import html, json, re, sys
from pathlib import Path
sys.path.insert(0, "notebooks"); sys.path.insert(0, "design")
from eval import load, runs, funnel, TYPES  # noqa: E402
from fill_review_mock import NAMES, ACTS  # noqa: E402  (import has no side effects)

T, A, human = load()
R = runs(T, A)
blind = json.loads(Path("data/eval/ai_verdicts_blind.json").read_text())["verdicts"]
src = Path("data/synthetic-expert-transcripts.md").read_text()
TOPIC = {int(n): tp for n, tp in re.findall(r"^\| (\d) \| ([^|]+?) \|", src, re.M)}
TX = {f"T{t['num']}-{ts // 60:02d}:{ts % 60:02d}": (t, txt) for t, ts, txt in A}
NOTES = {}
for b in src.split("\n## Transcript ")[1:]:
    k = json.loads(re.search(r"```json\n(.*?)\n```", b, re.S).group(1))
    for i in k["issues"]:
        NOTES[f"T{k['transcript']}-{i['timestamp']}"] = i["rationale"]
TOP = Path("design/1-review.html").read_text().split('<div class="top">')[1].split("</div>\n<main>")[0]
TOP = TOP.replace('<div class="step on"><b>1</b>Review screen</div><div class="step"><b>2</b>Scorecard</div>',
                  '<div class="step"><b>1</b>Review screen</div><div class="step on"><b>2</b>Scorecard</div>')
CSS = """
.runbar{display:flex;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.runbar .muted{color:var(--muted)}
.errs{display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:8px}
.err{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
.err.miss{border-top:4px solid var(--miss)} .err.alarm{border-top:3px solid var(--alarm)}
.err .lab{font-weight:600} .err .def{color:var(--muted);font-size:13px}
.err.miss .big{font-size:40px;font-weight:700;color:var(--miss);letter-spacing:-.5px;margin:4px 0 0}
.err.alarm .big{font-size:26px;font-weight:700;color:var(--alarm);margin:4px 0 0}
.err .big small{font-size:15px;font-weight:500;color:var(--muted);letter-spacing:0}
.flow{color:var(--muted);font-size:14px;margin:0 0 14px}
.errs{margin-bottom:24px!important}
.flow b{color:var(--ink);font-weight:600}
.grid{display:grid;grid-template-columns:1.15fr 1fr;gap:18px;align-items:start}
table{width:100%;border-collapse:collapse}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}
th{font-size:12px;font-weight:600;color:var(--muted);background:var(--soft);vertical-align:bottom}
th.grp{text-align:center;font-size:11px;letter-spacing:.3px;text-transform:uppercase;border-bottom:0;padding-bottom:2px}
th.grp.miss{color:var(--miss)} th.grp.alarm{color:var(--alarm)}
td:first-child,th:first-child{text-align:left}
td.m,th.m{background:var(--miss-tint)} td.m{font-weight:700;color:var(--miss)}
td.cnt{color:var(--ink);text-decoration:underline;text-decoration-color:var(--line);text-underline-offset:3px}
td.on{outline:2px solid var(--ink);outline-offset:-2px}
tr.base td{color:var(--muted);font-size:13px} tr.total td{font-weight:600;background:var(--soft);border-bottom:0}
.under{padding:10px 12px;font-size:13px;color:var(--muted);border-top:1px solid var(--line)}
.dd .ddh{padding:12px 14px;border-bottom:1px solid var(--line)} .dd .ddh b{display:block;font-size:15px}
.dd .ddh span{color:var(--muted);font-size:13px}
.p{padding:12px 14px;border-bottom:1px solid var(--line);font-size:13px}
.p:last-child{border-bottom:0}
.p .where{font-weight:600;margin-bottom:4px} .p .where span{color:var(--muted);font-weight:400}
.p .quote{margin:0 0 8px;color:var(--ink)}
.p dl{display:grid;grid-template-columns:96px 1fr;gap:4px 10px;margin:0}
.p dt{color:var(--muted)} .p dd{margin:0}
.p .row{display:flex;gap:10px;align-items:center;margin-top:8px;flex-wrap:wrap}
.check{display:inline-flex;gap:6px;align-items:center;color:var(--note)}
.check i{width:14px;height:14px;border:1.5px solid var(--faint);border-radius:3px;display:inline-block}
"""

def n(x): return len(x)

def page(run, dd_title, dd_sub, dd_ids, misses_mode, sel_cell):
    eng = R[run]; rows, tot = funnel(eng, human)
    typed = any(v and v["type"] for v in eng.values())
    def cell(cls, val, key):
        return f'<td class="{cls}{" on" if key == sel_cell else ""}">{val}</td>'
    body = []
    for x in TYPES:
        r = rows[x]
        f = [cell("cnt", n(r["flagged"]), (x, "flagged")), cell("cnt", n(r["acted"]), (x, "acted")), cell("cnt", n(r["cleared"]), (x, "cleared"))] if typed \
            else ['<td colspan="3" style="color:var(--faint);text-align:center">Flags have no type</td>']
        body.append(f'<tr><td>{NAMES[x]}</td>{cell("cnt", n(r["human"]), (x, "human"))}{cell("m cnt", n(r["missed"]), (x, "missed"))}{"".join(f)}</tr>')
    body.append(f'<tr class="total"><td>All types</td><td>{n(tot["human"])}</td>{cell("m cnt", n(tot["missed"]), ("all", "missed"))}'
                f'<td>{n(tot["flagged"])}</td><td>{n(tot["acted"])}</td><td>{n(tot["cleared"])}</td></tr>')
    under = ""
    if typed:
        same = [a for a in tot["acted"] if eng[a]["action"] == human[a]["action"]]
        under = f'<div class="under">Same action as the human on {n(same)} of the {n(tot["acted"])} rightly flagged passages. {n(tot["acted"]) - n(same)} differ, shown in the review screen.</div>'
    items = []
    for a in dd_ids:
        t, txt = TX[a]; h = human[a]; v = blind[a] if typed else None
        quote = html.escape(txt)
        ai_line = (f'{NAMES[v["type"]]} · {ACTS[v["action"]]}. {html.escape(v["reason"])}' if v and v["verdict"] == "flag"
                   else ("Flagged: names a company" if eng[a] else "Not flagged"))
        hv = f'{NAMES[h["type"]]} · {ACTS[h["action"]]}' if h else "Cleared"
        extra = ""
        if misses_mode:
            rc = {"T3-01:34": "No company named: expert says “us”", "T5-01:24": "No company named: “their”, “there”"}.get(a, "Not set yet")
            extra = f'<div class="row"><span class="muted" style="color:var(--muted)">Root cause</span><span class="sel" style="min-width:260px">{rc}</span><span class="check"><i></i>Human over-redacted: not a real miss</span></div>'
        items.append(f'''<div class="p"><div class="where">{TOPIC[t["num"]]} <span>· Transcript {t["num"]} · {a.split("-")[1]}</span></div>
<p class="quote">“{quote}”</p><dl><dt>Declaration</dt><dd>{html.escape(t["declaration"])}</dd>
<dt>Human verdict</dt><dd>{hv}{(". " + html.escape(NOTES[a])) if a in NOTES else ""}</dd><dt>AI</dt><dd>{ai_line}</dd></dl>{extra}</div>''')
    runlabel = "Blind AI reviewer" if typed else "Rules baseline: flags company names (made up)"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scorecard (design)</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="design.css"><style>{CSS}</style></head><body>
<div class="top">{TOP}</div>
<main>
<dl class="head"><dt>Customer</dt><dd>Dialectica Legal &amp; Compliance</dd>
<dt>User</dt><dd>Whoever decides the AI is ready to run <i style="color:var(--muted);font-weight:400">(to confirm who)</i></dd>
<dt>Job to be done</dt><dd>Judge, issue type by issue type, whether the AI is good enough to run</dd></dl>
<div class="notice">8 synthetic transcripts. Human verdicts here are the test set's answer key, so some misses in real data will be the human over-redacting: mark those in the drill-down.</div>
<div class="runbar"><span class="muted">Run</span><span class="sel" style="min-width:330px">{runlabel}</span></div>
<p class="flow lead"><b>{tot["reviewed"]}</b> passages reviewed by a human → AI flagged <b>{n(tot["flagged"])}</b> → human acted on <b>{n(tot["acted"])}</b>, cleared <b>{n(tot["cleared"])}</b></p>
<div class="errs">
<div class="err miss"><div class="lab">Missed by AI</div><div class="big">{n(tot["missed"])} <small>of {n(tot["human"])} passages the human acted on</small></div><div class="def">The human acted on it, and the AI didn't flag it.</div></div>
<div class="err alarm"><div class="lab">False alarms</div><div class="big">{n(tot["cleared"])} <small>of {n(tot["flagged"])} AI flags</small></div><div class="def">The AI flagged it, and the human cleared it.</div></div>
</div>

<div class="grid">
<div><h2>By issue type</h2><p class="sub">Every count opens the passages behind it.</p>
<div class="panel"><table><thead>
<tr><th></th><th colspan="2" class="grp miss">Misses</th><th colspan="3" class="grp alarm">False alarms</th></tr>
<tr><th>Issue type</th><th>Human acted on</th><th class="m">Missed by AI</th><th>AI flagged</th><th>Human acted on</th><th>Human cleared</th></tr>
</thead><tbody>{"".join(body)}</tbody></table>{under}</div></div>
<div><h2>{dd_title}</h2><p class="sub">{dd_sub}</p><div class="panel dd">{"".join(items)}</div></div>
</div>
</main></body></html>'''

mnpi = funnel(R["Blind AI reviewer"], human)[0]["MNPI"]["flagged"]
Path("design/2-scorecard.html").write_text(page("Blind AI reviewer", f"Material non-public information · AI flagged ({len(mnpi)})",
    "Each passage with the quote, the declaration, the human verdict and the AI's reason.", mnpi, False, ("MNPI", "flagged")))
miss = funnel(R["Rules baseline (flags company names)"], human)[1]["missed"]
Path("design/3-scorecard-misses.html").write_text(page("Rules baseline (flags company names)", f"All types · Missed by AI ({len(miss)})",
    "The eval reviewer sets a root cause for each miss, and marks any that were the human over-redacting.", miss, True, ("all", "missed")))
print("wrote design/2-scorecard.html and design/3-scorecard-misses.html")
