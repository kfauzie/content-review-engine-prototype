"""Write the two design pages for the AI performance benchmark (round 5).

  design/1-summary.html     header, missed issues by type with a carousel of examples per type, unneeded flags
  design/2-transcript.html  call context, full transcript, missed passage with issue type, reviewer comment, root cause

Counts are MADE UP for a 1,000-transcript sample (Kevin's call). Examples come from data/examples_illustrative.json:
four quote the synthetic test set word for word, the rest were written for the design. Call dates are invented.
The transcript page uses synthetic transcript 5, whose 01:24 passage the made-up rules engine missed (notebooks/eval.py);
the reviewer comment is the answer key's rationale for that passage.
Run from the run folder: python3 design/fill_check_mock.py
"""
import html
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, "notebooks")
from eval import load, runs  # noqa: E402

SAMPLE = 1000
# category, short description, found by reviewers, missed by AI -- made up
HIGH = [("Material non-public information", "Non-public facts that could move a listed company's share price", 38, 1),
        ("Current-employer confidential", "Non-public information about the expert's current employer", 52, 1),
        ("Declaration conflict", "Contradicts what the expert declared", 14, 0)]
LOWER = [("Source disclosure", "Names an insider as the source", 29, 6),
         ("Former-client confidential", "Confidential details from a former client or employer", 33, 4),
         ("Personal data", "Names or sensitive details of private individuals", 96, 11)]
UNNEEDED = 187  # made up
FOUND = sum(r[2] for r in HIGH + LOWER)
MISSED = sum(r[3] for r in HIGH + LOWER)
CAUGHT = FOUND - MISSED
assert (FOUND, CAUGHT, MISSED) == (262, 239, 23)

EXAMPLES = defaultdict(list)
for e in json.loads(Path("data/examples_illustrative.json").read_text())["examples"]:
    EXAMPLES[e["category"]].append(e)
for name, _, _, missed in HIGH + LOWER:
    assert len(EXAMPLES[name]) <= missed, f"{name}: more examples than misses"

# transcript page: synthetic transcript 5
EX, EX_TS, EX_TYPE = 5, "01:24", "Material non-public information"
T, A, human = load()
engine = runs(T, A)["Rules baseline (flags company names)"]
assert human[f"T{EX}-{EX_TS}"] and not engine[f"T{EX}-{EX_TS}"]
SRC = Path("data/synthetic-expert-transcripts.md").read_text()
TOPIC = {int(n): tp.strip() for n, tp in re.findall(r"^\| (\d) \| ([^|]+?) \|", SRC, re.M)}
KEY = json.loads(re.search(r"```json\n(.*?)\n```", SRC.split("\n## Transcript ")[EX], re.S).group(1))
REVIEWER = next(i["rationale"] for i in KEY["issues"] if i["timestamp"] == EX_TS)
ROOT_CAUSE = ("The AI looks for named companies, and none is named: the expert says “their”. Linking it to Northwind, "
              "a listed company he left in March 2026, needs the question before it and his declaration.")
t5 = next(x for x in T if x["num"] == EX)
EX_DATE = next(e["date"] for e in EXAMPLES[EX_TYPE] if e["source"] == f"test set T{EX}-{EX_TS}")


def ts(s):
    return f"{s // 60:02d}:{s % 60:02d}"


def nice(d):
    return date.fromisoformat(d).strftime("%-d %b %Y")


def initials(n):
    return "".join(p[0] for p in n.split()[:2]).upper()


