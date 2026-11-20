"""Write the two design pages for the AI performance benchmark (round 4).

  design/1-summary.html     headline, issues by type (one row expanded in place), unneeded flags
  design/2-transcript.html  call context and the full transcript, missed passage highlighted

Counts are MADE UP for a 1,000-transcript sample (Kevin's call). "Found" is what reviewers found; caught = found - missed.
The transcript is synthetic transcript 5 from the test set; its missed passage comes from the made-up rules engine run
scored in notebooks/eval.py against the answer key. Run from the run folder: python3 design/fill_check_mock.py
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, "notebooks")
from eval import load, runs  # noqa: E402

SAMPLE = 1000
# category, one-line description, found by reviewers, missed by AI -- made up
HIGH = [("Material non-public information", "Non-public facts about a listed company that could move its share price", 38, 1),
        ("Current-employer confidential", "Non-public information about the expert's current employer", 52, 1),
        ("Declaration conflict", "What the expert says contradicts their declaration", 14, 0)]
OTHER = [("Source disclosure", "Names a person inside a company as the source", 29, 6),
         ("Former-client confidential", "Confidential information about a former client or employer", 33, 4),
         ("Personal data", "Names or sensitive details of private individuals", 96, 11)]
UNNEEDED = 187  # passages the AI flagged that reviewers cleared -- made up
FOUND = sum(r[2] for r in HIGH + OTHER)
MISSED = sum(r[3] for r in HIGH + OTHER)
CAUGHT = FOUND - MISSED
assert (FOUND, CAUGHT, MISSED) == (262, 239, 23)

EX, EX_TS = 5, "01:24"
TYPE = "Material non-public information"
T, A, human = load()
engine = runs(T, A)["Rules baseline (flags company names)"]
assert human[f"T{EX}-{EX_TS}"] and not engine[f"T{EX}-{EX_TS}"], "the example must be a miss"
SRC = Path("data/synthetic-expert-transcripts.md").read_text()
TOPIC = {int(n): tp.strip() for n, tp in re.findall(r"^\| (\d) \| ([^|]+?) \|", SRC, re.M)}
t5 = next(x for x in T if x["num"] == EX)


def ts(s):
    return f"{s // 60:02d}:{s % 60:02d}"


CSS = """
:root{--bg:#f3f4f7;--card:#fff;--ink:#0f172a;--ink2:#334155;--muted:#64748b;--faint:#94a3b8;--line:#eceff3;
--red:#d1342f;--red-wash:#fdeeed;--amber:#b7791f;--amber-wash:#fdf6e7;--slate:#cbd5e1}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 Inter,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
nav{display:flex;align-items:center;justify-content:space-between;height:56px;padding:0 32px;background:var(--card);border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;font-weight:600}
.badge{font-size:12px;color:var(--muted);background:var(--bg);border-radius:999px;padding:3px 10px}
main{max-width:1040px;margin:0 auto;padding:36px 32px 64px}
.eyebrow{font-size:13px;color:var(--muted);font-weight:500}
h1{font-size:30px;line-height:1.25;letter-spacing:-.6px;margin:6px 0 22px;font-weight:650}
h1 .r{color:var(--red)}
.card{background:var(--card);border-radius:16px;box-shadow:0 1px 2px rgba(15,23,42,.04),0 0 0 1px var(--line)}
.split{height:10px;border-radius:5px;background:var(--slate);overflow:hidden;display:flex;margin-bottom:28px}
.split i{display:block;height:100%;background:var(--red)}
.legend{display:flex;gap:20px;font-size:13px;color:var(--muted);margin-bottom:28px}
.legend b{color:var(--ink);font-weight:600}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend .dot{width:9px;height:9px;border-radius:3px;display:inline-block}
.ct{display:flex;align-items:baseline;justify-content:space-between;padding:20px 24px 8px}
.ct h2{font-size:17px;margin:0;font-weight:650}
.grp{padding:14px 24px 6px;font-size:12px;font-weight:600;color:var(--faint);letter-spacing:.04em;text-transform:uppercase}
.row{display:grid;grid-template-columns:1fr 220px 18px;gap:20px;align-items:center;padding:14px 24px;border-top:1px solid var(--line)}
.row .n{font-weight:600;font-size:15px} .row .d{color:var(--muted);font-size:13px}
.row .s{text-align:right;color:var(--ink2);font-variant-numeric:tabular-nums}
.row .s .m{color:var(--red);font-weight:600} .row .s .z{color:var(--faint)}
.chev{width:7px;height:7px;border-right:1.5px solid var(--faint);border-bottom:1.5px solid var(--faint);transform:rotate(45deg);margin-top:-4px}
.row.open{background:#fbfbfc} .row.open .chev{transform:rotate(-135deg);margin-top:4px}
.ex{display:grid;grid-template-columns:3px 1fr 150px 18px;gap:14px;align-items:center;margin:0 24px 14px;padding:12px 14px;border-radius:12px;background:var(--red-wash)}
.ex .bar{height:100%;min-height:22px;border-radius:2px;background:var(--red)}
.ex q{color:var(--ink2)} .ex .w{color:var(--muted);font-size:13px;text-align:right}
.ex .go{width:7px;height:7px;border-right:1.5px solid var(--red);border-bottom:1.5px solid var(--red);transform:rotate(-45deg)}
.flags{display:flex;align-items:center;gap:14px;margin-top:16px;padding:16px 24px}
.flags .num{font-size:18px;font-weight:650;color:var(--amber);font-variant-numeric:tabular-nums}
.flags .txt{color:var(--ink2)}
.flags .dot{width:9px;height:9px;border-radius:3px;background:var(--amber)}
.back{display:inline-flex;align-items:center;gap:8px;color:var(--muted);margin-bottom:18px}
.back:before{content:"";width:7px;height:7px;border-left:1.5px solid var(--muted);border-bottom:1.5px solid var(--muted);transform:rotate(45deg)}
.ctx{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin-bottom:16px}
.ctx > div{padding:18px 22px;border-left:1px solid var(--line)} .ctx > div:first-child{border-left:0}
.ctx .k{font-size:12px;color:var(--faint);font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin-bottom:4px}
.ctx .v{color:var(--ink2)} .ctx .v b{color:var(--ink);font-weight:600}
.ctx .wide{grid-column:1/-1;border-left:0;border-top:1px solid var(--line)}
.tr{padding:10px 24px 18px}
.turn{display:grid;grid-template-columns:52px 1fr 250px;gap:16px;padding:9px 0}
.turn .t{color:var(--faint);font-variant-numeric:tabular-nums;font-size:13px;padding-top:1px}
.turn .who{font-size:12px;font-weight:600;color:var(--faint);margin-bottom:1px}
.turn.q .x{color:var(--muted)}
.turn.miss .x{background:var(--red-wash);box-shadow:inset 3px 0 0 var(--red);border-radius:10px;padding:10px 12px;margin:-2px 0}
.turn .tag{align-self:start;font-size:12px;font-weight:600;color:var(--red);background:var(--red-wash);border-radius:999px;padding:4px 10px;justify-self:start;margin-top:18px;white-space:nowrap}
"""
NAV = ('<nav><div class="brand"><svg width="20" height="20" viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="1" width="20" height="20" '
       'rx="6" fill="#0f172a"/><path d="M6 11.5l3 3 7-7" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" '
       'stroke-linejoin="round"/></svg>Content review engine</div><span class="badge">Illustrative</span></nav>')


def page(title, body):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&display=swap" '
            f'rel="stylesheet"><style>{CSS}</style></head><body>{NAV}<main>{body}</main></body></html>')


def row(name, desc, found, missed, open_=False):
    m = f'<span class="m">missed {missed}</span>' if missed else '<span class="z">missed 0</span>'
    out = (f'<div class="row{" open" if open_ else ""}"><div><div class="n">{name}</div><div class="d">{desc}</div></div>'
           f'<div class="s">caught {found - missed} of {found}, {m}</div><span class="chev"></span></div>')
    if open_:
        txt = next(x for s, w, x in t5["turns"] if ts(s) == EX_TS)
        first = re.split(r"(?<=[.!?])\s", txt)[0]
        out += (f'<a class="ex" href="2-transcript.html"><span class="bar"></span><q>{html.escape(first)}</q>'
                f'<span class="w">{TOPIC[EX]} · {EX_TS}</span><span class="go"></span></a>')
    return out


def summary():
    body = f'''<div class="eyebrow">AI performance benchmark · {SAMPLE:,} transcripts</div>
<h1>Reviewers found {FOUND} issues. The AI caught {CAUGHT} and missed <span class="r">{MISSED}</span>.</h1>
<div class="split"><i style="width:{MISSED / FOUND * 100:.2f}%;margin-left:auto"></i></div>
<div class="card"><div class="ct"><h2>Issues by type</h2></div>
<div class="grp">High priority</div>{"".join(row(*r, open_=(i == 0)) for i, r in enumerate(HIGH))}
<div class="grp">Other</div>{"".join(row(*r) for r in OTHER)}</div>
<div class="card flags"><span class="dot"></span><span class="txt">The AI also flagged <b class="num">{UNNEEDED}</b> passages reviewers cleared.</span></div>'''
    return page("AI performance benchmark (design)", body)


def transcript():
    t = t5
    role = re.sub(r"^[^.]+\.\s*", "", t["profile"]).rsplit(" Industry:", 1)[0]
    turns = []
    for s, who, txt in t["turns"]:
        miss = ts(s) == EX_TS
        spk = "Expert" if who == "EXPERT" else "Interviewer"
        tag = f'<span class="tag">Missed · {TYPE}</span>' if miss else "<span></span>"
        turns.append(f'<div class="turn{" q" if who != "EXPERT" else ""}{" miss" if miss else ""}"><span class="t">{ts(s)}</span>'
                     f'<div><div class="who">{spk}</div><div class="x">{html.escape(txt)}</div></div>{tag}</div>')
    name = t["profile"].split(".")[0]
    body = f'''<a class="back" href="1-summary.html">Benchmark</a>
<div class="eyebrow">Call topic</div><h1 style="margin-bottom:16px">{TOPIC[EX]}</h1>
<div class="card ctx"><div><div class="k">Expert</div><div class="v"><b>{name}</b></div></div>
<div style="grid-column:span 2"><div class="k">Role</div><div class="v">{html.escape(role)}</div></div>
<div class="wide"><div class="k">Declared</div><div class="v">{html.escape(t["declaration"])}</div></div></div>
<div class="card tr">{"".join(turns)}</div>'''
    return page("Transcript (design)", body)


if __name__ == "__main__":
    Path("design/1-summary.html").write_text(summary())
    Path("design/2-transcript.html").write_text(transcript())
    print(f"found {FOUND}, caught {CAUGHT}, missed {MISSED}; unneeded {UNNEEDED}")
