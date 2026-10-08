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
  ['art-study/the-good-shepherd.html', 'a[href="../art.html#gallery-original-the-good-shepherd"]', '#gallery-original-the-good-shepherd'],
  ['art-study/suffer-the-little-children.html', 'a[href="../art.html#gallery-original-suffer-the-little-children"]', '#gallery-original-suffer-the-little-children'],
  ['art-study/be-still.html', 'a[href="../art.html#gallery-original-be-still"]', '#gallery-original-be-still'],
  ...[
    ['What would you like to understand?', '/ask.html#ask-study-heading', '#ask-question'],
    ['Your Study Conversation', '/ask.html#conversation-heading', '.ask-conversation-section'],
    ['Explore by Topic', '/ask.html#topic-heading', '.ask-topic-section'],
    ['Continue Your Study', '/ask.html#continue-heading', '.ask-continue-section'],
    ['Make room to listen', '/ask.html#visual-resources-title', '[data-visual-resources]'],
    ['Try a question with a passage open', '/ask.html#connected-study', '#connected-study'],
    ['The Annunciation to Mary', '/timelines/life-of-christ-journey-map.html#dTitle', '#detail'],
    ['Choose a stop', '/timelines/willie-and-martin-handcart-map.html#detail-title', '#detail-panel'],
  ].map(([query, href, target]) => [`search.html?q=${encodeURIComponent(query)}`, `.fc-search-result a[href="${href}"]`, target]),
];
function measure(selector) {
  const target = document.querySelector(selector);
  if (!target) return { missing: selector };
  const rect = target.getBoundingClientRect();
  const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
  const fixed = header && ['fixed', 'sticky'].includes(getComputedStyle(header).position);
  let cover = fixed ? Math.ceil(header.getBoundingClientRect().height) : 0;
  const dock = document.querySelector('.timeline-map-dock');
  if (dock && !dock.contains(target) && !target.contains(dock)) {
    const box = dock.getBoundingClientRect(), style = getComputedStyle(dock);
    if (['fixed', 'sticky'].includes(style.position) && box.height > 0 &&
        box.top <= cover + 2 && box.bottom > cover && box.left < rect.right && box.right > rect.left) {
      cover = Math.ceil(box.bottom);
    }
  }
  const offset = cover + 16;
  const heading = Array.from(target.querySelectorAll('h1,h2,h3,h4')).find(item => !item.closest('[hidden]') && item.getClientRects().length);
  const headingRect = heading && heading.getBoundingClientRect();
  const maximum = Math.max(0, document.documentElement.scrollHeight - innerHeight);
  const expectedScroll = Math.max(0, Math.min(scrollY + rect.top - offset, maximum));
  return { top: rect.top, offset, cover, headingTop:headingRect?.top, headingBottom:headingRect?.bottom, scroll: scrollY, maximum, expectedScroll,
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
        await page.waitForLoadState('load');
        await page.evaluate(() => document.fonts.ready);
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
      // The legacy gallery retains aria-modal while closed. Its hidden panel
      // must allow section landings, while its actual viewer keeps ownership.
      await page.goto(`${base}/art.html#gallery-original-the-good-shepherd`, {waitUntil:'load'});
      await page.waitForTimeout(950);
      await page.locator('#gallery-original-the-good-shepherd').click();
      await page.locator('#imageModal.active').waitFor({state:'visible'});
      const viewerScroll = await page.evaluate(() => scrollY);
      await page.waitForTimeout(950);
      assert.equal(await page.locator('#imageModal.active').count(), 1);
      assert(Math.abs(await page.evaluate(() => scrollY) - viewerScroll) <= 1.5, 'Visible gallery viewer must retain reading position');
      await page.keyboard.press('Escape');
      await page.locator('#imageModal').waitFor({state:'hidden'});
      special.push({kind:'actual-gallery-viewer-ownership', width, viewerScroll});
      // The generated keyboard skip link keeps focus and replacement history,
      // but its destination must also clear the timeline's sticky phone header.
      for (const skipRoute of ['timelines/willie-and-martin-handcart-map.html', 'timelines/latter-day-saint-church-history-timeline.html', 'timelines/life-of-christ-journey-map.html']) {
      await page.goto(`${base}/${skipRoute}`, {waitUntil:'load'});
      const skip = page.locator('[data-focuschrist-skip-link="true"]');
      const skipTarget = await skip.getAttribute('href');
      const skipHistory = await page.evaluate(() => history.length);
      await skip.focus();
      await page.keyboard.press('Enter');
      await page.waitForTimeout(950);
      const skipLanding = await page.evaluate(measure, skipTarget);
      assert(skipLanding.error <= 1.5, JSON.stringify(skipLanding));
      assert(Number.isFinite(skipLanding.headingTop) && skipLanding.headingTop >= skipLanding.cover - 1, 'The first subject heading must clear the header and any pinned map dock: ' + JSON.stringify(skipLanding));
      assert.equal(await page.evaluate(() => '#' + document.activeElement.id), skipTarget);
      assert.equal(await page.evaluate(() => history.length), skipHistory);
      special.push({kind:'keyboard-skip-focus-and-history', route:skipRoute, width, ...skipLanding});
      }
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
    // Restore only the old modal guard to prove the real gallery link catches
    // the hidden aria-modal regression independently of the broader repair.
    const gallery = await browser.newPage({viewport:{width:1366,height:900},reducedMotion:'reduce'});
    await gallery.route('https://**', route => route.abort());
    const currentHeader = fs.readFileSync(path.join(root, 'header-scroll.js'), 'utf8');
    const oldGuard = currentHeader.replace(/function canAlign\(([^)]*)\) \{/, 'function canAlign($1) { if (document.querySelector(\'dialog[open], [role="dialog"][aria-modal="true"]\')) return false;');
    assert.notEqual(oldGuard, currentHeader);
    await gallery.route('**/header-scroll.js*', route => route.fulfill({contentType:'text/javascript',body:oldGuard}));
    await gallery.goto(`${base}/art-study/the-good-shepherd.html`, {waitUntil:'load'});
    await gallery.locator('a[href="../art.html#gallery-original-the-good-shepherd"]').click();
    await gallery.waitForLoadState('load');
    await gallery.waitForTimeout(950);
    const hiddenModalNegative = await gallery.evaluate(measure, '#gallery-original-the-good-shepherd');
    assert(hiddenModalNegative.error > 20 && hiddenModalNegative.top < 52, 'Old modal guard must reproduce the gallery artwork hidden under the header');
    special.push({kind:'hidden-modal-guard-negative', ...hiddenModalNegative});
    await gallery.close();
    const oldSkipPage = await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
    await oldSkipPage.route('https://**', route => route.abort());
    const oldSkip = currentHeader.replace("window.addEventListener('click', function (event) {", "window.addEventListener('click', function (event) { if (event.defaultPrevented) return;");
    assert.notEqual(oldSkip, currentHeader);
    await oldSkipPage.route('**/header-scroll.js*', route => route.fulfill({contentType:'text/javascript',body:oldSkip}));
    await oldSkipPage.goto(`${base}/timelines/willie-and-martin-handcart-map.html`, {waitUntil:'load'});
    await oldSkipPage.locator('[data-focuschrist-skip-link="true"]').focus();
    await oldSkipPage.keyboard.press('Enter');
    await oldSkipPage.waitForTimeout(950);
    const skipNegative = await oldSkipPage.evaluate(() => {
      const target = document.querySelector('#handcart-main h1, #handcart-main h2');
      return {headingTop:target.getBoundingClientRect().top, headerBottom:document.querySelector('.nav').getBoundingClientRect().bottom, focused:document.activeElement.id};
    });
    assert(skipNegative.headingTop < skipNegative.headerBottom, 'Old skip handler must reproduce the clipped phone heading');
    assert.equal(skipNegative.focused, 'handcart-main');
    special.push({kind:'prior-keyboard-skip-negative', ...skipNegative});
    await oldSkipPage.close();
    for (const dockDisabled of [false, true]) {
    const dockPage = await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
    await dockPage.route('https://**', route => route.abort());
    const withoutDock = currentHeader.replace("if (ownedTimelineLanding && target.closest('[data-timeline-pane]')) {", "if (false && ownedTimelineLanding && target.closest('[data-timeline-pane]')) {");
    assert.notEqual(withoutDock, currentHeader);
    await dockPage.route('**/header-scroll.js*', route => route.fulfill({contentType:'text/javascript',body:dockDisabled ? withoutDock : currentHeader}));
    await dockPage.goto(`${base}/timelines/life-of-christ-journey-map.html`, {waitUntil:'load'});
    await dockPage.evaluate(() => document.fonts.ready);
    await dockPage.waitForFunction(() => window.TimelineWorkspace && document.querySelector('.timeline-map-dock') &&
      document.querySelector('[data-focuschrist-skip-link="true"]'));
    await dockPage.locator('[data-focuschrist-skip-link="true"]').focus();
    await dockPage.keyboard.press('Enter');
    await dockPage.waitForTimeout(950);
    // Remove the single-snapshot readiness assumption; the original hosted
    // failure omitted geometry, so its exact cause remains unconfirmed. Both
    // current and mutated controls must retain their strict final geometry.
    let dockExpectedStateObserved = false;
    try {
      await dockPage.waitForFunction(disabled => {
        const main = document.querySelector('#main-content');
        const heading = Array.from(main.querySelectorAll('h1,h2,h3,h4')).find(item =>
          !item.closest('[hidden]') && item.getClientRects().length);
        const dock = document.querySelector('.timeline-map-dock');
        const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        const h = heading?.getBoundingClientRect(), d = dock?.getBoundingClientRect();
        return h && d && getComputedStyle(dock).position === 'sticky' &&
          d.top <= header.getBoundingClientRect().bottom + 2 &&
          h.left < d.right && h.right > d.left &&
          (disabled ? h.top < d.bottom && h.bottom > d.top : h.top >= d.bottom);
      }, dockDisabled, {timeout:5000});
      dockExpectedStateObserved = true;
    } catch (error) {
      if (error.name !== 'TimeoutError') throw error;
    }
    const dockFirstMeasurement = await dockPage.evaluate(measure, '#main-content');
    await dockPage.waitForTimeout(350);
    const dockNegative = await dockPage.evaluate(measure, '#main-content');
    const dockDiagnostics = await dockPage.evaluate(() => ({
      dockRect:document.querySelector('.timeline-map-dock').getBoundingClientRect().toJSON(),
      headerRect:document.querySelector('.nav[data-focuschrist-header="standard"]').getBoundingClientRect().toJSON(),
      focused:document.activeElement.id, fonts:document.fonts.status,
      workspaceReady:typeof window.TimelineWorkspace?.showStory === 'function',
      mainDisplay:getComputedStyle(document.querySelector('#main-content')).display,
    }));
    special.push({kind:dockDisabled ? 'pinned-map-dock-negative' : 'pinned-map-dock-current-control', ...dockNegative, dockFirstMeasurement, dockExpectedStateObserved, ...dockDiagnostics});
    assert(dockExpectedStateObserved && [dockFirstMeasurement, dockNegative].every(value => dockDisabled ?
      value.headingTop < value.cover && value.error > 100 : value.headingTop >= value.cover - 1 && value.error <= 1.5),
      `The current dock-aware landing must stay clear and the dock-disabled mutation must stay occluded: ${JSON.stringify({dockDisabled, dockFirstMeasurement, dockNegative, dockExpectedStateObserved, ...dockDiagnostics})}`);
    await dockPage.close();
    }
    for (const [kind, functionName, query, href, target] of [
      ['story-pane-negative', 'isTimelineStoryBookmark', 'The Annunciation to Mary', '/timelines/life-of-christ-journey-map.html#dTitle', '#detail'],
      ['ask-heading-negative', 'isAskContentBookmark', 'Your Study Conversation', '/ask.html#conversation-heading', '#conversation-heading'],
    ]) {
      const negativePage = await browser.newPage({viewport:{width:kind === 'story-pane-negative' ? 390 : 1366,height:900},reducedMotion:'reduce'});
      await negativePage.route('https://**', route => route.abort());
      const disabled = currentHeader.replace(`function ${functionName}(hash) {`, `function ${functionName}(hash) { return false;`);
      assert.notEqual(disabled, currentHeader);
      await negativePage.route('**/header-scroll.js*', route => route.fulfill({contentType:'text/javascript',body:disabled}));
      await negativePage.goto(`${base}/search.html?q=${encodeURIComponent(query)}`, {waitUntil:'load'});
      await negativePage.locator(`.fc-search-result a[href="${href}"]`).click();
      await negativePage.waitForLoadState('load');
      await negativePage.waitForTimeout(950);
      const failed = await negativePage.evaluate(measure, target);
      assert(kind === 'story-pane-negative' ? !failed.visible : failed.top < failed.cover, JSON.stringify(failed));
      special.push({kind, ...failed});
      await negativePage.close();
    }
    const composer = await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
    await composer.route('https://**', route => route.abort());
    await composer.goto(`${base}/ask.html?search-question=John%2020#ask-question`, {waitUntil:'load'});
    await composer.waitForTimeout(950);
    assert.equal(await composer.locator('#userInput').inputValue(), 'John 20');
    assert.equal(new URL(composer.url()).hash, '#ask-question');
    special.push({kind:'ask-composer-prefill-ownership-no-submission'});
    await composer.close();
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
    const dir = process.env.QA_REPORT_DIR || path.join(root, '.qa-artifacts');
    fs.mkdirSync(dir, {recursive:true});
    fs.writeFileSync(path.join(dir, 'section-top-navigation.json'), JSON.stringify({records,special}, null, 2));
  }
  console.log(`SECTION TOP NAVIGATION PASS: ${records.length} landing cases, ${special.length} history/deep-link/cancellation/negative checks`);
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
