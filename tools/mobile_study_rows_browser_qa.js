const fs=require('node:fs'),path=require('node:path');
const {JSDOM}=require('jsdom');
const selector='body.fc-site :is(.fc-study-nav:not(.jj-local-nav), .cfm-jump, .gc-jumps, .atonement-path, .cta-row, .journal-collections, .watch-theme-tabs, .filters, .era-pills, .controls-row)';
function inspectMobileStudyRows(selector){
 const issues=[],groups=[];
 for(const [index,nav] of [...document.querySelectorAll(selector)].entries()){
  const n=nav.getBoundingClientRect();if(!n.width||!n.height)continue;
  const cs=getComputedStyle(nav), left=n.left+parseFloat(cs.paddingLeft)+parseFloat(cs.borderLeftWidth),right=n.right-parseFloat(cs.paddingRight)-parseFloat(cs.borderRightWidth);
  const links=[...nav.children].filter(a=>['A','BUTTON'].includes(a.tagName)&&a.getBoundingClientRect().height>0);
  if(!links.length)issues.push(`group${index}: no measured controls`);
  const rows=[];
  for(const a of links){const r=a.getBoundingClientRect();let row=rows.find(x=>Math.abs(x[0].top-r.top)<2);if(!row){row=[];rows.push(row);}row.push({left:r.left,right:r.right,top:r.top,width:r.width,height:r.height});
   if((innerWidth<=700||nav.matches('.fc-study-nav,.cfm-jump,.gc-jumps,.atonement-path'))&&r.height<43.5)issues.push(`group${index}: target below44`);
   if(r.left<left-1||r.right>right+1)issues.push(`group${index}: control containment`);
   if(a.scrollWidth>a.clientWidth+1||a.scrollHeight>a.clientHeight+1)issues.push(`group${index}: label clipped`);
   if(a.matches('.cta-row > .cta')){
    const style=getComputedStyle(a);
    if(!['flex','inline-flex'].includes(style.display)||style.alignItems!=='center'||style.justifyContent!=='center')issues.push(`group${index}: CTA content not centered on both axes`);
    if(style.textAlign!=='center')issues.push(`group${index}: CTA wrapped text not centered`);
   }
  }
  if(innerWidth<=700){
   if(cs.display!=='grid')issues.push(`group${index}: mobile grid missing`);
   const widths=[];
   for(const row of rows){row.sort((a,b)=>a.left-b.left);if(Math.abs(row[0].left-left)>2||Math.abs(row.at(-1).right-right)>2)issues.push(`group${index}: incomplete row`);
    if(row.some(a=>Math.abs(a.width-row[0].width)>2))issues.push(`group${index}: unequal row widths`);
    if(row.length>1)widths.push(...row.map(a=>a.width));
   }
   if(widths.length&&Math.max(...widths)-Math.min(...widths)>2)issues.push(`group${index}: unequal column widths`);
  }
  groups.push({index,links:links.length,rows:rows.map(x=>x.length),display:cs.display});
 }
 if(document.documentElement.scrollWidth>innerWidth+1)issues.push('page overflow');
 const explanation=document.querySelector('.fc-opening-explanation');
 if(explanation&&innerWidth<=700&&explanation.getBoundingClientRect().height===0)issues.push('mobile introduction disappeared');
 return {issues,groups};
}
module.exports=async function(page,origin){
 const root=path.resolve(__dirname,'..'), routes=[...new Set([...fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').matchAll(/<loc>(.*?)<\/loc>/g)].map(x=>new URL(x[1]).pathname.slice(1)||'index.html'))];
 const consumers=routes.filter(route=>{const dom=new JSDOM(fs.readFileSync(path.join(root,route),'utf8'));const found=dom.window.document.querySelectorAll(selector).length;dom.window.close();return found;});
 const results=[];
 for(const [width,enlarged] of [[320,false],[390,false],[412,false],[700,false],[1280,false],[320,true],[390,true],[412,true],[700,true]]){
  await page.setViewportSize({width,height:900});
  for(const route of consumers){
   await page.goto(origin+'/'+route,{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
   await page.waitForFunction(selector=>[...document.querySelectorAll(selector)].every(nav=>nav.querySelector(':scope > a, :scope > button')),selector);
   await page.evaluate(({selector,enlarged})=>{for(const nav of document.querySelectorAll(selector)){let e=nav.parentElement;while(e){if(e.tagName==='DETAILS')e.open=true;e=e.parentElement;}}if(enlarged)document.documentElement.style.fontSize='200%';},{selector,enlarged});
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   const result=await page.evaluate(inspectMobileStudyRows,selector);const expected=await page.locator(selector).count();if(result.groups.length!==expected)result.issues.push('Hidden or unmeasured consumer: expected '+expected+' actual '+result.groups.length);results.push({route,width,enlarged,...result});
  }
 }
 await page.setViewportSize({width:390,height:900});await page.goto(origin+'/answers/look-unto-me-doctrine-and-covenants-6-36.html',{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
 const broken=await page.addStyleTag({content:selector+'{display:flex!important;flex-wrap:wrap!important;justify-content:center!important}'+selector+'>:is(a,button){width:auto!important;flex:0 1 auto!important;grid-column:auto!important}'});
 const negative=await page.evaluate(inspectMobileStudyRows,selector);await broken.evaluate(n=>n.remove());
 if(!negative.issues.some(x=>/incomplete row|unequal row widths|unequal column widths/.test(x)))throw Error('Old ragged mobile layout did not fail geometry check');
 const hiddenCopy=await page.addStyleTag({content:'body.fc-site p.fc-opening-explanation.fc-opening-explanation{display:none!important}'});
 const hiddenNegative=await page.evaluate(inspectMobileStudyRows,selector);await hiddenCopy.evaluate(n=>n.remove());
 if(!hiddenNegative.issues.includes('mobile introduction disappeared'))throw Error('Disappearing introduction fixture did not fail');
 await page.goto(origin+'/atonement.html',{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
 const oddBroken=await page.addStyleTag({content:'body.fc-site .atonement-path>a:last-child{grid-column:auto!important}'});const oddNegative=await page.evaluate(inspectMobileStudyRows,selector);await oddBroken.evaluate(n=>n.remove());if(!oddNegative.issues.some(x=>x.includes('incomplete row')))throw Error('Atonement partial final-row fixture did not fail');
 await page.goto(origin+'/answers/faith-in-jesus-christ-during-trials.html',{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
 const ctaBroken=await page.addStyleTag({content:'body.fc-site .cta-row > .cta{text-align:left!important;align-items:flex-start!important;justify-content:flex-start!important}'});
 const ctaNegative=await page.evaluate(inspectMobileStudyRows,selector);await ctaBroken.evaluate(n=>n.remove());
 if(!ctaNegative.issues.some(x=>x.includes('CTA content not centered on both axes'))||!ctaNegative.issues.some(x=>x.includes('CTA wrapped text not centered')))throw Error('Top/left CTA content fixture did not fail');
 return {consumers,cases:results.length,results,negative:negative.issues,oddNegative:oddNegative.issues,ctaNegative:ctaNegative.issues,failures:results.filter(x=>x.issues.length)};
};
