/* Executes the actual World timeline controller with its SVG fallback in JSDOM.
 * Real browser layout and the Leaflet provider remain separate checks. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM,VirtualConsole}=require('jsdom');
const html=fs.readFileSync(path.join(__dirname,'../timelines/world-and-scripture-timeline.html'),'utf8');
const dom=new JSDOM(html,{url:'https://focuschrist.com/timelines/world-and-scripture-timeline.html#viewer',runScripts:'outside-only',virtualConsole:new VirtualConsole()});
const w=dom.window,d=w.document;
w.matchMedia=()=>({matches:true,addEventListener(){},removeEventListener(){}});
w.HTMLElement.prototype.scrollIntoView=function(){};w.requestAnimationFrame=()=>0;
w.eval([...d.scripts].find(s=>s.textContent.includes('const DATA = ')).textContent);
const shown=id=>d.getElementById(id).style.display!=='none';
const click=selector=>d.querySelector(selector).click();
const routes=()=>d.querySelectorAll('#worldmap .routepath, #worldmap .ghostpath, #worldmap .party').length;
assert(shown('mapview')&&!shown('river'),'Moment & Map is the initial view');
assert(d.getElementById('modeMap').classList.contains('on'));
assert(routes()>0&&!d.getElementById('routeLegend').hidden,'Book of Mormon route visible with all categories');
click('#catChips [data-cat="bible"]');click('#catChips [data-cat="bom"]');
assert.equal(routes(),0,'World-only removes full and traveled scenario routes');
assert(d.getElementById('routeLegend').hidden);
assert(!/both journey paths are drawn|Book of Mormon promised-land pins/.test(d.getElementById('mapNote').textContent),'World-only does not claim Book of Mormon paths are displayed');
for(const category of ['bible','bom','dual'])assert(d.querySelector('[data-legend-category="'+category+'"]').hidden);
assert(!d.querySelector('[data-legend-category="world"]').hidden);
click('#catChips [data-cat="bible"]');
assert.equal(routes(),0,'Bible and World without Book of Mormon retain no scenario route');
assert(!d.querySelector('[data-legend-category="bible"]').hidden);
click('#catChips [data-cat="world"]');click('#catChips [data-cat="bible"]');click('#catChips [data-cat="bom"]');
assert(routes()>0&&!d.getElementById('routeLegend').hidden,'Book of Mormon-only restores routes and legend');
assert(d.getElementById('mapNote').textContent.includes('both journey paths are drawn'),'Book of Mormon scenario explanation returns with its routes');
click('#modelSeg [data-model="anchored"]');assert(!d.querySelectorAll('#worldmap .ghostpath').length,'Anchored setting retains no hypothetical paths');
for(const choice of ['meso','na','both']){click('#modelSeg [data-model="'+choice+'"]');assert(routes()>0,choice+' restores scenario routes');}
click('#modeChart');assert(shown('river')&&!shown('mapview'),'Explicit Timeline choice remains available');
click('#modeMap');assert(shown('mapview')&&!shown('river'),'Explicit return to map remains available');
assert.equal(d.querySelectorAll('#modelSeg [data-model]').length,4);
assert(/#viewer \.mapsettings #modelSeg\{[^}]*gap:8px/.test(html),'The authored settings rule supplies consistent spacing');
assert(/#viewer \.mapsettings #modelSeg button\{[^}]*border:1px solid/.test(html),'The authored setting rule supplies separate borders');
dom.window.close();
console.log('PASS: initial map, World/Bible/Book of Mormon filters, route legend, all four settings and explicit view switching (SVG controller; browser layout not covered).');
