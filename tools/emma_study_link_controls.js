'use strict';
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const recordBytes=require('node:fs').readFileSync(require('node:path').join(__dirname,'../docs/emma-study-link-additions.json'));
assert.equal(crypto.createHash('sha256').update(recordBytes).digest('hex'),'60cbcea5ec6b9c871d0a7028a59d16048f59af2e8ed45d487907fada749016e1','Exact reviewed Emma control manifest');
const records=JSON.parse(recordBytes).pages;
const owners=Object.freeze(['history/emma-elect-lady.html','history/emma-hymns.html','history/emma-winter-crossing.html','history/emma-relief-society.html','history/emma-last-testimony.html']);
const sourceSelector='.fc-study-visual-sources a:not(.fc-button--primary)';
assert.deepEqual(Object.keys(records).sort(),[...owners].sort());
function validate(doc,owner,selectors,source){
 assert(owners.includes(owner),'Unknown Emma owner');
 const record=records[owner];
 assert.equal(crypto.createHash('sha256').update(source).digest('hex'),record.source_sha256,'Current Emma source binding');
 assert.equal(selectors[0],sourceSelector);
 for(const selector of selectors)assert.equal(doc.querySelectorAll(selector).length,selector===sourceSelector?1:0,owner+': exact control family '+selector);
 const node=doc.querySelector(sourceSelector);
 assert.equal(node.tagName,'A');
 assert.deepEqual(Object.fromEntries([...node.attributes].map(a=>[a.name,a.value])),record.attrs,owner+': exact source attributes');
 assert.equal(node.textContent.trim().replace(/\s+/g,' '),record.label,owner+': exact source label');
 assert.equal(node.closest('figure')?.getAttribute('data-topic-art'),record.figure,owner+': exact source figure');
 for(const selector of ['.watch-topic-index a','nav[aria-label="Pioneer study sections"] a','.bom-story-directory a'])assert.equal(doc.querySelectorAll(selector).length,0,owner+': no numbered-navigation contribution');
}
function historicalInventory(inventory,validated){
 assert.deepEqual([...validated].sort(),[...owners].sort(),'All and only five unique validated owners');
 assert.equal(inventory.canonical_pages,137);
 const result=JSON.parse(JSON.stringify(inventory));result.canonical_pages-=5;
 for(const [selector,entry] of Object.entries(result.selectors)){
  const added=entry.pages.filter(p=>owners.includes(p));
  assert.deepEqual(added.sort(),selector===sourceSelector?[...owners].sort():[],'Exact new selector owners');
  if(selector===sourceSelector){assert(entry.count>=5);entry.count-=5;entry.pages=entry.pages.filter(p=>!owners.includes(p));}
 }
 for(const key of Object.keys(result.numbered_navigation))assert(!owners.some(p=>key.startsWith(p+' ')),'Unexpected Emma numbered navigation');
 return result;
}
module.exports={owners,sourceSelector,validate,historicalInventory};
