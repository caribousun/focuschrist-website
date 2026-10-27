'use strict';
const assert=require('node:assert/strict');
const {owners,sourceSelector,validate,historicalInventory}=require('./emma_study_link_controls');
module.exports=function selfTest(JSDOM,read,selectors){
 let negative=0;
 for(const owner of owners){
  const source=read(owner),original=new JSDOM(source);validate(original.window.document,owner,selectors,source);original.window.close();
  for(const kind of ['missing','duplicate','href','label','target','rel','figure','other-family','numbered','wrong-owner','source']){
   const dom=new JSDOM(source),doc=dom.window.document,node=doc.querySelector(sourceSelector);
   if(kind==='missing')node.remove();
   if(kind==='duplicate')node.after(node.cloneNode(true));
   if(['href','target','rel'].includes(kind))node.setAttribute(kind,'changed');
   if(kind==='label')node.textContent+=' changed';
   if(kind==='figure')node.closest('figure').setAttribute('data-topic-art','changed');
   if(kind==='other-family')doc.body.insertAdjacentHTML('beforeend','<div class="fc-resource-next"><a>Extra</a></div>');
   if(kind==='numbered')doc.body.insertAdjacentHTML('beforeend','<div class="watch-topic-index"><a>01Extra</a></div>');
   assert.throws(()=>validate(doc,kind==='wrong-owner'?'unknown.html':owner,selectors,kind==='source'?source+' ':source));negative++;dom.window.close();
  }
 }
 // Actual current pages supply the additive portion; old inventory remains independent.
 const old=JSON.parse(read('docs/study-link-control-inventory.json')),current=JSON.parse(JSON.stringify(old));
 current.canonical_pages+=5;current.selectors[sourceSelector].count+=5;
 current.selectors[sourceSelector].pages.push(...owners);current.selectors[sourceSelector].pages.sort();
 assert.deepEqual(historicalInventory(current,owners),old);
 for(const owner of owners){assert.throws(()=>historicalInventory(current,owners.filter(p=>p!==owner)));negative++;}
 assert.throws(()=>historicalInventory(current,[...owners,owners[0]]));negative++;
 assert.throws(()=>historicalInventory(current,[...owners,'unknown.html']));negative++;
 const drift=JSON.parse(JSON.stringify(current));drift.selectors[sourceSelector].count++;
 assert.throws(()=>assert.deepEqual(historicalInventory(drift,owners),old));negative++;
 return {actualOwnerPositives:5,negative};
};
