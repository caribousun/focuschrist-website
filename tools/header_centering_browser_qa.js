/* Rendered verification of desktop centering and unchanged original typography/hero layout. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),base=process.env.GALLERY_QA_BASE||'http://localhost:4187';
const pages=JSON.parse(fs.readFileSync(path.join(root,'art-gallery.json'))).pages.concat('/art-gallery.html');
const out=process.env.HEADER_QA_OUTPUT||path.resolve(root,'../gallery-qa/header-centering-results.json');
function capture(){
 const rect=el=>{if(!el)return null;const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,width:r.width,height:r.height}};
 const style=el=>{const s=getComputedStyle(el);return Object.fromEntries(['fontFamily','fontSize','fontWeight','letterSpacing','color','backgroundColor','borderColor','textAlign'].map(k=>[k,s[k]]))};
 const nav=document.querySelector('.nav-links'),nr=rect(nav);
 return {width:innerWidth,nav:nr,navDisplay:getComputedStyle(nav).display,offset:nr.left+nr.width/2-innerWidth/2,logo:rect(document.querySelector('.nav-logo')),menu:rect(document.querySelector('.hamburger-wrap')),
 typography:[...document.querySelectorAll('.nav-logo,.nav-links a,.fc-page-intro h1,.fc-page-intro .fc-eyebrow,.fc-page-intro-copy')].map(style),
 hero:[...document.querySelectorAll('[data-hero-viewer],.fc-page-intro,.cfm-hero,.gc-page-opening,.fc-gallery-intro')].map(el=>({rect:rect(el),style:style(el)}))};
}
(async()=>{const browser=await chromium.launch({channel:'chrome',headless:true}),results=[],failures=[];try{
for(const width of [1920,1366,390,1021,1100]){
 const page=await browser.newPage({viewport:{width,height:1000}});
 for(const source of (width===1021||width===1100?['/art.html']:pages)){
  await page.goto(base+source,{waitUntil:'domcontentloaded'});await page.evaluate(()=>document.fonts.ready);
  // Shared enhancements append styles after DOMContentLoaded; let them settle.
  await page.waitForTimeout(500);
  for(const scrolled of [false,true]){
   await page.evaluate(y=>window.scrollTo(0,y),scrolled?600:0);await page.waitForTimeout(220);
   const centered=await page.evaluate(capture);
   const override=await page.addStyleTag({content:'@media(min-width:1021px){body.fc-site .nav[data-focuschrist-header="standard"]{display:flex!important;}}'});
   const original=await page.evaluate(capture);await override.evaluate(el=>el.remove());
   const errors=[];
   if(width>=1021&&Math.abs(centered.offset)>1)errors.push('Navigation not centered');
   if(width>=1021&&(centered.logo.right>centered.nav.left||centered.nav.right>centered.menu.left))errors.push('Header controls overlap');
   if(JSON.stringify(centered.typography)!==JSON.stringify(original.typography))errors.push('Typography/colors changed');
   if(JSON.stringify(centered.hero)!==JSON.stringify(original.hero))errors.push('Hero/intro geometry or styling changed');
   if(width<1021&&JSON.stringify(centered)!==JSON.stringify(original))errors.push('Mobile layout changed');
   const row={page:source,width,scrolled,offset:centered.offset,display:centered.navDisplay,errors};results.push(row);if(errors.length)failures.push(row);
  }
 }
 await page.close();console.log('Verified width '+width);
}
}finally{await browser.close();fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify({results,failures},null,2))}
console.log(JSON.stringify({cases:results.length,failures:failures.length,evidence:out}));if(failures.length){console.log(JSON.stringify(failures));process.exitCode=1}
})().catch(error=>{console.error(error);process.exitCode=1});
