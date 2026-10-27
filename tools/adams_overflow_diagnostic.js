/* CI-only, diagnostic evidence; this does not establish release acceptance. */
'use strict';
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const crypto = require('node:crypto'), { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.qa-artifacts', 'adams-overflow-diagnostic');
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const TYPES = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.woff2':'font/woff2','.ico':'image/x-icon'};
// The first three baselines are exact prior actual owner-render evidence; the
// enlarged baseline is exact prior overflow-diagnostic evidence. Neither is a
// new render or acceptance. Compare against actual bytes served by this checkout.
const PRIOR={
 desktop:{hero:{x:0,y:52,width:1280,height:427.5},cue:{x:576.203125,y:673.953125,width:127.578125,height:44},textBottom:705.796875},
 phone:{hero:{x:0,y:77,width:390,height:448.5},cue:{x:131.203125,y:731.84375,width:127.578125,height:44},textBottom:763.6875},
 narrow:{hero:{x:0,y:77,width:320,height:226},cue:{x:96.203125,y:500.375,width:127.578125,height:44},textBottom:532.21875},
 enlarged:{hero:{x:0,y:84.84375,width:320,height:368},cue:{x:52.875,y:884.828125,width:214.234375,height:46.03125},textBottom:null}
};
async function compareProfiles(browser,origin,report) {
 const profiles=[{name:'desktop',width:1280,height:900,touch:false,scale:1},{name:'phone',width:390,height:844,touch:true,scale:1},{name:'narrow',width:320,height:568,touch:true,scale:1},{name:'enlarged',width:320,height:1000,touch:false,scale:2}];
 report.baselineEvidence={ownerReport:'docs/adams-integrated-context/owner-report.json',ownerReportSha256:'b73e052b4121c52ea9d68557af48b28ecda4ee64e11846973d6c46deaf122d8f',enlargedRun:40586004823,enlargedArtifactSha256:'90a7e12e0e41de5e37c72cde232932fe28dd1fc7a3582b3add60292db16d3cb9',oldCssSha256:'d936516926aa47c12c634b11b15278e1590502d0491d9b1f17cd90a0210fdeb1',oldIntroSha256:'742d429e6a674ce5d47889aab964a6bde60f3509bd9518e159499be6616112be',comparison:'exact CSS pixel equality; all deltas recorded'};
 const oldReport=fs.readFileSync(path.join(root,report.baselineEvidence.ownerReport));
 if(sha(oldReport)!==report.baselineEvidence.ownerReportSha256) throw new Error('Historical owner report bytes changed');
 const parsed=JSON.parse(oldReport);
 for(const item of [{path:'adams-integration.css',bytes:4965,sha256:report.baselineEvidence.oldCssSha256},{path:'timelines/adams-1881-introduction.html',bytes:8126,sha256:report.baselineEvidence.oldIntroSha256}]){const found=parsed.checked.filter(x=>x.path===item.path);if(found.length!==1||found[0].sha256!==item.sha256||found[0].bytes!==item.bytes)throw new Error('Prior source identity mismatch '+item.path);}
 const expectedProfiles={desktop:{width:1280,height:900,touch:false},phone:{width:390,height:844,touch:true},narrow:{width:320,height:568,touch:true}};
 for(const name of ['desktop','phone','narrow']) {
   const entry=parsed.profiles.find(p=>p.profile.name===name);const row=entry?.openingComparison?.current;
   for(const key of ['width','height','touch'])if(entry?.profile[key]!==expectedProfiles[name][key])throw new Error('Prior profile mismatch '+name+' '+key);
   if(!row)throw new Error('Missing prior geometry '+name);
   for(const target of ['hero','cue']) for(const key of ['x','y','width','height']) if(row[target][key]!==PRIOR[name][target][key])throw new Error('Prior geometry mismatch '+name+' '+target+' '+key);
   if(row.textBottom!==PRIOR[name].textBottom)throw new Error('Prior text baseline mismatch '+name);
 }
 report.profileComparisons=[];
 for(const profile of profiles) {
   const row={profile,baseline:profile.name==='enlarged'?null:PRIOR[profile.name],priorBrokenIntro:profile.name==='enlarged'?PRIOR.enlarged:null,errors:[],screenshots:[]};report.profileComparisons.push(row);let ctx;
   try {
    ctx=await browser.newContext({viewport:{width:profile.width,height:profile.height},isMobile:profile.touch,hasTouch:profile.touch,deviceScaleFactor:1,reducedMotion:'reduce',serviceWorkers:'block'});
    let n=0;await ctx.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==origin){if(report.blocked.length<200)report.blocked.push({origin:u.origin,path:u.pathname});return r.abort();}if(++n>1000){row.errors.push('request bound');return r.abort();}return r.continue();});
    await ctx.routeWebSocket('**/*',ws=>{const u=new URL(ws.url());if(report.blockedWebSockets.length<200)report.blockedWebSockets.push({origin:u.origin,path:u.pathname});ws.close();});
    const p=await ctx.newPage();p.setDefaultTimeout(5000);
    p.on('pageerror',e=>row.errors.push('pageerror '+String(e)));
    p.on('response',r=>{if(r.status()>=400)row.errors.push('HTTP '+r.status()+' '+new URL(r.url()).pathname);});
    if(profile.name==='enlarged'){
      const ref=await p.goto(origin+'/timelines/latter-day-saint-church-history-timeline.html',{waitUntil:'load',timeout:30000});if(!ref||ref.status()!==200)throw new Error('Reference response status');
      await p.evaluate(()=>{document.documentElement.style.fontSize='200%';});
      await p.evaluate(async()=>{const images=[...document.images].filter(n=>new URL(n.src,location.href).origin===location.origin);images.forEach(n=>n.loading='eager');await Promise.race([Promise.all(images.map(n=>n.decode().catch(()=>{}))),new Promise(r=>setTimeout(r,10000))]);await Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,5000))]);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
      row.reference=await p.evaluate(()=>{const rect=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,centerX:r.x+r.width/2,centerY:r.y+r.height/2};};const hero=document.querySelector('.timeline-life-hero'),cue=document.querySelector('.timeline-opening-continue');if(!hero||!cue)throw Error('Reference hero or Continue missing');const range=document.createRange();range.selectNodeContents(cue);return{hero:rect(hero),cue:rect(cue),textBottom:range.getBoundingClientRect().bottom,scrollWidth:document.documentElement.scrollWidth,rootFontSize:getComputedStyle(document.documentElement).fontSize};});
      row.baseline=row.reference;row.baselineOrigin='Actual reference Timeline at same viewport and font, not prior broken intro';
      const refshot=await p.screenshot({type:'png',fullPage:false,animations:'disabled',timeout:10000});fs.writeFileSync(path.join(out,'enlarged-reference-opening.png'),refshot,{flag:'wx'});row.screenshots.push({file:'enlarged-reference-opening.png',bytes:refshot.length,sha256:sha(refshot)});
    }
    const response=await p.goto(origin+'/timelines/adams-1881-introduction.html',{waitUntil:'load',timeout:30000});if(!response||response.status()!==200)throw new Error('intro response status');
    await p.evaluate(scale=>{document.documentElement.style.fontSize=(scale*100)+'%';},profile.scale);
    await p.evaluate(async()=>{const images=[...document.images].filter(n=>new URL(n.src,location.href).origin===location.origin);images.forEach(n=>n.loading='eager');await Promise.race([Promise.all(images.map(n=>n.decode().catch(()=>{}))),new Promise(r=>setTimeout(r,10000))]);await Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,5000))]);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
    await p.mouse.move(profile.width-2,profile.height-2);
    row.observed=await p.evaluate(()=>{const rect=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom,centerX:r.x+r.width/2,centerY:r.y+r.height/2};};const hero=document.querySelector('.timeline-life-hero'),cue=document.querySelector('.timeline-opening-continue');if(!hero||!cue)throw Error('Missing hero or Continue');const range=document.createRange();range.selectNodeContents(cue);return{hero:rect(hero),cue:rect(cue),textBottom:range.getBoundingClientRect().bottom,scrollWidth:document.documentElement.scrollWidth,innerWidth,controls:['.fc-search-trigger[data-site-search-trigger]','.hamburger'].map(sel=>{const e=document.querySelector(sel);if(!e)return{selector:sel,missing:true};const r=e.getBoundingClientRect(),s=getComputedStyle(e),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return{selector:sel,...rect(e),display:s.display,visibility:s.visibility,hit:!!hit&&(hit===e||e.contains(hit))};})};});
    for(const target of ['hero','cue'])if(row.baseline[target].centerX===undefined)row.baseline[target].centerX=row.baseline[target].x+row.baseline[target].width/2;row.geometryDiffs=[];for(const target of ['hero','cue'])for(const key of ['x','y','width','height','centerX']){const delta=row.observed[target][key]-row.baseline[target][key];row.geometryDiffs.push({target,key,delta});const locked=target==='hero'?['x','y','width','height'].includes(key):profile.name==='enlarged'?key==='centerX':['x','y','width','height'].includes(key);if(locked&&delta!==0)row.errors.push(target+' '+key+' differs by '+delta+'px');}const baselineDelta=row.observed.textBottom-row.baseline.textBottom;row.geometryDiffs.push({target:'cueText',key:'bottom',delta:baselineDelta});if(baselineDelta!==0)row.errors.push('Continue text baseline differs by '+baselineDelta+'px');
    if(profile.name==='enlarged'){
      row.priorBrokenGeometryDiffs=[];
      for(const target of ['hero','cue'])row.priorBrokenIntro[target].centerX=row.priorBrokenIntro[target].x+row.priorBrokenIntro[target].width/2;
      for(const target of ['hero','cue'])for(const key of ['x','y','width','height','centerX'])row.priorBrokenGeometryDiffs.push({target,key,delta:row.observed[target][key]-row.priorBrokenIntro[target][key]});
      row.priorBrokenGeometryStatus=row.priorBrokenGeometryDiffs.some(x=>x.delta!==0)?'CHANGED_OWNER_JUDGMENT_REQUIRED':'UNCHANGED';
      if(row.priorBrokenGeometryStatus==='CHANGED_OWNER_JUDGMENT_REQUIRED')report.ownerJudgmentRequired='Enlarged intro moved from prior rendered state; reconcile owner geometry mandate and reference comparison before release.';
    }
    if(row.observed.scrollWidth>profile.width)row.errors.push('Horizontal overflow '+(row.observed.scrollWidth-profile.width)+'px');
    for(const control of row.observed.controls)if(control.missing||control.display==='none'||control.visibility!=='visible'||!control.hit||control.width<44||control.height<44||control.x<0||control.right>profile.width||control.y<0||control.bottom>profile.height)row.errors.push('Unreachable or sub-44px control '+control.selector);
    row.cueVisibility=await p.evaluate(()=>{const e=document.querySelector('.timeline-opening-continue'),r=e.getBoundingClientRect(),s=getComputedStyle(e),range=document.createRange();range.selectNodeContents(e);const boxes=[...range.getClientRects()].filter(x=>x.width&&x.height).map(x=>({left:x.left,right:x.right,top:x.top,bottom:x.bottom}));const clipped=[];for(let a=e.parentElement;a&&a!==document.body&&a!==document.documentElement;a=a.parentElement){const q=a.getBoundingClientRect(),z=getComputedStyle(a);if((['hidden','clip'].includes(z.overflowX)&&boxes.some(x=>x.left<q.left||x.right>q.right))||(['hidden','clip'].includes(z.overflowY)&&boxes.some(x=>x.top<q.top||x.bottom>q.bottom)))clipped.push({tag:a.tagName,id:a.id,className:a.className});}return{display:s.display,visibility:s.visibility,rect:{left:r.left,right:r.right,top:r.top,bottom:r.bottom},textFragments:boxes,clippedBy:clipped};});
    const v=row.cueVisibility;if(v.display==='none'||v.visibility!=='visible'||v.rect.left<0||v.rect.right>profile.width||v.rect.top<0||v.rect.bottom>profile.height||!v.textFragments.length||v.clippedBy.length)row.errors.push('Continue is hidden, offscreen, clipped, or has no visible text');
    async function shot(label){const data=await p.screenshot({type:'png',fullPage:false,animations:'disabled',timeout:10000});const file=profile.name+'-'+label+'.png';fs.writeFileSync(path.join(out,file),data,{flag:'wx'});row.screenshots.push({file,bytes:data.length,sha256:sha(data)});}
    await shot('opening');
    try{const menu=p.locator('.hamburger');await menu.focus();await p.keyboard.press('Enter');await p.waitForFunction(()=>document.querySelector('.hamburger')?.getAttribute('aria-expanded')==='true'&&getComputedStyle(document.getElementById('hamburgerMenu')).display!=='none');row.menuBox=await p.locator('#hamburgerMenu').boundingBox();if(!row.menuBox||row.menuBox.x<0||row.menuBox.y<0||row.menuBox.x+row.menuBox.width>profile.width||row.menuBox.y+row.menuBox.height>profile.height)row.errors.push('Open menu outside viewport');await shot('menu');await p.keyboard.press('Escape');await p.waitForFunction(()=>document.querySelector('.hamburger')?.getAttribute('aria-expanded')==='false'&&getComputedStyle(document.getElementById('hamburgerMenu')).display==='none'&&document.activeElement===document.querySelector('.hamburger'));row.menuKeyboard='PASS';}catch(e){row.menuKeyboard='FAIL';row.errors.push('Menu keyboard '+String(e));}
    try{const search=p.locator('[data-site-search-trigger]');await search.focus();await p.keyboard.press('Enter');await p.waitForSelector('#fc-search-dialog[open]');row.searchBox=await p.locator('#fc-search-dialog').boundingBox();if(!row.searchBox||row.searchBox.x<0||row.searchBox.y<0||row.searchBox.x+row.searchBox.width>profile.width||row.searchBox.y+row.searchBox.height>profile.height)row.errors.push('Open search outside viewport');await shot('search');await p.keyboard.press('Escape');await p.waitForFunction(()=>!document.getElementById('fc-search-dialog')?.open&&document.activeElement===document.querySelector('[data-site-search-trigger]'));row.searchKeyboard='PASS';}catch(e){row.searchKeyboard='FAIL';row.errors.push('Search keyboard '+String(e));}
   }catch(e){row.errors.push(String(e&&e.stack||e));}finally{if(ctx)await ctx.close().catch(()=>{});}
   if(row.errors.length)report.errors.push('Profile '+profile.name+' has '+row.errors.length+' diagnostic findings');
 }
}

