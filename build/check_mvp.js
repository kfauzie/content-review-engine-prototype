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
    t("renders on a slow first load", await p.locator("h1").textContent() === "AI performance benchmark");
    await ctx.close();
  }

  const { ctx, p } = await fresh();
  const t0 = Date.now();
  await p.goto(url); await p.waitForSelector('body[data-ready="1"]');
  const num = async k => (await p.locator(`[data-n="${k}"]`).first().textContent()).trim();
  t("header numbers: 239 found by AI, 23 missed by AI, 187 false alarms",
    await num("caught") === "239" && await num("missed") === "23" && await num("false") === "187");
  const sizes = await p.evaluate(() => ["caught", "missed", "false"].map(k => parseFloat(getComputedStyle(document.querySelector(`[data-n="${k}"]`)).fontSize)));
  t("missed by AI is the largest number", sizes[1] > sizes[0] && sizes[1] > sizes[2], sizes.join("/"));
  const boxes = await p.evaluate(() => [".risk", ".fa"].map(s => document.querySelector(s).getBoundingClientRect().width));
  t("the compliance box is bigger than the false alarm box", boxes[0] > boxes[1] * 1.4, boxes.map(Math.round).join("/"));
  t("compliance heading, larger type", (await p.locator(".kh").textContent()) === "Compliance risks found in transcripts" &&
    await p.evaluate(() => parseFloat(getComputedStyle(document.querySelector(".kh")).fontSize)) >= 20);
  t("labels: found by AI, missed by AI", (await p.locator(".risk .lab").allTextContents()).join("|") === "found by AI|missed by AI");
  t("Liability risk next to 23; Operational cost in the false alarm box",
    (await p.locator(".risk .bigrow .tag").textContent()) === "Liability risk" && (await p.locator(".fa .tag").textContent()) === "Operational cost");
  t("false alarm box shows only 187 false alarms and its description", (await p.locator(".fa .fal").textContent()) === "false alarms" &&
    (await p.locator(".fa .lab").textContent()) === "flagged by AI, marked as non-risk by human reviewers" && await p.locator(".fa .sbar").count() === 0);
  t("no legends, no \"Confirmed\"", await p.locator(".sleg").count() === 0 && !(await p.locator("main").textContent()).includes("Confirmed"));
  t("subtitle", (await p.locator(".sub1").textContent()) === "We compared AI and human review across 1,000 transcripts to see where the AI misses compliance risks, and where it raises false alarms");
  t("three fixes, each with root cause, examples and next steps", await p.locator(".fix").count() === 3 &&
    (await p.locator(".fix").first().locator(".fl").allTextContents()).join("|") === "Root cause|Examples|Next steps" && await p.locator(".fix li").count() === 9);
  t("9 example quotes (3, 2, 4), each highlighted and linking to its transcript", await p.locator(".fix .fq mark").count() === 9 &&
    (await p.locator(".fix a.fq").evaluateAll(a => a.map(x => x.getAttribute("href")))).every(h => /^#t\//.test(h)) &&
    (await p.evaluate(() => [...document.querySelectorAll(".fix")].map(f => f.querySelectorAll(".fq").length).join())) === "3,2,4");
  const fb = await p.evaluate(() => [".risk", ".fa"].map(s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.width, r.height]; }));
  t("false alarm box is much smaller: under half the width and shorter", fb[1][0] < fb[0][0] / 2 && fb[1][1] < fb[0][1], fb.map(x => x.map(Math.round).join("x")).join(" vs "));
  t("expected impact boxes, no grey placeholders", (await p.locator(".fix .ih").allTextContents()).every(x => x === "Expected impact") &&
    (await p.locator(".fix [data-imp]").allTextContents()).join("|") ===
    "Reduces missed by AI by 107 high priority|Cuts false alarms by 12|Reduces missed by AI by 11|Cuts false alarms by 78" &&
    !/no change|not estimated/.test(await p.locator(".fixes").textContent()));
  t("category rows: a big number, \"of N\" and \"in this category\" beneath, no bars", await p.locator(".mini").count() === 0 &&
    (await p.locator('[data-cat="missed|Material non-public information"] .c').textContent()) === "5of 38" &&
    (await p.locator('[data-cat="false_alarm|Material non-public information"] .c').textContent()) === "60of 93" &&
    (await p.locator('[data-cat="missed|Material non-public information"] .cin').textContent()) === "in this category");

  const mnpi = p.locator('[data-cat="missed|Material non-public information"]');
  t("MNPI missed shows 3 of its 5 cards", await mnpi.locator(".ex").count() === 3 && (await mnpi.locator("[data-range]").textContent()) === "1–3 of 5");
  await mnpi.locator('.arr.r').click();
  t("next arrow moves the carousel by one", (await p.locator('[data-cat="missed|Material non-public information"] [data-range]').textContent()) === "2–4 of 5");
  await p.locator('[data-cat="missed|Material non-public information"] .arr.r').click();
  t("last page disables next", await p.locator('[data-cat="missed|Material non-public information"] .arr.r').isDisabled());
  await p.locator('[data-cat="missed|Material non-public information"] .arr.l').click();
  t("previous arrow moves back", (await p.locator('[data-cat="missed|Material non-public information"] [data-range]').textContent()) === "2–4 of 5");

  await p.locator('[data-cat="missed|Personal data"] .top').click();
  t("clicking a category hides its tiles", await p.locator('[data-cat="missed|Personal data"] .ex').count() === 0 &&
    (await p.locator('[data-cat="missed|Personal data"] .top').getAttribute("aria-expanded")) === "false");
  await p.keyboard.press("Enter");
  t("Enter on the focused category shows them again", await p.locator('[data-cat="missed|Personal data"] .ex').count() === 3);
  t("declaration conflict (0 missed) has no tiles and no toggle", await p.locator('[data-cat="missed|Declaration conflict"] [data-toggle]').count() === 0);
  t("outside the top categories, only fix examples open a transcript", await p.locator('[data-cat="missed|Personal data"] a.ex').count() === 1 &&
    (await p.locator('[data-cat="missed|Personal data"] a.ex .nm').textContent()) === "Hannah Booth" && await p.locator('[data-cat="missed|Former-client confidential"] a.ex').count() === 0);
  t("false alarms: top two have carousels, the rest show counts only",
    await p.locator('[data-cat="false_alarm|Material non-public information"] a.ex').count() === 3 && await p.locator('[data-cat="false_alarm|Personal data"] .ex').count() === 0);

  const links = await p.locator("a.ex").evaluateAll(a => a.map(x => x.getAttribute("href")));
  t("every visible top-category card links to a transcript", links.length >= 12 && links.every(h => /^#t\//.test(h)), `${links.length} links`);
  // open every transcript and check its passage and notes
  const ids = await p.evaluate(() => Object.keys(JSON.parse(document.getElementById("data").textContent).transcripts));
  let okAll = true;
  for (const id of ids) {
    await p.goto(`${url}#t/${id}`); await p.waitForSelector('body[data-view="transcript"]');
    const ok = await p.locator("#passage").count() === 1 && await p.locator(".note.rev").count() === 1 && await p.locator(".note.agent .ns").textContent() === "Analysis by an independent agent, from the original AI's log"
      && /^[A-Z][a-z]+ [A-Z][a-z]+, [A-Z]/.test(await p.locator(".note.rev .ns").textContent());
    if (!ok) { okAll = false; console.log("  problem in", id); }
  }
  t(`all ${ids.length} transcripts open with the passage, the reviewer's name, title and comment, and the agent analysis`, okAll);

  await p.goto(url); await p.waitForSelector('body[data-view="summary"]');
  await p.locator('[data-cat="missed|Material non-public information"] a.ex').first().click();
  await p.waitForSelector('body[data-view="transcript"]');
  t("clicking a card opens its transcript", (await p.locator(".htag").textContent()).startsWith("Missed · Material non-public information"));
  t("missed: note titled \"Why the original AI didn't flag it\"", (await p.locator(".note.agent .nt").textContent()) === "Why the original AI didn't flag it");
  t("call context: expert, call date, role, declared", await p.locator(".ctx .k").allTextContents().then(k => k.join("|")) === "Expert|Call date|Role|Declared");
  await p.locator(".back").click(); await p.waitForSelector('body[data-view="summary"]');
  t("back returns to the benchmark", await p.locator("h1").textContent() === "AI performance benchmark");
  await p.locator('[data-cat="false_alarm|Current-employer confidential"] a.ex').first().click();
  await p.waitForSelector('body[data-view="transcript"]');
  t("false alarm: amber passage, note titled \"Why the original AI flagged it\"",
    await p.locator(".hit.false_alarm").count() === 1 && (await p.locator(".note.agent .nt").textContent()) === "Why the original AI flagged it");
  await p.goto(url); await p.waitForSelector('body[data-view="summary"]');
  await p.locator('.fix[data-fix="people"] a.fq').first().click(); await p.waitForSelector('body[data-view="transcript"]');
  t("clicking a fix example opens its transcript", (await p.locator(".ctx .v b").textContent()) === "Elena Vasquez" && (await p.locator(".htag").textContent()) === "Missed · Source disclosure");
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
  t("phone shows one card at a time", await p.locator('[data-cat="missed|Material non-public information"] .ex').count() === 1);

  t("no console errors", errors.length === 0, errors.join(" | ") || "none");
  await ctx.close(); await b.close(); srv.close();
  console.log(fail ? `${fail} FAILED` : "Headless check passes"); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
