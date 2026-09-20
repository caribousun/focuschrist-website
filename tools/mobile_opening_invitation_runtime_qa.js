// Fit decisions are tested independently of browser geometry measurements.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('site-common.js', 'utf8');
const fn = source.slice(source.indexOf('    function initOpeningInvitation('), source.indexOf('    function initMobileOpening('));
function run({mobile=true, cueTop=760, grow=false, move=false, moveCue=false, wide=false, overflow=false, path='/birth-of-christ.html'}={}) {
  let added, scheduled, observer;
  const listeners = {};
  const rect=(top,height,width=300)=>({top,bottom:top+height,height,width});
  const host={};
  const heading={getBoundingClientRect:()=>rect(360+(added && !added.hidden && move ? 8:0),30)};
  const cue={parentElement:host,before(p){added=p;},getBoundingClientRect:()=>rect(cueTop+(added && !added.hidden && moveCue ? 8:0),44)};
  const intro={querySelector:s=>s==='.fc-mobile-scroll-cue'?cue:added,
    querySelectorAll:()=>[heading],getBoundingClientRect:()=>rect(62,overflow?820:added && !added.hidden && grow?800:770)};
  const window={innerHeight:844, location:{pathname:path}, addEventListener:(n,f)=>listeners[n]=f,
    requestAnimationFrame:f=>{scheduled=f;return 1;},cancelAnimationFrame:()=>{},ResizeObserver:class{constructor(f){observer=f;}observe(){}}};
  const document={createElement:()=>({clientWidth:300,scrollWidth:wide?320:300,getBoundingClientRect:()=>rect(650,64)})};
  const media={matches:mobile,addEventListener:(n,f)=>listeners['media-'+n]=f};
  vm.runInNewContext(fn+'initOpeningInvitation(intro, mobile);',{window,document,intro,mobile:media});
  if(scheduled)scheduled();
  return {added,window,media,refresh(){observer();scheduled();}};
}
assert.equal(run().added.hidden,false,'Show an explanation when it fits');
assert.equal(run({cueTop:725}).added.hidden,true,'Retain at least 16px cue clearance');
assert.equal(run({grow:true}).added.hidden,true,'Never enlarge the opening');
assert.equal(run({move:true}).added.hidden,true,'Never move the existing heading');
assert.equal(run({moveCue:true}).added.hidden,true,'Never move Continue');
assert.equal(run({wide:true}).added.hidden,true,'Never allow horizontal text clipping');
assert.equal(run({overflow:true}).added.hidden,true,'Do not add copy to an already overflowing opening');
assert.equal(run({mobile:false}).added.hidden,true,'Desktop remains unchanged');
assert.equal(run({path:'/404.html'}).added,undefined,'No filler on error pages');
assert.equal(run({path:'/index.html'}).added,undefined,'Do not duplicate an already sufficient main-page introduction');
const changed=run();changed.window.innerHeight=640;changed.refresh();assert.equal(changed.added.hidden,true,'Reevaluate available room after resize');
assert.notEqual(run({path:'/answers/what-is-eternal-marriage.html'}).added.textContent,run().added.textContent,'Use topic-specific descriptions');
console.log('OPENING EXPLANATION QA PASS: clearance, locked geometry, headings, cue, overflow, desktop, resize and authored copy');
