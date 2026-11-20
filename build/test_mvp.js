// ILLUSTRATIVE prototype (synthetic data). Known-answer tests for the numbers, the rules and the data. Run: node build/test_mvp.js
const fs = require("fs"), path = require("path");
const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(__dirname, "mvp.html"), "utf8");
const m = { exports: {} };
new Function("module", html.split('<script id="calc">')[1].split("</script>")[0])(m);
const C = m.exports;
const D = JSON.parse(html.split('<script id="data" type="application/json">')[1].split("</script>")[0].replace(/<\\\//g, "</"));
const FILE = JSON.parse(fs.readFileSync(path.join(root, "data/benchmark.json"), "utf8"));
const SRC = fs.readFileSync(path.join(root, "data/synthetic-expert-transcripts.md"), "utf8");
let fail = 0;
const t = (name, ok, got) => { if (!ok) fail++; console.log(`${ok ? "PASS" : "FAIL"} ${name}${got !== undefined ? ": " + got : ""}`); };

t("embedded data is exactly data/benchmark.json", JSON.stringify(D) === JSON.stringify(FILE));

// the made-up brief: name, found, missed, false alarms
const BRIEF = [["Material non-public information", 38, 5, 60], ["Current-employer confidential", 52, 4, 30], ["Declaration conflict", 14, 0, 9],
  ["Source disclosure", 29, 4, 8], ["Former-client confidential", 33, 3, 20], ["Personal data", 96, 7, 60]];
BRIEF.forEach(([n, f, mi, fa], i) => { const c = D.categories[i];
  t(`${n}: found ${f}, missed ${mi}, false alarms ${fa}`, c.name === n && c.found === f && c.missed === mi && c.false_alarms === fa); });
t("high priority first: the first three categories", D.categories.slice(0, 3).every(c => c.priority === "high") && D.categories.slice(3).every(c => c.priority === "lower"));

const T = C.totals(D);
t("1,000 transcripts", T.sample === 1000, T.sample);
t("262 compliance risks found by human reviewers", T.found === 262, T.found);
t("239 caught by AI = 262 - 23", T.caught === 239, T.caught);
t("23 missed by AI", T.missed === 23, T.missed);
t("187 false alarms", T.falseAlarms === 187, T.falseAlarms);
t("426 AI flags = 239 confirmed + 187 false alarms", T.flags === 426, T.flags);
t("9 high-priority misses = 5 + 4 + 0", T.highMissed === 9, T.highMissed);

const miss = C.rows(D, "missed"), fa = C.rows(D, "false_alarm");
t("missed rows: base is caught, count is missed", miss.every((r, i) => r.base === BRIEF[i][1] - BRIEF[i][2] && r.count === BRIEF[i][2]));
t("false alarm rows: base is confirmed, count is false alarms", fa.every((r, i) => r.base === BRIEF[i][1] - BRIEF[i][2] && r.count === BRIEF[i][3]));
t("bar scale for misses is the biggest category (personal data, 96)", C.barScale(miss) === 96, C.barScale(miss));
t("bar scale for false alarms is 89 + 60 = 149 (personal data)", C.barScale(fa) === 149, C.barScale(fa));

t("no data problems", C.problems(D).length === 0, C.problems(D).join("; ") || "none");
const count = (kind, cat) => C.cardsFor(D, kind, cat).length;
t("missed cards: 5, 4, 0, 4, 3, 7 (one per miss)", BRIEF.map(b => count("missed", b[0])).join() === "5,4,0,4,3,7");
t("false alarm cards: 5 and 4 in the top two categories, none elsewhere", BRIEF.map(b => count("false_alarm", b[0])).join() === "5,4,0,0,0,0");
const names = D.cards.map(c => c.name);
t("no person appears twice", new Set(names).size === names.length, `${names.length} cards`);
t("only top-category cards open a transcript, and all of them do", D.cards.every(c => Boolean(c.transcript) === D.top.includes(c.category)));
t("18 transcripts, one per clickable card", Object.keys(D.transcripts).length === 18 && D.cards.filter(c => c.transcript).length === 18);
t("test-set quotes are word for word from the test set", D.cards.filter(c => c.source.startsWith("test set")).every(c => SRC.includes(c.quote)));
t("test-set transcripts match the test set turn for turn", Object.values(D.transcripts).filter(x => x.source.startsWith("test set")).every(x =>
  x.turns.every(u => SRC.includes(`[${u.ts}] ${u.speaker}: ${u.text}`))));
Object.values(D.transcripts).forEach(x => {
  const ts = x.turns.map(u => u.ts);
  t(`${x.name}: timestamps increase, passage is an expert turn, notes present`, ts.every((v, i) => i === 0 || v > ts[i - 1]) &&
    x.turns.find(u => u.ts === x.passage_ts)?.speaker === "EXPERT" && x.reviewer_comment && x.root_cause && x.declaration && x.role);
});

const imp = C.fixImpact(D);
t("fix 1, declaration and question: 10 fewer misses (7 high priority), about 12 fewer false alarms (60 x 1/5)",
  imp[0].id === "declaration" && imp[0].missed === 10 && imp[0].highMissed === 7 && imp[0].falseAlarms === 12, JSON.stringify(imp[0]));
t("fix 2, people and sources: 11 fewer misses, false alarms not estimated (no examples)",
  imp[1].id === "people" && imp[1].missed === 11 && imp[1].falseAlarms === null, JSON.stringify(imp[1]));
t("fix 3, cited sources: no change to misses, about 78 fewer false alarms (60 x 4/5 + 30 x 4/4)",
  imp[2].id === "sources" && imp[2].missed === 0 && imp[2].falseAlarms === 78, JSON.stringify(imp[2]));
t("the fixes never claim more misses than exist, and 2 misses stay uncovered", imp.reduce((s, x) => s + x.missed, 0) === 21 &&
  D.cards.filter(c => c.kind === "missed" && !c.fix).map(c => c.name).join() === "Mateo Alvarez,Siobhan Kelly");
t("each fix has a title, a why and three how steps", D.fixes.length === 3 && D.fixes.every(f => f.title && f.why && f.how.length === 3));
t("every transcript names its reviewer and title", Object.values(D.transcripts).every(x => /^[A-Z][a-z]+ [A-Z][a-z]+, [A-Z]/.test(x.reviewer)));
t("carousel window clamps at the ends", JSON.stringify(C.windowOf(5, 4, 3)) === '{"start":2,"end":5}' && JSON.stringify(C.windowOf(5, -1, 3)) === '{"start":0,"end":3}');
t("three cards on desktop, two on tablet, one on phone", C.perView(1280) === 3 && C.perView(800) === 2 && C.perView(390) === 1);
t("initials and dates", C.initials("Mei Lin Tan") === "ML" && C.niceDate("2026-11-04") === "4 Nov 2026");

const text = html.replace(/<script id="data"[\s\S]*?<\/script>/, "") + JSON.stringify(D);
t("no em or en dashes", !/[—]/.test(text) && !/–/.test(html.replace(/<script id="data"[\s\S]*?<\/script>/, "").replace(/\$\{w\.start \+ 1\}–/, "")));
t("no 'real issues', percentages or status verdicts in the page's own copy",
  !/real issues|miss rate|not cautious enough|needs more evidence|unneeded/i.test(html.replace(/<script id="data"[\s\S]*?<\/script>/, "")));
t("wording: no \"Confirmed\", no \"Operational risk\"", !/Confirmed|confirmed|Operational risk/.test(html.replace(/<script id="data"[\s\S]*?<\/script>/, "")));
t("synthetic data is labelled on screen", html.includes('<span class="badge">Illustrative</span>'));
console.log(fail ? `${fail} FAILED` : "All tests pass"); process.exit(fail ? 1 : 0);
