/* Hosted Chromium geometry/flow corroboration; actual composition review is recorded separately. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.qa-artifacts', 'home-height-heroes');
const records = [];
fs.mkdirSync(out, { recursive: true });
(async () => {
  const server = http.createServer((request, response) => {
    const filename = path.resolve(root, '.' + decodeURIComponent(new URL(request.url, 'http://localhost').pathname));
    if (!filename.startsWith(root + path.sep)) { response.writeHead(403).end(); return; }
    const types = { '.html':'text/html; charset=utf-8', '.css':'text/css', '.js':'text/javascript', '.json':'application/json', '.webp':'image/webp', '.svg':'image/svg+xml', '.jpg':'image/jpeg', '.png':'image/png' };
    fs.readFile(filename, (error, data) => { if (error) response.writeHead(404).end(); else response.writeHead(200, { 'Content-Type':types[path.extname(filename)] || 'application/octet-stream' }).end(data); });
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = await chromium.launch({ headless:true });
    const context = await browser.newContext({ viewport:{ width:1440, height:1000 }, deviceScaleFactor:1 });
    await context.route('https://**', route => route.abort()); // Remote film/font checks are separate; original hero pixels are local.
    const inventory = JSON.parse(fs.readFileSync(path.join(root, 'docs/hero-home-height-audit-20260929.json'), 'utf8'));
    assert.equal(inventory.pages.length, 125, 'Historical route set plus Joseph research is classified');
    const page = await context.newPage();
    const base = `http://127.0.0.1:${server.address().port}`;
    await page.goto(`${base}/index.html`, {waitUntil:'domcontentloaded'});
    const home = await page.locator('.fc-home-hero').boundingBox();
    for (const record of inventory.pages) {
      await page.goto(`${base}/${record.page}`, {waitUntil:'domcontentloaded'});
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      if(record.page==='joseph-smith-likeness.html'){
        assert.equal(record.selector,'.fc-visual-hero','Joseph gateway reviewed hero is explicitly classified');
        assert.equal(await page.locator('.joseph-bridge-intro h1').textContent(),'Explore his life and the portrait');
        assert.deepEqual(await page.locator('#joseph-study-entrance .fc-button--primary').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href'))),['answers/who-was-joseph-smith.html#joseph-family-life','joseph-smith-portrait-research.html']);
        assert.equal(await page.locator('main img').count(),0);
        assert.equal(await page.locator('.fc-visual-hero[data-hero-viewer]').count(),1);
      }
      if (!record.selector) {
        assert.equal(await page.locator('.fc-visual-hero').count(), 0, `${record.page}: new designated hero requires classification`);
        records.push({page:record.page, classification:record.baseline_classification, compared:false});
        continue;
      }
      const frames = await page.locator(record.selector).all();
      assert(frames.length, `${record.page}: expected hero missing`);
      for (const frame of frames) {
        const bounds = await frame.boundingBox();
        records.push({page:record.page, bounds, home, compared:true});
        assert(bounds && Math.abs(bounds.height-home.height)<2, `${record.page}: hero height ${bounds?.height} differs from Home ${home.height}`);
      }
    }
    for (const width of [701,768,1440]) {
      await page.setViewportSize({width,height:1000});
      await page.goto(`${base}/index.html`, {waitUntil:'domcontentloaded'});
      const expected = await page.locator('.fc-home-hero').boundingBox();
      await page.goto(`${base}/come-follow-me.html`, {waitUntil:'domcontentloaded'});
      const frame = await page.locator('.cfm-desktop-picture').boundingBox();
      assert(frame && Math.abs(frame.height-expected.height)<2, 'CFM picture must match Home at each desktop width');
      await page.evaluate(() => {
        const sizes=[...document.querySelectorAll('.cfm-hero__copy, .cfm-hero__copy *')].map(el=>[el,parseFloat(getComputedStyle(el).fontSize)]);
        for (const [el,size] of sizes) el.style.setProperty('font-size',`${size*2}px`,'important');
      });
      const flow = await page.evaluate(() => {
        const copy=document.querySelector('.cfm-hero__copy'), picture=document.querySelector('.cfm-desktop-picture');
        return {copy:copy.getBoundingClientRect().toJSON(),picture:picture.getBoundingClientRect().toJSON(),overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,clipped:copy.scrollHeight>copy.clientHeight+2};
      });
      assert(flow.copy.top>=flow.picture.bottom-1 && !flow.clipped && flow.overflow<3, 'CFM200percent copy must flow below artwork without clipping or horizontal overflow');
      records.push({page:'come-follow-me.html',width,enlargedText:'200percent',flow});
    }
    for (const width of [390,320,700]) {
      await page.setViewportSize({width,height:844});
      await page.goto(`${base}/index.html`, {waitUntil:'domcontentloaded'});
      const phoneHome = await page.locator('.fc-home-hero').boundingBox();
      await page.goto(`${base}/answers/abrahamic-covenant.html`, {waitUntil:'domcontentloaded'});
      const hero = page.locator('[data-covenant-hero-slot] .fc-covenant-hero');
      const bounds = await hero.boundingBox();
      assert(bounds && Math.abs(bounds.height-phoneHome.height)<2, 'Covenant phone hero must match Home and remain visible');
      assert.equal(await page.locator('#picture-ac-jacob-ladder').count(),1);
      records.push({page:'answers/abrahamic-covenant.html',width,bounds,home:phoneHome});
    }
    console.log('PASS: all124canonical openings classified; every designated desktop picture hero matches actual Home; Covenant phone remains unique and visible.');
  } finally {
    fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(records, null, 2)+'\n');
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode=1; });
