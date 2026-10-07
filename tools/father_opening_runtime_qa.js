// DOM state regression; browser geometry is verified independently.
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const {JSDOM,VirtualConsole}=require('jsdom');
const source=fs.readFileSync('site-common.js','utf8');
const functions=source.slice(source.indexOf('    function initOpeningInvitation('),source.indexOf('    function initExternalLinks('));
const dom=new JSDOM(fs.readFileSync('answers/god-our-heavenly-father.html','utf8'),{url:'https://focuschrist.com/answers/god-our-heavenly-father.html',runScripts:'outside-only',virtualConsole:new VirtualConsole()});
const w=dom.window,doc=w.document,listeners=[];
const media={matches:true,addEventListener:(name,fn)=>listeners.push(fn)};
w.matchMedia=()=>media;w.requestAnimationFrame=fn=>{fn();return 1;};w.cancelAnimationFrame=()=>{};
const expected='What does it mean to know God as our Father? Read about His love through scripture and the experiences of people who sought Him, then bring your own questions to the study.';
const hero=doc.querySelector('.fc-topic-opening .fc-visual-hero');const heroMarkup=hero.outerHTML;
let unified=false;
function check(label){
 const guides=[...doc.querySelectorAll('p.fc-page-intro-copy')].filter(p=>p.textContent===expected);assert.equal(guides.length,1,label+': one exact authored guide');
 assert.equal(guides[0].textContent,expected);assert.equal(guides[0].hidden,false);assert.equal(guides[0].closest('[hidden]'),null);
 assert.equal([...doc.querySelectorAll('p')].filter(p=>p.textContent===expected).length,1,label+': no duplicate guide');
 assert.equal(doc.querySelectorAll('.fc-opening-explanation,.fc-father-opening-guide').length,0,label+': no obsolete or optional duplicate');
 assert.equal(hero.outerHTML,heroMarkup,label+': artwork markup remains locked');
 assert(guides[0].closest(unified?'[data-unified-opening],.fc-unified-opening-continuation':'.fc-topic-opening'),label+': paragraph remains in the opening reading flow');
}
w.innerWidth=390;w.innerHeight=650;w.eval(functions+'\ninitMobileOpening();');check('initial390x650');
for(const height of [700,800,650]){w.innerHeight=height;w.dispatchEvent(new w.Event('resize'));check('resize'+height);w.scrollY=360;w.dispatchEvent(new w.Event('scroll'));check('scroll'+height);w.scrollY=0;}
doc.documentElement.style.fontSize='200%';w.dispatchEvent(new w.Event('resize'));check('enlarged text');
media.matches=false;listeners.forEach(fn=>fn());check('desktop');media.matches=true;listeners.forEach(fn=>fn());check('phone again');
w.dispatchEvent(new w.Event('pageshow'));check('restored page');
// Exercise the actual shared retention code with controlled rectangles. These
// fixtures prove DOM order/state, not measured browser typography or geometry.
let cueBottom=0;
const nativeRect=w.HTMLElement.prototype.getBoundingClientRect;
w.HTMLElement.prototype.getBoundingClientRect=function(){return this.classList.contains('fc-unified-continue')?{top:cueBottom-44,bottom:cueBottom,left:0,right:100,width:100,height:44,x:0,y:cueBottom-44}:nativeRect.call(this);};
w.eval(fs.readFileSync('unified-opening.js','utf8'));
doc.dispatchEvent(new w.Event('DOMContentLoaded'));unified=true;check('unified fits');
assert(doc.querySelector('[data-unified-opening] p.fc-page-intro-copy'),'Guide initially remains in opening');
cueBottom=900;w.innerHeight=568;w.dispatchEvent(new w.Event('resize'));check('unified retained');
const retained=doc.querySelector('#fc-opening-retained');
assert(retained.querySelector('p.fc-page-intro-copy'),'Oversized guide is retained rather than lost');
assert.equal(doc.querySelector('.fc-unified-continue').getAttribute('href'),'#fc-opening-retained','Continue reaches the retained explanation');
const children=[...retained.children];
assert(children.findIndex(x=>x.matches('.fc-topic-subtitle'))<children.findIndex(x=>x.matches('.fc-page-intro-copy')),'Original subtitle remains before the explanation');
cueBottom=0;w.innerHeight=844;w.dispatchEvent(new w.Event('resize'));check('unified restored');
assert(doc.querySelector('[data-unified-opening] p.fc-page-intro-copy'),'Guide returns when space permits');
console.log('FATHER OPENING PASS: exact copy once, hero lock, initial/resize/scroll/enlarged/desktop/mobile/pageshow and unified retain/restore reading order. Geometry requires browser evidence.');
w.close();
