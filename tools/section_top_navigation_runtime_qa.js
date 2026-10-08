// Actual native clicks must land at the beginning of the visible subject.
// This complements anchor CSS byte bindings and the controller unit tests.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const cases = [
  ['index.html', '.fc-unified-continue', '#fc-opening-retained'],
  ['church-history.html', '.fc-history-topic-links a[href="#history-first-vision-title"]', '[data-fc-section-start="history-first-vision-title"]'],
  ['church-history.html', '.fc-history-topic-links a[href="#history-harmony-title"]', '[data-fc-section-start="history-harmony-title"]'],
  ['church-history.html', '.fc-history-topic-links a[href="#history-bom-evidence-title"]', '[data-fc-section-start="history-bom-evidence-title"]'],
  ['church-history.html', '.fc-history-topic-links a[href="#joseph-likeness-entry"]', '[data-fc-section-start="joseph-likeness-entry"]'],
  ['general-conference.html', 'a[href="#conference-april-2026"]', '#conference-april-2026'],
  ['timelines/latter-day-saint-church-history-timeline.html', '.timeline-opening-continue', null],
  ['timelines/willie-and-martin-handcart-map.html', '.timeline-opening-continue', null],
  ['timelines/life-of-christ-journey-map.html', '.timeline-opening-continue', null],
  ['answers/what-is-the-book-of-mormon.html', '.fc-unified-continue', null],
  ['art-study/the-living-christ.html', '.fc-unified-continue', null],
  ['pioneers.html', '.fc-unified-continue', null],
  ['come-follow-me.html', '.fc-unified-continue', null],
  ['joseph-smith-likeness.html', '.fc-unified-continue', null],
];
function measure(selector) {
  const target = document.querySelector(selector);
  if (!target) return { missing: selector };
  const rect = target.getBoundingClientRect();
  const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
  const fixed = header && ['fixed', 'sticky'].includes(getComputedStyle(header).position);
  const offset = (fixed ? Math.ceil(header.getBoundingClientRect().height) : 0) + 16;
  const maximum = Math.max(0, document.documentElement.scrollHeight - innerHeight);
  const expectedScroll = Math.max(0, Math.min(scrollY + rect.top - offset, maximum));
  return { top: rect.top, offset, scroll: scrollY, maximum, expectedScroll,
    error: Math.abs(scrollY - expectedScroll), visible: rect.height > 0,
    overflow: document.documentElement.scrollWidth > innerWidth + 1 };
}
const server = http.createServer((req, res) => {
  const file = path.resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
  if (!file.startsWith(root + path.sep)) return res.writeHead(403).end();
  fs.readFile(file, (error, data) => {
    if (error) return res.writeHead(404).end();
    const types = { '.html':'text/html; charset=utf-8', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.webp':'image/webp', '.png':'image/png', '.jpg':'image/jpeg' };
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' }).end(data);
  });
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless:true, ...(process.env.QA_BROWSER_CHANNEL ? {channel:process.env.QA_BROWSER_CHANNEL} : {}) });
  const records = [], special = [];
  try {
    for (const [width, height] of [[1366,900], [390,844], [320,740]]) {
      const page = await browser.newPage({ viewport:{width,height}, reducedMotion:'reduce' });
      await page.route('https://**', route => route.abort());
      for (const [route, linkSelector, destination] of cases) {
        await page.goto(`${base}/${route}`, { waitUntil:'load' });
        await page.evaluate(() => document.fonts.ready);
        const link = page.locator(linkSelector).filter({visible:true}).first();
        await link.waitFor();
        const selector = destination || await link.getAttribute('href');
        await link.click();
        await page.waitForTimeout(950);
        const record = { route, width, height, selector, ...await page.evaluate(measure, selector) };
        records.push(record);
        assert(record.visible && record.error <= 1.5 && !record.overflow, JSON.stringify(record));
        // Repeated same-hash navigation must align again without creating history.
        if (route === 'church-history.html') {
          const historyLength = await page.evaluate(() => history.length);
          await page.mouse.wheel(0, 250);
          await link.click();
          await page.waitForTimeout(950);
          const repeated = await page.evaluate(measure, selector);
          assert(repeated.error <= 1.5, JSON.stringify(repeated));
          assert.equal(await page.evaluate(() => history.length), historyLength);
          special.push({ kind:'repeat-hash', route, width, selector, ...repeated });
        }
      }
      // Fresh cross-page bookmark loads use the same explicit subject mapping.
      await page.goto(`${base}/church-history.html#history-first-vision-title`, {waitUntil:'load'});
      await page.waitForTimeout(950);
      const deep = await page.evaluate(measure, '[data-fc-section-start="history-first-vision-title"]');
      assert(deep.error <= 1.5, JSON.stringify(deep));
      special.push({kind:'deep-link', width, ...deep});
      // Actual user movement must cancel the bounded settling, without a snap back.
      await page.goto(`${base}/church-history.html`, {waitUntil:'load'});
      await page.locator('.fc-history-topic-links a[href="#history-first-vision-title"]').click();
      await page.waitForTimeout(80);
      await page.mouse.wheel(0, 250);
      await page.waitForTimeout(80);
      const afterWheel = await page.evaluate(() => scrollY);
      await page.waitForTimeout(950);
      assert(Math.abs(await page.evaluate(() => scrollY) - afterWheel) <= 1.5, 'Settling must not fight user scrolling');
      special.push({kind:'user-scroll-cancellation', width, afterWheel});
      // Same-document browser Back retains its native fragment restoration.
      // Programmatic fragment changes remain owned by the page controller.
      await page.evaluate(() => { location.hash = '#history-harmony-title'; });
      await page.waitForTimeout(950);
      const controlled = await page.evaluate(measure, '[data-fc-section-start="history-harmony-title"]');
      assert(controlled.error > 20, 'Programmatic fragment ownership must remain native');
      await page.goBack();
      await page.waitForTimeout(950);
      const restored = await page.evaluate(() => {
        const heading = document.getElementById('history-first-vision-title');
        return { hash:location.hash, top:heading.getBoundingClientRect().top,
          nativeMargin:parseFloat(getComputedStyle(heading).scrollMarginTop), scroll:scrollY };
      });
      assert.equal(restored.hash, '#history-first-vision-title');
      assert(Math.abs(restored.top - restored.nativeMargin) <= 1.5, JSON.stringify(restored));
      special.push({kind:'native-back-and-controller-ownership', width, ...restored});
      await page.close();
    }
    // A negative fixture removes the repair and reproduces the sticky-header bug.
    const page = await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
    await page.route('https://**', route => route.abort());
    await page.route('**/header-scroll.js*', route => route.fulfill({contentType:'text/javascript',body:'/* prior native landing, no correction */'}));
    await page.goto(`${base}/timelines/latter-day-saint-church-history-timeline.html`, {waitUntil:'load'});
    const negativeSelector = await page.locator('.timeline-opening-continue').getAttribute('href');
    await page.locator('.timeline-opening-continue').click();
    await page.waitForTimeout(950);
    const negative = await page.evaluate(measure, negativeSelector);
    assert(negative.error > 20, 'Negative baseline must fail the landing geometry oracle');
    special.push({kind:'prior-landing-negative', ...negative});
    await page.close();
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
    const dir = process.env.QA_REPORT_DIR || path.join(root, '.qa-artifacts');
    fs.mkdirSync(dir, {recursive:true});
    fs.writeFileSync(path.join(dir, 'section-top-navigation.json'), JSON.stringify({records,special}, null, 2));
  }
  console.log(`SECTION TOP NAVIGATION PASS: ${records.length} landing cases, ${special.length} history/deep-link/cancellation/negative checks`);
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
