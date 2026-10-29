'use strict';
// DRAFT current-source successor. The old manifest remains byte-pinned and
// untouched; this validates the actual four current documents rather than
// relabeling the old Elect Lady record as if still live.
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const CURRENT=Object.freeze(['history/emma-hymns.html','history/emma-winter-crossing.html','history/emma-relief-society.html','history/emma-last-testimony.html']);
const RETIRED='history/emma-elect-lady.html';
const SOURCE_HASH=Object.freeze({
 'history/emma-hymns.html':'55ee8b1a9b57154ca074282f2b6f44c19d77d15a63abd5adcde3286174625087',
 'history/emma-winter-crossing.html':'a2c6003789eaaf4458bb3f431943c2d4602908b19324054ef8ca9f0aab30a417',
 'history/emma-relief-society.html':'e90e7b25239973e2488f32e57482fd5cfbdabb6a7f3f1746599aded9cd546ebb',
 'history/emma-last-testimony.html':'ff608df4a3bb994d29834e253daac97b1721ecf2b3209a621e284f16ca91eb70'});
const sourceSelector='.fc-study-visual-sources a:not(.fc-button--primary)';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function recordsFromPredecessor(raw){
 assert.equal(sha(raw),'0288b172a41de26b01c59b8de642f65c7fac77aac30396e76ca709475d8c1922','historical control record drift');
 const pages=JSON.parse(raw).pages;assert.deepEqual(Object.keys(pages).sort(),[...CURRENT,RETIRED].sort(),'predecessor owners drift');return pages;
}
function validate(doc,owner,selectors,source,predecessorRaw){
 assert(CURRENT.includes(owner),'unknown/retired owner');assert.equal(sha(source),SOURCE_HASH[owner],'unreviewed actual current source');
 const record=recordsFromPredecessor(predecessorRaw)[owner];assert.equal(selectors[0],sourceSelector);
 for(const selector of selectors)assert.equal(doc.querySelectorAll(selector).length,selector===sourceSelector?1:0,owner+': control family');
 const node=doc.querySelector(sourceSelector);assert.equal(node.tagName,'A');assert.deepEqual(Object.fromEntries([...node.attributes].map(a=>[a.name,a.value])),record.attrs);
 assert.equal(node.textContent.trim().replace(/\s+/g,' '),record.label);const figure=node.closest('figure');assert(figure,'missing reference figure');assert.equal(figure.getAttribute('data-artwork-reference'),record.figure);assert.equal(figure.getAttribute('data-linked-picture-reference'),record.figure);assert.equal(figure.getAttribute('data-topic-art'),null,'story must not be a second artwork owner');const ownerLink=figure.querySelector('div > a');assert(ownerLink);assert.equal(ownerLink.getAttribute('href'),'emma-hale-smith.html#picture-'+record.figure,'reference must link to the hub owner');
 for(const selector of ['.watch-topic-index a','nav[aria-label="Pioneer study sections"] a','.bom-story-directory a'])assert.equal(doc.querySelectorAll(selector).length,0,owner+': no numbered-navigation contribution');
}
function historicalInventory(inventory,validated){
 assert.deepEqual([...validated].sort(),[...CURRENT].sort(),'all four unique current owners');assert.equal(inventory.canonical_pages,136);
 const result=JSON.parse(JSON.stringify(inventory));result.canonical_pages-=4;
 for(const [selector,entry] of Object.entries(result.selectors)){
  assert.equal(new Set(entry.pages).size,entry.pages.length,'duplicate selector-page owner');assert(!entry.pages.includes(RETIRED),'retired route in current inventory');const added=entry.pages.filter(p=>CURRENT.includes(p));
  assert.deepEqual(added.sort(),selector===sourceSelector?[...CURRENT].sort():[],'exact selector contribution');
  if(selector===sourceSelector){assert(entry.count>=4);entry.count-=4;entry.pages=entry.pages.filter(p=>!CURRENT.includes(p));}
 }
 for(const key of Object.keys(result.numbered_navigation))assert(![...CURRENT,RETIRED].some(p=>key.startsWith(p+' ')),'unexpected Emma numbered nav');
 return result;
}
module.exports={CURRENT,RETIRED,SOURCE_HASH,sourceSelector,recordsFromPredecessor,validate,historicalInventory};
