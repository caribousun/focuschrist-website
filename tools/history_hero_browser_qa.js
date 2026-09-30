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
const openingRecords = [];
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
    for (const slug of ['john-tanner', 'eleazer-miller', 'john-rowe-moyle']) {
      for (const [width, height] of [[390, 732], [320, 667]]) {
        const page = await context.newPage();
        await page.setViewportSize({ width, height });
        await page.goto(`http://127.0.0.1:${server.address().port}/history/${slug}.html`, { waitUntil:'domcontentloaded' });
        await page.locator('.fc-life-hero img').evaluate(img => img.decode());
        let normalSize;
        for (const enlarged of [false, true]) {
          if (enlarged) await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          const opening = await page.evaluate(() => {
            const h1 = document.querySelector('.fc-life-reading h1');
            const button = h1.parentElement.querySelector('.fc-actions .fc-button');
            const rect = node => { const r=node.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom}; };
            const headings = [...document.querySelectorAll('.fc-life-reading h1, .fc-life-reading h2')].map(h => ({ text:h.textContent, family:getComputedStyle(h).fontFamily, weight:getComputedStyle(h).fontWeight }));
            return {headings, title:rect(h1), button:rect(button), fontSize:parseFloat(getComputedStyle(h1).fontSize), overflow:document.documentElement.scrollWidth>innerWidth+1, titleClipped:h1.scrollHeight>h1.clientHeight+1, buttonClipped:button.scrollWidth>button.clientWidth+1, readingOverflow:getComputedStyle(h1.parentElement).overflowY};
          });
          const label = `${slug} ${width} ${enlarged?'200%':'100%'}`;
          assert(opening.headings.length>1 && opening.headings.every(h => /^Georgia\b/i.test(h.family.replaceAll('"','')) && h.weight==='400'), label+' must use the shared Georgia400 heading theme');
          assert(!opening.overflow && !opening.titleClipped && !opening.buttonClipped, label+' clipped reading controls');
          assert(opening.button.height>=44 && opening.button.x>=-1 && opening.button.x+opening.button.width<=width+1, label+' accessible button geometry');
          assert(opening.button.y>=opening.title.bottom-1, label+' title/action overlap');
          if (!enlarged) {
            normalSize=opening.fontSize;
            assert(opening.title.y>=0 && opening.button.bottom<=height, label+' complete opening must fit shorter phone viewport');
          } else {
            // Shared clamp(1.5rem,8vw,2rem): 390px grows from31.2px to48px at200% root text.
            assert(opening.fontSize>=normalSize*1.4, label+' headings must respond meaningfully to enlarged text');
            assert(!['hidden','clip'].includes(opening.readingOverflow), label+' enlarged opening must grow naturally');
          }
          const screenshot=path.join(out,`${slug}-${width}x${height}-${enlarged?'200':'100'}.png`);
          await page.screenshot({path:screenshot,fullPage:false,animations:'disabled'});
          const button=page.locator('.fc-life-reading').first().locator('.fc-actions .fc-button').first();
          await button.scrollIntoViewIfNeeded();
          await button.focus();
          assert(await button.evaluate(b=>document.activeElement===b), label+' Begin action must remain focusable');
          openingRecords.push({page:slug,viewport:[width,height],enlarged,...opening,screenshot:path.relative(root,screenshot)});
          await page.evaluate(()=>scrollTo(0,0));
        }
        await page.close();
      }
    }
    console.log('PASS: hosted Chromium1440 rendered all three full hero regions with varied scene pixels');
    console.log('PASS:12 shorter-phone openings, themed headings, complete normal Begin action and natural enlarged-text flow');
  } finally {
    fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(records, null, 2)+'\n');
    fs.writeFileSync(path.join(out, 'phone-openings.json'), JSON.stringify(openingRecords, null, 2)+'\n');
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode=1; });
