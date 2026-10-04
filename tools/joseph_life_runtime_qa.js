const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..');
const dom=new JSDOM(fs.readFileSync(path.join(root,'joseph-smith-likeness.html'),'utf8'),{url:'https://focuschrist.com/joseph-smith-likeness.html',runScripts:'outside-only',pretendToBeVisual:true});
const w=dom.window,d=w.document;w.HTMLElement.prototype.scrollIntoView=function(){this.dataset.qaScrolled='true';};
w.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','');};w.HTMLDialogElement.prototype.close=function(){this.removeAttribute('open');this.dispatchEvent(new w.Event('close'));};
for(const file of ['topic-artwork-details.js','full-image-viewer.js'])w.eval(fs.readFileSync(path.join(root,file),'utf8'));
d.dispatchEvent(new w.Event('DOMContentLoaded'));const click=n=>n.dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true,button:0}));
const triggers=[...d.querySelectorAll('.joseph-life-scene figure > a')];assert.equal(triggers.length,10);
for(const t of triggers){
 const owner=t.closest('article.joseph-life-scene');t.focus();click(t);const panel=d.getElementById('topicArtworkDetailDialog');assert(panel.open);assert.equal(panel.querySelector('img').src,t.href);
 const expected=[...t.closest('figure').querySelectorAll('figcaption a[href]')].map(a=>a.href);
 assert.deepEqual([...panel.querySelectorAll('[data-topic-art-source]')].map(a=>a.href),expected.slice(0,3),'All actual scene source actions retained');
 const full=panel.querySelector('[data-full-image-viewer]');full.focus();click(full);const viewer=d.querySelector('.fc-full-image-viewer');assert(viewer.open);click(viewer.querySelector('button'));assert(panel.open&&!viewer.open&&d.activeElement===full);
 click(panel.querySelector('[data-topic-art-close]'));assert(d.activeElement===t);click(t);const resume=panel.querySelector('[data-topic-art-continue]');assert.equal(new URL(resume.href).hash,'#'+owner.id);click(resume);assert(!panel.open&&d.activeElement===owner&&owner.dataset.qaScrolled==='true','Continue returns to exact individual scene');
}
w.close();console.log('PASS ten family detail/fullsize/source/close paths and exact individual-scene Continue focus; rendered geometry remains separate.');
