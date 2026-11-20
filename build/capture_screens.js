// ILLUSTRATIVE prototype. Saves screenshots of the main states for review. Run: node build/capture_screens.js <outdir> [scale]
const { chromium } = require("playwright"); const http = require("http"), fs = require("fs"), path = require("path");
const out = path.resolve(process.argv[2] || "screens"), scale = +(process.argv[3] || 1);
fs.mkdirSync(out, { recursive: true });
const srv = http.createServer((q, r) => { r.writeHead(200, { "Content-Type": "text/html" }); r.end(fs.readFileSync(path.join(__dirname, "mvp.html"))); });
(async () => {
  await new Promise(ok => srv.listen(0, ok)); const url = `http://localhost:${srv.address().port}/`;
  const b = await chromium.launch();
  for (const [name, w, h] of [["desktop", 1280, 900], ["tablet", 768, 1024], ["phone", 390, 844]]) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale, reducedMotion: "reduce" });
    await p.goto(url); await p.waitForSelector('body[data-ready="1"]'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    await p.screenshot({ path: path.join(out, `${name}-benchmark.png`), fullPage: true });
    const id = await p.locator('[data-cat="missed|Material non-public information"] a.ex').first().getAttribute("href");
    await p.goto(url + id); await p.waitForSelector('body[data-view="transcript"]'); await p.waitForTimeout(400);
    await p.screenshot({ path: path.join(out, `${name}-transcript.png`), fullPage: true });
  }
  const p = await b.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: scale, reducedMotion: "reduce" });
  await p.goto(url + "#t/false-alarm-chloe-martin"); await p.waitForSelector('body[data-view="transcript"]'); await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(out, "desktop-false-alarm.png"), fullPage: true });
  console.log("saved to", out); await b.close(); srv.close();
})();
