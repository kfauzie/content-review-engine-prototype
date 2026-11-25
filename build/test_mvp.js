// ILLUSTRATIVE prototype (synthetic data). Known-answer tests for the numbers, the rules and the data. Run: node build/test_mvp.js
const fs = require("fs"), path = require("path");
const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(__dirname, "mvp.html"), "utf8");
const m = { exports: {} };
new Function("module", html.split('<script id="calc">')[1].split("</script>")[0])(m);
const C = m.exports;
const D = JSON.parse(html.split('<script id="data" type="application/json">')[1].split("</script>")[0].replace(/<\\\//g, "</"));
const FILE = JSON.parse(fs.readFileSync(path.join(root, "data/benchmark.json"), "utf8"));
const SRC = fs.readFileSync(path.join(root, "data/eval/test_set_masked.md"), "utf8");  // the eval and the page only see masked text
const GATE = JSON.parse(fs.readFileSync(path.join(root, "data/eval/release_gate.json"), "utf8"));
let fail = 0;
const t = (name, ok, got) => { if (!ok) fail++; console.log(`${ok ? "PASS" : "FAIL"} ${name}${got !== undefined ? ": " + got : ""}`); };

t("embedded data is exactly data/benchmark.json", JSON.stringify(D) === JSON.stringify(FILE));

// the made-up brief: name, found, missed, false alarms
const BRIEF = [["Material non-public information", 38, 5, 60], ["Current-employer confidential", 52, 4, 30], ["Declaration conflict", 14, 0, 9],
  ["Source disclosure", 29, 4, 8], ["Former-client confidential", 33, 3, 20], ["Personal data", 96, 7, 60]];
BRIEF.forEach(([n, f, mi, fa], i) => { const c = D.categories[i];
  t(`${n}: found ${f}, missed ${mi}, false alarms ${fa}`, c.name === n && c.found === f && c.missed === mi && c.false_alarms === fa); });
t("high priority first: the first three categories", D.categories.slice(0, 3).every(c => c.priority === "high") && D.categories.slice(3).every(c => c.priority !== "high"));

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
t("false alarm cards by issue category: 5, 4, 1, 4, 2, 2 (new examples kept outside the top two, so fix estimates hold)", BRIEF.map(b => count("false_alarm", b[0])).join() === "5,4,1,4,2,2");
const names = D.cards.map(c => c.name);
t("no person appears twice", new Set(names).size === names.length, `${names.length} cards`);
const fixNames = new Set(D.fixes.flatMap(f => f.examples.map(x => x.name)));
t("every top-category card opens a transcript; elsewhere only fix examples do", D.cards.every(c => Boolean(c.transcript) === (D.top.includes(c.category) || fixNames.has(c.name))));
t("20 transcripts, one per clickable card (18 top-category, 2 fix examples)", Object.keys(D.transcripts).length === 20 && D.cards.filter(c => c.transcript).length === 20);
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
  D.cards.filter(c => c.kind === "missed" && !c.fix).length === 2);
t("each fix has a title, a root cause, 2 to 4 examples and three next steps", D.fixes.length === 3 && D.fixes.every(f => f.title && f.root_cause && f.how.length === 3 && f.examples.length >= 2 && f.examples.length <= 4));
t("each fix labels its cause: missed for fixes 1 and 2, false alarm for fix 3", D.fixes.map(f => f.cause_label).join("|") === "Why the AI missed it|Why the AI missed it|Why the AI raised a false alarm");
t("the number of examples varies across fixes (3, 2, 4)", D.fixes.map(f => f.examples.length).join() === "3,2,4");
t("every fix example opens its transcript", D.fixes.every(f => f.examples.every(x => x.transcript && D.transcripts[x.transcript] && D.transcripts[x.transcript].name === x.name)));
t("each fix example quotes its card word for word, highlights a phrase in it, and is tagged to that fix", D.fixes.every(f => f.examples.every(x => {
  const c = D.cards.find(k => k.name === x.name); return c && c.quote === x.quote && c.date === x.date && x.quote.includes(x.highlight) && c.fix === f.id; })));
t("every transcript names its reviewer and title", Object.values(D.transcripts).every(x => /^Reviewer \d{4}, [A-Z]/.test(x.reviewer)));
t("each reviewer comment is timestamped one or two days after the call", Object.values(D.transcripts).every(x => {
  const gap = (new Date(x.reviewed_at.split("T")[0]) - new Date(x.date)) / 864e5; return /^\d{4}-\d\d-\d\dT\d\d:\d\d$/.test(x.reviewed_at) && (gap === 1 || gap === 2); }));
t("each fix example carries its call timestamp, matching its card and transcript passage", D.fixes.every(f => f.examples.every(x =>
  x.ts === D.cards.find(c => c.name === x.name).ts && x.ts === D.transcripts[x.transcript].passage_ts)));
t("date and time format", C.niceDateTime("2026-11-13T11:17") === "13 Nov 2026, 11:17");
t("every card has a highlight that appears word for word in its quote", D.cards.every(c => c.highlight && c.quote.includes(c.highlight)));
t("false alarm types: 98 + 41 + 27 + 21 = 187, the same total as by issue type", D.false_alarm_types.map(x => x.count).join() === "98,41,27,21" &&
  D.false_alarm_types.reduce((s, x) => s + x.count, 0) === C.totals(D).falseAlarms);
t("every false alarm card has a type; examples per type: 7, 3, 4, 4", D.cards.filter(c => c.kind === "false_alarm").every(c => c.fa_type) &&
  D.false_alarm_types.map(x => C.faTypeCards(D, x.id).length).join() === "7,3,4,4");
t("carousel window clamps at the ends", JSON.stringify(C.windowOf(5, 4, 3)) === '{"start":2,"end":5}' && JSON.stringify(C.windowOf(5, -1, 3)) === '{"start":0,"end":3}');
t("three cards on desktop, two on tablet, one on phone", C.perView(1280) === 3 && C.perView(800) === 2 && C.perView(390) === 1);
t("dates", C.niceDate("2026-11-04") === "4 Nov 2026");

// masking: every name is an ID; the same person or company keeps one ID everywhere
const ID = /^(Expert|Person|Reviewer|Company|Client|Staff) \d{4}$/;
t("every card and transcript names the expert by ID", D.cards.every(c => /^Expert \d{4}$/.test(c.name)) && Object.values(D.transcripts).every(x => /^Expert \d{4}$/.test(x.name)));
t("card and transcript links use IDs, not names", D.cards.every(c => /^(missed|false-alarm)-expert-\d{4}$/.test(c.id)));
t("every ID in a transcript carries role tags", [...Object.values(D.transcripts), ...Object.values(D.release.transcripts)].every(x =>
  Object.entries(x.entities).every(([k, v]) => ID.test(k) && v.length > 0)));
const tsx = D.release.transcripts, empOf = n => Object.entries(tsx[n].entities).filter(([, v]) => v.some(z => z.startsWith("expert's"))).map(([k]) => k);
t("the expert's employer keeps its role: transcript 2 'Company, listed, current employer'", Object.entries(tsx[2].entities).some(([k, v]) => k.startsWith("Company") && v.join() === "listed,expert's current employer"));
t("the same company has the same ID in the test set and in the benchmark transcripts", (() => {
  const a = D.transcripts[D.cards.find(c => c.source === "test set T5-01:24").transcript]; return a.declaration === tsx[5].declaration && empOf(5).every(id => a.declaration.includes(id)); })());
t("no emails or phone numbers left", !/[\w.+-]+@[\w-]+\.[\w.]+/.test(JSON.stringify(D)) && !(JSON.stringify(D).match(/\+?\(?\d[\d ()-]{7,}\d/g) || []).some(x => x.replace(/\D/g, "").length >= 9));

// testing a new version: the page's scoring equals the Python eval (notebooks/release_gate.py) for every version
const RL = D.release, srt = a => [...a].sort().join();
RL.versions.forEach(v => {
  const s = C.scoreVersion(RL, v.id), g = C.gateResult(RL, v.id), p = GATE[v.id];
  t(`${v.id}: page scoring equals the Python eval`, s.flags === p.flags && s.caught === p.caught && s.issues === p.issues && s.missed_total === p.missed_total &&
    s.missed_high === p.missed_high && srt(s.false_alarms) === srt(p.false_alarms) && Object.keys(p.missed).every(x => srt(s.missed[x]) === srt(p.missed[x])) &&
    Object.keys(p.false_alarms_by_type).every(x => srt(s.false_alarms_by_type[x]) === srt(p.false_alarms_by_type[x])), JSON.stringify({ caught: s.caught, fa: s.false_alarms.length }));
  t(`${v.id}: result equals the Python eval`, g.passed === p.result.passed && g.headline === p.result.headline && g.reason === p.result.reason && g.links.join() === p.result.links.join(), g.headline);
});
const sc = id => C.scoreVersion(RL, id), faT = id => RL.clean.types.map(t => sc(id).false_alarms_by_type[t.id].length).join();
t("v1.0 (current production): 3 of 7 caught, 4 missed (2 high priority), 5 false alarms (3 public source, 1 harmless mention, 1 market talk)",
  sc("v1.0").caught === 3 && sc("v1.0").missed_total === 4 && sc("v1.0").missed_high === 2 && faT("v1.0") === "3,1,1");
t("v1.1: all 7 caught, 0 missed, 2 false alarms (1 public source, 1 harmless company mention), ready for shadow testing",
  sc("v1.1").caught === 7 && sc("v1.1").missed_total === 0 && faT("v1.1") === "1,1,0" && C.gateResult(RL, "v1.1").headline === "Ready for shadow testing");
t("v1.2: not ready, missed MNPI in transcript 5 (the hedged hint), linked", C.gateResult(RL, "v1.2").headline === "Not ready: missed MNPI in transcript 5" &&
  C.gateResult(RL, "v1.2").links.join() === "T5-01:24");
t("every flagged clean answer has a reviewer note saying why it is not an issue", RL.versions.every(v => sc(v.id).false_alarms.every(a => RL.clean.answers[a] && RL.clean.answers[a].note)));
t("version labels in plain words", RL.versions.map(v => v.label).join("|") === "Current production (v1.0)|New version: reads the expert's declaration (v1.1)|New version: cheaper model (v1.2)");
t("every version's outputs cover every expert answer and are labelled simulated", RL.versions.every(v => RL.answers.every(a => v.outputs[a])) && /SIMULATED/.test(RL.note));
t("v1.2 differs from v1.1 only on T5-01:24", RL.answers.filter(a => JSON.stringify(RL.versions[1].outputs[a]) !== JSON.stringify(RL.versions[2].outputs[a])).join() === "T5-01:24");
t("release log is prefilled with v1.0's release", RL.log.length === 1 && RL.log[0].version === "v1.0" && ID.test(RL.log[0].by));
t("kill-switch copy under the result", html.includes("In production, the same check runs on live spot-checks. A miss in a high-priority type triggers the kill switch, and that type goes back to full human review."));
t("the term \"release gate\" isn't shown anywhere on the page", !/release gate/i.test(html.replace(/<script id="data"[\s\S]*?<\/script>/, "").replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "")));
t("reviewers are internal", Object.values(D.transcripts).every(x => /\(internal\)$/.test(x.reviewer)));
t("no reviewer comment names the company we work for", Object.values(D.transcripts).every(x => !/dialectica/i.test(x.reviewer_comment)));
t("priorities: three high, two medium, one low", D.categories.map(c => c.priority).join() === "high,high,high,medium,low,medium");

const text = html.replace(/<script id="data"[\s\S]*?<\/script>/, "") + JSON.stringify(D);
t("no em or en dashes", !/[—]/.test(text) && !/–/.test(html.replace(/<script id="data"[\s\S]*?<\/script>/, "").replace(/\$\{w\.start \+ 1\}–/g, "")));
t("no 'real issues', percentages or status verdicts in the page's own copy",
  !/real issues|miss rate|not cautious enough|needs more evidence|unneeded/i.test(html.replace(/<script id="data"[\s\S]*?<\/script>/, "")));
t("wording: no \"Confirmed\", no \"Operational risk\"", !/Confirmed|confirmed|Operational risk/.test(html.replace(/<script id="data"[\s\S]*?<\/script>/, "")));
t("synthetic data is labelled on screen", html.includes('<span class="badge">Illustrative · synthetic data</span>'));
console.log(fail ? `${fail} FAILED` : "All tests pass"); process.exit(fail ? 1 : 0);
