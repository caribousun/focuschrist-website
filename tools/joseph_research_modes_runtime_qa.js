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
for(const invalid of ['not-json','[1,1]','[]']){
 const broken=setup('',false),bd=broken.window.document;
 bd.querySelector('.research-chapters > a').dataset.researchSections=invalid;
 broken.window.eval(script);
 assert([...bd.querySelectorAll('.research-part')].every(s=>!s.hidden),'Invalid chapter metadata must retain all content');
 assert(bd.querySelector('.research-mode-switch').hidden,'Invalid metadata must not expose nonfunctional controls');
 broken.window.close();
}
const dom=setup(),w=dom.window,d=w.document,r=d.getElementById('portrait-research');
assert.equal(r.dataset.readingMode,'chapters');
const chapterLinks=[...d.querySelectorAll('.research-chapters > a')];
assert.equal(chapterLinks.length,5);
const expectedGroups=[[1,2],[4,5],[6,7,8,9],[11,12],[3,10,13,14,15]];
assert.deepEqual(chapterLinks.map(a=>JSON.parse(a.dataset.researchSections)),expectedGroups,'Reviewed reader-journey chapter coverage');
assert.deepEqual([...d.querySelectorAll('.research-part')].map(s=>Number(s.id.replace('portrait-section-',''))),expectedGroups.flat(),'Reader order must follow the evidence before synthesis');
for(const [i,a] of chapterLinks.entries()){
 assert.equal(a.getAttribute('href'),'#portrait-section-'+expectedGroups[i][0]);
 assert(a.querySelector('strong').textContent.trim(),'Chapter label belongs to canonical card');
}

for(const a of chapterLinks){
 a.click();const section=d.querySelector(a.getAttribute('href'));
 assert(!section.hidden,'Selected chapter must be visible');
 assert.equal(a.getAttribute('aria-current'),'step');
 const group=expectedGroups[chapterLinks.indexOf(a)];
 assert.deepEqual([...d.querySelectorAll('.research-part')].filter(s=>!s.hidden).map(s=>Number(s.id.replace('portrait-section-',''))),group);
 assert(d.querySelector('.research-mode-status').textContent.endsWith(a.querySelector('strong').textContent.trim()+'.'),'Status label must follow manuscript card');
 assert.deepEqual(signature(d),baseline,'Chapter mode must preserve all text/images/source paths in one DOM');
}
for(const target of d.querySelectorAll('.research-part[id],.research-feature-study[id],.research-source[id]')){
 w.history.replaceState(null,'','#'+target.id);w.dispatchEvent(new w.HashChangeEvent('hashchange'));
 assert(!target.closest('.research-part').hidden,'Every feature/source/section deep link must reveal its actual group');
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
 win.TextEncoder=TextEncoder; let qaReturnTarget, qaScroll; const qaStyle=win.getComputedStyle.bind(win); win.getComputedStyle = el => el===qaReturnTarget ? {scrollMarginTop:'200px'} : qaStyle(el); Object.defineProperty(win.document.documentElement,'scrollHeight',{value:10000}); win.scrollTo = options => { qaScroll=options; }; const prepareReturn = target => { qaReturnTarget=target; qaScroll=null; target.getBoundingClientRect=()=>({top:2000}); }; const frames=new Map(); let frameId=0; win.requestAnimationFrame=fn=>{frames.set(++frameId,fn);return frameId;}; win.cancelAnimationFrame=id=>frames.delete(id); const tickFrames=()=>{const batch=[...frames.values()];frames.clear();batch.forEach(fn=>fn());};
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
  assert.equal(panel.querySelector('h2').textContent.trim(),trigger.closest('figure').querySelector('figcaption h3, figcaption h4').textContent.trim());
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
  prepareReturn(target); click(resume); tickFrames(); tickFrames();
  assert(!panel.open&&doc.activeElement===target&&qaScroll?.top===1800&&qaScroll.behavior==='instant');
  assert(!doc.body.classList.contains('fc-dialog-open'),'No leaked scroll lock');
  picturePaths++;
 }
 app.window.close();
}
console.log(`PASS ${picturePaths} actual research picture paths across both modes: titles, sources, full originals, nested close, focus and lesson return.`);

// Only the exact reviewed Hyrum biography belongs to this research route.
const biography='https://www.gutenberg.org/cache/epub/46602/pg46602-images.html';
const variants=[biography,biography.replace('https:','http:'),biography+'?other=1',biography+'#other',biography.replace('www.gutenberg.org','www.gutenberg.org.evil.example'),biography.replace('46602-images','46602'),biography.replace('46602','46734')];
for(const route of ['/joseph-smith-portrait-research.html','/joseph-smith-likeness.html','/answers/who-was-joseph-smith.html']){
 const fixture=new JSDOM('<main><figure><a href="assets/test.webp"><img src="assets/test.webp" alt="Test"></a><figcaption><h3>Source boundary</h3>'+variants.map(url=>'<a href="'+url+'">Biography</a>').join('')+'</figcaption></figure></main>',{url:'https://focuschrist.com'+route,runScripts:'outside-only'});
 const fw=fixture.window,fd=fw.document;
 fw.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','');};fw.HTMLElement.prototype.scrollIntoView=function(){};
 fw.eval(fs.readFileSync(path.join(root,'topic-artwork-details.js'),'utf8'));fd.dispatchEvent(new fw.Event('DOMContentLoaded'));
 fd.querySelector('figure>a').dispatchEvent(new fw.MouseEvent('click',{bubbles:true,cancelable:true,button:0}));
 assert.deepEqual([...fd.querySelectorAll('[data-topic-art-source]')].map(a=>a.href),route==='/joseph-smith-portrait-research.html'?[biography]:[],'Biography URL and owner route must both match exactly');
 fixture.window.close();
}
console.log('PASS exact Hyrum biography allowance with protocol, path, query, fragment, hostile-host and other-route negatives.');
