/* DOM/target regressions only; actual geometry is tested separately. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..'),source=fs.readFileSync(path.join(root,'unified-opening.js'),'utf8');
const inventory=JSON.parse(fs.readFileSync(path.join(root,'docs/unified-opening-inventory.json')));
assert.equal(inventory.pages.length,129);assert.equal(inventory.pages.filter(x=>x.hero).length,47);
let checks=0;
for(const file of ['answers/abrahamic-covenant.html','answers/prayer-and-personal-revelation.html','art.html','come-follow-me.html','general-conference.html','history/john-tanner.html','jesus-christ/parables/barren-fig.html']){
 const dom=new JSDOM(fs.readFileSync(path.join(root,file),'utf8'),{url:'https://focuschrist.com/'+file,runScripts:'outside-only',pretendToBeVisual:true});
 const w=dom.window,d=w.document,media={matches:false,addEventListener(){}};
 w.matchMedia=()=>media;w.ResizeObserver=class{observe(){}};w.requestAnimationFrame=fn=>{fn();return 1;};
 const images=[...d.images].map(x=>x.outerHTML),text=d.body.textContent;
 w.eval(source);d.dispatchEvent(new w.Event('DOMContentLoaded'));
 const cue=d.querySelector('.fc-unified-continue');
 if(file.includes('/parables/')){assert.equal(cue,null);dom.window.close();continue;}
 assert(cue&&cue.getAttribute('href'),file+': working invitation target');
 assert.equal(d.querySelectorAll('.fc-unified-continue').length,1);
 assert.deepEqual([...d.images].map(x=>x.outerHTML),images,file+': image markup retained');
 const opening=d.querySelector('[data-unified-opening]');
 opening.getBoundingClientRect=()=>({top:500-w.scrollY,bottom:700-w.scrollY});
 Object.defineProperty(w,'scrollY',{value:200,writable:true});w.dispatchEvent(new w.Event('resize'));
 assert.equal(opening.style.getPropertyValue('--unified-opening-top'),'500px');
 w.scrollY=400;w.dispatchEvent(new w.Event('resize'));
 assert.equal(opening.style.getPropertyValue('--unified-opening-top'),'500px',file+': scrolling cannot change document top');
 assert.equal(w.scrollY,400,file+': measurement never scrolls');
 if(file.includes('covenant'))assert(opening.querySelector('.lede').textContent.includes('God’s promise to Abraham'));
 if(file==='art.html')assert.equal(cue.getAttribute('href'),'#art-gallery');
 assert(d.body.textContent.length>=text.length,file+': retained copy is not deleted');
 checks++;dom.window.close();
}
{
 const dom=new JSDOM('<body class="fc-site"><a class="fc-visual-hero"></a><section class="fc-page-intro"><div class="fc-container--standard"><h1>Study</h1><p class="fc-page-intro-copy">Retained explanation</p><a class="fc-scroll-cue" href="#study">Continue</a></div></section><main id="study">Study body</main></body>',{url:'https://focuschrist.com/test.html',runScripts:'outside-only'});
 const w=dom.window,d=w.document;w.matchMedia=()=>({matches:false,addEventListener(){}});w.ResizeObserver=class{observe(){}};w.requestAnimationFrame=fn=>{fn();return 1;};
 w.eval(source);d.dispatchEvent(new w.Event('DOMContentLoaded'));
 const cue=d.querySelector('.fc-unified-continue'),copy=d.querySelector('.fc-page-intro-copy');
 assert.equal(cue.textContent,'Continue \u2193','Arrow is a real Unicode down arrow');
 Object.defineProperty(w,'innerHeight',{value:844,writable:true});Object.defineProperty(w,'scrollY',{value:400,writable:true});
 cue.getBoundingClientRect=()=>({bottom:900-w.scrollY});
 w.dispatchEvent(new w.Event('resize'));
 assert(copy.closest('.fc-unified-opening-continuation'),'Scrolled measurement retains overflowing copy below opening');
 assert.equal(cue.getAttribute('href'),'#fc-opening-retained','Continue enters retained copy before original study target');
 w.dispatchEvent(new w.Event('resize'));
 assert(copy.closest('.fc-unified-opening-continuation'),'Repeated scrolled resize cannot restore copy that does not fit');
 assert.equal(w.scrollY,400);
 w.innerHeight=1200;w.dispatchEvent(new w.Event('resize'));
 assert(copy.closest('[data-unified-opening]'),'Copy returns when space is available');
 assert(d.querySelector('.fc-unified-opening-continuation').hidden,'Empty continuation has no spacing');
 assert.equal(cue.getAttribute('href'),'#study');
 dom.window.close();
}
{
 const common=fs.readFileSync(path.join(root,'site-common.js'),'utf8');
 const start=common.indexOf("        const openingStyle = document.createElement('link');");
 const end=common.indexOf("        if (/[?&]gallery-",start);
 assert(start>=0&&end>start,'Production stylesheet loader located');
 for(const outcome of ['load','error']){
  const dom=new JSDOM('<head></head><body></body>',{runScripts:'outside-only'});
  const w=dom.window,calls=[];
  w.relativeAssetHref=x=>x;w.appendScript=(...args)=>calls.push(args);
  w.eval(common.slice(start,end));
  assert.equal(calls.length,0,'Delayed CSS must not start opening measurements');
  const style=w.document.querySelector('link');
  style.dispatchEvent(new w.Event(outcome));
  assert.equal(calls.length,outcome==='load'?1:0,'Only successful CSS readiness enables adapter');
  if(outcome==='load'){style.dispatchEvent(new w.Event('load'));assert.equal(calls.length,1,'Adapter loads once');}
  dom.window.close();
 }
}
console.log(`UNIFIED OPENING DOM PASS: ${checks} template families; delayed stylesheet readiness, failure fallback, targets, retained-copy destination, scrolled resize, empty continuation, valid arrow, image retention and nonhero exclusion`);
