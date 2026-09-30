/* Hosted desktop/phone/enlarged-text footer interaction checks. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.qa-artifacts', 'footer-navigation');
fs.mkdirSync(out, {recursive:true});
const results=[];
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
    browser=await chromium.launch({headless:true});
    const context=await browser.newContext({reducedMotion:'reduce'});
    await context.route('https://**',route=>route.abort());
    const page=await context.newPage();
    for(const route of ['index.html','answers/aaronic-priesthood-restoration.html','history/john-rowe-moyle.html']) {
      for(const width of [1440,390,320]) for(const enlarged of [false,true]) {
        await page.setViewportSize({width,height:1000});
        await page.goto(`http://127.0.0.1:${server.address().port}/${route}?footer-check=1`,{waitUntil:'domcontentloaded'});
        await page.waitForFunction(()=>[...document.styleSheets].some(s=>s.href && s.href.includes('footer-navigation.css')));
        if(enlarged) await page.evaluate(()=>document.documentElement.style.fontSize='32px');
        const button=page.locator('[data-focuschrist-back-to-top]');
        await button.scrollIntoViewIfNeeded();
        const box=await button.boundingBox();
        assert(box && box.height>=44 && box.x>=-1 && box.x+box.width<=width+1,'Visible44pxminimum touch target inside viewport');
        assert(await button.evaluate(b=>b.scrollWidth<=b.clientWidth+1),'Footer label clipped');
        const before=page.url();
        const screenshot=path.join(out,route.replaceAll('/','-')+'-'+width+(enlarged?'-200':'')+'.png');
        await page.screenshot({path:screenshot,animations:'disabled'});
        await button.focus();await page.keyboard.press('Enter');
        await page.waitForFunction(()=>window.scrollY===0);
        assert.equal(page.url(),before,'Top action changed route');
        assert(await page.evaluate(()=>document.activeElement.matches('.nav[data-focuschrist-header="standard"],main,body')),'Keyboard focus not moved to top');
        if(route.includes('aaronic')) assert.equal(await page.locator('.breadcrumbs').count(),0);
        results.push({route,width,enlarged,box,scrollTop:0,focus:'top navigation',screenshot:path.relative(root,screenshot)});
      }
    }
    console.log('PASS:18 desktop/phone/enlarged-text footer views, keyboard same-page top return and visible touch targets');
  } finally {
    fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2)+'\n');
    if(browser)await browser.close();
    await new Promise(resolve=>server.close(resolve));
  }
})().catch(error=>{console.error(error);process.exitCode=1});
