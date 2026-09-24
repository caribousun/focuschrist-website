/* Called by the existing CI-only canonical browser gate. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
module.exports = async function checkInteractionPresentation(page, origin, routes) {
  const results = [];
  const record = (test, data) => results.push({test, ...data});
  try {
    for (const width of [320, 390, 768, 1024, 1366, 1920]) {
      await page.setViewportSize({width, height: 1000});
      for (const route of routes.filter(r => r.startsWith('answers/'))) {
        await page.goto(origin + '/' + route, {waitUntil:'load'});
        const rail = await page.evaluate(() => {
          const main = document.querySelector('main');
          const rect = main.getBoundingClientRect(), style = getComputedStyle(main);
          const standard = parseFloat(getComputedStyle(document.body).getPropertyValue('--fc-standard'));
          return {width:rect.width, left:rect.left, padding:parseFloat(style.paddingLeft), viewport:document.documentElement.clientWidth, standard};
        });
        const expected = Math.min(rail.standard, rail.viewport - 2 * Math.min(24, Math.max(16, width * .02)));
        assert(Math.abs(rail.width - expected) < 2, route + ' incorrect outer rail at ' + width);
        assert(Math.abs(rail.left - (rail.viewport - expected) / 2) < 2, route + ' rail is not centered');
        assert.equal(rail.padding, 0, route + ' double horizontal gutter');
      }
      await page.goto(origin + '/watch.html', {waitUntil:'load'});
      const row = await page.evaluate(() => {
        const section=document.querySelector('[data-watch-shorts]'), bounds=section.getBoundingClientRect();
        return {open:section.querySelector('details').open, desktop:section.hasAttribute('data-shorts-desktop'), left:bounds.left, right:bounds.right,
          cards:[...section.querySelectorAll('.watch-short')].map(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,right:r.right};})};
      });
      assert.equal(row.desktop, width >= 1024);
      assert.equal(row.open, width >= 1024);
      assert.equal(row.cards.length, 4);
      if (width >= 1024) for (const card of row.cards) {
        assert(Math.abs(card.y - row.cards[0].y) < 1, 'Shorts must share one desktop row');
        assert(Math.abs(card.width - row.cards[0].width) < 1, 'Shorts widths differ');
        assert(card.x >= row.left - 1 && card.right <= row.right + 1, 'Shorts escape rails');
      }
      record('rails-and-shorts', {width, answerPages:routes.filter(r=>r.startsWith('answers/')).length, row});
    }
    await page.setViewportSize({width:1366,height:1000});
    const cases = [
      ['index.html','.fc-home-purpose-paths .fc-card'],
      ['index.html','.fc-page-intro .fc-button'],
      ['answers.html','.fc-answers-jumps a'],
      ['answers/faith-in-jesus-christ-during-trials.html','.notice'],
      ['answers/faith-in-jesus-christ-during-trials.html','.cta'],
      ['watch.html','.watch-short'],
      ['watch.html','.watch-short-open'],
      ['jesus-christ/mortal-ministry.html','.jj-local-nav a'],
      ['pioneers.html','nav[aria-label="Pioneer study sections"] .fc-button'],
      ['pioneers.html','.journal-action'],
      ['church-history.html','.fc-history-art-panel figcaption > a'],
    ];
    for (const [route, selector] of cases) {
      await page.emulateMedia({reducedMotion:'no-preference'});
      await page.goto(origin+'/'+route,{waitUntil:'load'});
      if (selector === '.jj-local-nav a') await page.locator('.jj-chapter-picker > summary').click();
      const target=page.locator(selector).first();
      await target.hover();
      await page.waitForTimeout(240);
      const hover=await target.evaluate(n=>({transform:getComputedStyle(n).transform, left:n.getBoundingClientRect().left,right:n.getBoundingClientRect().right}));
      assert(!['none','matrix(1, 0, 0, 1, 0, 0)'].includes(hover.transform),route+' missing hover: '+selector);
      assert(hover.left>=-1 && hover.right<=1367,'Hover escapes horizontal page');
      await page.emulateMedia({reducedMotion:'reduce'});
      const reduced=await target.evaluate(n=>getComputedStyle(n).transform);
      assert.equal(reduced,'none','Reduced motion ignored: '+selector);
      record('hover-reduced-motion',{route,selector,hover,reduced});
    }
    await page.emulateMedia({reducedMotion:'no-preference'});
    await page.goto(origin+'/index.html');
    const action=page.locator('.fc-page-intro .fc-button').first();
    await action.focus();
    await page.keyboard.press('Tab');
    await page.keyboard.press('Shift+Tab');
    await page.waitForTimeout(240);
    assert(await action.evaluate(n=>n.matches(':focus-visible')),'Keyboard focus must stay visible');
    assert.notEqual(await action.evaluate(n=>getComputedStyle(n).transform),'none');
    record('keyboard-focus',{visible:true,motion:true});
    // Demonstrate the width gate would catch the original 920px defect.
    await page.goto(origin+'/answers/faith-in-jesus-christ-during-trials.html');
    await page.addStyleTag({content:'body.fc-site main.content-wrap.article { width:920px !important; }'});
    assert.notEqual(Math.round(await page.locator('main').evaluate(n=>n.getBoundingClientRect().width)),1040);
    record('original-width-negative-fixture',{detected:true});
    console.log('PASS interaction presentation: answer rails, desktop Shorts, hover and reduced motion');
  } finally {
    fs.mkdirSync(path.join('.qa-artifacts'),{recursive:true});
    fs.writeFileSync('.qa-artifacts/interaction-presentation.json',JSON.stringify({results},null,2)+'\n');
  }
};
