'use strict';
// Keep the prior current story validator for each remaining owner. The former
// route is a compatibility document, never treated as a reading-first page.
const assert=require('node:assert/strict');
const CURRENT=Object.freeze(['history/emma-hymns.html','history/emma-winter-crossing.html','history/emma-relief-society.html','history/emma-last-testimony.html']);
const RETIRED='history/emma-elect-lady.html';
const historyVersion='20261009-directory-alignment-1',connectedVersion='20261008-promotion-spacing-1';
function inspect(doc=document){return {history:!!doc.querySelector('.fc-life-reading'),links:[...doc.querySelectorAll('link[rel="stylesheet"]')].map(n=>n.getAttribute('href')),readingFirst:doc.body.classList.contains('fc-emma-study'),heroes:doc.querySelectorAll('.fc-life-hero').length,openings:doc.querySelectorAll('.fc-life-reading.fc-life-opening').length,bodies:doc.querySelectorAll('.fc-life-reading:not(.fc-life-opening)').length,directories:doc.querySelectorAll('.fc-life-directory').length,summaries:doc.querySelectorAll('.fc-life-directory > summary').length};}
function validate(route,parsed,previous=require('./emma_history_reading_contract')){assert(CURRENT.includes(route),'unknown or retired story route');assert(previous&&typeof previous.validate==='function','missing prior exact validator');previous.validate(route,parsed);}
function partition(histories,validated){
 assert.equal(new Set(histories).size,histories.length,'duplicate route');assert(!histories.includes(RETIRED),'retired route cannot be canonical');
 assert.deepEqual([...validated].sort(),[...CURRENT].sort(),'all four current owners validated exactly once');assert(CURRENT.every(p=>histories.includes(p)),'missing current owner');
 return histories.filter(p=>!CURRENT.includes(p));
}
module.exports={CURRENT,owners:CURRENT,RETIRED,historyVersion,connectedVersion,inspect,validate,partition};
