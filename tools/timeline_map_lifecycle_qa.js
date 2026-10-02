/* Renderer ownership regression: fallback and filter changes must not remove library-owned children. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{JSDOM}=require('jsdom');
const html=fs.readFileSync(path.join(__dirname,'../timelines/willie-and-martin-handcart-map.html'),'utf8');
const dom=new JSDOM(html,{url:'https://focuschrist.com/timelines/willie-and-martin-handcart-map.html',runScripts:'outside-only'}),w=dom.window,d=w.document;
w.HTMLElement.prototype.scrollIntoView=function(){};
const instances=[];let destroyed=0;const violations=[];
w.MapHelpers={mountMap(renderer,options,unavailable){const child=d.createElement('div');child.textContent='Library-owned map';renderer.appendChild(child);const record={renderer,child,unavailable,options,count:options.places.length};instances.push(record);return {destroy(){if(child.parentNode!==renderer)violations.push('Owned child removed before library disposal');else renderer.removeChild(child);destroyed++;}};}};
const script=[...d.scripts].find(s=>s.textContent.includes('var STOPS ='));assert(script);w.eval(script.textContent);
assert.equal(instances.length,1);assert.equal(instances[0].count,33);instances[0].unavailable();instances[0].unavailable();assert.equal(d.querySelectorAll('.map-fallback').length,1);assert.equal(instances[0].child.parentNode,instances[0].renderer);
d.querySelector('[data-filter="willie"]').click();assert.equal(destroyed,1);assert.equal(instances.length,2);assert(instances[1].count>0&&instances[1].count<33);assert.equal(d.querySelectorAll('.map-fallback').length,0);
instances[0].unavailable();assert.equal(d.querySelectorAll('.map-fallback').length,0,'Stale unavailable callback must not alter active map');assert(!instances[1].renderer.hidden);
instances[1].unavailable();assert.equal(d.querySelectorAll('.map-fallback').length,1);d.querySelector('[data-filter="all"]').click();assert.equal(destroyed,2);assert.equal(instances[2].count,33);assert.deepEqual(violations,[]);
for(const filter of ['all','willie','martin','shared','sea']){
 const old=instances.at(-1);d.querySelector('[data-filter="'+filter+'"]').click();
 const live=instances.at(-1);const cards=[...d.querySelectorAll('.stop-card')];
 const before=d.querySelector('#detail-title').textContent;
 old.options.onSelectPlace(0);
 assert.equal(d.querySelector('#detail-title').textContent,before,'Stale pin callback ignored');
 for(let i=0;i<cards.length;i++)for(const selected of [false,true]){
   const holder=d.createElement('div');
   holder.innerHTML=live.options.marker(live.options.places[i],i,selected);
   const pin=holder.firstElementChild;
   const expected=Number(cards[i].querySelector('.stop-num').textContent);
   assert.equal(Number(pin.dataset.stopNumber),expected,'Filtered pin keeps original journey number');
   assert.equal(pin.textContent.trim(),String(expected),'Number remains exact after marker repaint/zoom');
   live.options.onSelectPlace(i);
   assert.equal(d.querySelector('#detail-title').textContent,cards[i].querySelector('h3').textContent,'Selected pin matches exact right-panel story');
   assert(d.querySelector('#detail-kicker').textContent.startsWith('Stop '+expected+' of 33'));
 }
}
assert.deepEqual(violations,[]);
d.querySelector('.stop-card').click();assert(d.querySelector('#detail-panel.is-open'));assert(d.querySelector('#detail-body').textContent.length>100);dom.window.close();console.log('PASS: provider fallback preserves renderer ownership, remount disposes safely, stale callbacks ignored, full story remains usable.');
