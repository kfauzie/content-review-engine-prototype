// ILLUSTRATIVE prototype. Headless click-through: loads the page, uses every control, and checks phone and tablet widths
// and a slow first load. Run: node build/check_mvp.js
const { chromium } = require("playwright");
const http = require("http"), fs = require("fs"), path = require("path");
const file = path.join(__dirname, "mvp.html");
const srv = http.createServer((q, r) => { r.writeHead(200, { "Content-Type": "text/html" }); r.end(fs.readFileSync(file)); });
let fail = 0;
const t = (name, ok, got) => { if (!ok) fail++; console.log(`${ok ? "PASS" : "FAIL"} ${name}${got !== undefined ? ": " + got : ""}`); };

(async () => {
  await new Promise(ok => srv.listen(0, ok));
  const url = `http://localhost:${srv.address().port}/`;
  const b = await chromium.launch();
  const errors = [];
  const fresh = async (opts = {}) => {
    const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, ...opts });
    const p = await ctx.newPage();
    p.on("console", m => m.type() === "error" && !/fonts\.(googleapis|gstatic)/.test(m.text()) && errors.push(m.text()));
    p.on("pageerror", e => errors.push(e.message));
    return { ctx, p };
  };

  // slow first load: fonts delayed 1.5 s, fresh profile
  {
    const { ctx, p } = await fresh();
    await p.route(/fonts\.(googleapis|gstatic)\.com/, async r => { await new Promise(s => setTimeout(s, 1500)); r.continue().catch(() => r.abort()); });
    await p.goto(url); await p.waitForSelector('body[data-ready="1"]', { timeout: 8000 });
    t("renders on a slow first load", await p.locator("h1").textContent() === "Content review AI: performance benchmark");
    await ctx.close();
  }

  const { ctx, p } = await fresh();
  const t0 = Date.now();
  await p.goto(url); await p.waitForSelector('body[data-ready="1"]');
  const num = async k => (await p.locator(`[data-n="${k}"]`).first().textContent()).trim();
  t("header numbers: 239 found by AI, 23 missed by AI, 187 false alarms",
    await num("caught") === "239" && await num("missed") === "23" && await num("false") === "187");
  const sizes = await p.evaluate(() => ["caught", "missed", "false"].map(k => parseFloat(getComputedStyle(document.querySelector(`[data-n="${k}"]`)).fontSize)));
  t("missed by AI is the largest number; 239 is a small caption", sizes[1] > sizes[2] && sizes[0] <= 14, sizes.join("/"));
  t("caption under the bar: 239 found by AI", (await p.locator(".risk .cap").textContent()) === "239 found by AI");
  t("no \"Also measured\" label", !(await p.locator("main").textContent()).includes("Also measured"));
  const boxes = await p.evaluate(() => [".risk", ".fa"].map(s => document.querySelector(s).getBoundingClientRect().width));
  t("the compliance zone is bigger than the false alarm zone", boxes[0] > boxes[1] * 1.8, boxes.map(Math.round).join("/"));
  t("compliance heading, larger type", (await p.locator(".kh").textContent()) === "262 compliance risks found in the transcripts" &&
    await p.evaluate(() => parseFloat(getComputedStyle(document.querySelector(".kh")).fontSize)) >= 20);
  t("label: missed by AI", (await p.locator(".risk .lab").allTextContents()).join("|") === "missed by AI");
  t("Liability risk next to 23; Operational cost in the false alarm box",
    (await p.locator(".risk .bigrow .tag").textContent()) === "Liability risk" && (await p.locator(".fa .tag").textContent()) === "Operational cost");
  t("false alarm box shows only 187 false alarms and its description", (await p.locator(".fa .fal").textContent()) === "false alarms" &&
    (await p.locator(".fa .lab").textContent()) === "flagged by AI, marked as non-risk by human reviewers" && await p.locator(".fa .sbar").count() === 0);
  t("no legends, no \"Confirmed\"", await p.locator(".sleg").count() === 0 && !(await p.locator("main").textContent()).includes("Confirmed"));
  t("subtitle", (await p.locator(".sub1").textContent()) === "We compared the content review AI with human reviewers across 1,000 transcripts to see where it misses compliance risks, and where it raises false alarms.");
  t("fix titles", (await p.locator(".fix h3").allTextContents()).join("|") === "Give the AI the expert's declaration|Flag possible insider contacts|Check if the cited source is already public");
  t("recommendation examples show date and call timestamp", (await p.locator('.fix[data-fix="declaration"] .fq .by').first().textContent()) === `${(await p.evaluate(() => JSON.parse(document.getElementById("data").textContent).fixes[0].examples[0].name))} · 4 Nov 2026 · 01:34`);
  t("first example reads as written", (await p.locator('.fix[data-fix="declaration"] .fq').first().textContent()).startsWith("\u201cFor us specifically, we're moving list price up 12% on the mid-market tier from January.\u201d"));
  t("three fixes, each with root cause, examples and next steps", await p.locator(".fix").count() === 3 &&
    (await p.locator(".fix .fl").allTextContents()).join("|") === "Why the AI missed it|Examples|What we'll change|Why the AI missed it|Examples|What we'll change|Why the AI raised a false alarm|Examples|What we'll change" && await p.locator(".fix li").count() === 9);
  t("9 example quotes (3, 2, 4), each highlighted and linking to its transcript", await p.locator(".fix .fq mark").count() === 9 &&
    (await p.locator(".fix a.fq").evaluateAll(a => a.map(x => x.getAttribute("href")))).every(h => /^#t\//.test(h)) &&
    (await p.evaluate(() => [...document.querySelectorAll(".fix")].map(f => f.querySelectorAll(".fq").length).join())) === "3,2,4");
  const fb = await p.evaluate(() => [".risk", ".fa"].map(s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.width, r.height, r.top]; }));
  t("one summary panel: false alarms beside the hero at about 30% width, same row height", fb[1][0] < fb[0][0] / 2 && Math.abs(fb[1][1] - fb[0][1]) < 2 && Math.abs(fb[1][2] - fb[0][2]) < 2,
    fb.map(x => x.slice(0, 2).map(Math.round).join("x")).join(" vs "));
  t("secondary number is at most half the hero number", sizes[2] <= sizes[1] / 2, sizes.join("/"));
  t("section title \"Possible improvements\" with its source subtitle, no estimate note", (await p.locator(".fixes").evaluate(e => e.previousElementSibling.previousElementSibling.textContent)) === "Possible improvements" && await p.locator(".est").count() === 0 &&
    (await p.locator(".secsub").textContent()) === "Based on the human reviewers' comments and an independent review of the AI's logs");
  t("expected impact boxes, no grey placeholders", (await p.locator(".fix .ih").allTextContents()).every(x => x === "Expected impact") &&
    (await p.locator(".fix [data-imp]").allTextContents()).join("|") ===
    "10 fewer risks missed by AI, 7 of them high priority|12 fewer false alarms|11 fewer risks missed by AI|78 fewer false alarms" &&
    !/no change|not estimated/.test(await p.locator(".fixes").textContent()));
  t("category rows: a big number, \"of N\" and \"in this category\" beneath, no bars", await p.locator(".mini").count() === 0 &&
    (await p.locator('[data-cat="missed|Material non-public information"] .c').textContent()) === "5of 38" &&
    (await p.locator('[data-cat="fatype|public-source"] .c').textContent()) === "98of 187" &&
    (await p.locator('[data-cat="fatype|public-source"] .cin').textContent()) === "of all false alarms" &&
    (await p.locator('[data-cat="missed|Material non-public information"] .cin').textContent()) === "in this category");

  const fams = await p.evaluate(() => [...new Set([...document.querySelectorAll("h1,h2,.kh,.n,.fq,.lab,.d")].map(e => getComputedStyle(e).fontFamily.split(",")[0].replace(/["']/g, "").trim()))]);
  t("one font family throughout", fams.length === 1, fams.join(" | "));
  t("category examples are rows: masked expert ID, quote with highlight, date and call time, no names or initials",
    await p.locator(".cat .rx").count() === 41 && await p.locator(".cat .nm, .cat .fq").count() === 0 &&
    (await p.locator(".cat .rx").evaluateAll(a => a.every(x => x.querySelector("mark") && !x.querySelector(".av") &&
      /^Expert \d{4} · \d{1,2} [A-Z][a-z]{2} \d{4} · \d\d:\d\d$/.test(x.querySelector(".when").textContent)))));
  const inView = id => p.evaluate(i => { const r = document.getElementById(i).getBoundingClientRect(); return r.top >= 0 && r.top < innerHeight; }, id);
  await p.locator(".risk.jump").click(); await p.waitForTimeout(900);
  t("clicking the compliance box scrolls to \"Missed by AI, by type\"", await inView("sec-missed"));
  await p.evaluate(() => scrollTo(0, 0)); await p.locator(".fa.jump").click(); await p.waitForTimeout(900);
  t("clicking the false alarm box scrolls to \"False alarms, by type\"", await inView("sec-false"));
  await p.evaluate(() => scrollTo(0, 0)); await p.locator(".risk.jump").focus(); await p.keyboard.press("Enter"); await p.waitForTimeout(900);
  t("Enter on the focused compliance box does the same", await inView("sec-missed"));
  await p.evaluate(() => scrollTo(0, 0));
  const mnpi = p.locator('[data-cat="missed|Material non-public information"]');
  t("MNPI missed lists all 5 examples as rows, no carousel", await mnpi.locator(".rx").count() === 5 && await p.locator(".arr, [data-range]").count() === 0);
  await p.locator('[data-cat="missed|Personal data"] .top').click();
  t("clicking a category hides its tiles", await p.locator('[data-cat="missed|Personal data"] .ex').count() === 0 &&
    (await p.locator('[data-cat="missed|Personal data"] .top').getAttribute("aria-expanded")) === "false");
  await p.keyboard.press("Enter");
  t("Enter on the focused category shows them again", await p.locator('[data-cat="missed|Personal data"] .ex').count() === 7);
  t("declaration conflict (0 missed) has no tiles and no toggle", await p.locator('[data-cat="missed|Declaration conflict"] [data-toggle]').count() === 0);
  t("outside the top categories, only fix examples open a transcript", await p.locator('[data-cat="missed|Personal data"] a.ex').count() === 1 &&
    /^Expert \d{4} · 13 Nov 2026 · 01:24$/.test(await p.locator('[data-cat="missed|Personal data"] a.ex .when').textContent()) && await p.locator('[data-cat="missed|Former-client confidential"] a.ex').count() === 0);
  t("false alarms are grouped by type of false alarm, with examples where there are some",
    (await p.locator('[data-cat^="fatype|"] .n').allTextContents()).join("|") === "Public source cited|The expert's own opinion or estimate|Former employer, left long ago|Public market talk" &&
    await p.locator('[data-cat="fatype|public-source"] a.ex').count() === 7 && await p.locator('[data-cat="fatype|own-view"] .ex').count() === 3 && await p.locator('[data-cat="fatype|own-view"] a.ex').count() === 0 &&
    await p.locator('[data-cat^="false_alarm|"]').count() === 0);

  const links = await p.locator("a.ex").evaluateAll(a => a.map(x => x.getAttribute("href")));
  t("every visible top-category card links to a transcript", links.length >= 12 && links.every(h => /^#t\//.test(h)), `${links.length} links`);
  // open every transcript and check its passage and notes
  const ids = await p.evaluate(() => Object.keys(JSON.parse(document.getElementById("data").textContent).transcripts));
  let okAll = true;
  for (const id of ids) {
    await p.goto(`${url}#t/${id}`); await p.waitForSelector('body[data-view="transcript"]');
    const ok = await p.locator("#passage").count() === 1 && await p.locator(".note.rev").count() === 1 && await p.locator(".note.agent .ns").textContent() === "From an independent review of the AI's log"
      && /^Reviewer \d{4}, [A-Z]/.test(await p.locator(".note.rev .ns").textContent());
    if (!ok) { okAll = false; console.log("  problem in", id); }
  }
  t(`all ${ids.length} transcripts open with the passage, the reviewer's name, title and comment, and the agent analysis`, okAll);

  await p.goto(url); await p.waitForSelector('body[data-view="summary"]');
  await p.locator('[data-cat="missed|Material non-public information"] a.ex').first().click();
  await p.waitForSelector('body[data-view="transcript"]');
  t("clicking a card opens its transcript", (await p.locator(".htag").textContent()).startsWith("Missed · Material non-public information"));
  t("reviewer's comment shows reviewer ID, title, date and time", /^Reviewer \d{4}, [A-Za-z ]+ \(internal\) · \d{1,2} [A-Z][a-z]{2} \d{4}, \d\d:\d\d$/.test(await p.locator(".note.rev .ns").textContent()), await p.locator(".note.rev .ns").textContent());
  t("missed: note titled \"Why the original AI didn't flag it\"", (await p.locator(".note.agent .nt").textContent()) === "Why the original AI didn't flag it");
  t("call context: expert, call date, role, declared", await p.locator(".ctx .k").allTextContents().then(k => k.join("|")) === "Expert|Call date|Role|Declared");
  await p.locator(".back").click(); await p.waitForSelector('body[data-view="summary"]');
  t("back returns to the benchmark", await p.locator("h1").textContent() === "Content review AI: performance benchmark");
  await p.locator('[data-cat="fatype|public-source"] a.ex').first().click();
  await p.waitForSelector('body[data-view="transcript"]');
  t("false alarm: amber passage, note titled \"Why the original AI flagged it\"",
    await p.locator(".hit.false_alarm").count() === 1 && (await p.locator(".note.agent .nt").textContent()) === "Why the original AI flagged it");
  await p.goto(url); await p.waitForSelector('body[data-view="summary"]');
  await p.locator('.fix[data-fix="people"] a.fq').first().click(); await p.waitForSelector('body[data-view="transcript"]');
  t("clicking a fix example opens its transcript", /^Expert \d{4}$/.test(await p.locator(".ctx .v b").textContent()) && (await p.locator(".htag").textContent()) === "Missed · Source disclosure");
  await p.goto(`${url}#t/nope`); await p.waitForSelector('body[data-ready="1"]');
  t("an unknown transcript link says so and offers the way back", (await p.locator(".notfound").count()) === 1);
  t(`main flow in ${((Date.now() - t0) / 1000).toFixed(1)} s`, Date.now() - t0 < 20000);

  for (const [w, h] of [[390, 844], [768, 1024]]) {
    await p.setViewportSize({ width: w, height: h });
    for (const hash of ["", `#t/${ids[0]}`]) {
      await p.goto(url + hash); await p.waitForSelector('body[data-ready="1"]');
      const sw = await p.evaluate(() => document.documentElement.scrollWidth);
      t(`${w}px ${hash ? "transcript" : "benchmark"}: no sideways scrolling`, sw <= w, `${sw}px`);
    }
  }
  await p.setViewportSize({ width: 390, height: 844 }); await p.goto(url); await p.waitForSelector('body[data-ready="1"]');
  t("phone lists every example as a row", await p.locator('[data-cat="missed|Material non-public information"] .rx').count() === 5);

  await p.setViewportSize({ width: 1280, height: 900 }); await p.goto(url); await p.waitForSelector('body[data-ready="1"]');
  t("top bar and badge", (await p.locator(".brand").textContent()) === "Content review engine· AI benchmark" && (await p.locator(".badge").textContent()) === "Illustrative · synthetic data");

  // test a new version against current production
  await p.goto(`${url}#test`); await p.waitForSelector('body[data-view="test"]');
  t("version page: tab, crumb and title", (await p.locator(".brand").textContent()) === "Content review engine· Test a new version" &&
    await p.locator('[data-tab="test"][aria-current]').count() === 1 && (await p.locator("h1").textContent()) === "Test a new version against current production");
  t("no \"release gate\" wording on screen", !/release gate/i.test(await p.locator("body").innerText()));
  t("versions in plain words; v1.1 picked", (await p.locator(".ver").allTextContents()).join("|") ===
    "Current production (v1.0)|New version: reads the expert's declaration (v1.1)|New version: cheaper model (v1.2)" && await p.locator('input[value="v1.1"]').isChecked());
  t("order: picker and Run, the version's description, then the release log", await p.evaluate(() => {
    const y = q => document.querySelector(q).getBoundingClientRect().top; return y(".vers") < y("[data-run]") && y("[data-run]") < y(".about") && y(".about") < y(".log"); }));
  t("no result before a run; log prefilled with v1.0's release", await p.locator("#result").count() === 0 &&
    await p.locator(".log tbody tr").count() === 1 && (await p.locator(".log tbody tr").textContent()).includes("Released"));
  await p.locator("[data-run]").click();
  t("a short loading state while it runs", (await p.locator(".loading").textContent()).includes("Running on 8 transcripts") && await p.locator("[data-run]").isDisabled());
  await p.waitForSelector("#result");
  t("v1.1: green \"Ready for shadow testing\"", (await p.locator(".result.pass .rh").textContent()) === "Ready for shadow testing");
  t("kill-switch copy under the result", (await p.locator(".result .ks").textContent()).startsWith("In production, the same check runs on live spot-checks."));
  t("order: comparison, then results, then the release log", await p.evaluate(() => {
    const y = q => document.querySelector(q).getBoundingClientRect().top; return y(".about") < y("#result") && y("#result") < y(".measure") && y(".measure") < y(".res-list") && y(".res-list") < y(".log"); }));
  const stats = await p.locator(".measure .stat").allTextContents();
  t("misses side by side, every number labelled", stats.slice(0, 4).join("|") === "3 of 7 actual issues caught|4 missed (2 high priority)|7 of 7 actual issues caught|0 missed (0 high priority)", stats.slice(0, 4).join("|"));
  t("false alarms side by side", stats.slice(4).join("|") === "5 false alarms (flagged, but not an issue)|2 false alarms (flagged, but not an issue)", stats.slice(4).join("|"));
  t("misses by issue type underneath, zeros labelled", (await p.locator(".measure").first().locator(".col").nth(1).locator(".tv").allTextContents()).every(x => x === "0 missed"));
  t("false alarms by type of non-issue underneath", (await p.locator(".measure").nth(1).locator(".col").nth(1).locator("li").allTextContents())
    .map(x => x.replace(/Transcript.*/, "").replace(/\s+/g, " ").trim()).join("|") === "Public source cited 1 false alarm|Harmless company mention 1 false alarm|Public market talk 0 false alarms");
  t("results list v1.1's two false alarms with the reasons", await p.locator(".res-row.f").count() === 2 && await p.locator(".res-row.m").count() === 0 &&
    (await p.locator(".res-row.f").first().textContent()).includes("v1.1 said"));
  t("the run is logged: Ready, by Staff 0001 (you)", await p.locator(".log tbody tr").count() === 2 &&
    /Ready.*Staff 0001 \(you\)/.test(await p.locator(".log tbody tr").first().textContent()));
  await p.locator('.ver:has(input[value="v1.2"])').click();
  t("picking v1.2 shows its description", (await p.locator(".about .vd").textContent()) === "The same instructions as v1.1, on a cheaper and faster model.");
  await p.locator("[data-run]").click(); await p.waitForSelector("#result");
  t("v1.2: red \"Not ready: missed MNPI in transcript 5\"", (await p.locator(".result.fail .rh").textContent()) === "Not ready: missed MNPI in transcript 5");
  t("the result links to the passage", (await p.locator(".result .rl a").getAttribute("href")) === "#ts/5/01:24/v1.2");
  await p.locator(".result .rl a").click(); await p.waitForSelector('body[data-view="testset"]');
  t("the passage: missed MNPI, answer key and what v1.2 said", await p.locator("#passage").count() === 1 &&
    (await p.locator(".htag").textContent()) === "Missed · Material non-public information" && (await p.locator(".note.agent").textContent()).includes("Not flagged"));
  t("masked names show as IDs with role tags, tinted by kind", await p.locator(".tr .ent.expert").count() > 0 && await p.locator(".tr .ent.company").count() > 0 &&
    (await p.locator(".legend li").allTextContents()).some(x => /^Company \d{4}listed · expert's former employer \(left March 2026\)$/.test(x)));
  await p.locator(".back").click(); await p.waitForSelector('body[data-view="test"]');
  t("back on the page, the last result is still shown", await p.locator(".result.fail").count() === 1 && await p.locator(".log tbody tr").count() === 3);
  await p.reload(); await p.waitForSelector('body[data-view="test"]');
  t("the log survives a reload", await p.locator(".log tbody tr").count() === 3);
  await p.locator('.ver:has(input[value="v1.0"])').click(); await p.locator("[data-run]").click(); await p.waitForSelector("#result");
  t("v1.0 against itself: not ready on its two high-priority misses, one column",
    (await p.locator(".result.fail .rh").textContent()) === "Not ready: missed current-employer confidential in transcript 3 and MNPI in transcript 5" &&
    await p.locator(".result .rl a").count() === 2 && await p.locator(".measure").first().locator(".col").count() === 1);
  await p.goto(`${url}#ts/9/00:00/v1.1`); await p.waitForSelector('body[data-ready="1"]');
  t("an unknown passage link says so", await p.locator(".notfound").count() === 1);
  await p.goto(`${url}#t/${ids[0]}`); await p.waitForSelector('body[data-view="transcript"]');
  t("transcript notes: human, internal reviewer in green; AI analysis in rose", (await p.locator(".note.rev .nt").textContent()) === "Human reviewer's comment" &&
    /\(internal\) · /.test(await p.locator(".note.rev .ns").textContent()) &&
    await p.evaluate(() => getComputedStyle(document.querySelector(".note.rev")).backgroundColor !== getComputedStyle(document.querySelector(".note.agent")).backgroundColor));
  await p.goto(url); await p.waitForSelector('body[data-view="summary"]');
  t("priority tags on issue types: 3 high, 2 medium, 1 low", (await p.locator("#sec-missed ~ .cat .pri, .sec .cat .pri").allTextContents()).filter(x => x).length >= 6 &&
    await p.locator(".cat .pri.high").count() === 3 && await p.locator(".cat .pri.medium").count() === 2 && await p.locator(".cat .pri.low").count() === 1);
  t("each section sits on a white card", await p.locator(".sec").count() === 3);
  t("purple only on buttons, links and the selected state: none in the benchmark's cards and notes", await p.evaluate(() =>
    [...document.querySelectorAll(".cat, .cat *, .fix, .fix *, .kpis *")].every(e => !/rgb\(91, 70, 194\)/.test(getComputedStyle(e).color + getComputedStyle(e).backgroundColor + getComputedStyle(e).borderLeftColor))));
  for (const [w, h] of [[390, 844], [768, 1024]]) {
    await p.setViewportSize({ width: w, height: h });
    await p.goto(`${url}#test`); await p.waitForSelector('body[data-view="test"]'); await p.locator("[data-run]").click(); await p.waitForSelector("#result");
    let sw = await p.evaluate(() => document.documentElement.scrollWidth);
    t(`${w}px version page after a run: no sideways scrolling`, sw <= w, `${sw}px`);
    await p.goto(`${url}#ts/5/01:24/v1.2`); await p.waitForSelector('body[data-view="testset"]');
    sw = await p.evaluate(() => document.documentElement.scrollWidth);
    t(`${w}px reviewed-transcript passage: no sideways scrolling`, sw <= w, `${sw}px`);
  }
  t("no console errors", errors.length === 0, errors.join(" | ") || "none");
  await ctx.close(); await b.close(); srv.close();
  console.log(fail ? `${fail} FAILED` : "Headless check passes"); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