async function main() {
  if (process.env.CI !== 'true' || process.argv.length !== 2) throw new Error('Hosted CI only; fixed route and profile');
  const actual = execFileSync('git', ['rev-parse','HEAD'], {cwd:root,encoding:'utf8'}).trim();
  if (!process.env.EXPECTED_CHECKOUT_SHA || actual !== process.env.EXPECTED_CHECKOUT_SHA) throw new Error('Checkout SHA mismatch');
  fs.mkdirSync(out, {recursive:true});
  const report = {scope:'Diagnostic only, not release acceptance', checkout:actual, profile:{width:320,height:1000,rootFontSize:'200%'}, route:'/timelines/adams-1881-introduction.html', fidelity:'External requests are blocked here; the original canonical runner does not block them. Exact 371px reproduction is an observation, not proof of cause.', expectedCanonicalScrollWidth:371, served:[], blocked:[], blockedWebSockets:[], errors:[]};
  let server, browser, context, requests=0, servedBytes=0;
  try {
    report.actualSources=['adams-integration.css','timelines/adams-1881-introduction.html','timelines/latter-day-saint-church-history-timeline.html'].map(name=>{const bytes=fs.readFileSync(path.join(root,name));return {path:name,bytes:bytes.length,sha256:sha(bytes)};});
    if(report.actualSources[0].sha256!=='3c8a2390e93e94f5d67d3b7a4356f018d78df7ea5c654a3841366549df76d131'||report.actualSources[1].sha256!=='742d429e6a674ce5d47889aab964a6bde60f3509bd9518e159499be6616112be'||report.actualSources[2].sha256!=='d3aa8f0ee8947f1c1f8b6402cd5e0361e9c7498de84d91c058c608998431edc5')throw new Error('Actual candidate CSS or unchanged introduction source differs');
    server = http.createServer((req,res) => {
      if (!['GET','HEAD'].includes(req.method)) return res.writeHead(405).end();
      let requested;
      try { requested = decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname); } catch { return res.writeHead(400).end(); }
      const parts=requested.split('/').filter(Boolean), ext=path.extname(requested).toLowerCase();
      if (parts.some(x=>x.startsWith('.')) || !TYPES[ext] || (parts.length>1 && !['assets','history','timelines','scripture-data'].includes(parts[0]))) return res.writeHead(403).end();
      const file=path.resolve(root,'.'+requested);
      if (!file.startsWith(root+path.sep)) return res.writeHead(403).end();
      try {
        const stat=fs.lstatSync(file);
        if (!stat.isFile() || stat.isSymbolicLink() || fs.realpathSync(file)!==file || stat.size>8*1024*1024) return res.writeHead(403).end();
        const bytes=fs.readFileSync(file); servedBytes+=bytes.length;
        if (servedBytes>128*1024*1024) return res.writeHead(413).end();
        report.served.push({path:requested,bytes:bytes.length,sha256:sha(bytes)});
        res.writeHead(200,{'Content-Type':TYPES[ext]}); res.end(req.method==='HEAD'?undefined:bytes);
      } catch { res.writeHead(404).end(); }
    });
    await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
    const origin='http://127.0.0.1:'+server.address().port;
    browser=await chromium.launch({headless:true});
    report.browserVersion=browser.version();
    context=await browser.newContext({viewport:{width:320,height:1000},deviceScaleFactor:1,serviceWorkers:'block'});
    await context.route('**/*', route=>{
      const url=new URL(route.request().url());
      if (url.origin!==origin) { if(report.blocked.length<200) report.blocked.push({origin:url.origin,path:url.pathname}); return route.abort(); }
      if (++requests>1000) { report.errors.push('Request bound exceeded'); return route.abort(); }
      return route.continue();
    });
    await context.routeWebSocket('**/*', ws=>{ const url=new URL(ws.url()); if(report.blockedWebSockets.length<200) report.blockedWebSockets.push({origin:url.origin,path:url.pathname}); ws.close(); });
    const page=await context.newPage();
    page.on('pageerror',e=>report.errors.push('pageerror: '+String(e).slice(0,2000)));
    page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP '+r.status()+' '+new URL(r.url()).pathname);});
    const response=await page.goto(origin+report.route,{waitUntil:'load',timeout:30000});
    report.status=response?.status() || null;
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%';});
    await page.evaluate(async()=>{
      const local=[...document.images].filter(n=>new URL(n.src,location.href).origin===location.origin);
      local.forEach(n=>{n.loading='eager';});
      await Promise.race([Promise.all(local.map(n=>n.decode().catch(()=>{}))),new Promise(resolve=>setTimeout(resolve,10000))]);
      await Promise.race([document.fonts.ready,new Promise(resolve=>setTimeout(resolve,5000))]);
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    });
    report.measurement=await page.evaluate(()=>{
      const box=r=>({x:r.x,y:r.y,left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height});
      const styleKeys=['display','visibility','opacity','position','overflowX','overflowY','whiteSpace','fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','width','minWidth','maxWidth','height','boxSizing','paddingLeft','paddingRight','marginLeft','marginRight','marginTop','marginBottom','paddingTop','paddingBottom','transform','transformOrigin','content','left','right','top','bottom','inset','overflowWrap','zIndex'];
      const styles=s=>Object.fromEntries(styleKeys.map(k=>[k,s[k]]));
      const selector=n=>{const chain=[];for(let e=n;e&&e.nodeType===1;e=e.parentElement){const parent=e.parentElement;const index=parent?[...parent.children].indexOf(e)+1:1;chain.push(e.tagName.toLowerCase()+':nth-child('+index+')');}return chain.reverse().join(' > ');};
      const nodes=[...document.querySelectorAll('*')];
      const elements=nodes.map((e,i)=>({index:i,selector:selector(e),tag:e.tagName.toLowerCase(),id:e.id||null,classes:e.getAttribute('class'),rect:box(e.getBoundingClientRect()),clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,offsetWidth:e.offsetWidth,scrollLeft:e.scrollLeft,clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,style:styles(getComputedStyle(e)),before:styles(getComputedStyle(e,'::before')),after:styles(getComputedStyle(e,'::after'))}));
      const texts=[];const walker=document.createTreeWalker(document.documentElement,NodeFilter.SHOW_TEXT);
      while(walker.nextNode()) { const n=walker.currentNode,range=document.createRange();range.selectNodeContents(n);texts.push({parent:selector(n.parentElement),text:n.data,rect:box(range.getBoundingClientRect()),fragments:[...range.getClientRects()].map(box)}); }
      return {innerWidth,innerHeight,devicePixelRatio,scrollX,scrollY,documentScrollWidth:document.documentElement.scrollWidth,bodyScrollWidth:document.body.scrollWidth,rootFontSize:getComputedStyle(document.documentElement).fontSize,fontStatus:document.fonts.status,images:[...document.images].map(i=>({src:i.currentSrc||i.src,complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight})),elements,texts};
    });
    report.reproduction=report.measurement.documentScrollWidth===report.expectedCanonicalScrollWidth ? 'MATCHES_371PX_CANONICAL_OBSERVATION' : 'NOT_REPRODUCED_371PX_CANONICAL_OBSERVATION';
    const shot=await page.screenshot({type:'png',fullPage:false,animations:'disabled',timeout:10000});
    fs.writeFileSync(path.join(out,'adams-320-200-percent.png'),shot,{flag:'wx'});
    report.screenshot={file:'adams-320-200-percent.png',bytes:shot.length,sha256:sha(shot)};
    const full=await page.screenshot({type:'png',fullPage:true,animations:'disabled',timeout:10000});
    fs.writeFileSync(path.join(out,'adams-320-200-percent-full-page.png'),full,{flag:'wx'});
    report.fullPageScreenshot={file:'adams-320-200-percent-full-page.png',bytes:full.length,sha256:sha(full)};
    await compareProfiles(browser,origin,report);
    for(const source of report.actualSources) if(!report.served.some(row=>row.path==='/'+source.path&&row.sha256===source.sha256)) report.errors.push('Actual source not served: '+source.path);
    if(report.status!==200) report.errors.push('Document did not return 200');
  } catch(e) { report.errors.push(String(e && e.stack || e)); }
  finally {
    if(context) await context.close().catch(()=>{});
    if(browser) await browser.close().catch(()=>{});
    if(server) await new Promise(resolve=>server.close(resolve));
    fs.writeFileSync(path.join(out,'diagnostic.json'),JSON.stringify(report,null,2)+'\n');
  }
  if(report.errors.length || !report.measurement || !report.screenshot) process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1;});
