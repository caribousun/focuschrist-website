/* Scoped rendering regression; independent human-facing pixel review remains separate. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {execFileSync} = require('node:child_process');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.qa-artifacts', 'conference-archive-mobile');
const baselineRef = '83a22ee68187bbce39d5abbbcaf3e5a52090dd1e';
const selector = '#conference-april-2026 > summary';
const result = {baselineRef, measurements: [], negatives: [], status: 'INCOMPLETE'};

function measure() {
  const summary = document.querySelector('#conference-april-2026 > summary');
  const count = summary.querySelector('.gc-session-count');
  const rect = e => {const r = e.getBoundingClientRect(); return {x:r.x, y:r.y+scrollY, width:r.width, height:r.height, right:r.right};};
  const lineRects = [];
  for (const node of summary.childNodes) if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
    const range = document.createRange(); range.selectNodeContents(node);
    for (const r of range.getClientRects()) if (r.width && r.height) lineRects.push({x:r.x, y:r.y+scrollY, right:r.right, height:r.height});
  }
  const distinctLines = [...new Set(lineRects.map(r => Math.round(r.y)))].length;
  const cs = getComputedStyle(count), ss = getComputedStyle(summary);
  return {viewport:innerWidth, rootFont:getComputedStyle(document.documentElement).fontSize,
    summary:rect(summary), titleLines:distinctLines, titleRects:lineRects,
    count:{text:count.textContent.trim(), rect:rect(count), display:cs.display, visibility:cs.visibility,
      position:cs.position, clipPath:cs.clipPath, hidden:count.hidden, ariaHidden:count.getAttribute('aria-hidden')},
    summaryFont:ss.fontSize, summaryWrap:ss.flexWrap, plus:getComputedStyle(summary,'::after').content,
    pageOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
    archiveTalks:document.querySelectorAll('[data-archive-talk]').length,
    currentTalks:document.querySelectorAll('[data-conference-talk]').length,
    upperLinks:[...document.querySelectorAll('.fc-next-conference .fc-conference-actions a')].map(e=>({text:e.textContent.trim(),href:e.getAttribute('href'),rect:rect(e)}))};
}

function normalMobileDefects(m) {
  const errors = [];
  if (m.titleLines !== 1) errors.push('archive title is not one line');
  if (m.count.position !== 'absolute' || m.count.rect.width > 1.1 || m.count.rect.height > 1.1 || m.count.clipPath !== 'inset(50%)') errors.push('archive count still occupies a visible line');
  if (m.summary.height > 70) errors.push('archive header is not compact');
  if (m.pageOverflow > 2) errors.push('page horizontal overflow');
  return errors;
}

async function accessibleSummary(page, cdp) {
  const document = await cdp.send('DOM.getDocument');
  const node = await cdp.send('DOM.querySelector', {nodeId:document.root.nodeId,selector});
  const ax = await cdp.send('Accessibility.getPartialAXTree', {nodeId:node.nodeId,fetchRelatives:false});
  const summary = ax.nodes.find(n => !n.ignored && n.name && n.name.value.includes('April 2026 archive'));
  assert(summary, 'native summary remains in the accessibility tree');
  assert(summary.name.value.includes('37 messages') && summary.name.value.includes('4 sessions'), 'visually clipped count remains in accessible summary name');
  return {role:summary.role.value,name:summary.name.value};
}

async function preserved(page, cdp, m) {
  assert.equal(m.count.text, '37 messages · 4 sessions');
  assert.notEqual(m.count.display, 'none'); assert.notEqual(m.count.visibility, 'hidden');
  assert.equal(m.count.hidden, false); assert.notEqual(m.count.ariaHidden, 'true');
  assert.equal(m.archiveTalks,37); assert.equal(m.currentTalks,38);
  assert.deepEqual(m.upperLinks.map(x=>({text:x.text,href:x.href})),[
    {text:'Official October collection ↗',href:'https://www.churchofjesuschrist.org/study/general-conference/2026/10?lang=eng'},
    {text:'April 2026 archive ↓',href:'#conference-april-2026'}
  ]);
  m.accessibility = await accessibleSummary(page, cdp);
}

(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const server = http.createServer((req,res)=>{
    const filename=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
    if(!filename.startsWith(root+path.sep)){res.writeHead(403).end();return;}
    const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'};
    fs.readFile(filename,(e,b)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':types[path.extname(filename)]||'application/octet-stream'}).end(b));
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r)); let browser;
  try {
    browser=await chromium.launch({headless:true,...(process.env.FOCUS_QA_CHROMIUM_EXECUTABLE ? {executablePath:process.env.FOCUS_QA_CHROMIUM_EXECUTABLE} : {})}); const context=await browser.newContext();
    await context.route('https://**',route=>route.abort()); const page=await context.newPage(); const cdp=await context.newCDPSession(page);
    const url=`http://127.0.0.1:${server.address().port}/general-conference.html`;
    async function load(width){await page.setViewportSize({width,height:1000});await page.goto(url,{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);}
    for (const width of [320,390,412,700,701,1280]) {
      await load(width); const m=await page.evaluate(measure); m.phase='candidate';
      await preserved(page,cdp,m);
      if(width<=700) assert.deepEqual(normalMobileDefects(m),[],`mobile ${width}`);
      else {assert.equal(m.count.position,'static');assert(m.count.rect.width>100,'desktop count visible');}
      await page.locator(selector).screenshot({path:path.join(out,`${width}-summary.png`)});
      result.measurements.push(m);
      // Exercise the actual archive jump and native keyboard disclosure, then all four nested sessions.
      await page.locator('.fc-next-conference a[href="#conference-april-2026"]').click();
      assert.equal(new URL(page.url()).hash,'#conference-april-2026');
      const archive=page.locator('#conference-april-2026');
      if(await archive.getAttribute('open')!==null) await page.locator(selector).click();
      await page.locator(selector).focus(); await page.keyboard.press('Enter');
      assert.notEqual(await archive.getAttribute('open'),null,'keyboard opens archive');
      const sessions=page.locator('[data-archive-session]'); assert.equal(await sessions.count(),4);
      const counts=[9,10,9,9];
      for(let i=0;i<4;i++) {
        const session=sessions.nth(i); const heading=session.locator(':scope > summary');
        await heading.click(); assert.notEqual(await session.getAttribute('open'),null);
        assert.equal(await session.locator('[data-archive-talk]:visible').count(),counts[i]);
        assert.equal(await session.locator(':scope > summary .gc-session-count').isVisible(),true,'nested session counts stay visible');
        await heading.click(); assert.equal(await session.getAttribute('open'),null);
      }
      await page.locator(selector).focus(); await page.keyboard.press('Space');
      assert.equal(await archive.getAttribute('open'),null,'keyboard closes archive');
    }
    // Enlarged text may wrap; it must remain readable, contained and operable.
    for(const width of [320,390,412]) {
      await load(width); await page.addStyleTag({content:'html{font-size:200%!important}'});
      const m=await page.evaluate(measure);m.phase='200-percent-root-text';await preserved(page,cdp,m);
      assert.equal(m.rootFont,'32px');assert.equal(m.summaryWrap,'wrap');
      for(const r of m.titleRects){assert(r.x>=m.summary.x-1 && r.right<=m.summary.right+1,'enlarged title stays inside summary');assert(r.y+r.height<=m.summary.y+m.summary.height+1,'enlarged text not clipped');}
      await page.locator(selector).click();assert.notEqual(await page.locator('#conference-april-2026').getAttribute('open'),null);
      await page.locator(selector).screenshot({path:path.join(out,`${width}-200percent-summary.png`)});
      result.measurements.push(m);
    }
    const baseline=execFileSync('git',['show',`${baselineRef}:general-conference-section.css`],{cwd:root});
    const pattern='**/general-conference-section.css?*';
    for(const width of [320,390,412,700,701,1280]) {
      await load(width);const current=await page.evaluate(measure);
      await page.route(pattern,route=>route.fulfill({contentType:'text/css',body:baseline}));
      await page.reload({waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);const before=await page.evaluate(measure);
      if(width<=700) assert(normalMobileDefects(before).includes('archive count still occupies a visible line'),'original CSS must fail compact-count control');
      if(width===390) assert(before.summary.height>current.summary.height+10,'reported original mobile wrap is reproduced');
      if(width>700) for(const name of ['summary'])for(const field of ['x','y','width','height'])assert(Math.abs(before[name][field]-current[name][field])<1,`desktop ${width} ${name}.${field} unchanged`);
      result.negatives.push({width,baselineHeight:before.summary.height,candidateHeight:current.summary.height,baselineDefects:width<=700?normalMobileDefects(before):[],desktopUnchanged:width>700});
      await page.unroute(pattern);await page.reload({waitUntil:'load'});
      const restored=await page.evaluate(measure);if(width<=700)assert.deepEqual(normalMobileDefects(restored),[],'candidate route restored');
    }
    // A display:none shortcut must not pass accessible preservation.
    await load(390);const hidden=await page.addStyleTag({content:'#conference-april-2026 > summary > .gc-session-count{display:none!important}'});
    let rejected=false;try{await preserved(page,cdp,await page.evaluate(measure));}catch{rejected=true;}
    assert(rejected,'inaccessible hidden-count mutation must fail');await hidden.evaluate(e=>e.remove());
    result.negatives.push({case:'display-none count',rejected});result.status='PASS';
    console.log('PASS: 6 widths, original390px wrap negative, accessible count, native keyboard/nested archive37, unchanged upper links/desktop geometry and200% text containment.');
  } catch(e) {result.status='FAIL';result.error=e.stack;throw e;}
  finally {fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2)+'\n');if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