CSS = """
:root{--bg:#f2f4f7;--card:#fff;--ink:#0f172a;--ink2:#334155;--muted:#64748b;--faint:#94a3b8;--line:#e9edf2;
--red:#d1342f;--red-wash:#fdeeed;--hi:#b42318;--hi-wash:#fef3f2;--lo:#475569;--lo-wash:#f1f5f9;--amber:#b7791f;--amber-wash:#fdf6e7}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 Inter,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
nav{display:flex;align-items:center;justify-content:space-between;height:56px;padding:0 32px;background:var(--card);border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;font-weight:600}
.badge{font-size:12px;color:var(--muted);background:var(--bg);border-radius:999px;padding:3px 10px}
main{max-width:1120px;margin:0 auto;padding:36px 32px 64px}
h1{font-size:36px;letter-spacing:-.9px;margin:0 0 14px;font-weight:700}
.head{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;margin-bottom:32px;flex-wrap:wrap}
.line{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 14px;color:var(--muted);font-size:15px}
.line b{color:var(--ink);font-weight:600}
.line .sep{color:var(--faint)}
.line .missed{display:inline-flex;align-items:baseline;gap:8px;background:var(--red-wash);color:var(--red);border-radius:12px;padding:4px 14px;font-weight:600}
.line .missed b{font-size:34px;color:var(--red);letter-spacing:-1px;line-height:1.1}
.uf{display:flex;align-items:center;gap:10px;background:var(--card);border-radius:12px;padding:10px 14px;box-shadow:0 0 0 1px var(--line);color:var(--ink2)}
.uf b{color:var(--amber);font-size:18px}
.uf .tag{font-size:12px;font-weight:600;color:var(--amber);background:var(--amber-wash);border-radius:999px;padding:2px 9px}
h2{font-size:18px;margin:0 0 14px;font-weight:650}
.grp{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:22px 0 10px}
.grp i{width:10px;height:10px;border-radius:3px;display:inline-block}
.cat{background:var(--card);border-radius:16px;box-shadow:0 1px 2px rgba(15,23,42,.04),0 0 0 1px var(--line);margin-bottom:12px;overflow:hidden}
.cat .top{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:center;padding:18px 22px}
.cat.hi{box-shadow:inset 4px 0 0 var(--hi),0 0 0 1px var(--line)}
.cat .n{font-size:18px;font-weight:650;letter-spacing:-.2px} .cat .d{color:var(--muted);font-size:13px}
.cat .c{font-size:28px;font-weight:700;letter-spacing:-.6px;font-variant-numeric:tabular-nums;text-align:right;line-height:1}
.cat .c small{display:block;font-size:12px;font-weight:500;color:var(--muted);letter-spacing:0;margin-top:4px}
.cat.hi .c{color:var(--hi)} .cat.lo .c{color:var(--lo)} .cat .c.zero{color:var(--faint)}
.car{padding:0 22px 18px}
.carhead{display:flex;justify-content:flex-end;align-items:center;gap:8px;margin:-6px 0 10px;color:var(--faint);font-size:12px}
.arr{width:28px;height:28px;border-radius:50%;box-shadow:0 0 0 1px var(--line);display:grid;place-items:center;background:#fff}
.arr:before{content:"";width:6px;height:6px;border-right:1.5px solid var(--ink2);border-bottom:1.5px solid var(--ink2)}
.arr.l:before{transform:rotate(135deg);margin-left:3px} .arr.r:before{transform:rotate(-45deg);margin-right:3px}
.arr.off{opacity:.4}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.ex{display:flex;flex-direction:column;gap:14px;border-radius:12px;padding:14px 16px;background:var(--bg)}
.cat.hi .ex{background:var(--hi-wash)}
.ex q{color:var(--ink);display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;font-size:13.5px}
.who{display:flex;align-items:center;gap:10px;margin-top:auto}
.av{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;font-size:11px;font-weight:700;color:#fff;background:var(--lo)}
.cat.hi .av{background:var(--hi)}
.who .nm{font-weight:600;font-size:13px;line-height:1.2} .who .dt{color:var(--muted);font-size:12px}
.back{display:inline-flex;align-items:center;gap:8px;color:var(--muted);margin-bottom:18px}
.back:before{content:"";width:7px;height:7px;border-left:1.5px solid var(--muted);border-bottom:1.5px solid var(--muted);transform:rotate(45deg)}
.eyebrow{font-size:13px;color:var(--muted);font-weight:500;margin-bottom:4px}
.ctx{display:grid;grid-template-columns:1fr 1fr 2fr;background:var(--card);border-radius:16px;box-shadow:0 0 0 1px var(--line);margin-bottom:16px}
.ctx > div{padding:16px 20px;border-left:1px solid var(--line)} .ctx > div:first-child{border-left:0}
.ctx .wide{grid-column:1/-1;border-left:0;border-top:1px solid var(--line)}
.ctx .k{font-size:12px;color:var(--faint);font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin-bottom:3px}
.ctx .v{color:var(--ink2)} .ctx .v b{color:var(--ink)}
.tr{background:var(--card);border-radius:16px;box-shadow:0 0 0 1px var(--line);padding:12px 24px 18px}
.turn{display:grid;grid-template-columns:52px 1fr;gap:16px;padding:9px 0}
.turn .t{color:var(--faint);font-variant-numeric:tabular-nums;font-size:13px;padding-top:1px}
.turn .s{font-size:12px;font-weight:600;color:var(--faint);margin-bottom:1px}
.turn.q .x{color:var(--muted)}
.hit{border-radius:12px;background:var(--red-wash);box-shadow:inset 3px 0 0 var(--red);padding:12px 14px}
.hit .tag{display:inline-block;font-size:12px;font-weight:600;color:var(--red);background:#fff;border-radius:999px;padding:2px 10px;margin-bottom:6px}
.notes{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px}
.note{background:#fff;border-radius:10px;padding:10px 12px;box-shadow:0 0 0 1px #f6d4d1}
.note .k{font-size:12px;font-weight:600;color:var(--muted);margin-bottom:2px}
"""
NAV = ('<nav><div class="brand"><svg width="20" height="20" viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="1" width="20" height="20" '
       'rx="6" fill="#0f172a"/><path d="M6 11.5l3 3 7-7" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" '
       'stroke-linejoin="round"/></svg>Content review engine</div><span class="badge">Illustrative</span></nav>')


