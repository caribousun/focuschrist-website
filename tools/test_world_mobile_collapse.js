/* DOM-level behavior only; browser rendering and keyboard defaults are separate. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM,VirtualConsole}=require('jsdom');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'timelines/world-and-scripture-timeline.html'),'utf8');
const script=fs.readFileSync(path.join(root,'timeline-mobile-collapse.js'),'utf8');
async function run(){
 const dom=new JSDOM(html,{url:'https://focuschrist.com/timelines/world-and-scripture-timeline.html#viewer',runScripts:'outside-only',virtualConsole:new VirtualConsole()});
 const w=dom.window,d=w.document;let listener;
 const media={matches:true,addEventListener(type,fn){assert.equal(type,'change');listener=fn;}};
 w.matchMedia=query=>{assert.equal(query,'(max-width:900px)');return media;};
 const $=s=>d.querySelector(s), flush=()=>new Promise(resolve=>w.queueMicrotask(resolve));
 $('#modeChart').classList.remove('on');$('#modeMap').classList.add('on');
 w.eval(script);
 const view=$('#mobileViewToggle'),play=$('#mobilePlaybackToggle'),viewPanel=$('#mobileViewControls'),playPanel=$('#mobilePlaybackControls');
 assert(viewPanel.hidden&&playPanel.hidden,'Both controls start compact on mobile');
 assert.equal(d.querySelectorAll('#mobileViewControls').length,1);assert.equal(d.querySelectorAll('#mobilePlaybackControls').length,1);
 assert.equal(view.getAttribute('aria-controls'),viewPanel.id);assert.equal(play.getAttribute('aria-controls'),playPanel.id);
 assert.equal(view.getAttribute('aria-expanded'),'false');assert.equal(play.getAttribute('aria-expanded'),'false');
 assert.match(view.textContent,/Moment & Map/);assert.match(play.textContent,/600 BC/);
 assert(!playPanel.contains($('.map-options-row')),'Geography and map settings remain outside playback');
 view.click();play.click();assert(!viewPanel.hidden&&!playPanel.hidden);assert.equal(view.getAttribute('aria-expanded'),'true');assert.equal(play.getAttribute('aria-expanded'),'true');
 $('#q').value='Egypt';$('#catChips [data-cat="bible"]').setAttribute('aria-pressed','false');$('#yearInput').value='-500';$('#yearLabel').textContent='500 BC';await flush();assert.match(play.textContent,/500 BC/);
 $('#modeMap').classList.remove('on');$('#modeChart').classList.add('on');await flush();assert.match(view.textContent,/Timeline/);
 view.click();assert(viewPanel.hidden&&!playPanel.hidden,'Closing one panel leaves the other open');play.click();assert(viewPanel.hidden&&playPanel.hidden);view.click();play.click();
 assert.equal($('#q').value,'Egypt');assert.equal($('#yearInput').value,'-500');assert.equal($('#catChips [data-cat="bible"]').getAttribute('aria-pressed'),'false');assert($('#modeChart').classList.contains('on'));
 // Closing a focused panel through a resize returns focus to its visible toggle.
 view.click();media.matches=false;listener();assert(!viewPanel.hidden&&!playPanel.hidden&&view.hidden&&play.hidden,'Desktop exposes both controls and hides toggles');
 $('#q').focus();media.matches=true;listener();assert(viewPanel.hidden&&!view.hidden);assert.equal(d.activeElement,view,'Focus returns when a resize collapses its panel');
 view.focus();media.matches=false;listener();assert(view.hidden&&!viewPanel.hidden);assert.equal(d.activeElement,$('#modeChart'),'Focus moves to the selected view on desktop');
 assert.equal($('#q').value,'Egypt');assert.equal($('#yearInput').value,'-500');
 dom.window.close();
 const desktop=new JSDOM(html,{runScripts:'outside-only',virtualConsole:new VirtualConsole()}),dw=desktop.window,dd=dw.document;
 assert(dd.getElementById('mobileViewToggle').hidden&&dd.getElementById('mobilePlaybackToggle').hidden,'Controls stay available if JavaScript does not run');
 assert(!dd.getElementById('mobileViewControls').hidden&&!dd.getElementById('mobilePlaybackControls').hidden);
 dw.matchMedia=()=>({matches:false,addEventListener(){}});dw.eval(script);
 assert(dd.getElementById('mobileViewToggle').hidden&&dd.getElementById('mobilePlaybackToggle').hidden,'Desktop starts without mobile toggles');
 assert(!dd.getElementById('mobileViewControls').hidden&&!dd.getElementById('mobilePlaybackControls').hidden,'Desktop starts with controls visible');desktop.window.close();
 console.log('PASS: independent mobile disclosures, labels, values, focus and desktop resize (DOM-level; browser presentation separate).');
}
run().catch(e=>{console.error(e);process.exitCode=1;});
