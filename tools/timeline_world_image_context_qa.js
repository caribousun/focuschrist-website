/* Every pictured World event opens its own in-page context and entry.
 * This does not certify image historical identity, live layout or external sources. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {JSDOM,VirtualConsole}=require('jsdom');
const html=fs.readFileSync(path.join(__dirname,'../timelines/world-and-scripture-timeline.html'),'utf8');
const data=JSON.parse(html.match(/^const DATA = (.*);$/m)[1]);
const dom=new JSDOM(html,{url:'https://focuschrist.com/timelines/world-and-scripture-timeline.html#viewer',runScripts:'outside-only',virtualConsole:new VirtualConsole()});
const w=dom.window,d=w.document;
w.matchMedia=()=>({matches:true,addEventListener(){},removeEventListener(){}});
w.HTMLElement.prototype.scrollIntoView=function(){};w.requestAnimationFrame=()=>0;
w.HTMLDialogElement.prototype.showModal=function(){this.open=true};
w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'))};
const controller=[...d.scripts].find(s=>s.textContent.includes('const DATA = '));
const context=d.getElementById('timeline-image-context-controller');
w.eval(controller.textContent+'\n'+context.textContent);d.getElementById('modeCards').click();
let checked=0,undated=0;
for(const [i,e] of data.entries()){
 if(!e.img)continue;
 if(e.start===null){const q=d.getElementById('q');q.value=e.site;q.dispatchEvent(new w.Event('input'));undated++;}
 const trigger=d.querySelector('#cards [data-timeline-entry-index="'+i+'"]');assert(trigger,'Missing picture for entry '+i);
 assert.equal(new URL(trigger.href).pathname,e.img);trigger.click();
 const dialog=d.getElementById('timelineImageContext');assert(dialog.open);
 const name=e.site.replace(/\*\*\*/g,'');assert.equal(dialog.querySelector('h2').textContent,name);
 assert.equal(new URL(dialog.querySelector('img').src).pathname,e.img);
 const source=dialog.querySelector('[data-image-source]');assert.equal(source.href,e.imgpage,'Photo attribution remains separately linked');
 dialog.querySelector('[data-image-entry]').click();assert.equal(d.querySelector('#detail h2').textContent,name,'Explore returns to the same event');checked++;
}
assert.equal(checked,197);assert.equal(undated,1);dom.window.close();
console.log('PASS: all 197 pictured World events open their own in-page image context and matching entry, including one searched undated entry.');
