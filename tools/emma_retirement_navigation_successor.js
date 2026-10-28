'use strict';
// DRAFT: current-source-first adapter to the *historical* navigation inventory.
// It never claims the restored predecessor represents current UI. Requires an
// independently reviewed owner/asset gate and full checkout before integration.
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex'),bare=p=>p==='/'?'index.html':p.replace(/^\//,'');
const hub='history/emma-hale-smith.html',retired='history/emma-elect-lady.html',hymn='history/emma-hymns.html';
const CURRENT=Object.freeze({[hub]:'7511f2d034d6117cb9e4d0da896c3ff778c1f0a2165c0425361b47c1d6fb3573',[retired]:'6de7bd0b21f0561913ba251163e552588a3fe065df83fd6cd1ccb9b6365ccbba',[hymn]:'55ee8b1a9b57154ca074282f2b6f44c19d77d15a63abd5adcde3286174625087'});
const PRIOR=Object.freeze({[hub]:'50c334379066722ef6e80e97d70f0f2ca431777b5857eb15b998da65cc1783cf',[retired]:'f32c79609f15d51e9c85b2f4bc941de38d2626c944e33f1876fc574f46f7986c',[hymn]:'719bc7f899ebc188f33322c4c7c6bea9e326b209e28e2d49855543185e12aedb'});
const PRIOR_ROUTES_SHA='ba19da4af6ba32219ff9555ecf5ddd466077acd9a6ee09a7d49f29c07d1f4284';
const KEYS=['emma-story1-ride','emma-story2-hymnal','emma-story3-quincy','emma-story4-hospitality','emma-story5-testimony','emma-h1','emma-h3','emma-h4','emma-h5','emma-journey-origin',...Array.from({length:10},(_,i)=>'emma-journey-'+String(i+3).padStart(2,'0'))];
function assertCurrent(routes,read,JSDOM){
 const normalized=routes.map(bare);assert.equal(normalized.length,138);assert.equal(new Set(normalized).size,138);assert(!normalized.includes(retired));
 assert.equal(sha([...normalized,retired].sort().join('\n')),PRIOR_ROUTES_SHA,'unknown/omitted current canonical route');
 for(const [route,digest] of Object.entries(CURRENT))assert.equal(sha(read(route)),digest,'exact current source '+route);
 const page=new JSDOM(read(hub)),redirect=new JSDOM(read(retired));
 try{
  const doc=page.window.document,figures=[...doc.querySelectorAll('figure[data-exclusive-artwork]')];assert.equal(figures.length,20);assert.deepEqual(figures.map(n=>n.getAttribute('data-exclusive-artwork')).sort(),[...KEYS].sort());
  const ids=[...doc.querySelectorAll('[id]')].map(n=>n.id);assert.equal(ids.length,new Set(ids).size);assert.equal(doc.querySelectorAll('figure.fc-life-hero').length,1);
  for(const key of KEYS){const a=doc.querySelectorAll(`figure#picture-${key}[data-exclusive-artwork="${key}"][data-topic-art="${key}"]`);assert.equal(a.length,1,key);assert.equal(a[0].querySelectorAll(':scope > a[aria-haspopup="dialog"]').length,1,key+' trigger');assert.equal(a[0].querySelectorAll(':scope > figcaption[data-picture-panel-copy][hidden]').length,1,key+' detail copy');}
  for(const id of ['emma-beginnings','emma-pen-family','emma-songs-separation','emma-relief-questions','emma-household','emma-remaining-years','print-emma'])assert.equal(doc.querySelectorAll('#'+id).length,1,id);
  const r=redirect.window.document;assert.equal(r.querySelector('meta[name="robots"]')?.getAttribute('content'),'noindex, follow');assert.equal(r.querySelector('link[rel="canonical"]')?.getAttribute('href'),'https://focuschrist.com/history/emma-hale-smith.html');assert.equal(r.querySelectorAll('a[href="emma-hale-smith.html"]').length,1);
 }finally{page.window.close();redirect.window.close()}
}
function priorReader(read){
 const fixtures={[hub]:'docs/emma-journey-retirement-predecessors/emma-hale-smith.html.source',[retired]:'docs/emma-journey-retirement-predecessors/emma-elect-lady.html.source',[hymn]:'docs/emma-journey-retirement-predecessors/emma-hymns.html.source'};
 return route=>Object.hasOwn(fixtures,route)?read(fixtures[route]):read(route);
}
function historicProjection(inventory,routes,selectors,numbered,read,readPrior,JSDOM,priorIntegration){
 assertCurrent(routes,read,JSDOM);assert.equal(inventory.canonical_pages,138,'actual current canonical inventory');
 for(const [route,digest] of Object.entries(PRIOR))assert.equal(sha(readPrior(route)),digest,'unchanged historical fixture '+route);
 assert(priorIntegration&&typeof priorIntegration.historicalControlInventory==='function','previous exact validator required');
 const projected=JSON.parse(JSON.stringify(inventory));
 // Project only the three exact changed pages from actual current DOM to
 // verified prior DOM. Unrelated inventory remains untouched for old checks.
 for(const route of [hub,hymn,retired]){
  const current=route===retired?null:new JSDOM(read(route));const prior=new JSDOM(readPrior(route));
  try{
   for(const selector of selectors){
    const item=projected.selectors[selector];assert(item,'selector absent');
    const now=current?current.window.document.querySelectorAll(selector).length:0,old=prior.window.document.querySelectorAll(selector).length;
    assert.equal(item.pages.includes(route),now>0,'actual current membership '+route+' '+selector);item.count+=old-now;assert(item.count>=0);item.pages=item.pages.filter(p=>p!==route);if(old)item.pages.push(route);item.pages.sort();
   }
   for(const selector of numbered){const key=route+' '+selector,rows=d=>[...d.querySelectorAll(selector)].map(n=>({href:n.getAttribute('href'),label:n.textContent.replace(/\s+/g,' ').trim()}));const now=current?rows(current.window.document):[],old=rows(prior.window.document);assert.deepEqual(projected.numbered_navigation[key]||[],now,'actual current numbered controls '+key);delete projected.numbered_navigation[key];if(old.length)projected.numbered_navigation[key]=old;}
  }finally{if(current)current.window.close();prior.window.close()}
 }
 projected.canonical_pages=139;
 const historicalRead=route=>Object.hasOwn(PRIOR,route)?readPrior(route):read(route);
 return priorIntegration.historicalControlInventory(projected,selectors,numbered,historicalRead,JSDOM);
}
module.exports={CURRENT,PRIOR,KEYS,assertCurrent,priorReader,historicProjection};
