/* Exact rendered header buffers; called after each profile applies text scaling. */
'use strict';
const assert=require('node:assert/strict');
function clear(a,b){return Math.min(a.right,b.right)<=Math.max(a.left,b.left)||Math.min(a.bottom,b.bottom)<=Math.max(a.top,b.top);}
assert.throws(()=>assert(clear({left:20,right:260,top:20,bottom:65},{left:240,right:284,top:20,bottom:64})), 'Old enlarged wordmark/control overlap must fail');
module.exports=async function(page){
 await page.evaluate(()=>window.dispatchEvent(new Event('resize')));
 await page.waitForTimeout(100);
 if(await page.evaluate(()=>innerWidth>1020))return {desktopDelegatedToExistingHeaderChecks:true};
 const g=await page.locator('[data-focuschrist-header="standard"]').evaluate(h=>{
  const rect=n=>{const r=n.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};};
  return {header:rect(h),logo:rect(h.querySelector('.nav-logo')),search:rect(h.querySelector('.fc-search-trigger')),menu:rect(h.querySelector('.hamburger')),width:innerWidth,offset:parseFloat(getComputedStyle(document.querySelector('[data-timeline-workspace]')).getPropertyValue('--timeline-menu-height'))};
 });
 assert(Math.abs(g.offset-g.header.height)<=1,'Workspace offset follows actual header height');
 const overlap=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>0&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>0;
 for(const key of ['search','menu']){const r=g[key];assert(r.width>=44&&r.height>=44,key+' full44px pointer target');assert(r.left>=0&&r.right<=g.width&&r.top>=g.header.top&&r.bottom<=g.header.bottom+1,key+' inside header');assert(!overlap(r,g.logo),key+' does not overlap wordmark');}
 assert(g.menu.left-g.search.right>=7,'Search/menu retain8px buffer');
 const rowOverlap=Math.min(g.logo.bottom,g.search.bottom)-Math.max(g.logo.top,g.search.top)>0;
 assert(rowOverlap?g.search.left-g.logo.right>=11:g.search.top-g.logo.bottom>=7,'Wordmark retains12px same-row or8px wrapped-row buffer');
 return g;
};
