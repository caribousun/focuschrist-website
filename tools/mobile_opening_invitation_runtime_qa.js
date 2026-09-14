const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('site-common.js', 'utf8');
const fn = source.slice(source.indexOf('    function initOpeningInvitation('), source.indexOf('    function initMobileOpening('));
function run({height=844, mobile=true, cueTop=760, grow=false, move=false, path='/index.html'}={}) {
  let added, scheduled, observer;
  const listeners = {};
  const host = {appendChild(p) {added=p;}};
  const heading = {getBoundingClientRect:()=>({top:added && !added.hidden && move ? 370:360})};
  const cue = {getBoundingClientRect:()=>({top:cueTop})};
  const intro = {
    querySelector(s) {
      if(s==='.fc-mobile-scroll-cue')return cue;
      if(s==='.fc-opening-invitation')return added;
      if(s==='h1')return heading;
      return host;
    },
    getBoundingClientRect:()=>({height:added && !added.hidden && grow ? 550:500})
  };
  const window={innerHeight:height, location:{pathname:path}, addEventListener:(n,f)=>listeners[n]=f,
    requestAnimationFrame:f=>{scheduled=f;return 1;},cancelAnimationFrame:()=>{}};
  const document={createElement:()=>({children:[],appendChild(n){this.children.push(n);},getBoundingClientRect:()=>({height:48,bottom:720})})};
  vm.runInNewContext(fn+'initOpeningInvitation(intro, mobile);', {window,document,intro,mobile:{matches:mobile}, ResizeObserver:class{constructor(f){observer=f;}observe(){}}});
  if(scheduled)scheduled();
  return {added,window,listeners,refresh(){observer();scheduled();}};
}
assert.equal(run().added.hidden,false,'Show a useful invitation when it fits');
assert.equal(run({cueTop:735}).added.hidden,true,'Retain at least24px cue clearance');
assert.equal(run({grow:true}).added.hidden,true,'Never enlarge the opening');
assert.equal(run({move:true}).added.hidden,true,'Never move the original heading');
assert.equal(run({height:640}).added.hidden,true,'Short phones keep original content only');
assert.equal(run({mobile:false}).added.hidden,true,'Desktop remains unchanged');
assert.equal(run({path:'/404.html'}).added,undefined,'No filler on error pages');
const changed=run();changed.window.innerHeight=640;changed.refresh();assert.equal(changed.added.hidden,true,'Reevaluate after resize');
assert.notEqual(run({path:'/ask.html'}).added.children[1].textContent,run().added.children[1].textContent,'Author page-specific questions');
console.log('OPENING INVITATION QA PASS: clearance, geometry, original heading, short screens, desktop, resize and authored copy');
