/* Exercises the actual tile controller in JSDOM; rendered layout is separate. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM,VirtualConsole}=require('jsdom');
const html=fs.readFileSync(path.join(__dirname,'../timelines/adams-1881-chart.html'),'utf8');
(async()=>{
 for(const width of [1440,390]){
  const dom=new JSDOM(html,{url:'https://focuschrist.com/timelines/adams-1881-chart.html',runScripts:'outside-only',virtualConsole:new VirtualConsole()});
  const w=dom.window,d=w.document;w.matchMedia=()=>({matches:width<600,addEventListener(){}});
  w.requestAnimationFrame=f=>{w.pendingFrame=f;return 1};w.HTMLElement.prototype.scrollIntoView=function(){};
  Object.defineProperties(d.getElementById('viewport'),{clientWidth:{value:width},clientHeight:{value:600}});
  const scripts=[...d.scripts].filter(s=>s.textContent.includes('const TILE=')||s.textContent.startsWith('assets[')||s.textContent.includes("const vp=document.getElementById('viewport')"));
  w.eval(scripts.map(s=>s.textContent).join('\n'));w.pendingFrame();
  const status=d.getElementById('progress');assert(status.hidden&&!status.textContent);
  assert(d.querySelectorAll('#tiles img').length>0,'Tile rendering remains active');
  assert(d.getElementById('mini')&&d.getElementById('miniview'),'Minimap remains present');
  assert(d.getElementById('zoom').textContent.includes('%'),'Zoom display remains active');
  d.documentElement.requestFullscreen=()=>Promise.reject(new Error('test'));
  d.getElementById('full').click();await new Promise(resolve=>setTimeout(resolve,0));
  assert(!status.hidden&&status.textContent==='Fullscreen unavailable in this browser','Real fullscreen failure remains visible');
  dom.window.close();
 }
 console.log('PASS: desktop/phone tile controller hides diagnostics while retaining tiles, zoom, minimap and fullscreen error.');
})().catch(e=>{console.error(e);process.exitCode=1});
