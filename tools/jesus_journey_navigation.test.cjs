const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM}=require('jsdom');
const repo=path.resolve(__dirname,'..');
const code=fs.readFileSync(path.join(repo,'jesus-journey.js'),'utf8');
const file='jesus-christ/mortal-ministry.html';
function setup(hash='',evaluate=true,route=file){
 const dom=new JSDOM(fs.readFileSync(path.join(repo,route),'utf8'),{url:'https://focuschrist.com/'+route+hash,runScripts:'outside-only',pretendToBeVisual:true});
 const w=dom.window,errors=[],scrolls=[];
 w.HTMLElement.prototype.scrollIntoView=function(){scrolls.push(this.id||this.className)};
 w.addEventListener('error',e=>errors.push(e.message));
 if(evaluate)w.eval(code);
 return {dom,w,d:w.document,errors,scrolls,close:()=>w.close()};
}
function chapters(s){return [...s.d.querySelectorAll('.jj-local-nav a[href^="#"]')].map(x=>s.d.getElementById(x.hash.slice(1)))}
function shown(s){return chapters(s).filter(x=>!x.hidden).map(x=>x.id)}
const tick=()=>new Promise(r=>setTimeout(r,40));
test('initial chapter, controls, aria-current and next/previous focus',()=>{
 const s=setup();try{
 assert.deepEqual(shown(s),['baptism']);
 const [prev,next]=s.d.querySelectorAll('.jj-chapter-steps button');
 assert.equal(prev.disabled,true);assert.equal(next.disabled,false);
 next.click();assert.deepEqual(shown(s),['come-and-see']);assert.equal(s.w.location.hash,'#come-and-see');
 assert.equal(s.d.activeElement,chapters(s)[1].querySelector('h2'));
 assert.equal(s.d.querySelector('[aria-current="step"]').hash,'#come-and-see');
 prev.click();assert.deepEqual(shown(s),['baptism']);assert.equal(prev.disabled,true);
 assert.equal(s.errors.length,0);
 }finally{s.close()}
});
test('every real journey page retains all chapters without JS and selects one with JS',()=>{
 const routes=['answers/jesus-christ-latter-day-saint-beliefs.html'];
 function walk(dir){for(const e of fs.readdirSync(path.join(repo,dir),{withFileTypes:true})){const r=dir+'/'+e.name;if(e.isDirectory())walk(r);else if(r.endsWith('.html'))routes.push(r)}}walk('jesus-christ');
 let count=0;for(const route of routes){const s=setup('',false,route);try{const cs=chapters(s);if(!cs.length)continue;count++;assert(cs.every(x=>x&&!x.hidden),route+' fallback');assert.equal(s.d.querySelector('.jj-chapter-controls'),null);s.w.eval(code);assert.equal(shown(s).length,1,route);assert.equal(s.errors.length,0,route)}finally{s.close()}}
 assert(count>=77);
});
test('initial chapter and nested picture hashes reveal the containing chapter',async()=>{
 for(const hash of ['#transfiguration','#picture-mm-transfiguration']){const s=setup(hash);try{await tick();assert.deepEqual(shown(s),['transfiguration']);assert(s.scrolls.includes(hash.slice(1)));assert.equal(s.errors.length,0)}finally{s.close()}}
});
test('chapter picker closes and focus moves to selected heading; last next is disabled',()=>{
 const s=setup();try{const picker=s.d.querySelector('.jj-chapter-picker');picker.open=true;const links=s.d.querySelectorAll('.jj-local-nav a');links[links.length-1].click();assert.equal(picker.open,false);assert.deepEqual(shown(s),['jerusalem']);assert.equal(s.d.activeElement,s.d.querySelector('#jerusalem h2'));assert.equal(s.d.querySelectorAll('.jj-chapter-steps button')[1].disabled,true)}finally{s.close()}
});
test('whole-study toggle and focus recovery never strand focus in a hidden chapter',()=>{
 const s=setup();try{const mode=s.d.querySelector('.jj-mode');mode.click();assert.equal(shown(s).length,chapters(s).length);assert.equal(mode.getAttribute('aria-pressed'),'true');assert.equal(s.d.querySelector('.jj-chapter-steps').hidden,true);s.d.querySelector('#transfiguration a').focus();mode.click();assert.deepEqual(shown(s),['baptism']);assert.equal(s.d.activeElement,s.d.querySelector('#baptism h2'));assert.equal(mode.getAttribute('aria-pressed'),'false')}finally{s.close()}
});
test('Back and Forward restore chapters and nested picture bookmarks',async()=>{
 const s=setup();try{const next=s.d.querySelectorAll('.jj-chapter-steps button')[1];next.click();next.click();assert.deepEqual(shown(s),['nathanael']);s.w.history.back();await tick();assert.deepEqual(shown(s),['come-and-see']);s.w.history.forward();await tick();assert.deepEqual(shown(s),['nathanael']);s.w.location.hash='#picture-mm-transfiguration';await tick();assert.deepEqual(shown(s),['transfiguration']);s.w.history.back();await tick();assert.deepEqual(shown(s),['nathanael']);assert.equal(s.errors.length,0)}finally{s.close()}
});
test('invalid and malformed hashes are safe; empty hash restores first chapter',async()=>{
 const s=setup('#missing');try{assert.deepEqual(shown(s),['baptism']);s.w.location.hash='#%E0%A4%A';await tick();assert.equal(s.errors.length,0);s.d.querySelectorAll('.jj-chapter-steps button')[1].click();s.w.location.hash='';await tick();assert.deepEqual(shown(s),['baptism'])}finally{s.close()}
});
test('same-page picture link reveals target before downstream click listeners',()=>{
 const s=setup();try{const a=s.d.createElement('a');a.href='#picture-mm-transfiguration';s.d.body.append(a);let revealed=false;a.addEventListener('click',e=>{e.preventDefault();revealed=!s.d.querySelector('#transfiguration').hidden});a.click();assert(revealed);assert.deepEqual(shown(s),['transfiguration'])}finally{s.close()}
});
test('print reveals all chapters and restores reading mode',()=>{
 const s=setup('#transfiguration');try{s.w.dispatchEvent(new s.w.Event('beforeprint'));assert.equal(shown(s).length,chapters(s).length);s.w.dispatchEvent(new s.w.Event('afterprint'));assert.deepEqual(shown(s),['transfiguration'])}finally{s.close()}
});
test('modified chapter-picker click does not navigate current document',()=>{
 const s=setup();try{const a=s.d.querySelectorAll('.jj-local-nav a')[3];a.addEventListener('click',e=>e.preventDefault());a.dispatchEvent(new s.w.MouseEvent('click',{bubbles:true,ctrlKey:true}));assert.deepEqual(shown(s),['baptism'])}finally{s.close()}
});
test('modified same-page picture link must not change current chapter',()=>{
 const s=setup();try{const a=s.d.createElement('a');a.href='#picture-mm-transfiguration';s.d.body.append(a);a.addEventListener('click',e=>e.preventDefault());a.dispatchEvent(new s.w.MouseEvent('click',{bubbles:true,ctrlKey:true}));assert.deepEqual(shown(s),['baptism'])}finally{s.close()}
});
test('rapid valid-to-malformed bookmark change remains safe before animation frame',async()=>{
 const s=setup('#transfiguration');try{s.w.history.replaceState(null,'','#%E0%A4%A');await tick();assert.deepEqual(s.errors,[])}finally{s.close()}
});
test('Back closes nested owned dialogs and restores focus after shared close cleanup',async()=>{
 const s=setup();try{
 s.d.querySelectorAll('.jj-chapter-steps button')[1].click();
 const trigger=s.d.querySelector('#come-and-see a');
 const dialogs=[['topicArtworkDetailDialog',''],['fc-scripture-reader',''],['','fc-full-image-viewer']].map(([id,cls])=>{
  const dialog=s.d.createElement('dialog');dialog.id=id;dialog.className=cls;dialog.setAttribute('open','');s.d.body.append(dialog);
  dialog.addEventListener('close',()=>trigger.focus());
  // HTML dialog close events are queued; jsdom has no native dialog.close implementation.
  dialog.close=function(){this.removeAttribute('open');s.w.setTimeout(()=>this.dispatchEvent(new s.w.Event('close')),0)};
  return dialog;
 });
 s.w.history.back();await tick();
 assert(dialogs.every(d=>!d.hasAttribute('open')));assert.deepEqual(shown(s),['baptism']);
 assert.equal(s.d.activeElement,s.d.querySelector('#baptism h2'));assert.deepEqual(s.errors,[]);
 }finally{s.close()}
});

