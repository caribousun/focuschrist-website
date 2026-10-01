// Exercise the shared footer action on every canonical page, not a synthetic subset.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM} = require('jsdom');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root,name),'utf8');
const artworkDisclosure = 'Artwork on focusChrist includes AI-generated artistic interpretations. Illustrative and reconstructed details are not photographs or eyewitness records of the people or events shown.';
const pages = [...read('sitemap.xml').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname);
assert.equal(pages.length,125);
assert.ok(pages.includes('/answers/race-priesthood-and-temple-blessings.html'),'new dependent study must receive the shared footer test');
let bareGalleryEntries=0;
for(const route of [...pages,'/404.html','/search.html']){
 const file=route==='/'?'index.html':route.slice(1),dom=new JSDOM(read(file),{url:'https://focuschrist.com'+route});
 for(const a of dom.window.document.querySelectorAll('a[href]')){
  const url=new URL(a.href);
  if(url.origin==='https://focuschrist.com'&&url.pathname==='/art-gallery.html'&&!url.search&&!url.hash){
   assert.equal(file,'art.html','Generic Art destinations must not skip the approved opening: '+file);
   assert.equal(a.textContent.trim(),'Browse All Artwork','Only the explicit complete-gallery action bypasses Art');bareGalleryEntries++;
  }
 }
 dom.window.close();
}
assert.equal(bareGalleryEntries,1,'Art must retain its one explicit complete-gallery entry');
for(const route of [...pages, '/404.html']){
 const file=route==='/'?'index.html':route.slice(1);
 const dom=new JSDOM(read(file),{url:'https://focuschrist.com'+route+'?from=footer#reading',runScripts:'outside-only'});
 const w=dom.window,d=w.document;let scroll;
 const savedArt=d.querySelectorAll('footer [data-focuschrist-art-gallery]');
 for(const a of savedArt)assert.equal(new URL(a.href).pathname,'/art.html',file+' any saved Art entry must use approved page');
 const artCase=([...pages,'/404.html'].indexOf(route))%3;
 if(artCase!==0){const p=d.createElement('p'),a=d.createElement('a');a.setAttribute('data-focuschrist-art-gallery','');a.href=artCase===1?'/art-gallery.html':'/art.html';a.textContent='Art Gallery';p.append(a);d.querySelector('footer').append(p);}
 const savedDisclosure=d.querySelectorAll('footer [data-focuschrist-artwork-disclosure="footer"]');
 assert.equal(savedDisclosure.length,1,file+' saved footer disclosure must work without scripts');
 assert.equal(savedDisclosure[0].textContent,artworkDisclosure,file+' exact artwork disclosure');
 const independence=[...d.querySelectorAll('footer p')].find(p=>p.textContent.startsWith('focusChrist is an independent faith-based website'));
 assert(independence,file+' existing independence notice');
 assert.equal(independence.nextElementSibling,savedDisclosure[0],file+' notices must be adjacent');
 const independenceBefore=independence.outerHTML;
 // Exercise both saved-page preservation and recovery for older generated pages.
 if(pages.indexOf(route)%2===0) savedDisclosure[0].remove();

 assert.equal(d.querySelectorAll('.breadcrumbs, .jj-breadcrumbs, nav[aria-label="Breadcrumb"]').length,0,file+' must not restore pathway rows');
 w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){}});
 w.requestAnimationFrame=()=>0;
 w.scrollTo=options=>{scroll=options};
 w.eval(read('site-common.js'));
 d.dispatchEvent(new w.Event('DOMContentLoaded'));
 const buttons=d.querySelectorAll('[data-focuschrist-back-to-top]');
 assert.equal(buttons.length,1,file);
 const b=buttons[0];assert.equal(b.type,'button');assert.equal(b.textContent,'Back to top');
 assert(b.closest('footer[data-focuschrist-footer="standard"]'));
 assert.equal(d.querySelectorAll('link[data-focuschrist-footer-navigation]').length,1);
 assert.equal(new URL(d.querySelector('link[data-focuschrist-footer-navigation]').href).pathname,'/footer-navigation.css','Nested footer stylesheet must resolve at site root');
 const before=w.location.href;b.focus();b.click();
 assert.equal(w.location.href,before,'Back to top must not change page, query, or fragment');
 assert.equal(scroll.top,0);assert.equal(scroll.left,0);assert.equal(scroll.behavior,'instant');
 assert(d.activeElement.matches('.nav[data-focuschrist-header="standard"], main, body'),file+' focus did not return to top');
 assert(!d.activeElement.contains(b),'Focus must leave the footer');
 const focused=d.activeElement;b.focus();assert(!focused.hasAttribute('tabindex'),'Temporary focus target must clean up');
 d.dispatchEvent(new w.Event('DOMContentLoaded'));
 assert.equal(d.querySelectorAll('[data-focuschrist-back-to-top]').length,1,'No duplicate action after reinitialization');
 assert.equal(d.querySelectorAll('[data-focuschrist-artwork-disclosure]').length,1,file+' disclosure must be idempotent');
 const art=d.querySelectorAll('footer [data-focuschrist-art-gallery]');
 assert.equal(art.length,1,file+' Art footer entry must remain unique');
 assert.equal(new URL(art[0].href).pathname,'/art.html',file+' Art footer and menu share destination');
 assert([...d.querySelectorAll('.nav a[href]')].some(a=>new URL(a.href).pathname==='/art.html'),file+' matching Art menu destination');
 const disclosure=d.querySelector('[data-focuschrist-artwork-disclosure]');
 assert.equal(disclosure.textContent,artworkDisclosure);
 assert.equal(independence.nextElementSibling,disclosure,file+' runtime notice adjacency');
 assert.equal(independence.outerHTML,independenceBefore,file+' independence notice preserved exactly');
 assert.equal(disclosure.tagName,'P');
 assert.equal(disclosure.getAttribute('style'),null,'Use existing footer formatting');

 dom.window.close();
}
const template=new JSDOM(read('docs/history-stories/footer.html.template')).window.document;
const artPage=new JSDOM(read('art.html')).window.document;
assert(artPage.querySelector('a[href="art-gallery.html"]'),'Separate gallery remains available from Art');
assert.equal(template.querySelector('[data-focuschrist-artwork-disclosure]').textContent,artworkDisclosure,'History builder must preserve saved disclosure');
const review=JSON.parse(read('docs/footer-navigation-review-20260929.json'));
assert.equal(review.removed_breadcrumb_pages.length,102);
for(const file of review.removed_breadcrumb_pages){
 const d=new JSDOM(read(file)).window.document;
 assert.equal(d.querySelectorAll('.breadcrumbs, .jj-breadcrumbs, nav[aria-label="Breadcrumb"]').length,0,file);
 assert([...d.querySelectorAll('a[href]')].some(a=>/(?:answers|art)\.html(?:#|$)|jesus-christ/.test(a.getAttribute('href'))),'Answers return destination retained');
}
for(const file of ['god-our-heavenly-father.html','restored-church-of-jesus-christ.html']){
 const d=new JSDOM(read('answers/'+file)).window.document;
 assert(d.querySelector('a[href="stand-forever.html#stand-forever"]'),'Existing parent-return pill retained');
}
const css=read('footer-navigation.css');
assert(!/position\s*:\s*(?:fixed|absolute)/.test(css),'Footer control must remain in normal flow');
assert(css.includes('max-width: 100%; white-space: normal;'));
assert(css.includes(':focus-visible'));
console.log(`PASS:${pages.length} canonical plus404 same-page footer actions, focus/route preservation, idempotence,102 removed trails and preserved return destinations`);
