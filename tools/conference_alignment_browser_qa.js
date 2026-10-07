/* Independent geometry regression; actual UI1/UI2/root visual reviews remain required. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {execFileSync} = require('node:child_process');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.qa-artifacts', 'conference-alignment');
const records = [];
function probe() {
  const rect = e => {const r=e.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
  const center = r => r.x+r.width/2;
  const nav=document.querySelector('.gc-jumps'), n=rect(nav), rows=[];
  for(const e of nav.children){const r=rect(e);let row=rows.find(x=>Math.abs(x.y-r.y)<2);if(!row){row={y:r.y,left:r.x,right:r.right};rows.push(row);}row.left=Math.min(row.left,r.x);row.right=Math.max(row.right,r.right);}
  const figures=[...document.querySelectorAll('#general-conference .fc-study-visual')].map(e=>{const r=rect(e), parent=rect(e.closest('.gc-block')||e.parentElement);return {r,parent,error:Math.abs(center(r)-center(parent))};});
  const arrows=[];
  for(const e of document.querySelectorAll('.fc-button,.fc-unified-continue')){
    const r=rect(e);if(!r.width||!r.height)continue;
    const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let node;
    while((node=walker.nextNode()))for(let i=0;i<node.textContent.length;i++)if(/[↓↗→]/u.test(node.textContent[i])){
      const range=document.createRange();range.setStart(node,i);range.setEnd(node,i+1);const g=range.getBoundingClientRect();
      if(g.width)arrows.push({text:e.textContent.trim(),rightClearance:r.right-g.right,leftClearance:g.left-r.x,verticalClearance:Math.min(g.top-r.y,r.bottom-g.bottom)});
    }
  }
  const select=document.querySelector('#conference-session'),ss=getComputedStyle(select),sr=rect(select);
  const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=`${ss.fontStyle} ${ss.fontWeight} ${ss.fontSize} ${ss.fontFamily}`;
  const textWidth=Math.max(...[...select.options].map(o=>ctx.measureText(o.textContent).width));
  const dropdown={r:sr,appearance:ss.appearance,position:ss.backgroundPosition,size:ss.backgroundSize,image:ss.backgroundImage,paddingRight:parseFloat(ss.paddingRight),textClearance:sr.width-parseFloat(ss.paddingLeft)-parseFloat(ss.paddingRight)-textWidth,options:[...select.options].map(o=>o.value)};
  return {width:innerWidth,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,navRows:rows.map(r=>({...r,error:Math.abs((r.left+r.right)/2-center(n))})),figures,arrows,dropdown,hero:rect(document.querySelector('.gc-page-opening')),picture:rect(document.querySelector('.gc-intro-visual')),cue:rect(document.querySelector('.fc-unified-continue'))};
}
function defects(r){return [
  ...(r.overflow>2?['overflow']:[]),
  ...r.navRows.flatMap((x,i)=>x.error>2?[`navigation row${i} off center`]:[]),
  ...r.figures.flatMap((x,i)=>x.error>2?[`visual group${i} off center`]:[]),
  ...(r.dropdown.appearance!=='none'||!r.dropdown.image.includes('data:image/svg+xml')||!r.dropdown.position.includes('12px')||r.dropdown.size!=='10px 6px'||r.dropdown.paddingRight<36||r.dropdown.textClearance<0?['session dropdown chevron or text clearance']:[]),
  ...r.arrows.flatMap((x,i)=>x.rightClearance<12||x.leftClearance<12||x.verticalClearance<5?[`arrow${i} too near pill edge`]:[])
];}
(async()=>{
 fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{const filename=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!filename.startsWith(root+path.sep)){res.writeHead(403).end();return;}const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'};fs.readFile(filename,(e,b)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':types[path.extname(filename)]||'application/octet-stream'}).end(b));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 try{
  browser=await chromium.launch({headless:true});const context=await browser.newContext();await context.route('https://**',route=>route.abort());const page=await context.newPage();
  const url=`http://127.0.0.1:${server.address().port}/general-conference.html`;
  for(const width of [1905,1722,1280,900,701,700,412,320]){
   await page.setViewportSize({width,height:1000});await page.goto(url,{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);const result=await page.evaluate(probe);
   assert.equal(result.figures.length,5,'all five body art/text groups discovered');assert(result.arrows.length>=4,'arrow pills must actually be measured');
   assert.deepEqual(result.dropdown.options,['all','saturday-morning','saturday-afternoon','sunday-morning','sunday-afternoon'],'native session options preserved');
   assert.deepEqual(defects(result),[],`viewport${width}`);records.push(result);
   for(const [value,count] of [['saturday-morning',9],['saturday-afternoon',10],['sunday-morning',9],['sunday-afternoon',10],['all',38]]){await page.locator('#conference-session').selectOption(value);assert.equal(await page.locator('[data-conference-talk]:not([hidden])').count(),count,'native session filtering');}
  }
  await page.setViewportSize({width:1905,height:1000});await page.goto(url,{waitUntil:'load'});const current=await page.evaluate(probe);
  // Load the released CSS as the genuine negative control, and protect locked opening bounds.
  const baseline=execFileSync('git',['show','317200dc:general-conference-section.css'],{cwd:root});
  await page.route('**/general-conference-section.css?*',route=>route.fulfill({contentType:'text/css',body:baseline}));await page.reload({waitUntil:'load'});const before=await page.evaluate(probe);
  assert(defects(before).some(x=>x.startsWith('navigation row')),'published navigation defect must be detected');
  assert(defects(before).some(x=>x.startsWith('visual group')),'published art/text defect must be detected');
  assert(defects(before).includes('session dropdown chevron or text clearance'),'published native edge-arrow defect must be detected');
  for(const key of ['hero','picture','cue'])for(const field of ['x','y','width','height'])assert(Math.abs(before[key][field]-current[key][field])<1,`locked${key}.${field}`);
  for(const field of ['width','height'])assert(Math.abs(before.dropdown.r[field]-current.dropdown.r[field])<1,`native dropdown outer${field}`);
  await page.unroute('**/general-conference-section.css?*');await page.reload({waitUntil:'load'});
  const bad=await page.addStyleTag({content:'.gc-page .fc-button{padding-right:0!important;padding-left:0!important}'});const edge=await page.evaluate(probe);assert(defects(edge).some(x=>x.startsWith('arrow')),'edge-touching arrow must fail');await bad.evaluate(e=>e.remove());
  console.log('PASS:8viewports, every nav row/five body visual groups, session chevron inset/native options, glyph edge clearance, published defect negatives and locked hero/Continue bounds.');
 }finally{fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(records,null,2)+'\n');if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
