/* Hosted Chromium corroboration: save real viewport rasters and inspect their hero pixels. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { spawnSync } = require('node:child_process');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.qa-artifacts', 'history-heroes');
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
    for (const slug of ['john-tanner', 'eleazer-miller', 'john-rowe-moyle']) {
      const page = await context.newPage();
      await page.goto(`http://127.0.0.1:${server.address().port}/history/${slug}.html`, { waitUntil:'domcontentloaded' });
      const hero = page.locator('.fc-life-hero > a.fc-visual-hero');
      const image = hero.locator('img');
      await image.evaluate(async img => { await img.decode(); });
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const bounds = await hero.boundingBox();
      assert(bounds && Math.abs(bounds.width/bounds.height - 2048/684) < .01, 'Standard desktop hero frame changed');
      const source = await image.evaluate(img => ({ src:img.currentSrc, width:img.naturalWidth, height:img.naturalHeight, complete:img.complete }));
      const stories = JSON.parse(fs.readFileSync(path.join(root, 'docs/history-stories/stories.json'), 'utf8')).stories;
      const ready = JSON.parse(fs.readFileSync(path.join(root, 'docs/history-stories/art-ready.json'), 'utf8'));
      const expected = ready[stories.find(story => story.id === slug).hero_unit_id].desktop;
      assert(source.complete && source.width > 1500 && new URL(source.src).pathname === '/' + expected, 'Use the exact reviewed responsive asset');
      const screenshot = path.join(out, slug+'-1440.png');
      await page.screenshot({ path:screenshot, fullPage:false, animations:'disabled' });
      const inspected = spawnSync('python', [path.join(root, 'tools/history_hero_pixels_qa.py'), screenshot, JSON.stringify(bounds)], { encoding:'utf8' });
      const raster = inspected.stdout.trim() ? JSON.parse(inspected.stdout.trim()) : { failures:[inspected.stderr || 'Raster inspection produced no result'] };
      records.push({ page:slug, viewport:[1440,1000], bounds, source, screenshot:path.relative(root, screenshot), raster });
      await page.close();
    }
    assert(records.every(record => !record.raster.failures.length), 'Hero raster has a blank/near-solid region; inspect saved screenshots');
    console.log('PASS: hosted Chromium1440 rendered all three full hero regions with varied scene pixels');
  } finally {
    fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(records, null, 2)+'\n');
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode=1; });