def page(title, body):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&display=swap" '
            f'rel="stylesheet"><style>{CSS}</style></head><body>{NAV}<main>{body}</main></body></html>')


def cat(name, desc, found, missed, level):
    ex = EXAMPLES[name]
    c = f'<div class="c{" zero" if not missed else ""}">{missed}<small>missed</small></div>'
    out = f'<div class="cat {level}"><div class="top"><div><div class="n">{name}</div><div class="d">{desc}</div></div>{c}</div>'
    if ex:
        cards = []
        for e in ex[:3]:
            href = ' href="2-transcript.html"' if e["source"] == f"test set T{EX}-{EX_TS}" else ""
            cards.append(f'<a class="ex"{href}><q>{html.escape(e["quote"])}</q><div class="who"><span class="av">{initials(e["name"])}</span>'
                         f'<div><div class="nm">{e["name"]}</div><div class="dt">{nice(e["date"])} · {e["ts"]}</div></div></div></a>')
        nav = (f'<div class="carhead">1–{min(3, len(ex))} of {len(ex)}<span class="arr l off"></span>'
               f'<span class="arr r{" off" if len(ex) <= 3 else ""}"></span></div>') if len(ex) > 3 else ""
        out += f'<div class="car">{nav}<div class="cards">{"".join(cards)}</div></div>'
    return out + "</div>"


def summary():
    body = f'''<div class="head"><div><h1>AI performance benchmark</h1>
<div class="line"><span><b>{SAMPLE:,}</b> transcripts</span><span class="sep">·</span><span><b>{FOUND}</b> issues found by human reviewers</span>
<span class="sep">·</span><span>AI caught <b>{CAUGHT}</b></span><span class="missed">missed <b>{MISSED}</b></span></div></div>
<div class="uf"><b>{UNNEEDED}</b> unneeded flags <span class="tag">Operational cost</span></div></div>
<h2>Missed issues by type</h2>
<div class="grp"><i style="background:var(--hi)"></i>High priority</div>{"".join(cat(*r, "hi") for r in HIGH)}
<div class="grp"><i style="background:var(--lo)"></i>Medium and low priority</div>{"".join(cat(*r, "lo") for r in LOWER)}'''
    return page("AI performance benchmark (design)", body)


def transcript():
    t = t5
    name = t["profile"].split(".")[0]
    role = re.sub(r"^[^.]+\.\s*", "", t["profile"]).rsplit(" Industry:", 1)[0]
    turns = []
    for s, who, txt in t["turns"]:
        spk = "Expert" if who == "EXPERT" else "Interviewer"
        if ts(s) == EX_TS:
            x = (f'<div class="hit"><span class="tag">Missed · {EX_TYPE}</span><div>{html.escape(txt)}</div>'
                 f'<div class="notes"><div class="note"><div class="k">Reviewer\'s comment</div>{html.escape(REVIEWER)}</div>'
                 f'<div class="note"><div class="k">Why the AI didn\'t flag it</div>{html.escape(ROOT_CAUSE)}</div></div></div>')
        else:
            x = f'<div class="x">{html.escape(txt)}</div>'
        turns.append(f'<div class="turn{" q" if who != "EXPERT" else ""}"><span class="t">{ts(s)}</span><div><div class="s">{spk}</div>{x}</div></div>')
    body = f'''<a class="back" href="1-summary.html">Benchmark</a>
<div class="eyebrow">Call topic</div><h1 style="font-size:30px">{TOPIC[EX]}</h1>
<div class="ctx"><div><div class="k">Expert</div><div class="v"><b>{name}</b></div></div>
<div><div class="k">Call date</div><div class="v">{nice(EX_DATE)}</div></div>
<div><div class="k">Role</div><div class="v">{html.escape(role)}</div></div>
<div class="wide"><div class="k">Declared</div><div class="v">{html.escape(t["declaration"])}</div></div></div>
<div class="tr">{"".join(turns)}</div>'''
    return page("Transcript (design)", body)


if __name__ == "__main__":
    Path("design/1-summary.html").write_text(summary())
    Path("design/2-transcript.html").write_text(transcript())
    print(f"found {FOUND}, caught {CAUGHT}, missed {MISSED}; unneeded {UNNEEDED}; examples per type: "
          f"{ {k: len(v) for k, v in EXAMPLES.items()} }")
