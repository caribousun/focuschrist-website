/* Same-origin visual review tool; no external data or browser automation dependency. */
'use strict';
const page = document.getElementById('page'), size = document.getElementById('size');
const preview = document.getElementById('preview'), stage = document.getElementById('stage');
const report = document.getElementById('report');
let mediaIndex = -1;
function fit() {
  const [width,height] = size.value.split(',').map(Number);
  const scale = Math.min(1,(document.documentElement.clientWidth-32)/width);
  preview.style.width=width+'px'; preview.style.height=height+'px'; preview.style.transform=`scale(${scale})`;
  stage.style.height=height*scale+'px';
}
function openPage() {
  mediaIndex=-1; fit();
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Page load timed out')),15000);
    preview.onload=async()=>{clearTimeout(timer);await preview.contentDocument.fonts.ready;resolve();};
    preview.src='../'+page.value+'?layout-review=geometry';
  });
}
function measure() {
 const d=preview.contentDocument,w=preview.contentWindow;
 const nav=d.querySelector('.nav'),hero=d.querySelector('.fc-visual-hero');
 const rows=[...d.querySelectorAll('.fc-study-feature')].map(row=>{
  const prose=row.querySelector(':scope > div'),card=row.querySelector(':scope > .fc-resource-card');
  const p=prose.getBoundingClientRect(),c=card.getBoundingClientRect();
  const side=c.left>=p.right-1;
  return {key:card.dataset.resourceKey,sideBySide:side,proseHeight:Math.round(p.height),cardHeight:Math.round(c.height),excess:side?Math.round(c.height-p.height):0};
 });
 const n=nav?.getBoundingClientRect(),h=hero?.getBoundingClientRect();
 return {page:page.value,viewport:[w.innerWidth,w.innerHeight],overflow:d.documentElement.scrollWidth>d.documentElement.clientWidth+1,heroTop:h?.top,headerBottom:n?.bottom,heroClear:!h||!n||h.top>=n.bottom-1,rows};
}
document.getElementById('open').onclick=()=>openPage().then(()=>report.textContent=JSON.stringify(measure(),null,2));
document.getElementById('top').onclick=()=>{preview.contentWindow.scrollTo(0,0);mediaIndex=-1;};
document.getElementById('next').onclick=()=>{
 const d=preview.contentDocument,items=[...d.querySelectorAll('.fc-study-feature,.fc-resource-grid')];
 if(!items.length)return;mediaIndex=(mediaIndex+1)%items.length;
 const item=items[mediaIndex];preview.contentWindow.scrollTo(0,item.getBoundingClientRect().top+preview.contentWindow.scrollY-100);
 report.textContent=JSON.stringify(measure(),null,2);
};
document.getElementById('audit').onclick=async()=>{
 const results=[]; report.textContent='Audit running';
 try {for(const option of [...page.options])for(const viewport of [...size.options]){
  page.value=option.value;size.value=viewport.value;await openPage();results.push(measure());
  report.textContent=JSON.stringify({progress:results.length,results},null,2);
 }}catch(error){report.textContent+='\n'+error.message;}
 report.dataset.complete='true';
};
window.addEventListener('resize',fit);
fetch('../sitemap.xml').then(r=>r.text()).then(xml=>{
 const sitemap=new DOMParser().parseFromString(xml,'text/xml');
 for(const loc of sitemap.querySelectorAll('loc')){
  const path=new URL(loc.textContent).pathname.slice(1)||'index.html';
  const option=document.createElement('option');option.value=path;option.textContent=path;page.append(option);
 }
 page.value='ask.html';return openPage();
}).then(()=>report.textContent=JSON.stringify(measure(),null,2)).catch(error=>report.textContent=error.message);
