const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {JSDOM}=require('jsdom');
const script=fs.readFileSync(require('node:path').join(__dirname,'../header-scroll.js'),'utf8');
function setup({reduced=false,path='/study.html'}={}){
 const dom=new JSDOM('<html style="scroll-behavior:auto"><body><nav class="nav" data-focuschrist-header="standard"></nav><a id="go" href="#lesson">Go</a><section id="lesson"><h2>Lesson</h2></section></body></html>',{url:'https://focuschrist.com'+path,runScripts:'outside-only'});
 const w=dom.window, frames=[], calls=[];w.requestAnimationFrame=f=>frames.push(f);w.matchMedia=()=>({matches:reduced});
 w.HTMLElement.prototype.getBoundingClientRect=()=>({top:1500});w.HTMLElement.prototype.getClientRects=()=>[{width:300,height:200}];w.HTMLElement.prototype.animate=function(k,o){calls.push({node:this,k,o});return{cancel(){calls.push('cancel')}}};w.eval(script);
 const click=(opts={})=>{const e=new w.MouseEvent('click',{bubbles:true,cancelable:true,...opts});w.document.getElementById('go').dispatchEvent(e);return e};
 const flush=()=>{while(frames.length)frames.splice(0).forEach(f=>f())};
 return {w,calls,click,flush,link:w.document.getElementById('go'),style:w.document.documentElement.style};
}
test('native same-page jump is instant, history is not rewritten, destination fades, repeated hash works',()=>{
 const x=setup();let writes=0;x.w.history.pushState=()=>writes++;const e=x.click();assert.equal(e.defaultPrevented,false);assert.equal(x.style.getPropertyValue('scroll-behavior'),'auto');assert.equal(x.style.getPropertyPriority('scroll-behavior'),'');x.flush();assert.equal(x.style.scrollBehavior,'auto');assert.equal(writes,0);assert.equal(x.calls[0].node.id,'lesson');assert.equal(x.calls[0].o.duration,200);x.click();x.flush();assert.equal(x.calls.filter(v=>v!=='cancel').length,2);
});
test('reduced motion jumps instantly without animation',()=>{const x=setup({reduced:true});x.click();assert.equal(x.style.scrollBehavior,'auto');x.flush();assert.equal(x.calls.length,0)});
test('specialized canceled handler retains ownership and receives no fade',()=>{const x=setup();x.link.addEventListener('click',e=>{assert.equal(x.style.scrollBehavior,'auto');e.preventDefault()});assert.equal(x.click().defaultPrevented,true);x.flush();assert.equal(x.calls.length,0);assert.equal(x.style.scrollBehavior,'auto')});
for(const [name,href,options] of [['cross-page','other.html#lesson',{}],['external','https://example.com/#lesson',{}],['modified','#lesson',{ctrlKey:true}],['missing','#absent',{}],['query change','?mode=other#lesson',{}]])test(name+' untouched',()=>{const x=setup();x.link.href=href;x.click(options);assert.equal(x.style.scrollBehavior,'auto');x.flush();assert.equal(x.calls.length,0)});
test('Ask and dialog links untouched',()=>{for(const ask of [true,false]){const x=setup({path:ask?'/ask.html':'/study.html'});if(!ask){const d=x.w.document.createElement('dialog');x.link.replaceWith(d);d.append(x.link)}x.click();assert.equal(x.style.scrollBehavior,'auto');x.flush();assert.equal(x.calls.length,0)}});
test('rapid consecutive navigation keeps author style untouched and fades latest only',()=>{const x=setup();x.style.setProperty('scroll-behavior','auto','important');x.click();x.click();x.flush();assert.equal(x.style.scrollBehavior,'auto');assert.equal(x.style.getPropertyPriority('scroll-behavior'),'important');assert.equal(x.calls.length,1)});

test('short native movement has no added fade',()=>{const x=setup();x.w.document.getElementById('lesson').getBoundingClientRect=()=>({top:200});x.click();x.flush();assert.equal(x.calls.length,0)});
test('native scrolling and history default to instant in shared CSS',()=>{const css=fs.readFileSync(require.resolve('../site-system.css'),'utf8');assert.match(css,/html \{ scroll-behavior: auto; \}/);assert.doesNotMatch(css,/html \{ scroll-behavior: smooth; \}/)});
