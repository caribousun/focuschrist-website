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
const desktopOpeningRecords = [];
fs.mkdirSync(out, { recursive: true });
async function checkContinue(page,label,enlarged) {
  const cue=page.locator('[data-unified-opening] .fc-unified-continue');
  assert.equal(await cue.count(),1,label+' single Continue');
  const g=await cue.evaluate(n=>{const r=n.getBoundingClientRect(),target=document.getElementById(n.hash.slice(1));return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,viewport:innerHeight,client:document.documentElement.clientWidth,target:n.hash,retained:!!target&&target.matches('.fc-unified-opening-continuation'),clipped:n.scrollWidth>n.clientWidth+1};});
  assert(g.height>=44&&!g.clipped&&g.x>=-1&&g.x+g.width<=g.client+1,label+' Continue complete touch target');
  assert(Math.abs(g.x+g.width/2-g.client/2)<=1,label+' Continue centered');
  assert(g.retained,label+' Continue enters retained introduction');
  if(!enlarged) assert(Math.abs(g.bottom-(g.viewport-20))<=1,label+' Continue exact20px bottom inset');
  await cue.scrollIntoViewIfNeeded();await cue.focus();
  assert(await cue.evaluate(n=>document.activeElement===n),label+' Continue keyboard focus');
  await cue.press('Enter');
  await page.waitForFunction(hash=>location.hash===hash,g.target);
  assert(await page.locator('.fc-unified-opening-continuation .fc-actions .fc-button').isVisible(),label+' retained action remains visible after Continue');
}
async function checkReflectionSpacing(page, label) {
  const geometry = await page.locator('.fc-life-reflections').evaluate(grid => {
    const actions=grid.nextElementSibling;
    const returnRow=actions.nextElementSibling;
    const g=grid.getBoundingClientRect(), a=actions.getBoundingClientRect(), r=returnRow.getBoundingClientRect();
    return {before:a.top-g.bottom,after:r.top-a.bottom,links:[...actions.querySelectorAll('a'),returnRow.querySelector('a')].map(link=>{const box=link.getBoundingClientRect();return {width:box.width,height:box.height,left:box.left,right:box.right,clipped:link.scrollWidth>link.clientWidth+1 && getComputedStyle(link).display!=='inline'};}),viewport:innerWidth};
  });
  assert(geometry.before>=23.5 && geometry.after>=23.5, label+' reflection/scripture/return gaps must be at least24px');
  assert(geometry.links.every(link=>link.width>0 && link.height>0 && link.left>=-1 && link.right<=geometry.viewport+1 && !link.clipped), label+' closing links contained and readable');
  const links=page.locator('.fc-life-reflections + .fc-actions a, .fc-life-reflections + .fc-actions + p a');
  for (let i=0;i<await links.count();i++) {
    const link=links.nth(i);await link.scrollIntoViewIfNeeded();await link.focus();
    assert(await link.evaluate(a=>document.activeElement===a), label+' closing links remain reachable');
  }
  await links.last().evaluate(link=>link.scrollIntoView({block:'end'}));
  geometry.screenshot=path.join(out,label.replace(/[^a-z0-9]+/gi,'-')+'-reflection.png');
  await page.screenshot({path:geometry.screenshot,fullPage:false,animations:'disabled'});
  await page.evaluate(()=>scrollTo(0,0));
  return geometry;
}
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
    browser = await chromium.launch({ headless:true, ...(process.env.QA_BROWSER_CHANNEL ? {channel:process.env.QA_BROWSER_CHANNEL} : {}) });
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
      records[records.length-1].reflection=await checkReflectionSpacing(page, slug+' desktop1440');
      await page.close();
    }
    assert(records.every(record => !record.raster.failures.length), 'Hero raster has a blank/near-solid region; inspect saved screenshots');
    for (const slug of ['john-tanner', 'eleazer-miller', 'john-rowe-moyle']) {
      for (const [width,height] of [[1280,720],[1366,768],[1536,792],[1920,990],[1920,900]]) {
        const page=await context.newPage();
        await page.setViewportSize({width,height});
        await page.goto(`http://127.0.0.1:${server.address().port}/history/${slug}.html`, {waitUntil:'domcontentloaded'});
        await page.locator('.fc-life-hero img').evaluate(img=>img.decode());
        await page.locator('[data-unified-opening] .fc-unified-continue').waitFor({state:'visible'});
        let normalSize;
        for (const enlarged of [false,true]) {
          if (enlarged) await page.evaluate(()=>{document.documentElement.style.fontSize='200%';});
          await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
          const geometry=await page.evaluate(()=>{
            const opening=document.querySelector('.fc-life-opening');
            const h=opening.querySelector('h1'),button=document.querySelector('.fc-unified-opening-continuation .fc-actions .fc-button'),summary=document.querySelector('.fc-life-directory summary');
            const rect=n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom};};
            return {hero:rect(document.querySelector('.fc-life-hero > a.fc-visual-hero')),heading:rect(h),button:rect(button),summary:rect(summary),fontSize:parseFloat(getComputedStyle(h).fontSize),fontFamily:getComputedStyle(h).fontFamily,fontWeight:getComputedStyle(h).fontWeight,overflow:document.documentElement.scrollWidth>innerWidth+1,readingOverflow:getComputedStyle(opening).overflowY,clipped:[h,button,summary].some(n=>n.scrollHeight>n.clientHeight+1||n.scrollWidth>n.clientWidth+1),directoryOpen:summary.parentElement.open};
          });
          const label=`${slug} desktop${width}x${height} ${enlarged?'200%':'100%'}`;
          assert(Math.abs(geometry.hero.width/geometry.hero.height-2048/684)<.01,label+' standard hero frame unchanged');
          assert(/^Georgia\b/i.test(geometry.fontFamily.replaceAll('"',''))&&geometry.fontWeight==='400',label+' standard heading theme');
          assert(!geometry.overflow&&!geometry.clipped&&!geometry.directoryOpen,label+' opening must remain readable and collapsed');
          for (const control of [geometry.button,geometry.summary]) assert(control.height>=44&&control.x>=-1&&control.x+control.width<=width+1,label+' complete touch targets');
          assert([geometry.button,geometry.summary].every(control=>control.y>=geometry.heading.bottom-1),label+' both controls must follow the heading');
          const overlapWidth=Math.min(geometry.button.x+geometry.button.width,geometry.summary.x+geometry.summary.width)-Math.max(geometry.button.x,geometry.summary.x);
          const overlapHeight=Math.min(geometry.button.bottom,geometry.summary.bottom)-Math.max(geometry.button.y,geometry.summary.y);
          assert(overlapWidth<=1||overlapHeight<=1,label+' opening control rectangles must not overlap');
          if (!enlarged) {
            normalSize=geometry.fontSize;
            const expectedSize=Math.max(32,Math.min(48,height*.5-width*.1669921875-95));
            assert(normalSize>=32-.1&&normalSize<=48+.1&&Math.abs(normalSize-expectedSize)<.2,label+' dynamic desktop heading follows available height within32-48px');
            assert(geometry.button.y>=height-1&&geometry.summary.y>=height-1,label+' retained Begin and directory follow the initial opening');
          } else {
            assert(geometry.fontSize>=normalSize*1.3,label+' enlarged heading must grow');
            assert(!['hidden','clip'].includes(geometry.readingOverflow),label+' enlarged opening must scroll naturally');
          }
          const screenshot=path.join(out,`${slug}-desktop${width}x${height}-${enlarged?'200':'100'}.png`);
          await page.screenshot({path:screenshot,fullPage:false,animations:'disabled'});
          await checkContinue(page,label,enlarged);
          for (const selector of ['.fc-unified-opening-continuation .fc-actions .fc-button','.fc-life-directory summary']) {
            const control=page.locator(selector);await control.scrollIntoViewIfNeeded();await control.focus();
            assert(await control.evaluate(n=>document.activeElement===n),label+' opening controls remain reachable');
          }
          const summary=page.locator('.fc-life-directory summary');await summary.press('Enter');
          assert(await summary.evaluate(n=>n.parentElement.open),label+' directory opens');await summary.press('Enter');
          assert(await summary.evaluate(n=>!n.parentElement.open),label+' directory closes');
          desktopOpeningRecords.push({page:slug,viewport:[width,height],enlarged,...geometry,screenshot:path.relative(root,screenshot)});
          await page.evaluate(()=>scrollTo(0,0));
        }
        await page.close();
      }
    }
    for (const slug of ['john-tanner', 'eleazer-miller', 'john-rowe-moyle']) {
      for (const [width, height] of [[390, 732], [320, 667], [412, 743], [432, 810]]) {
        const page = await context.newPage();
        await page.setViewportSize({ width, height });
        await page.goto(`http://127.0.0.1:${server.address().port}/history/${slug}.html`, { waitUntil:'domcontentloaded' });
        await page.locator('.fc-life-hero img').evaluate(img => img.decode());
        await page.locator('[data-unified-opening] .fc-unified-continue').waitFor({state:'visible'});
        let normalSize;
        for (const enlarged of [false, true]) {
          if (enlarged) await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          const opening = await page.evaluate(() => {
            const h1 = document.querySelector('.fc-life-reading h1');
            const button = document.querySelector('.fc-unified-opening-continuation .fc-actions .fc-button');
            const summary = document.querySelector('.fc-life-directory summary');
            const rect = node => { const r=node.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom}; };
            const headings = [...document.querySelectorAll('.fc-life-reading h1, .fc-life-reading h2')].map(h => ({ text:h.textContent, family:getComputedStyle(h).fontFamily, weight:getComputedStyle(h).fontWeight }));
            return {headings, title:rect(h1), button:rect(button), summary:rect(summary), firstBodyHeading:rect(document.querySelector('.fc-life-body-start > h2')), directoryOpen:summary.parentElement.open, summaryClipped:summary.scrollHeight>summary.clientHeight+1 || summary.scrollWidth>summary.clientWidth+1, fontSize:parseFloat(getComputedStyle(h1).fontSize), overflow:document.documentElement.scrollWidth>innerWidth+1, titleClipped:h1.scrollHeight>h1.clientHeight+1, buttonClipped:button.scrollWidth>button.clientWidth+1, readingOverflow:getComputedStyle(h1.parentElement).overflowY};
          });
          const label = `${slug} ${width} ${enlarged?'200%':'100%'}`;
          assert(opening.headings.length>1 && opening.headings.every(h => /^Georgia\b/i.test(h.family.replaceAll('"','')) && h.weight==='400'), label+' must use the shared Georgia400 heading theme');
          assert(!opening.overflow && !opening.titleClipped && !opening.buttonClipped, label+' clipped reading controls');
          assert(opening.button.height>=44 && opening.button.x>=-1 && opening.button.x+opening.button.width<=width+1, label+' accessible button geometry');
          assert(!opening.directoryOpen && !opening.summaryClipped && opening.summary.height>=44 && opening.summary.x>=-1 && opening.summary.x+opening.summary.width<=width+1, label+' complete collapsed directory touch target');
          assert(opening.summary.y>=opening.button.bottom-1, label+' directory/action overlap');
          assert(opening.button.y>=opening.title.bottom-1, label+' title/action overlap');
          if (!enlarged) {
            normalSize=opening.fontSize;
            assert(opening.firstBodyHeading.y>=height+16, label+' first story heading must begin below the initial screen');
            assert(Math.abs(normalSize-32)<.1, label+' shared phone heading size');
            assert(opening.button.y>=height-1&&opening.summary.y>=height-1, label+' retained controls follow initial opening');
            assert(opening.title.y>=0 && opening.title.bottom<=height-20, label+' title must fit shorter phone viewport');
          } else {
            // Shared phone heading is 2rem and doubles with 200% root text.
            assert(opening.fontSize>=normalSize*1.4, label+' headings must respond meaningfully to enlarged text');
            assert(!['hidden','clip'].includes(opening.readingOverflow), label+' enlarged opening must grow naturally');
          }
          const screenshot=path.join(out,`${slug}-${width}x${height}-${enlarged?'200':'100'}.png`);
          await page.screenshot({path:screenshot,fullPage:false,animations:'disabled'});
          await checkContinue(page,label,enlarged);
          const button=page.locator('.fc-unified-opening-continuation .fc-actions .fc-button').first();
          await button.scrollIntoViewIfNeeded();
          await button.focus();
          assert(await button.evaluate(b=>document.activeElement===b), label+' Begin action must remain focusable');
          const summary=page.locator('.fc-life-directory summary');
          await summary.scrollIntoViewIfNeeded();
          await summary.focus();
          assert(await summary.evaluate(s=>document.activeElement===s), label+' directory remains keyboard reachable');
          await summary.press('Enter');
          assert(await summary.evaluate(s=>s.parentElement.open), label+' directory opens with keyboard');
          await summary.press('Enter');
          assert(await summary.evaluate(s=>!s.parentElement.open), label+' directory closes with keyboard');
          opening.reflection=await checkReflectionSpacing(page,label);
          openingRecords.push({page:slug,viewport:[width,height],enlarged,...opening,screenshot:path.relative(root,screenshot)});
          await page.evaluate(()=>scrollTo(0,0));
        }
        await page.close();
      }
    }
    console.log('PASS: hosted Chromium1440 rendered all three full hero regions with varied scene pixels');
    console.log('PASS:24 phone openings, unchanged themed headings, complete Begin/directory controls and natural enlarged-text flow');
  } finally {
    fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(records, null, 2)+'\n');
    fs.writeFileSync(path.join(out, 'desktop-openings.json'), JSON.stringify(desktopOpeningRecords, null, 2)+'\n');
    fs.writeFileSync(path.join(out, 'phone-openings.json'), JSON.stringify(openingRecords, null, 2)+'\n');
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode=1; });
