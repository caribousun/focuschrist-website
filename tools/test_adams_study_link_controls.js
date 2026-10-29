'use strict';
const assert=require('node:assert/strict'),helper=require('./adams_study_link_controls');
function assertHistoricalRoutes(routes,read){
 assert(Array.isArray(routes),'Verified historical routes required');
 const expected=[...read('sitemap.xml').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname);
 expected.push('/history/emma-elect-lady.html');
 assert.equal(new Set(routes).size,routes.length,'No duplicate historical routes');
 assert.deepEqual([...routes].sort(),expected.sort(),'Exact historical route set required');
}
module.exports=function(JSDOM,read,selectors,routes){
 const fixtures=['<p class="fc-study-visual-sources"><a>Extra</a></p>','<p class="pioneer-source-links"><a>Extra</a></p>','<p class="fc-resource-next"><a>Extra</a></p>','<nav class="fc-study-nav"><a>Extra</a></nav>','<nav class="cfm-jump"><a>Extra</a></nav>','<nav class="gc-jumps"><a>Extra</a></nav>','<a class="source-link">Extra</a>','<div class="fc-topic-artwork-detail"><a data-topic-art-source>Extra</a></div>','<nav aria-label="Pioneer study sections"><a class="fc-button">Extra</a></nav>','<div class="bom-story-directory"><a>Extra</a></div>','<div class="atonement-path"><a class="fc-button">Extra</a></div>','<nav class="watch-topic-index"><a>Extra</a></nav>'];
 assert.equal(fixtures.length,selectors.length);
 for(const route of [helper.owner,helper.landing]){
  const source=read(route);let dom=new JSDOM(source);helper.validate(dom.window.document,route,selectors,source,read);dom.window.close();
  for(const [i,fixture] of fixtures.entries()){
   dom=new JSDOM(source);const doc=dom.window.document;doc.body.insertAdjacentHTML('beforeend',fixture);assert(doc.querySelector(selectors[i]));assert.throws(()=>helper.validate(doc,route,selectors,source,read),assert.AssertionError);dom.window.close();
  }
  dom=new JSDOM(source);assert.throws(()=>helper.validate(dom.window.document,'unknown.html',selectors,source,read),assert.AssertionError);assert.throws(()=>helper.validate(dom.window.document,route,selectors,source+' ',read),assert.AssertionError);dom.window.close();
 }
 // Use the explicitly validated predecessor route set supplied by the caller.
 // The current sitemap deliberately omits a retired Emma route.
 assertHistoricalRoutes(routes,read);
 const retired='/history/emma-elect-lady.html',intro='/timelines/adams-1881-introduction.html';
 const other=routes.find(r=>r!==retired&&r!=='/'+helper.owner);
 for(const bad of [routes.filter(r=>r!==retired),[...routes,retired],routes.map(r=>r===other?'/unknown.html':r),routes.map(r=>r===retired?intro:r)])assert.throws(()=>assertHistoricalRoutes(bad,read),assert.AssertionError);
 const inventory={canonical_pages:138,selectors:Object.fromEntries(selectors.map(s=>[s,{count:7,pages:['old.html']}])) ,numbered_navigation:{'old.html nav':[]}};
 const validated=[helper.owner,helper.landing];const expected=JSON.parse(JSON.stringify(inventory));expected.canonical_pages=137;
 assert.deepEqual(helper.beforeEmmaInventory(inventory,validated,routes,read),expected);
 for(const bad of [[],[helper.owner],[helper.owner,helper.owner],[helper.owner,'unknown.html']])assert.throws(()=>helper.beforeEmmaInventory(inventory,bad,routes,read),assert.AssertionError);
 for(const bad of [routes.filter(r=>r!=='/'+helper.owner),[...routes,'/'+helper.owner],routes.map(r=>r==='/' + helper.owner?'/unknown.html':r)])assert.throws(()=>helper.beforeEmmaInventory(inventory,validated,bad,read),assert.AssertionError);
 for(const name of [helper.owner,helper.landing]){let bad=JSON.parse(JSON.stringify(inventory));bad.selectors[selectors[0]].pages.push(name);assert.throws(()=>helper.beforeEmmaInventory(bad,validated,routes,read),assert.AssertionError);bad=JSON.parse(JSON.stringify(inventory));bad.numbered_navigation[name+' nav']=[];assert.throws(()=>helper.beforeEmmaInventory(bad,validated,routes,read),assert.AssertionError);}
 const bad=JSON.parse(JSON.stringify(inventory));bad.canonical_pages=137;assert.throws(()=>helper.beforeEmmaInventory(bad,validated,routes,read),assert.AssertionError);
 const source=read(helper.landing),dom=new JSDOM(source);dom.window.document.querySelector('a[href="timelines/adams-1881-chart.html"]').classList.remove('fc-button--primary');assert.throws(()=>helper.validate(dom.window.document,helper.landing,selectors,source,read),assert.AssertionError);dom.window.close();
};
