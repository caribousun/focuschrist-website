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
      assert(await page.locator(selectors).count(), `${url}: no covered grid found`);
      for (const row of rows) {
        assert(row.uncovered <= 3, `${url} @${width}: incomplete final row ${JSON.stringify(row)}`);
        assert(row.overflow <= 3, `${url} @${width}: overflowing row ${JSON.stringify(row)}`);
        checked++;
      }
      if (url === 'pioneers.html' && width > 700) {
        const rhythm = await page.evaluate(() => {
          const cards = [...document.querySelectorAll('.pioneer-story-card')].map(n => ({
            top:n.getBoundingClientRect().top,
            bottom:n.querySelector('.pioneer-source-links').getBoundingClientRect().bottom
          }));
          return {
            navigation:[...document.querySelectorAll('nav[aria-label="Pioneer study sections"] .fc-button')].map(n=>({color:getComputedStyle(n).color,radius:getComputedStyle(n).borderRadius,border:getComputedStyle(n).borderTopColor,fill:getComputedStyle(n).backgroundImage,marker:n.querySelector('.pioneer-trail-number')?.textContent,decorative:n.querySelector('.pioneer-trail-number')?.getAttribute('aria-hidden')==='true',height:n.getBoundingClientRect().height,clipped:n.scrollWidth>n.clientWidth})),
            rails:[...document.querySelectorAll('main > nav[aria-label="Pioneer study sections"] > div,main > .qa-section > .qa-container,main > .pioneer-visual-chapter > div,main > .pioneer-story-chapter,main > .pioneer-timeline-group,main > .section,main > .fc-resource-section,main > .fc-study-hub,#guided-reflections > div')].map(n => ({left:n.getBoundingClientRect().left,width:n.getBoundingClientRect().width})),
            features:[...document.querySelectorAll('.pioneer-story-card > .pioneer-source-links')].map(n => ({
              width:n.getBoundingClientRect().width,
              inner:n.parentElement.clientWidth - 48,
              below:n.getBoundingClientRect().top >= Math.max(n.previousElementSibling.getBoundingClientRect().bottom,n.parentElement.querySelector('figure').getBoundingClientRect().bottom)
            })),
            pairs:cards.slice(1).flatMap((n,i) => Math.abs(n.top-cards[i].top)<3 ? [Math.abs(n.bottom-cards[i].bottom)] : []),
            intros:[...document.querySelectorAll('.pioneer-story-intro,.pioneer-visual-intro')].every(n =>
              [n,...n.children].every(c => ['start','left'].includes(getComputedStyle(c).textAlign))),
            gap:document.querySelector('#guided-reflections .fc-actions').getBoundingClientRect().top -
              document.querySelector('#guided-reflections .fc-study-grid').getBoundingClientRect().bottom
          };
        });
        assert(rhythm.pairs.length === 7 && rhythm.pairs.every(gap => gap < 3), 'Pioneer paired source footers must align');
        assert(rhythm.navigation.length===9 && rhythm.navigation.every((n,i)=>n.color==='rgb(255, 242, 220)' && n.radius==='10px' && n.border==='rgb(156, 175, 170)' && n.fill==='linear-gradient(145deg, rgb(49, 85, 71), rgb(29, 59, 56))' && n.marker===String(i+1).padStart(2,'0') && n.decorative && n.height>=68 && !n.clipped), 'Pioneer chapter directory must preserve nine numbered stops, accessible labels, exact shared green/cream controls and unclipped 68px targets: '+JSON.stringify(rhythm.navigation));
        assert(rhythm.intros, 'Pioneer desktop introductions must share one alignment');
        assert(rhythm.gap >= 27 && rhythm.gap <= 29, 'Pioneer closing action buffer must remain 28px');
        assert(rhythm.rails.length >= 17 && rhythm.rails.every(r => Math.abs(r.left-rhythm.rails[0].left)<2 && Math.abs(r.width-rhythm.rails[0].width)<2), 'Pioneer body sections must share the Home/Answers standard outer rail');
        assert(rhythm.features.length === 4 && rhythm.features.every(f=>Math.abs(f.width-f.inner)<3 && f.below), 'Pioneer feature sources must span below the whole image-and-account row');
      }
    }
    for (const width of [1366,900,600,390]) for (const url of pages) await check(url, width);
    for (const width of [520,521,700,701,1000,1001,1050,1051]) {
      for (const url of ['pioneers.html','ask.html','general-conference.html','answers/stand-forever.html','answers/settle-this-in-your-hearts.html']) await check(url, width);
    }
    // Chapter labels must remain usable on narrow phones and with enlarged text.
    for (const width of [320,390,701,1024]) for (const scale of [1,2]) {
      await page.setViewportSize({width,height:900});
      await page.goto(origin + '/pioneers.html', {waitUntil:'load'});
      await page.evaluate(scale => { document.documentElement.style.fontSize = `${100*scale}%`; },scale);
      const stops = await page.evaluate(() => ({
        overflow:document.documentElement.scrollWidth>innerWidth,
        links:[...document.querySelectorAll('nav[aria-label="Pioneer study sections"] .fc-button')].map(n=>({
          clipped:n.scrollWidth>n.clientWidth+1 || n.scrollHeight>n.clientHeight+1,
          height:n.getBoundingClientRect().height,
          target:!!document.querySelector(n.getAttribute('href'))
        }))
      }));
      assert(!stops.overflow && stops.links.length===9 && stops.links.every(n=>!n.clipped && n.height>=68 && n.target), `Pioneer chapter navigation overflow at ${width}px / ${scale}x text`);
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
