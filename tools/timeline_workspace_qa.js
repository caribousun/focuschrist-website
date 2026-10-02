/* Production shared controller in JSDOM: DOM/state ownership only, rendered scrolling is hosted QA. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{JSDOM}=require('jsdom');
const source=fs.readFileSync(path.join(__dirname,'../timeline-workspace.js'),'utf8');
for(const desktop of [false,true]){
 const dom=new JSDOM('<nav data-focuschrist-header="standard"></nav><section id="journeyWorkspace" data-timeline-workspace><div data-timeline-pane="events" style="overflow:auto"><button id="original">Original event</button></div><div data-timeline-pane="map"><div id="map"></div></div><div data-timeline-pane="detail">Story</div></section>',{url:'https://focuschrist.com/timelines/test.html',runScripts:'outside-only'}),w=dom.window,d=w.document;
 const media={matches:desktop,addEventListener(name,fn){this.change=fn;}};w.matchMedia=()=>media;w.requestAnimationFrame=()=>1;w.scrollTo=()=>{throw new Error('Choice interactions must not scroll the document');};
 w.eval(source);const api=w.TimelineWorkspace,events=d.querySelector('[data-timeline-pane="events"]'),workspace=d.querySelector('[data-timeline-workspace]'),original=d.getElementById('original');const choices=[{index:3,label:'4. Exact fourth event'},{index:19,label:'20. Exact twentieth event'}];let selected=null;
 const open=()=>api.showChoices('Nearby events',choices,index=>{selected=index;w.dispatchEvent(new w.CustomEvent('timeline:select',{detail:{index}}));});
 events.scrollTop=137;assert.equal(open(),!desktop);
 if(desktop){assert.equal(d.querySelector('.timeline-place-choices'),null);assert.equal(events.scrollTop,137);dom.window.close();continue;}
 let panel=d.querySelector('.timeline-place-choices');assert.equal(panel.parentElement,events,'Choices use the actual lower scrolling pane');assert.equal(w.getComputedStyle(events).overflow,'auto');assert(events.classList.contains('timeline-choice-mode'));assert.equal(original.parentElement,events,'Full matching events remain intact');assert.equal(events.scrollTop,0);assert.equal(workspace.dataset.mobileView,'events');assert.equal(d.activeElement,panel.querySelector('h3'));
 assert.deepEqual([...panel.querySelectorAll('button')].slice(1).map(n=>n.textContent),choices.map(c=>c.label));panel.querySelectorAll('button')[2].click();assert.equal(selected,19);assert.equal(d.querySelector('.timeline-place-choices'),null);assert(!events.classList.contains('timeline-choice-mode'));assert.equal(events.scrollTop,137);assert.equal(workspace.dataset.mobileView,'story');
 api.showEvents();events.scrollTop=75;open();d.querySelector('.timeline-choices-back').click();assert.equal(d.querySelector('.timeline-place-choices'),null);assert.equal(events.scrollTop,75);assert.equal(workspace.dataset.mobileView,'events');assert.equal(selected,19,'Cancellation does not choose a story');assert.equal(original.parentElement,events);
 open();w.dispatchEvent(new w.CustomEvent('timeline:filter',{detail:{indices:[3]}}));assert.equal(d.querySelector('.timeline-place-choices'),null);assert.equal(workspace.dataset.mobileView,'events');assert.equal(original.parentElement,events);
 open();api.showStory();assert.equal(d.querySelector('.timeline-place-choices'),null);assert.equal(workspace.dataset.mobileView,'story');
 open();media.matches=true;if(media.change)media.change();assert.equal(d.querySelector('.timeline-place-choices'),null,'Desktop transition restores ordinary event list');
 dom.window.close();
}
console.log('PASS: mobile choices occupy the real Events pane, preserve full list and scroll position, select exact story, cancel/filter/view/desktop transitions clear choices; desktop retains map popup contract.');
