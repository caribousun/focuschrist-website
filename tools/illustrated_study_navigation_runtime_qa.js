const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
for(const page of ['answers/why-latter-day-saints-build-temples.html','birth-of-christ.html']){
 const dom=new JSDOM(read(page),{url:'https://focuschrist.com/'+page,runScripts:'outside-only'});
 const w=dom.window,d=w.document;
 w.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','')};
 w.HTMLDialogElement.prototype.close=function(){this.removeAttribute('open')};
 w.HTMLElement.prototype.scrollIntoView=function(){};
 const onward=d.createElement('section');onward.id='next-study';onward.innerHTML='<a href="/unrelated-sentinel.html">Unrelated sentinel</a>';d.querySelector('main').prepend(onward);
 w.eval(read('topic-artwork-details.js'));d.dispatchEvent(new w.Event('DOMContentLoaded'));
 const trigger=page.startsWith('answers/')?d.querySelector('#temple-history figure > a'):d.querySelector('[data-topic-study="art-study/the-living-christ.html"]');
 assert(trigger);trigger.dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true,button:0}));
 const panel=d.querySelector('.fc-topic-artwork-detail');assert(panel&&panel.hasAttribute('open'));
 const links=[...panel.querySelectorAll('a')];
 assert(!links.some(a=>a.href.includes('unrelated-sentinel')),'Never guess picture destination from first page-wide link');
 assert(links.some(a=>a.hasAttribute('data-topic-art-continue')),'Continue Lesson retained');
 assert(links.some(a=>a.hasAttribute('data-full-image-viewer')),'Full-size retained');
 assert(links.some(a=>a.hasAttribute('data-topic-art-source')),'Scripture/source retained');
 if(page.startsWith('birth'))assert(links.some(a=>a.getAttribute('href')==='art-study/the-living-christ.html'&&a.textContent==='Explore The Living Christ study'),'Explicit relevant study route and specific label retained');
 assert(d.querySelector('#next-study a'),'Authored page onward navigation remains');dom.window.close();
}
console.log('ILLUSTRATED NAVIGATION runtime PASS: no guessed unrelated subject; explicit study, sources, full-size and lesson return retained.');
