"""Write design/1-check.html: one screen, one story. Quotes are verbatim from the test set.
The three top numbers are made up, for a 1,000-transcript sample, counted in transcripts (Kevin's call).
The example misses come from the made-up rules engine run in notebooks/eval.py.
Run from the run folder: python3 design/fill_check_mock.py"""
import html, re, sys
from pathlib import Path
sys.path.insert(0, "notebooks")
from eval import load, runs, funnel  # noqa: E402

PLACEHOLDER = dict(transcripts="1,000", missed=23, alarms=187)
NAMES = {"MNPI": "Material non-public information", "Current employer confidential": "Current-employer confidential",
         "Source disclosure": "Source disclosure", "PII": "Personal data"}
WHY = {  # root cause of each miss, written during failure analysis (judgement)
    "T5-01:24": "No company is named, and the hint is hedged (“I'm not saying anything specific”). “Their Q3 numbers” only points to Northwind, a listed company he left in March, through the question before it and his declaration.",
    "T3-01:34": "The expert never names the company. “For us” only means Teallight once you know she still works there, which is in her declaration, not in the sentence.",
    "T6-01:34": "The problem is the source, a named insider (“my contact Jamie Holt”), not a company name or a figure.",
    "T8-01:24": "A private person and their health, with nothing about a company to set off a flag.",
}
ORDER = ["T5-01:24", "T3-01:34", "T6-01:34", "T8-01:24"]

T, A, human = load()
missed = funnel(runs(T, A)["Rules baseline (flags company names)"], human)[1]["missed"]
assert sorted(missed) == sorted(ORDER), missed
src = Path("data/synthetic-expert-transcripts.md").read_text()
TOPIC = {int(n): tp.strip() for n, tp in re.findall(r"^\| (\d) \| ([^|]+?) \|", src, re.M)}
TX = {f"T{t['num']}-{ts // 60:02d}:{ts % 60:02d}": (t, txt) for t, ts, txt in A}

rows = []
for i, a in enumerate(ORDER):
    t, txt = TX[a]
    key = next(i["quote"] for b in src.split("\n## Transcript ")[1:] if b.startswith(f"{t['num']}:")
               for i in __import__("json").loads(re.search(r"```json\n(.*?)\n```", b, re.S).group(1))["issues"] if i["timestamp"] == a.split("-")[1])
    first = re.split(r"(?<=[.!?])\s", key)[0]
    assert first in txt
    rows.append(f'''<div class="miss{' open' if i == 0 else ''}">
<div class="row"><span class="type">{NAMES[human[a]["type"]]}</span><span class="snip">“{html.escape(first)}”</span><span class="where">{TOPIC[t["num"]]} · {a.split("-")[1]}</span><span class="chev"></span></div>
{f'<div class="body"><p class="quote">“{html.escape(txt)}”</p><div class="why"><b>Why the AI missed it</b><p>{html.escape(WHY[a])}</p></div></div>' if i == 0 else ''}
</div>''')

page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI check (design)</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="design.css">
<style>
main{{max-width:960px}}
h1{{font-size:24px;line-height:1.3;margin:6px 0 6px;letter-spacing:-.3px}}
.lede{{color:var(--muted);margin:0 0 24px}}
.nums{{display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:16px;margin-bottom:32px}}
.num{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px}}
.num .lab{{font-weight:600}} .num .def{{color:var(--muted);font-size:13px}}
.num .big{{font-size:30px;font-weight:700;margin:6px 0 2px;letter-spacing:-.5px;font-variant-numeric:tabular-nums}}
.num.miss{{border-top:4px solid var(--miss)}} .num.miss .big{{color:var(--miss);font-size:40px}}
.num.alarm{{border-top:3px solid var(--alarm)}} .num.alarm .big{{color:var(--alarm)}}
.listhead{{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:10px}}
.listhead span{{color:var(--muted);font-size:13px}}
.miss{{background:var(--panel);border:1px solid var(--line);border-radius:10px;margin-bottom:8px}}
.miss .row{{display:grid;grid-template-columns:220px 1fr 240px 16px;gap:14px;align-items:center;padding:12px 16px}}
.type{{font-weight:600;color:var(--miss)}}
.snip{{color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.where{{color:var(--muted);font-size:13px;text-align:right;white-space:nowrap}}
.chev{{width:8px;height:8px;border-right:1.5px solid var(--muted);border-bottom:1.5px solid var(--muted);transform:rotate(-45deg)}}
.miss.open{{border-color:var(--miss-line);box-shadow:inset 3px 0 0 var(--miss)}}
.miss.open .chev{{transform:rotate(45deg)}}
.body{{padding:0 16px 16px 16px;display:grid;gap:12px}}
.quote{{margin:0;font-size:15px;line-height:1.55}}
.why{{background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:10px 12px}}
.why b{{font-size:12px;letter-spacing:.3px;text-transform:uppercase;color:var(--muted)}}
.why p{{margin:4px 0 0}}
.note{{color:var(--muted);font-size:12px;margin-top:18px}}
</style></head><body>
<div class="top"><div class="mark"><svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="1" width="20" height="20" rx="5" fill="#1c2230"/><path d="M6 11.5l3 3 7-7" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="16.5" cy="16.5" r="2.4" fill="#3843c4" stroke="#fff" stroke-width="1.2"/></svg>Content review engine</div><div class="synth">Illustrative</div></div>
<main>
<h1>Before we let the AI do more, check it against what reviewers already decided.</h1>
<p class="lede">Run the AI on a sample of transcripts reviewers have already decided, and count where the two disagree.</p>
<div class="nums">
<div class="num"><div class="lab">Sample transcripts</div><div class="big">{PLACEHOLDER["transcripts"]}</div><div class="def">Already reviewed by people</div></div>
<div class="num miss"><div class="lab">Missed by AI</div><div class="big">{PLACEHOLDER["missed"]}</div><div class="def">Transcripts where reviewers found a problem in a passage the AI didn't flag</div></div>
<div class="num alarm"><div class="lab">False alarms</div><div class="big">{PLACEHOLDER["alarms"]}</div><div class="def">Transcripts where the AI was overly cautious: it flagged something reviewers cleared</div></div>
</div>
<div class="listhead"><h2>Missed by AI</h2><span>4 examples of the {PLACEHOLDER["missed"]}. Click one to see the quote and why the AI missed it</span></div>
{"".join(rows)}
<p class="note">Illustrative. The three numbers are made up for a 1,000-transcript sample. The misses are examples from a synthetic test set, quoted word for word. Nothing here is Dialectica's data.</p>
</main></body></html>'''
Path("design/1-check.html").write_text(page)
print("wrote design/1-check.html")
