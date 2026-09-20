/* Real-browser release gate: inspect final row coverage, not even card counts. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const selectors = '.fc-resource-grid,.fc-study-grid,.ask-continue-grid,.fc-voice-grid,.gc-pathways,.fc-talk-list';
const pages = [...fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)]
  .map(m => new URL(m[1]).pathname.slice(1) || 'index.html')
  .filter(p => /class="[^"]*\b(?:fc-resource-grid|fc-study-grid|ask-continue-grid|fc-voice-grid|gc-pathways|fc-talk-list)\b/.test(fs.readFileSync(path.join(root, p), 'utf8')));

function measure(selector) {
  return [...document.querySelectorAll(selector)].flatMap(grid => {
    const cards = [...grid.children].map(n => n.getBoundingClientRect()).filter(r => r.width && r.height);
    if (cards.length < 2 || !['grid','flex'].includes(getComputedStyle(grid).display)) return [];
    const lastTop = Math.max(...cards.map(r => r.top));
    // Mixed figure/article cards may have different top margins within one row.
    const last = cards.filter(r => r.top <= lastTop + 3 && r.bottom > lastTop + 3);
    const rect = grid.getBoundingClientRect(), style = getComputedStyle(grid);
    const left = rect.left + parseFloat(style.borderLeftWidth) + parseFloat(style.paddingLeft);
    const right = rect.right - parseFloat(style.borderRightWidth) - parseFloat(style.paddingRight);
    const uncovered = Math.max(Math.min(...last.map(r => r.left)) - left, right - Math.max(...last.map(r => r.right)));
    return [{className: grid.className, cards: cards.length, uncovered, overflow: Math.max(...cards.map(r => r.right)) - right}];
  });
}

(async () => {
  const server = http.createServer((req, res) => {
    const filename = path.resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
    if (!filename.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
    const types = {'.html':'text/html', '.css':'text/css', '.js':'text/javascript', '.json':'application/json', '.webp':'image/webp', '.svg':'image/svg+xml'};
    fs.readFile(filename, (error, data) => { if (error) res.writeHead(404).end(); else res.writeHead(200, {'Content-Type':types[path.extname(filename)] || 'application/octet-stream'}).end(data); });
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage();
    const origin = `http://127.0.0.1:${server.address().port}`;
    let checked = 0;
    async function check(url, width) {
      await page.setViewportSize({width, height:1000});
      await page.goto(origin + '/' + url, {waitUntil:'load'});
      await page.evaluate(() => document.querySelectorAll('details[data-conference-session]').forEach(n => { n.open = true; }));
      await page.evaluate(() => document.fonts.ready);
      const rows = await page.evaluate(measure, selectors);
      assert(rows.length, `${url}: no rendered grid coverage`);
      for (const row of rows) {
        assert(row.uncovered <= 3, `${url} @${width}: incomplete final row ${JSON.stringify(row)}`);
        assert(row.overflow <= 3, `${url} @${width}: overflowing row ${JSON.stringify(row)}`);
        checked++;
      }
    }
    for (const width of [1366,900,600,390]) for (const url of pages) await check(url, width);
    for (const width of [520,521,700,701,1000,1001,1050,1051]) {
      for (const url of ['ask.html','general-conference.html','answers/stand-forever.html','answers/settle-this-in-your-hearts.html']) await check(url, width);
    }
    // Prove that deleting the repair produces the owner's exact regression.
    await page.setViewportSize({width:1366,height:1000});
    await page.goto(origin + '/answers/settle-this-in-your-hearts.html', {waitUntil:'load'});
    await page.evaluate(() => document.querySelector('link[href*="complete-card-rows.css"]').remove());
    const broken = await page.evaluate(measure, '#companion-messages .fc-resource-grid');
    assert(broken.some(row => row.uncovered > 100), 'Negative fixture failed to detect the stranded third card');
    console.log(`PASS: ${pages.length} pages, ${checked} rendered grids, responsive boundaries and removed-repair negative fixture`);
  } finally { await browser.close(); await new Promise(resolve => server.close(resolve)); }
})().catch(error => { console.error(error); process.exitCode = 1; });
