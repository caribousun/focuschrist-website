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
const expected='Explore scripture about our Heavenly Father, His love, and our relationship with Him. Follow the passages and questions throughout the study.';
const hero=doc.querySelector('.fc-topic-opening .fc-visual-hero');const heroMarkup=hero.outerHTML;
function check(label){
 const guides=doc.querySelectorAll('.fc-father-opening-guide');assert.equal(guides.length,1,label+': one authored guide');
 assert.equal(guides[0].textContent,expected);assert.equal(guides[0].hidden,false);assert.equal(guides[0].closest('[hidden]'),null);
 assert.equal(doc.querySelectorAll('.fc-topic-opening .fc-opening-explanation').length,0,label+': no optional duplicate');
 assert.equal(hero.outerHTML,heroMarkup,label+': artwork markup remains locked');
 assert(guides[0].closest('.fc-topic-opening'),label+': paragraph remains in opening');
}
w.innerWidth=390;w.innerHeight=650;w.eval(functions+'\ninitMobileOpening();');check('initial390x650');
for(const height of [700,800,650]){w.innerHeight=height;w.dispatchEvent(new w.Event('resize'));check('resize'+height);w.scrollY=360;w.dispatchEvent(new w.Event('scroll'));check('scroll'+height);w.scrollY=0;}
doc.documentElement.style.fontSize='200%';w.dispatchEvent(new w.Event('resize'));check('enlarged text');
media.matches=false;listeners.forEach(fn=>fn());check('desktop');media.matches=true;listeners.forEach(fn=>fn());check('phone again');
w.dispatchEvent(new w.Event('pageshow'));check('restored page');
console.log('FATHER OPENING PASS: initial650, resize700/800/650, scroll, enlarged text, desktop/mobile and pageshow preserve exact copy once and hero markup. Geometry requires browser evidence.');
w.close();
