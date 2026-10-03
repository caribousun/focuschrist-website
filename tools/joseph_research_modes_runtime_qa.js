/* Actual chapter/Read All behavior; rendered geometry remains a browser gate. */
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'joseph-smith-portrait-research.html'),'utf8');
const script=fs.readFileSync(path.join(root,'joseph-smith-research.js'),'utf8');
function setup(suffix='',run=true){
 const dom=new JSDOM(html,{url:'https://focuschrist.com/joseph-smith-portrait-research.html'+suffix,runScripts:'outside-only',pretendToBeVisual:true});
 dom.window.HTMLElement.prototype.scrollIntoView=function(){};
 dom.window.requestAnimationFrame=fn=>fn();
 if(run)dom.window.eval(script);
 return dom;
}
function signature(doc){return [...doc.querySelectorAll('.research-part')].map(s=>({id:s.id,text:s.textContent.replace(/\s+/g,' ').trim(),images:[...s.querySelectorAll('img')].map(x=>x.getAttribute('src')),links:[...s.querySelectorAll('a[href]')].map(x=>x.getAttribute('href'))}));}
const fallback=setup('',false),fd=fallback.window.document;
assert.equal(fd.querySelectorAll('.research-part').length,15);
assert([...fd.querySelectorAll('.research-part')].every(s=>!s.hidden),'No-JS must expose the complete study');
assert(fd.querySelector('.research-mode-switch').hidden,'Nonfunctional mode controls hidden without JS');
const baseline=signature(fd);
fallback.window.close();
const dom=setup(),w=dom.window,d=w.document,r=d.getElementById('portrait-research');
assert.equal(r.dataset.readingMode,'chapters');
const chapterLinks=[...d.querySelectorAll('.research-chapters > a')];
assert.equal(chapterLinks.length,5);
for(const a of chapterLinks){
 a.click();const section=d.querySelector(a.getAttribute('href'));
 assert(!section.hidden,'Selected chapter must be visible');
 assert.equal(a.getAttribute('aria-current'),'step');
 assert.deepEqual(signature(d),baseline,'Chapter mode must preserve all text/images/source paths in one DOM');
}
const source=d.querySelector('.research-source[id]');
assert(source,'Actual source deep-link target required');
w.history.pushState(null,'','#'+source.id);w.dispatchEvent(new w.PopStateEvent('popstate'));
assert(!source.closest('.research-part').hidden,'Back/forward source hash must reveal its chapter');
if(source.closest('details'))assert(source.closest('details').open,'Source disclosure must open for hash target');
const anchor=d.querySelector('[data-research-reading-block]');
assert(anchor && anchor.id,'Reading position needs a stable anchor');
w.history.replaceState(null,'','#'+anchor.id);w.dispatchEvent(new w.HashChangeEvent('hashchange'));
anchor.getClientRects=()=>[{top:120}];anchor.getBoundingClientRect=()=>({top:120});
d.querySelector('[data-research-mode="all"]').click();
assert.equal(r.dataset.readingMode,'all');
assert.equal(w.location.hash,'#'+anchor.id,'Mode switch should retain reading position');
assert([...d.querySelectorAll('.research-part')].every(s=>!s.hidden));
assert.equal(d.querySelector('[data-research-mode="all"]').getAttribute('aria-pressed'),'true');
assert.deepEqual(signature(d),baseline,'Read All must not omit/duplicate text, images or links');
d.querySelector('[data-research-mode="chapters"]').click();
assert.equal(r.dataset.readingMode,'chapters');assert(!anchor.closest('.research-part').hidden);
assert.equal(w.location.hash,'#'+anchor.id);
w.history.replaceState(null,'','?view=all#'+source.id);w.dispatchEvent(new w.PopStateEvent('popstate'));
assert.equal(r.dataset.readingMode,'all');assert([...d.querySelectorAll('.research-part')].every(s=>!s.hidden));
dom.window.close();
const reload=setup('?view=all#'+source.id);
assert.equal(reload.window.document.getElementById('portrait-research').dataset.readingMode,'all');
assert([...reload.window.document.querySelectorAll('.research-part')].every(s=>!s.hidden));
reload.window.close();
console.log('PASS actual chapter/Read All behavior, one-DOM content/image/link parity, source hashes, history events, position anchor and no-JS full study. Pixel geometry and complete artwork interactions remain separate browser gates.');

