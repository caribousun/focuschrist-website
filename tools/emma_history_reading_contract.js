'use strict';
const assert=require('node:assert/strict');
const owners=Object.freeze(['history/emma-elect-lady.html','history/emma-hymns.html','history/emma-winter-crossing.html','history/emma-relief-society.html','history/emma-last-testimony.html']);
const historyVersion='20261009-directory-alignment-1',connectedVersion='20261008-promotion-spacing-1';
function inspect(doc=document){return {history:!!doc.querySelector('.fc-life-reading'),links:[...doc.querySelectorAll('link[rel="stylesheet"]')].map(n=>n.getAttribute('href')),readingFirst:doc.body.classList.contains('fc-emma-study'),heroes:doc.querySelectorAll('.fc-life-hero').length,openings:doc.querySelectorAll('.fc-life-reading.fc-life-opening').length,bodies:doc.querySelectorAll('.fc-life-reading:not(.fc-life-opening)').length,directories:doc.querySelectorAll('.fc-life-directory').length,summaries:doc.querySelectorAll('.fc-life-directory > summary').length};}
function validate(route,parsed){
 assert(owners.includes(route),'Unknown reading-first history owner');
 assert.equal(parsed.history,true);assert.equal(parsed.readingFirst,true,'Explicit reading-first story type');assert.equal(parsed.heroes,0,'Reading-first story must not masquerade as hero');assert.equal(parsed.openings,1);assert(parsed.bodies>0);assert.equal(parsed.directories,1);assert.equal(parsed.summaries,1);
 for(const [file,version] of [['history-stories.css',historyVersion],['connected-study.css',connectedVersion]]){
  const links=parsed.links.filter(n=>new URL(n,'https://focuschrist.com/'+route).pathname.endsWith('/'+file));assert.equal(links.length,1,route+' required unique '+file);assert.equal(new URL(links[0],'https://focuschrist.com/'+route).searchParams.get('v'),version,route+' required '+file+' version');
 }
}
function partition(histories,validated){assert.equal(new Set(histories).size,histories.length,'Duplicate history owner');assert.deepEqual([...validated].sort(),[...owners].sort(),'All five typed owners validated exactly once');assert(owners.every(p=>histories.includes(p)),'Missing typed history owner');return histories.filter(p=>!owners.includes(p));}
module.exports={owners,historyVersion,connectedVersion,inspect,validate,partition};
