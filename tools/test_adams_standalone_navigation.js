'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM}=require('jsdom');
const {ADAMS_ROUTE,assertAdamsStandalone,withoutAdamsCanonical}=require('./adams_standalone_navigation');
function selfTest(routes,read){
  const html=read(ADAMS_ROUTE.slice(1)),helper=read('tools/adams_chart_browser_qa.js');
  const check=(mutate=()=>{},route=ADAMS_ROUTE,source=html,worker=helper)=>{
    const dom=new JSDOM(html,{url:'https://focuschrist.com'+ADAMS_ROUTE,runScripts:'outside-only'});
    try{mutate(dom.window.document);return assertAdamsStandalone(route,source,dom.window.document,worker);}finally{dom.window.close();}
  };
  assert.equal(check().sharedFooter,false);
  const before=JSON.stringify(routes),remaining=withoutAdamsCanonical(routes,read);
  assert.equal(remaining.length,137);assert.equal(JSON.stringify(routes),before);
  let negatives=0;const rejects=fn=>{assert.throws(fn,assert.AssertionError);negatives++;};
  rejects(()=>check(()=>{},'/timelines/unknown.html'));
  rejects(()=>check(()=>{},ADAMS_ROUTE,html+' '));
  rejects(()=>check(()=>{},ADAMS_ROUTE,html,helper+' '));
  for(const mutate of [
    d=>d.querySelector('h1').remove(),
    d=>{d.querySelector('h1').textContent='Changed title';},
    d=>{d.querySelector('h1').hidden=true;},
    d=>{d.querySelector('.fc-adams-strip').style.display='none';},
    d=>{d.querySelector('.fc-adams-home').href='../timeline.html#choose-timeline';},
    d=>{d.querySelector('.fc-adams-home').textContent='focusChrist Home';},
    d=>d.querySelector('.fc-adams-home').remove(),
    d=>d.querySelector('.fc-adams-home').after(d.querySelector('.fc-adams-home').cloneNode(true)),
    d=>{d.querySelector('.fc-adams-back').href='../timeline.html';},
    d=>{d.querySelector('.fc-adams-credit').textContent='Unreviewed credit';},
    d=>{d.querySelector('.fc-adams-note').textContent='Changed independence';},
    d=>{d.querySelector('.fc-adams-credit a').rel='';},
    d=>{d.querySelector('.fc-adams-credit a').removeAttribute('target');},
    d=>{d.querySelector('.fc-adams-credit a').rel='noopener';},
    d=>{const n=d.createElement('script');n.src='../site-common.js';d.head.append(n);},
    d=>d.body.append(d.createElement('iframe')),
    d=>d.body.append(d.createElement('footer')),
    d=>{d.querySelector('meta[name="viewport"]').content='width=device-width,user-scalable=no';}
  ])rejects(()=>check(mutate));
  rejects(()=>withoutAdamsCanonical(routes.filter(r=>r!==ADAMS_ROUTE),read));
  rejects(()=>withoutAdamsCanonical([...routes,ADAMS_ROUTE],read));
  rejects(()=>withoutAdamsCanonical(routes.map(r=>r===ADAMS_ROUTE?'/timelines/unknown.html':r),read));
  rejects(()=>withoutAdamsCanonical(routes,name=>read(name)+(name===ADAMS_ROUTE.slice(1)?' ':'')));
  assert.equal(negatives,25);
  return {positive:2,negative:negatives,scope:'Exact standalone DOM/source contract; no supplied script or rendered execution.'};
}
module.exports={selfTest};
if(require.main===module){const root=path.resolve(__dirname,'..'),read=name=>fs.readFileSync(path.join(root,name),'utf8'),routes=[...read('sitemap.xml').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname);console.log(JSON.stringify(selfTest(routes,read)));}