// Exercise every actual reference through the shared study and full-size panels.
// This is DOM interaction evidence only; real viewport/focus rendering is separate.
let picturePaths=0;
for(const mode of ['chapters','all']){
 const app=setup(mode==='all'?'?view=all':'');
 const win=app.window,doc=win.document;
 win.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','');};
 win.HTMLDialogElement.prototype.close=function(){this.removeAttribute('open');this.dispatchEvent(new win.Event('close'));};
 win.HTMLElement.prototype.scrollIntoView=function(){this.dataset.qaScrolled='true';};
 for(const asset of ['topic-artwork-details.js','full-image-viewer.js']){
  assert([...doc.scripts].some(s=>s.src&&new URL(s.src).pathname==='/'+asset),'Page must load actual shared panel scripts');
  win.eval(fs.readFileSync(path.join(root,asset),'utf8'));
 }
 doc.dispatchEvent(new win.Event('DOMContentLoaded'));
 const click=node=>node.dispatchEvent(new win.MouseEvent('click',{bubbles:true,cancelable:true,button:0}));
 const triggers=[...doc.querySelectorAll('#portrait-research figure > a[href]')].filter(a=>a.querySelector('img'));
 assert(triggers.length>0);
 for(const trigger of triggers){
  const section=trigger.closest('.research-part');
  win.history.replaceState(null,'',(mode==='all'?'?view=all':'')+'#'+section.id);
  win.dispatchEvent(new win.HashChangeEvent('hashchange'));
  assert(!section.hidden,'Picture belongs to reachable visible chapter');
  assert(trigger.hasAttribute('data-topic-artwork-detail'),'Every reference opens normal detail panel');
  trigger.focus();click(trigger);
  const panel=doc.getElementById('topicArtworkDetailDialog'),viewer=doc.querySelector('.fc-full-image-viewer');
  assert(panel.open&&!viewer.open,'Study first, then full size');
  assert.equal(panel.querySelector('h2').textContent.trim(),trigger.closest('figure').querySelector('h4').textContent.trim());
  assert.equal(panel.querySelector('img').src,trigger.href,'Detail window must reveal full unchanged source');
  const sourceLinks=[...panel.querySelectorAll('[data-topic-art-source]')];
  const expected=[...trigger.closest('figure').querySelectorAll('figcaption a[href]')].filter(a=>new URL(a.href).origin!==win.location.origin).map(a=>a.href);
  assert.deepEqual(sourceLinks.map(a=>a.href),[...new Set(expected)].slice(0,3),'Exact source destinations remain available');
  const full=panel.querySelector('[data-full-image-viewer]');
  assert.equal(full.href,trigger.href);full.focus();click(full);
  assert(panel.open&&viewer.open);assert.equal(viewer.querySelector('img').src,trigger.href);
  click(viewer.querySelector('button'));
  assert(!viewer.open&&panel.open&&doc.activeElement===full,'Nested close restores panel action focus');
  click(panel.querySelector('[data-topic-art-close]'));
  assert(!panel.open&&doc.activeElement===trigger,'Close restores invoking reference');
  click(trigger);
  const resume=panel.querySelector('[data-topic-art-continue]');
  const target=doc.getElementById(new URL(resume.href).hash.slice(1));
  assert(target&&!target.closest('figure'),'Continue goes to surrounding research');
  click(resume);
  assert(!panel.open&&doc.activeElement===target&&target.dataset.qaScrolled==='true');
  assert(!doc.body.classList.contains('fc-dialog-open'),'No leaked scroll lock');
  picturePaths++;
 }
 app.window.close();
}
console.log(`PASS ${picturePaths} actual research picture paths across both modes: titles, sources, full originals, nested close, focus and lesson return.`);
