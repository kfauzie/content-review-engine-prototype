"""Write the three design pages for the AI review check, from made-up counts plus examples from the test set.

  design/1-summary.html   main page: transcripts reviewed, missed by AI (by category), false alarms (collapsed)
  design/2-category.html  one category's examples (material non-public information, missed by AI)
  design/3-example.html   one example: the transcript excerpt and why the AI missed it

Counts are MADE UP for a 1,000-transcript sample (Kevin's call) and counted in transcripts throughout, assuming no
transcript has misses in two categories. Rates and shares are computed here from those counts.
Example quotes are verbatim from the synthetic test set. Run from the run folder: python3 design/fill_check_mock.py
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, "notebooks")
from data_review import SRC, parse  # noqa: E402

SAMPLE = 1000
# category: (description, real issues, missed by AI, AI flags, false alarms) -- all made up
CATS = {
    "high": [
        ("Material non-public information", "Non-public facts about a listed company that could move its share price", 38, 1, 97, 60),
        ("Current-employer confidential", "Non-public information about the expert's current employer", 52, 1, 81, 30),
        ("Declaration conflict", "What the expert says contradicts their declaration", 14, 0, 23, 9),
    ],
    "other": [
        ("Source disclosure", "Names a person inside a company as the source", 29, 6, 31, 8),
        ("Former-client confidential", "Confidential information about a former client or employer", 33, 4, 49, 20),
        ("Personal data", "Names or sensitive details of private individuals", 96, 11, 145, 60),
    ],
}
ROWS = [r for g in CATS.values() for r in g]
for name, _, real, missed, flags, alarms in ROWS:
    assert (flags - alarms) + missed == real, f"{name}: rightly flagged + missed must equal real issues"
MISSED = sum(r[3] for r in ROWS)
ALARMS = sum(r[5] for r in ROWS)
REAL = sum(r[2] for r in ROWS)
FLAGS = sum(r[4] for r in ROWS)
HIGH_MISSED = sum(r[3] for r in CATS["high"])
assert (MISSED, ALARMS, HIGH_MISSED) == (23, 187, 2)

# the example shown on pages 2 and 3: transcript 5, 01:24 (a miss by the made-up rules engine in notebooks/eval.py)
EX_T, EX_TS = 5, 84
WHY = ("No company is named, and the hint is hedged (“I'm not saying anything specific”). "
       "“Their Q3 numbers” points to Northwind, a listed company he left in March 2026, only through the question "
       "before it and his declaration.")

T = {t["num"]: t for t in parse(SRC.read_text())}
TOPIC = {int(n): tp.strip() for n, tp in re.findall(r"^\| (\d) \| ([^|]+?) \|", SRC.read_text(), re.M)}


def pct(a, b):
    return f"{a / b * 100:.1f}%" if b else "0.0%"


def ts(s):
    return f"{s // 60:02d}:{s % 60:02d}"


CSS = """
main{max-width:900px}
.crumbs{color:var(--muted);font-size:13px;margin:4px 0 10px}
.crumbs a{color:var(--muted)}
h1{font-size:22px;margin:0 0 18px;letter-spacing:-.3px}
.total{color:var(--muted);margin:-8px 0 20px}
.total b{color:var(--ink);font-size:18px}
.sec{background:var(--panel);border:1px solid var(--line);border-radius:10px;margin-bottom:16px}
.sec.miss{border-top:4px solid var(--miss)}
.sechead{display:flex;align-items:baseline;gap:14px;padding:16px 18px 6px;flex-wrap:wrap}
.sechead .lab{font-weight:600;font-size:16px}
.sechead .big{font-size:34px;font-weight:700;color:var(--miss);letter-spacing:-.5px;font-variant-numeric:tabular-nums}
.sechead .rate{color:var(--muted)}
.goal{margin:4px 18px 12px;padding:8px 12px;border-radius:8px;background:var(--miss-tint);border:1px solid var(--miss-line);color:var(--miss);font-weight:600;display:inline-block}
table{width:100%;border-collapse:collapse}
th,td{padding:11px 18px;border-top:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}
th{font-size:12px;font-weight:600;color:var(--muted);background:var(--soft)}
td:first-child,th:first-child{text-align:left}
th.grp{text-transform:uppercase;letter-spacing:.3px;font-size:11px;color:var(--ink)}
td .name{font-weight:600} td .desc{color:var(--muted);font-size:13px}
td.c{color:var(--miss);font-weight:700}
tr.row td:last-child{width:28px}
td.r{white-space:nowrap}
.chev{display:inline-block;width:7px;height:7px;border-right:1.5px solid var(--muted);border-bottom:1.5px solid var(--muted);transform:rotate(-45deg)}
.sec.alarm .sechead{padding-bottom:14px}
.sec.alarm .sechead .lab{font-size:15px}
.sec.alarm .sechead .big{font-size:22px;color:var(--alarm)}
.sec.alarm .sechead .chev{margin-left:auto;transform:rotate(45deg)}
.stats{color:var(--muted);margin:-10px 0 18px}
.ex{display:grid;grid-template-columns:150px 1fr 16px;gap:14px;padding:12px 18px;align-items:center}
.ex .where{color:var(--muted);font-size:13px}
.part{padding:14px 18px}
.part h2{font-size:12px;letter-spacing:.3px;text-transform:uppercase;color:var(--muted);margin:0 0 8px}
.line{display:grid;grid-template-columns:52px 120px 1fr;gap:10px;margin-bottom:8px}
.line .t{color:var(--faint);font-variant-numeric:tabular-nums} .line .s{color:var(--muted);font-size:13px;padding-top:1px}
.line.hit .q{background:var(--miss-tint);border-left:3px solid var(--miss);padding:4px 8px;border-radius:4px}
.note{color:var(--muted);font-size:12px;margin-top:16px}
"""
TOP = ('<div class="top"><div class="mark"><svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="1" width="20" '
       'height="20" rx="5" fill="#1c2230"/><path d="M6 11.5l3 3 7-7" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" '
       'stroke-linejoin="round"/><circle cx="16.5" cy="16.5" r="2.4" fill="#3843c4" stroke="#fff" stroke-width="1.2"/></svg>'
       'Content review engine</div><div class="synth">Illustrative</div></div>')
NOTE = '<p class="note">Illustrative: made-up counts; example from a synthetic test set.</p>'


def page(title, body):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
            f'<link rel="stylesheet" href="design.css"><style>{CSS}</style></head><body>{TOP}<main>{body}{NOTE}</main></body></html>')


def summary():
    rows = []
    for key, label in (("high", "High priority"), ("other", "Other")):
        rows.append(f'<tr><th class="grp">{label}</th><th>Missed</th><th>Miss rate</th><th>Share of misses</th><th></th></tr>')
        for name, desc, real, missed, *_ in CATS[key]:
            href = ' onclick="location.href=\'2-category.html\'"' if name == "Material non-public information" else ""
            rows.append(f'<tr class="row"{href}><td><div class="name">{name}</div><div class="desc">{desc}</div></td>'
                        f'<td{" class=\"c\"" if missed else ""}>{missed}</td><td class="r">{pct(missed, real)} <span style="color:var(--faint)">of {real}</span></td>'
                        f'<td>{pct(missed, MISSED)}</td><td><span class="chev"></span></td></tr>')
    body = f'''<h1>AI review check: {SAMPLE:,} reviewed transcripts</h1>
<div class="sec miss"><div class="sechead"><span class="lab">Missed by AI</span><span class="big">{MISSED}</span>
<span class="rate">{pct(MISSED, REAL)} of {REAL} real issues</span></div>
<div class="goal">High priority missed by AI: {HIGH_MISSED} (goal: 0)</div>
<table>{"".join(rows)}</table></div>
<div class="sec alarm"><div class="sechead"><span class="lab">False alarms</span><span class="big">{ALARMS}</span>
<span class="rate">{pct(ALARMS, FLAGS)} of {FLAGS} AI flags</span><span class="chev"></span></div></div>'''
    return page("AI review check (design)", body)


def category():
    name, desc, real, missed, *_ = CATS["high"][0]
    t = T[EX_T]
    txt = next(x for s, w, x in t["turns"] if s == EX_TS)
    first = re.split(r"(?<=[.!?])\s", txt)[0]
    body = f'''<div class="crumbs"><a href="1-summary.html">AI review check</a> › Missed by AI</div>
<h1>{name}</h1><p class="stats">{desc}. {missed} missed · {pct(missed, real)} of {real} real issues · {pct(missed, MISSED)} of all misses</p>
<div class="sec"><div class="ex" onclick="location.href='3-example.html'"><span class="where">{TOPIC[EX_T]} · {ts(EX_TS)}</span>
<span>“{html.escape(first)}”</span><span class="chev"></span></div></div>'''
    return page("Missed by AI: category (design)", body)


def example():
    t = T[EX_T]
    i = [s for s, _, _ in t["turns"]].index(EX_TS)
    lines = []
    for s, who, txt in t["turns"][i - 1:i + 1]:
        spk = "Expert" if who == "EXPERT" else "Interviewer"
        lines.append(f'<div class="line{" hit" if s == EX_TS else ""}"><span class="t">{ts(s)}</span><span class="s">{spk}</span>'
                     f'<span class="q">{html.escape(txt)}</span></div>')
    body = f'''<div class="crumbs"><a href="1-summary.html">AI review check</a> › <a href="2-category.html">Material non-public information</a></div>
<h1>{TOPIC[EX_T]} · Transcript {EX_T}</h1>
<div class="sec"><div class="part"><h2>Transcript</h2>{"".join(lines)}</div></div>
<div class="sec"><div class="part"><h2>Why the AI missed it</h2><p style="margin:0">{html.escape(WHY)}</p></div></div>'''
    return page("Missed by AI: example (design)", body)


if __name__ == "__main__":
    for f, fn in (("1-summary.html", summary), ("2-category.html", category), ("3-example.html", example)):
        Path("design", f).write_text(fn())
    print(f"missed {MISSED} ({pct(MISSED, REAL)} of {REAL}); high priority {HIGH_MISSED}; false alarms {ALARMS} ({pct(ALARMS, FLAGS)} of {FLAGS})")
    for name, _, real, missed, flags, alarms in ROWS:
        print(f"  {name}: missed {missed} ({pct(missed, real)} of {real}, {pct(missed, MISSED)} of misses); "
              f"false alarms {alarms} ({pct(alarms, flags)} of {flags}, {pct(alarms, ALARMS)} of false alarms)")
