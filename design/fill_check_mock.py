"""Write the three design pages for the AI performance benchmark.

  design/1-summary.html     headline, missed issues and unneeded flags, counts by category
  design/2-category.html    one category's transcripts (material non-public information, missed issues)
  design/3-transcript.html  a full transcript with every passage marked: flagged correctly, missed, unneeded flag

Counts are MADE UP for a 1,000-transcript sample (Kevin's call) and shown as counts only, in transcripts.
The transcript and its highlights are real: synthetic transcript 5, scored in notebooks/eval.py with the made-up rules
engine (the only run with misses and unneeded flags), against the test set's answer key.
Run from the run folder: python3 design/fill_check_mock.py
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, "notebooks")
from eval import load, runs  # noqa: E402

SAMPLE = 1000
# category, description, real issues, missed, AI flags, unneeded flags -- all made up
HIGH = [("Material non-public information", "Non-public facts about a listed company that could move its share price", 38, 1, 97, 60),
        ("Current-employer confidential", "Non-public information about the expert's current employer", 52, 1, 81, 30),
        ("Declaration conflict", "What the expert says contradicts their declaration", 14, 0, 23, 9)]
OTHER = [("Source disclosure", "Names a person inside a company as the source", 29, 6, 31, 8),
         ("Former-client confidential", "Confidential information about a former client or employer", 33, 4, 49, 20),
         ("Personal data", "Names or sensitive details of private individuals", 96, 11, 145, 60)]
ALL = HIGH + OTHER
for name, _, real, missed, flags, unneeded in ALL:
    assert (flags - unneeded) + missed == real, name
MISSED, REAL = sum(r[3] for r in ALL), sum(r[2] for r in ALL)
UNNEEDED, FLAGS = sum(r[5] for r in ALL), sum(r[4] for r in ALL)
HIGH_MISSED = sum(r[3] for r in HIGH)
assert (MISSED, REAL, UNNEEDED, FLAGS, HIGH_MISSED) == (23, 262, 187, 426, 2)

EX = 5
TYPE_NAMES = {"MNPI": "Material non-public information", "Current employer confidential": "Current-employer confidential",
              "Declaration conflict": "Declaration conflict", "Source disclosure": "Source disclosure",
              "Confidentiality breach": "Former-client confidential", "PII": "Personal data"}
WHY = {"T5-01:24": "No company is named, and the hint is hedged. “Their Q3 numbers” points to Northwind only through "
                   "the question before it and the expert's declaration."}

T, A, human = load()
engine = runs(T, A)["Rules baseline (flags company names)"]
SRC = Path("data/synthetic-expert-transcripts.md").read_text()
TOPIC = {int(n): tp.strip() for n, tp in re.findall(r"^\| (\d) \| ([^|]+?) \|", SRC, re.M)}


def ts(s):
    return f"{s // 60:02d}:{s % 60:02d}"


CSS = """
:root{--ink:#0f172a;--ink2:#334155;--muted:#64748b;--faint:#94a3b8;--line:#e8ecf2;--bg:#ffffff;--wash:#f8fafc;
--risk:#c8331f;--risk-wash:#fdf1ef;--cost:#9a6a12;--cost-wash:#fbf6ea;--ok:#15803d;--ok-wash:#eefaf2}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
nav{display:flex;align-items:center;justify-content:space-between;padding:18px 40px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;font-weight:600;font-size:14px;letter-spacing:-.1px}
.badge{font-size:12px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:3px 10px}
main{max-width:920px;margin:0 auto;padding:56px 40px 80px}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:34px;line-height:1.2;letter-spacing:-.8px;margin:10px 0 10px;font-weight:650}
.lede{font-size:17px;color:var(--muted);margin:0 0 48px}
.stats{display:grid;grid-template-columns:1.45fr 1fr;gap:20px;margin-bottom:64px}
.stat{border-radius:18px;padding:26px 28px}
.stat.risk{background:var(--risk-wash)} .stat.cost{background:var(--wash)}
.stat .k{display:flex;align-items:center;gap:10px;font-weight:600}
.stat .tag{font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px}
.risk .tag{color:var(--risk);background:#fff} .cost .tag{color:var(--cost);background:#fff}
.stat .n{font-size:64px;font-weight:700;letter-spacing:-2px;line-height:1;margin:18px 0 6px;font-variant-numeric:tabular-nums}
.risk .n{color:var(--risk)} .cost .n{font-size:44px;color:var(--ink2);letter-spacing:-1.2px}
.stat .of{color:var(--muted)}
.stat .hp{margin-top:18px;padding-top:16px;border-top:1px solid #f3d6d0;display:flex;align-items:baseline;gap:10px;color:var(--ink2)}
.stat .hp b{font-size:22px;color:var(--risk)}
h2{font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
.group{margin:22px 0 8px;font-size:13px;font-weight:600;color:var(--ink2)}
.rows{border-top:1px solid var(--line)}
.r{display:grid;grid-template-columns:1fr 140px 120px 18px;align-items:center;gap:16px;padding:16px 4px;border-bottom:1px solid var(--line)}
.r .name{font-weight:500}
.r .bar{height:6px;border-radius:3px;background:var(--line);overflow:hidden}
.r .bar i{display:block;height:100%;background:var(--risk);border-radius:3px}
.r .c{text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)}
.r .c b{color:var(--ink);font-weight:600}
.r .go{width:7px;height:7px;border-right:1.5px solid var(--faint);border-bottom:1.5px solid var(--faint);transform:rotate(-45deg)}
.r.zero .bar i{background:transparent} .r.zero .c b{color:var(--faint)}
.sec2{margin-top:72px}
.sec2 .r .bar i{background:#d9b979}
.sec2 .r .name{color:var(--ink2)}
.sec2 .r{padding:10px 4px;font-size:14px}
.sec2 h2{color:var(--faint)}
.sec2 .group{font-size:12px;color:var(--muted);margin-top:16px}
.card .go{width:7px;height:7px;border-right:1.5px solid var(--faint);border-bottom:1.5px solid var(--faint);transform:rotate(-45deg)}
.back{display:inline-flex;align-items:center;gap:8px;color:var(--muted);font-size:14px;margin-bottom:28px}
.back:before{content:"";width:7px;height:7px;border-left:1.5px solid var(--muted);border-bottom:1.5px solid var(--muted);transform:rotate(45deg)}
.sub{color:var(--muted);margin:0 0 36px}
.sub b{color:var(--risk)}
.card{display:grid;grid-template-columns:1fr 18px;gap:16px;align-items:center;border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:12px}
.card .t{font-weight:600} .card .m{color:var(--muted);font-size:13px;margin-bottom:6px}
.card q{color:var(--ink2)}
.legend{display:flex;gap:18px;margin:0 0 32px;font-size:13px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend i{width:10px;height:10px;border-radius:3px;display:inline-block}
.turn{display:grid;grid-template-columns:56px 1fr;gap:16px;padding:10px 0}
.turn .ts{color:var(--faint);font-size:13px;font-variant-numeric:tabular-nums;padding-top:2px}
.turn.q .txt{color:var(--muted)}
.turn .who{font-size:12px;font-weight:600;color:var(--faint);letter-spacing:.04em;text-transform:uppercase;margin-bottom:2px}
.mark{border-radius:12px;padding:12px 14px;margin:2px 0}
.mark .lab{font-size:12px;font-weight:600;margin-bottom:4px}
.mark.missed{background:var(--risk-wash);box-shadow:inset 3px 0 0 var(--risk)} .mark.missed .lab{color:var(--risk)}
.mark.unneeded{background:var(--cost-wash);box-shadow:inset 3px 0 0 #d9b979} .mark.unneeded .lab{color:var(--cost)}
.mark.correct{background:var(--ok-wash);box-shadow:inset 3px 0 0 var(--ok)} .mark.correct .lab{color:var(--ok)}
.mark .why{margin-top:8px;font-size:13px;color:var(--ink2)}
"""
NAV = ('<nav><div class="brand"><svg width="20" height="20" viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="1" width="20" height="20" '
       'rx="6" fill="#0f172a"/><path d="M6 11.5l3 3 7-7" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" '
       'stroke-linejoin="round"/></svg>Content review engine</div><span class="badge">Illustrative</span></nav>')


def page(title, body):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&display=swap" '
            f'rel="stylesheet"><style>{CSS}</style></head><body>{NAV}<main>{body}</main></body></html>')


def rows(cats, idx_missed, idx_total, maxv, link_first=False):
    out = []
    for i, c in enumerate(cats):
        v, tot = c[idx_missed], c[idx_total]
        href = ' href="2-category.html"' if link_first and i == 0 else ""
        out.append(f'<a class="r{" zero" if v == 0 else ""}"{href}><span class="name">{c[0]}</span>'
                   f'<span class="bar"><i style="width:{v / maxv * 100:.0f}%"></i></span>'
                   f'<span class="c"><b>{v}</b> of {tot}</span><span class="go"></span></a>')
    return "".join(out)


def summary():
    mx = max(r[3] for r in ALL); mu = max(r[5] for r in ALL)
    body = f'''<div class="eyebrow">AI performance benchmark</div>
<h1>AI and human review compared on {SAMPLE:,} transcripts</h1>
<p class="lede">Where the AI misses issues, and where it over-flags.</p>
<div class="stats">
<div class="stat risk"><div class="k">Missed issues <span class="tag">Compliance risk</span></div>
<div class="n">{MISSED}</div><div class="of">of {REAL} real issues</div>
<div class="hp"><b>{HIGH_MISSED}</b> high priority</div></div>
<div class="stat cost"><div class="k">Unneeded flags <span class="tag">Operational cost</span></div>
<div class="n">{UNNEEDED}</div><div class="of">of {FLAGS} AI flags</div></div>
</div>
<h2>Missed issues by category</h2>
<div class="group">High priority</div><div class="rows">{rows(HIGH, 3, 2, mx, True)}</div>
<div class="group">Other</div><div class="rows">{rows(OTHER, 3, 2, mx)}</div>
<div class="sec2"><h2>Unneeded flags by category</h2>
<div class="group">High priority</div><div class="rows">{rows(HIGH, 5, 4, mu)}</div>
<div class="group">Other</div><div class="rows">{rows(OTHER, 5, 4, mu)}</div></div>'''
    return page("AI performance benchmark (design)", body)


def category():
    name, desc, real, missed, *_ = HIGH[0]
    t = next(x for x in T if x["num"] == EX)
    txt = next(x for s, w, x in t["turns"] if f"T{EX}-{ts(s)}" == "T5-01:24")
    first = re.split(r"(?<=[.!?])\s", txt)[0]
    body = f'''<a class="back" href="1-summary.html">Benchmark</a>
<div class="eyebrow">Missed issues</div><h1>{name}</h1>
<p class="sub"><b>{missed}</b> of {real} real issues missed · {desc}</p>
<a class="card" href="3-transcript.html"><div><div class="m">{TOPIC[EX]} · 01:24</div><q>{html.escape(first)}</q></div><span class="go"></span></a>'''
    return page("Missed issues: category (design)", body)


def transcript():
    t = next(x for x in T if x["num"] == EX)
    out = []
    for s, who, txt in t["turns"]:
        a = f"T{EX}-{ts(s)}"
        if who != "EXPERT":
            out.append(f'<div class="turn q"><span class="ts">{ts(s)}</span><div><div class="who">Interviewer</div><div class="txt">{html.escape(txt)}</div></div></div>')
            continue
        e, h = engine[a], human[a]
        kind = "correct" if e and h else "missed" if h else "unneeded" if e else None
        inner = f'<div class="txt">{html.escape(txt)}</div>'
        if kind:
            lab = {"correct": f"Flagged correctly · {TYPE_NAMES[h['type']]}" if h else "",
                   "missed": f"Missed · {TYPE_NAMES[h['type']]}" if h else "",
                   "unneeded": "Unneeded flag · reviewer cleared it"}[kind]
            why = f'<div class="why">{html.escape(WHY[a])}</div>' if a in WHY else ""
            inner = f'<div class="mark {kind}"><div class="lab">{lab}</div>{inner}{why}</div>'
        out.append(f'<div class="turn"><span class="ts">{ts(s)}</span><div><div class="who">Expert</div>{inner}</div></div>')
    body = f'''<a class="back" href="2-category.html">Material non-public information</a>
<div class="eyebrow">Transcript {EX}</div><h1>{TOPIC[EX]}</h1>
<div class="legend"><span><i style="background:var(--ok)"></i>Flagged correctly</span><span><i style="background:var(--risk)"></i>Missed</span><span><i style="background:#d9b979"></i>Unneeded flag</span></div>
{"".join(out)}'''
    return page("Transcript (design)", body)


if __name__ == "__main__":
    for f, fn in (("1-summary.html", summary), ("2-category.html", category), ("3-transcript.html", transcript)):
        Path("design", f).write_text(fn())
    print(f"missed {MISSED} of {REAL}; high priority {HIGH_MISSED}; unneeded {UNNEEDED} of {FLAGS}")
