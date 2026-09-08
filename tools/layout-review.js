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
    let settling=false;
    const previousDocument=preview.contentDocument;
    const timer=setTimeout(()=>{clearInterval(poll);reject(new Error('Page load timed out: '+page.value));},20000);
    preview.src='../'+page.value+'?layout-review='+Date.now();
    const poll=setInterval(async()=>{
      const d=preview.contentDocument;
      if(settling||!d||d===previousDocument||d.URL!==preview.src||!d.querySelector('h1')||d.readyState==='loading')return;
      settling=true;clearInterval(poll);
      await Promise.race([d.fonts.ready,new Promise(done=>setTimeout(done,2000))]);
      await new Promise(done=>setTimeout(done,350));
      clearTimeout(timer);resolve();
    },100);
  });
}
function measure(frame=preview,pagePath=page.value) {
 const d=frame.contentDocument,w=frame.contentWindow;
 const nav=d.querySelector('.nav'),hero=d.querySelector('.fc-visual-hero');
 const rows=[...d.querySelectorAll('.fc-study-feature')].flatMap(row=>{
  const prose=row.querySelector(':scope > div'),card=row.querySelector(':scope > .fc-resource-card');
  if(!prose||!card)return [];
  const p=prose.getBoundingClientRect(),c=card.getBoundingClientRect();
  const side=c.left>=p.right-1;
  return {key:card.dataset.resourceKey,sideBySide:side,proseHeight:Math.round(p.height),cardHeight:Math.round(c.height),excess:side?Math.round(c.height-p.height):0};
 });
 const n=nav?.getBoundingClientRect(),h=hero?.getBoundingClientRect();
 const intro=d.querySelector('.fc-page-intro'),introBottom=intro?.getBoundingClientRect().bottom;
 const actions=[...d.querySelectorAll('.fc-page-intro .fc-actions a,.fc-page-intro .fc-actions button')].map(a=>a.getBoundingClientRect().bottom);
 const actionsVisible=actions.every(bottom=>bottom<=w.innerHeight-8);
 const approvedHero=hero?.matches('.fc-home-hero,.fc-answer-detail-hero');
 const approvedHeroStyle=approvedHero?w.getComputedStyle(hero,'::before'):null;
 const approvedHeroExpectedSize=w.innerWidth<=700?'auto 120%':'100% auto';
 const approvedHeroExpectedPosition=w.innerWidth<=700?'50% 24%':'50% 50%';
 const approvedHeroCentered=!approvedHero||approvedHeroStyle.backgroundPosition===approvedHeroExpectedPosition||approvedHeroStyle.backgroundPosition==='center';
 const heroRatioFit=!hero||w.innerWidth<=700||Math.abs(h.height-(h.width*684/2048))<=1;
 const approvedRatioFit=!approvedHero||heroRatioFit;
 const approvedHeroFit=!approvedHero||((approvedHeroStyle.backgroundSize===approvedHeroExpectedSize||(approvedHeroExpectedSize==='100% auto'&&approvedHeroStyle.backgroundSize==='100%'))&&approvedHeroCentered&&approvedRatioFit);
 const headerHeightFit=!nav||Math.abs(n.height-(w.innerWidth>1020?52:62))<=1;
 const mobileFlow=w.innerWidth<=700;
 const openingVisible=mobileFlow||!introBottom||introBottom>=w.innerHeight-1;
 const openingAligned=mobileFlow||!introBottom||(introBottom>=w.innerHeight-1&&introBottom<=w.innerHeight+12);
 const nextTop=intro?.nextElementSibling?.getBoundingClientRect().top;
 const nextSectionHidden=mobileFlow||!nextTop||nextTop>=w.innerHeight-1;
 const rect = element => { const r=element.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,right:r.right}; };
 const container=intro?.querySelector('.fc-container--standard');
 const children=container?[...container.children].filter(e=>w.getComputedStyle(e).display!=='none').map(e=>({className:e.className,...rect(e)})):[];
 const pills=[...d.querySelectorAll('.fc-page-intro .fc-actions .fc-button')].map(e=>({text:e.textContent.trim(),...rect(e),font:w.getComputedStyle(e).fontSize,padding:w.getComputedStyle(e).padding}));
 const heroSnapshot=hero?[hero,...hero.querySelectorAll('img')].map(e=>({tag:e.tagName,...rect(e),styles:[null,'::before','::after'].map(pseudo=>{const s=w.getComputedStyle(e,pseudo);return Object.fromEntries(['height','width','min-height','aspect-ratio','background-image','background-size','background-position','object-fit','object-position','mask-image','transform'].map(k=>[k,s.getPropertyValue(k)]));})})):[];
 const textBounds=container?[...container.querySelectorAll('p,h1,a,button,.fc-page-intro-scripture')].map(e=>{const range=d.createRange();range.selectNodeContents(e);const r=range.getBoundingClientRect();const b=e.getBoundingClientRect();return {text:e.textContent.trim().slice(0,60),bottom:r.bottom,left:r.left,right:r.right,clipped:r.left<b.left-2||r.right>b.right+2||r.bottom>introBottom+1};}):[];
 const mobileBottomSpace=mobileFlow&&children.length?introBottom-children.at(-1).bottom:null;
 const mobileInterChildGaps=mobileFlow?children.slice(1).map((child,index)=>child.y-children[index].bottom):[];
 const mobileMaxInterChildGap=mobileInterChildGaps.length?Math.max(...mobileInterChildGaps):0;
 const compactMobileSpace=!mobileFlow||(mobileBottomSpace<=40&&mobileMaxInterChildGap<=40);
 const contentContained=children.every(r=>r.x>=-1&&r.right<=d.documentElement.clientWidth+1&&r.bottom<=introBottom+1)&&textBounds.every(r=>!r.clipped);
 return {container:container?rect(container):null,children,pills,heroSnapshot,textBounds,contentContained,mobileBottomSpace,mobileMaxInterChildGap,compactMobileSpace,heroHeight:h?.height,stylesheet:d.querySelector('link[href*="site-system.css"]')?.getAttribute('href'),page:pagePath,viewport:[w.innerWidth,w.innerHeight],overflow:d.documentElement.scrollWidth>d.documentElement.clientWidth+1,introBottom,nextTop,openingVisible,openingAligned,nextSectionHidden,actionsVisible,heroRatioFit,headerHeightFit,approvedHeroFit,approvedRatioFit,approvedHeroExpectedSize,approvedHeroBackgroundSize:approvedHeroStyle?.backgroundSize,approvedHeroBackgroundPosition:approvedHeroStyle?.backgroundPosition,heroTop:h?.top,headerBottom:n?.bottom,heroClear:!h||!n||h.top>=n.bottom-1,rows};
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
 let auditError=null;
 const scope=new URLSearchParams(location.search).get('scope');
 const jobs=[...page.options].filter(option=>scope==='primary'?!option.value.includes('/')&&option.value!=='404.html':scope==='detail'?option.value.includes('/')||option.value==='404.html':true);
 const selectedSizes=new URLSearchParams(location.search).get('sizes')?.split('|').map(v=>v.replace('x',','));
 const viewports=[...size.options].filter(option=>!selectedSizes||selectedSizes.includes(option.value));
 const expected=jobs.length*viewports.length;
 try {for(const option of jobs){
   page.value=option.value;
   for(const viewport of viewports){
     size.value=viewport.value;
     await openPage();
     results.push(measure());
     report.textContent=JSON.stringify({progress:results.length,total:expected,results},null,2);
   }
 }}catch(error){auditError=error.message;}
 const failures=results.filter(result=>!result.contentContained||!result.compactMobileSpace||result.overflow||!result.heroClear||!result.openingVisible||!result.openingAligned||!result.nextSectionHidden||!result.actionsVisible||!result.heroRatioFit||!result.headerHeightFit||!result.approvedHeroFit);
 report.textContent=JSON.stringify({complete:true,pass:!auditError&&results.length===expected&&failures.length===0,error:auditError,expected,checked:results.length,failures,results},null,2);
 report.dataset.complete='true';report.dataset.pass=String(!auditError&&results.length===expected&&failures.length===0);
};
window.addEventListener('resize',fit);
fetch('../sitemap.xml').then(r=>r.text()).then(xml=>{
 const sitemap=new DOMParser().parseFromString(xml,'text/xml');
 for(const loc of sitemap.querySelectorAll('loc')){
  const path=new URL(loc.textContent).pathname.slice(1)||'index.html';
  const option=document.createElement('option');option.value=path;option.textContent=path;page.append(option);
 }
 if(![...page.options].some(option=>option.value==='404.html')){
  const option=document.createElement('option');option.value='404.html';option.textContent='404.html';page.append(option);
 }
 const params=new URLSearchParams(location.search);
 page.value=params.get('page')||'ask.html';
 if(params.has('size'))size.value=params.get('size');
 return openPage();
}).then(()=>{report.textContent=JSON.stringify(measure(),null,2);if(new URLSearchParams(location.search).has('audit'))document.getElementById('audit').click();}).catch(error=>report.textContent=error.message);
