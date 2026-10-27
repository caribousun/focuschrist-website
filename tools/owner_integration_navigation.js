'use strict';
// Exact current source/DOM validation; explicit old fixtures are never current UI evidence.
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const MANIFEST='docs/owner-integration-contract/source-manifest.json';
const MANIFEST_SHA='ede123415bdeda93becf9d1b88acd2b07fa2f80c985335624ef39ee4d8f00aca';
const ROUTE_SHA='ba19da4af6ba32219ff9555ecf5ddd466077acd9a6ee09a7d49f29c07d1f4284';
const chart='timelines/adams-1881-chart.html',intro='timelines/adams-1881-introduction.html',landing='timeline.html',hub='history/emma-hale-smith.html';
const stories={'history/emma-elect-lady.html':'emma-story1-ride','history/emma-hymns.html':'emma-story2-hymnal','history/emma-winter-crossing.html':'emma-story3-quincy','history/emma-relief-society.html':'emma-story4-hospitality','history/emma-last-testimony.html':'emma-story5-testimony'};
const currentPages=[chart,intro,landing,hub,...Object.keys(stories)];
const digest=value=>crypto.createHash('sha256').update(value).digest('hex');
const clean=n=>n.textContent.replace(/\s+/g,' ').trim();
const bare=p=>p==='/'?'index.html':p.replace(/^\//,'');
function manifest(read){const raw=read(MANIFEST);assert.equal(digest(raw),MANIFEST_SHA,'Exact integration manifest');const m=JSON.parse(raw);assert.equal(m.schema,1);assert.equal(Object.keys(m.files).length,11);return m;}
function assertSource(route,source,read){const item=manifest(read).files[route];assert(item,'Known integration source');assert.equal(Buffer.byteLength(source),item.bytes,route+' bytes');assert.equal(digest(source),item.sha256,route+' current source');return item;}
function assertCurrentDOM(route,doc){
 assert(currentPages.includes(route),'Known current integration page');
 const one=s=>{const a=doc.querySelectorAll(s);assert.equal(a.length,1,route+' unique '+s);return a[0];};
 const nav=one('nav[data-focuschrist-header="standard"]');
 assert.equal(nav.querySelectorAll('[data-site-search-trigger]').length,1,'Current shared Search');
 const menu=nav.querySelector('.hamburger');assert(menu&&menu.getAttribute('role')==='button'&&menu.getAttribute('tabindex')==='0'&&menu.getAttribute('aria-controls')==='hamburgerMenu','Current keyboard menu');
 assert.equal(nav.querySelectorAll('#hamburgerMenu').length,1);
 const footer=one('footer[data-focuschrist-footer="standard"]'),ind=footer.querySelectorAll('[data-focuschrist-independence="footer"]'),dis=footer.querySelectorAll('[data-focuschrist-artwork-disclosure="footer"]');
 assert.equal(ind.length,1);assert.equal(dis.length,1);assert.equal(ind[0].nextElementSibling,dis[0],'Adjacent current footer notices');
 one('h1');const ids=[...doc.querySelectorAll('[id]')].map(n=>n.id);assert.equal(ids.length,new Set(ids).size,'No duplicate current IDs');
 if(route===chart||route===intro){
  assert.equal(one('link[rel="canonical"]').getAttribute('href'),'https://focuschrist.com/'+route);
  assert.equal(doc.querySelectorAll('.fc-adams-strip').length,0,'Rejected top strip absent');
  assert.equal(one('link[href*="site-system.css"]').getAttribute('href'),'../site-system.css?v=20261005-mobile-study-rows-1');
  assert.equal(nav.querySelector('[data-site-search-trigger]').getAttribute('href'),'../search.html');
  const credit=footer.querySelector('.fc-adams-credit');assert(credit&&clean(credit).includes('courtesy of the David Rumsey Map Collection')&&clean(credit).includes('The image is in the public domain.'));
  const commons=credit.querySelector('a');assert.equal(commons.getAttribute('href'),'https://commons.wikimedia.org/wiki/File:Adams_Synchronological_Chart,_1881.jpg');assert.equal(commons.target,'_blank');assert(commons.relList.contains('noopener')&&commons.relList.contains('noreferrer'));
 }
 if(route===chart){assert.equal(clean(one('#toolbar h1.title')),'Adams’ Chart · 1881');for(const id of ['toolbar','viewport','tiles','fit','full','fillScreen','showNav','mini'])assert(one('#'+id).closest('main#adams-chart-main'),'Chart controls remain in bounded main');}
 if(route===intro){
  const hero=one('.fc-visual-hero.timeline-life-hero.timeline-history-hero');assert.equal(hero.querySelector('img').getAttribute('src'),'../assets/adams-chart/adams-16-0-0.jpg');
  const opening=one('header.fc-page-intro.timeline-life-intro.timeline-history-intro');const cue=opening.querySelectorAll('a.fc-scroll-cue.timeline-opening-continue');assert.equal(cue.length,1);assert.equal(cue[0].getAttribute('href'),'#adams-overview');one('section#adams-overview');assert.equal(one('#adams-open-chart').getAttribute('href'),'adams-1881-chart.html');
 }
 if(route===landing){const section=one('section#adams-1881');assert.equal(section.querySelectorAll('.fc-button--primary[href="timelines/adams-1881-introduction.html"]').length,1);assert.equal(section.querySelectorAll('a[href="timelines/adams-1881-introduction.html"] > img').length,1);}
 if(route===hub){
  const owners=[...doc.querySelectorAll('figure[data-exclusive-artwork]')],expected=[...Object.values(stories),'emma-h1','emma-h3','emma-h4','emma-h5','emma-c1','emma-c3','emma-c4','emma-c5'].sort();assert.deepEqual(owners.map(n=>n.dataset.exclusiveArtwork).sort(),expected,'Exactly nine Emma/four retained Christ owners');assert.equal(doc.querySelectorAll('#picture-emma-c2').length,0);
  for(const scene of Object.values(stories)){const figure=one('#picture-'+scene+'[data-exclusive-artwork="'+scene+'"][data-topic-art="'+scene+'"]');const a=figure.querySelectorAll(':scope > a[aria-haspopup="dialog"]');assert.equal(a.length,1);assert.equal(a[0].getAttribute('href'),'/assets/page-art/emma-life/'+scene+'-review-1536.webp');assert.equal(figure.querySelectorAll(':scope > figcaption[data-picture-panel-copy][hidden]').length,1);}
  for(const id of ['elect-lady-right-person','hymns-book','crossing-words','relief-relieved','testimony-kept'])one('section#'+id);
 }
 if(stories[route]){
  const scene=stories[route],figure=one('figure[data-artwork-reference="'+scene+'"][data-linked-picture-reference="'+scene+'"]');assert.equal(doc.querySelectorAll('figure[data-exclusive-artwork]').length,0,'Reference page has no competing owner');assert.equal(figure.querySelectorAll(':scope > a').length,0,'Reference must not be recaptured by detail controller');const image=figure.querySelectorAll(':scope > div > a > img');assert.equal(image.length,1);assert.equal(image[0].parentElement.getAttribute('href'),'emma-hale-smith.html#picture-'+scene);
 }
}
function validateAll(read,JSDOM){const m=manifest(read);for(const [route] of Object.entries(m.files)){const source=read(route);assertSource(route,source,read);if(currentPages.includes(route)){const d=new JSDOM(source);try{assertCurrentDOM(route,d.window.document);}finally{d.window.close();}}}}
function projectCanonicalRoutes(routes,read){const normalized=routes.map(bare);assert.equal(normalized.length,139);assert.equal(new Set(normalized).size,139);assert.equal(digest([...normalized].sort().join('\n')),ROUTE_SHA,'Exact139 canonical set');for(const route of [chart,intro,landing,'adams-integration.css','adams-integration.js'])assertSource(route,read(route),read);return routes.filter(r=>![chart,intro].includes(bare(r)));}
function historicalSource(route,source,read){
 const item=assertSource(route,source,read),h=item.historical;assert(h,'No invented predecessor for new page');let raw=Buffer.from(source);
 for(const s of [...h.inverse_spans].reverse()){const before=Buffer.from(s.before,'base64'),after=Buffer.from(s.after,'base64');assert(raw.subarray(s.current_offset,s.current_offset+after.length).equals(after),'Exact inverse context');raw=Buffer.concat([raw.subarray(0,s.current_offset),before,raw.subarray(s.current_offset+after.length)]);}
 assert.equal(raw.length,h.bytes);assert.equal(digest(raw),h.sha256,'Exact historical endpoint');return raw.toString('utf8');
}
function historicalRead(read){return route=>{
 if(route==='tools/adams_chart_browser_qa.js'){const raw=read('docs/adams-chart-import/history/v9/tools__adams_chart_browser_qa.js.source');assert.equal(digest(raw),'69c7e3713659f885c65fd69bc78c61b93a58a80f413c47816c3b57b84b074343');return raw;}
 if(route==='sitemap.xml')return read(route).replace(/\s*<url>\s*<loc>https:\/\/focuschrist\.com\/timelines\/adams-1881-introduction\.html<\/loc>\s*<\/url>/,'');
 const item=manifest(read).files[route];return item&&item.historical?historicalSource(route,read(route),read):read(route);
};}
function historicalControlInventory(inventory,selectors,numbered,read,JSDOM){
 assert.equal(inventory.canonical_pages,139);const result=JSON.parse(JSON.stringify(inventory));const past=historicalRead(read);
 for(const route of currentPages){
  const source=read(route);assertSource(route,source,read);const current=new JSDOM(source),old=route===intro?null:new JSDOM(past(route));
  try{
   assertCurrentDOM(route,current.window.document);
   for(const selector of selectors){const now=current.window.document.querySelectorAll(selector).length,prior=old?old.window.document.querySelectorAll(selector).length:0;const item=result.selectors[selector];assert(item);assert.equal(item.pages.includes(route),now>0,'Actual discovered current owner '+route+' '+selector);item.count+=prior-now;assert(item.count>=0);item.pages=item.pages.filter(p=>p!==route);if(prior)item.pages.push(route);item.pages.sort();}
   for(const selector of numbered){const key=route+' '+selector;const rows=doc=>[...doc.querySelectorAll(selector)].map(n=>({href:n.getAttribute('href'),label:clean(n)}));const now=rows(current.window.document),prior=old?rows(old.window.document):[];assert.deepEqual(result.numbered_navigation[key]||[],now,'Actual numbered controls '+key);delete result.numbered_navigation[key];if(prior.length)result.numbered_navigation[key]=prior;}
  }finally{current.window.close();if(old)old.window.close();}
 }
 result.canonical_pages=138;return result;
}
module.exports={MANIFEST,MANIFEST_SHA,chart,intro,landing,hub,stories,currentPages,assertSource,assertCurrentDOM,validateAll,projectCanonicalRoutes,historicalSource,historicalRead,historicalControlInventory};
