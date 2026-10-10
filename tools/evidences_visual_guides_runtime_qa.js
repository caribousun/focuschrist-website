const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM,VirtualConsole}=require('jsdom');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const entries=JSON.parse(read('docs/evidences-visual-guides-review-20260923.json')).records;
const dom=new JSDOM(read('book-of-mormon-evidences.html'),{url:'https://focuschrist.com/book-of-mormon-evidences.html',runScripts:'outside-only',virtualConsole:new VirtualConsole()});
const {window:w}=dom,d=w.document;
w.TextEncoder=TextEncoder; const frames=new Map(); let frameId=0; w.requestAnimationFrame=fn=>{frames.set(++frameId,fn);return frameId;}; w.cancelAnimationFrame=id=>frames.delete(id); const tickFrames=()=>{const batch=[...frames.values()];frames.clear();batch.forEach(fn=>fn());}; let qaReturnTarget,qaScroll;const qaStyle=w.getComputedStyle.bind(w);w.getComputedStyle=el=>el===qaReturnTarget?{scrollMarginTop:'200px'}:qaStyle(el);Object.defineProperty(d.documentElement,'scrollHeight',{value:10000});w.scrollTo=options=>{qaScroll=options;};
w.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','')};
w.HTMLDialogElement.prototype.close=function(){this.removeAttribute('open');this.dispatchEvent(new w.Event('close'))};
w.HTMLElement.prototype.scrollIntoView=function(){this.dataset.qaScrolled='true'};
for(const script of d.scripts){const src=script.src&&new URL(script.src).pathname.slice(1);if(['topic-artwork-details.js','full-image-viewer.js'].includes(src))w.eval(read(src));}
d.dispatchEvent(new w.Event('DOMContentLoaded'));
const click=n=>n.dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true,button:0}));
for(const e of entries){
 const fig=d.querySelector(`[data-bom-visual-guide="${e.key}"]`),trigger=fig.querySelector('a');
 assert.equal(fig.querySelector('source').getAttribute('srcset'),e.desktop_asset);
 assert.equal(fig.querySelector('source').media,'(min-width: 701px)');
 assert.equal(fig.querySelector('img').getAttribute('src'),e.asset);
 trigger.focus();click(trigger);
 const panel=d.getElementById('topicArtworkDetailDialog'),viewer=d.querySelector('.fc-full-image-viewer');
 assert(panel.open&&!viewer.open);assert.equal(panel.querySelector('img').src,trigger.href);
 const copy=panel.querySelector('.fc-artwork-detail-copy');
 for(const [,url] of e.sources)assert([...copy.querySelectorAll('a')].some(a=>a.href===url),e.key+' retains primary source in study copy');
 assert(copy.textContent.includes(e.caption),'Exact caption retained');
 const full=panel.querySelector('[data-full-image-viewer]');full.focus();click(full);
 assert(viewer.open&&panel.open);assert.equal(viewer.querySelector('img').src,trigger.href);
 click(viewer.querySelector('button'));assert(!viewer.open&&panel.open);assert.equal(d.activeElement,full);
 click(panel.querySelector('[data-topic-art-close]'));assert(!panel.open);assert.equal(d.activeElement,trigger);
 click(trigger);const resume=panel.querySelector('[data-topic-art-continue]');assert(resume);qaReturnTarget=d.getElementById(new URL(resume.href).hash.slice(1));qaScroll=null;qaReturnTarget.getBoundingClientRect=()=>({top:2000});click(resume);tickFrames();tickFrames();assert.equal(d.activeElement,qaReturnTarget);assert.equal(qaScroll?.top,1800);assert.equal(qaScroll.behavior,'instant');assert(!panel.open);assert(!d.body.classList.contains('fc-dialog-open'));
}
w.close();console.log('Evidences SVG runtime PASS: 12 responsive sources, caption source links, study/full-size nested dialogs, close focus and lesson return.');
