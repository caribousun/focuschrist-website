'use strict';
// Static JSDOM only: supplied scripts are never evaluated by this test module.
const assert=require('node:assert/strict');
const contract=require('./owner_integration_navigation');
function selfTest(routes,read,JSDOM){
 let positive=0,negative=0;const rejects=fn=>{assert.throws(fn,assert.AssertionError);negative++;};
 const check=(route,mutation)=>{const dom=new JSDOM(read(route));try{if(mutation)mutation(dom.window.document);contract.assertCurrentDOM(route,dom.window.document);}finally{dom.window.close();}};
 contract.validateAll(read,JSDOM);positive++;
 for(const route of contract.currentPages){check(route);positive++;
  for(const mutation of [d=>d.querySelector('[data-site-search-trigger]').remove(),d=>d.querySelector('.hamburger').remove(),d=>d.querySelector('footer[data-focuschrist-footer]').remove(),d=>d.querySelector('[data-focuschrist-independence]').remove(),d=>d.querySelector('[data-focuschrist-artwork-disclosure]').remove(),d=>d.querySelector('h1').remove()])rejects(()=>check(route,mutation));
  rejects(()=>contract.assertSource(route,read(route)+' ',read));
 }
 for(const mutation of [d=>d.querySelector('.timeline-opening-continue').setAttribute('href','#missing'),d=>d.querySelector('.timeline-life-hero img').setAttribute('src','wrong.jpg'),d=>d.querySelector('#adams-open-chart').remove()])rejects(()=>check(contract.intro,mutation));
 for(const mutation of [d=>d.querySelector('#viewport').remove(),d=>d.querySelector('.fc-adams-credit a').removeAttribute('target'),d=>d.querySelector('.fc-adams-credit a').setAttribute('rel','noopener'),d=>d.body.insertAdjacentHTML('beforeend','<div class="fc-adams-strip">Old strip</div>')])rejects(()=>check(contract.chart,mutation));
 for(const scene of Object.values(contract.stories)){
  rejects(()=>check(contract.hub,d=>d.querySelector('#picture-'+scene).remove()));
  rejects(()=>check(contract.hub,d=>{const f=d.querySelector('#picture-'+scene);f.after(f.cloneNode(true));}));
 }
 rejects(()=>check(contract.hub,d=>d.body.insertAdjacentHTML('beforeend','<figure id="picture-emma-c2" data-exclusive-artwork="emma-c2"></figure>')));
 for(const [route,scene] of Object.entries(contract.stories))for(const mutation of [
  d=>d.querySelector('figure[data-artwork-reference]').setAttribute('data-exclusive-artwork',scene),
  d=>d.querySelector('figure[data-artwork-reference] > div > a').setAttribute('href','wrong.html'),
  d=>{const wrapper=d.querySelector('figure[data-artwork-reference] > div');wrapper.replaceWith(...wrapper.childNodes);}
 ])rejects(()=>check(route,mutation));
 const before=JSON.stringify(routes);assert.equal(contract.projectCanonicalRoutes(routes,read).length,137);assert.equal(JSON.stringify(routes),before);positive++;
 rejects(()=>contract.projectCanonicalRoutes(routes.filter(p=>p!=='/'+contract.intro),read));
 rejects(()=>contract.projectCanonicalRoutes([...routes,routes[0]],read));
 rejects(()=>contract.projectCanonicalRoutes(routes.map(p=>p==='/'+contract.intro?'/unknown.html':p),read));
 rejects(()=>contract.projectCanonicalRoutes(routes,p=>read(p)+(p===contract.chart?' ':'')));
 rejects(()=>contract.assertSource('unknown.html','unknown',read));
 rejects(()=>contract.historicalSource(contract.intro,read(contract.intro),read));
 const manifest=JSON.parse(read(contract.MANIFEST));
 for(const [route,item] of Object.entries(manifest.files))if(item.historical){const restored=contract.historicalSource(route,read(route),read);assert.equal(require('node:crypto').createHash('sha256').update(restored).digest('hex'),item.historical.sha256);positive++;}
 // Exact current contributions are removed and exact predecessor contributions
 // restored; an unrelated owner remains visible, never silently filtered.
 const selectors=['.fc-study-visual-sources a:not(.fc-button--primary)','.fc-resource-next a'];
 const numbered=['.watch-topic-index a','nav[aria-label="Pioneer study sections"] a','.bom-story-directory a'];
 function inventory(sourceRead,selected,count){const out={canonical_pages:count,selectors:{},numbered_navigation:{}};for(const s of selectors)out.selectors[s]={count:1,pages:['unrelated.html']};
  for(const route of selected){const dom=new JSDOM(sourceRead(route));try{const d=dom.window.document;for(const s of selectors){const n=d.querySelectorAll(s).length;if(n){out.selectors[s].count+=n;out.selectors[s].pages.push(route);}}for(const s of numbered){const rows=[...d.querySelectorAll(s)].map(n=>({href:n.getAttribute('href'),label:n.textContent.replace(/\s+/g,' ').trim()}));if(rows.length)out.numbered_navigation[route+' '+s]=rows;}}finally{dom.window.close();}}
  for(const item of Object.values(out.selectors))item.pages.sort();return out;}
 const current=inventory(read,contract.currentPages,139),past=inventory(contract.historicalRead(read),contract.currentPages.filter(p=>p!==contract.intro),138);
 assert.deepEqual(contract.historicalControlInventory(current,selectors,numbered,read,JSDOM),past);positive++;
 const drift=JSON.parse(JSON.stringify(current));drift.selectors[selectors[0]].count++;rejects(()=>assert.deepEqual(contract.historicalControlInventory(drift,selectors,numbered,read,JSDOM),past));
 return {positive,negative,scope:'Exact current DOM/source and explicit historical contribution inverses only; no browser, script evaluation, or full-site acceptance.'};
}
module.exports={selfTest};
if(require.main===module){const fs=require('node:fs'),path=require('node:path'),root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');const routes=[...read('sitemap.xml').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname);console.log(JSON.stringify(selfTest(routes,read,require('jsdom').JSDOM)));}
