'use strict';
// One byte-pinned existing-artifact viewer. No supplied scripts run here.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const ADAMS_ROUTE = '/timelines/adams-1881-chart.html';
const PAGE_SHA = '95802a989d818d0ff7297660274c62f18140950b0bf58fc96a90277ef1e1cb90';
const HELPER_SHA = '69c7e3713659f885c65fd69bc78c61b93a58a80f413c47816c3b57b84b074343';
const CREDIT = 'Sebastian C. Adams, Synchronological Chart (1881). Chart image from Wikimedia Commons, courtesy of the David Rumsey Map Collection. The image is in the public domain.';
const INDEPENDENCE = 'focusChrist is an independent faith-based website and is not an official website of, sponsored by, or endorsed by The Church of Jesus Christ of Latter-day Saints. For official Church information, visit ChurchofJesusChrist.org.';
const digest = text => crypto.createHash('sha256').update(text).digest('hex');
const clean = node => node.textContent.replace(/\s+/g,' ').trim();
function assertAdamsSource(route, html, helper) {
  assert.equal(route, ADAMS_ROUTE, 'Exact standalone owner only');
  assert.equal(Buffer.byteLength(html), 62030);
  assert.equal(digest(html), PAGE_SHA, 'Exact V9 standalone source');
  assert.equal(Buffer.byteLength(helper), 26883);
  assert.equal(digest(helper), HELPER_SHA, 'Exact 101-state hosted helper');
}
function withoutAdamsCanonical(routes, read) {
  assert.equal(routes.length, 138, '137 existing routes plus exact Adams owner');
  assert.equal(new Set(routes).size, 138, 'No duplicate canonical routes');
  assert.equal(routes.filter(r=>r===ADAMS_ROUTE).length, 1, 'Missing exact Adams owner');
  assertAdamsSource(ADAMS_ROUTE, read(ADAMS_ROUTE.slice(1)), read('tools/adams_chart_browser_qa.js'));
  return routes.filter(route=>route!==ADAMS_ROUTE);
}
function assertAdamsStandalone(route, html, document, helper) {
  assertAdamsSource(route, html, helper);
  const one = selector => {const nodes=document.querySelectorAll(selector);assert.equal(nodes.length,1,'Unique '+selector);return nodes[0];};
  const heading=one('h1');assert(heading.matches('#toolbar .toprow > h1.title'));assert.equal(clean(heading),'Adams’ Chart · 1881');
  const strip=one('#toolbar > .fc-adams-strip');
  const back=one('.fc-adams-back'),home=one('.fc-adams-home');
  assert.equal(back.parentElement,strip);assert.equal(home.parentElement,strip);
  assert.equal(back.getAttribute('href'),'../timeline.html#choose-timeline');assert.equal(clean(back),'Back to timelines');
  assert.equal(home.getAttribute('href'),'../index.html');assert.equal(clean(home),'FocusChrist Home');
  assert.equal(new Set([back,home].map(a=>new URL(a.href).pathname)).size,2,'Distinct real local destinations');
  const notes=strip.querySelectorAll(':scope > p.fc-adams-note');assert.equal(notes.length,2);
  assert.equal(clean(notes[0]),INDEPENDENCE);assert.equal(clean(notes[1]),CREDIT);assert(notes[1].matches('.fc-adams-credit'));
  for(const element of [heading,back,home,...notes])for(let n=element;n;n=n.parentElement){assert(!n.hidden&&n.getAttribute('aria-hidden')!=='true','Required standalone copy is not hidden');assert(!/(?:display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\D|$))/i.test(n.getAttribute('style')||''),'No inline hiding of required standalone copy');}
  const church=notes[0].querySelectorAll('a');assert.equal(church.length,1);assert.equal(church[0].getAttribute('href'),'https://www.churchofjesuschrist.org/');
  const credit=notes[1].querySelectorAll('a');assert.equal(credit.length,1);assert.equal(credit[0].getAttribute('href'),'https://commons.wikimedia.org/wiki/File:Adams_Synchronological_Chart,_1881.jpg');
  for(const a of [...church,...credit]){assert.equal(a.target,'_blank');assert(a.relList.contains('noopener')&&a.relList.contains('noreferrer'));}
  assert.equal(document.querySelectorAll('script[src],iframe,footer').length,0,'Standalone has no shared controller or invented footer');
  assert.equal(document.querySelectorAll('[data-focuschrist-artwork-disclosure]').length,0,'Exact reviewed standalone source has no added disclosure element');
  assert.equal(one('link[rel="canonical"]').getAttribute('href'),'https://focuschrist.com'+ADAMS_ROUTE);
  assert.equal(one('meta[name="viewport"]').getAttribute('content'),'width=device-width,initial-scale=1,viewport-fit=cover');
  return {route,kind:'exact-existing-artifact-standalone',source_sha256:PAGE_SHA,helper_sha256:HELPER_SHA,sharedFooter:false,renderedEvidence:'Requires the separately reviewed current hosted 101-state report; this DOM contract is not rendered proof.'};
}
module.exports={ADAMS_ROUTE,PAGE_SHA,HELPER_SHA,assertAdamsSource,withoutAdamsCanonical,assertAdamsStandalone};
