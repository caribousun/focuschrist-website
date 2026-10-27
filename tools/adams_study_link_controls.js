'use strict';
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const {ADAMS_ROUTE,assertAdamsSource,withoutAdamsCanonical}=require('./adams_standalone_navigation');
const owner=ADAMS_ROUTE.slice(1),landing='timeline.html';
const numbered=['.watch-topic-index a','nav[aria-label="Pioneer study sections"] a','.bom-story-directory a'];
const digest=s=>crypto.createHash('sha256').update(s).digest('hex');
function validate(doc,route,selectors,source,read){
 assert([owner,landing].includes(route),'Exact Adams source or existing landing only');
 if(route===owner)assertAdamsSource(ADAMS_ROUTE,source,read('tools/adams_chart_browser_qa.js'));
 else {
  assert.equal(digest(source),'fa3b12da544899f8935874508b9abe64b84b6fd2af1e5bfec8a368ce6a638578','Exact reviewed landing successor');
  const links=doc.querySelectorAll('a[href="timelines/adams-1881-chart.html"]');assert.equal(links.length,1);
  assert.equal(links[0].getAttribute('class'),'fc-button fc-button--primary');
  assert.equal(links[0].textContent,"Adams' 1881 Chart of History");
  assert(links[0].closest('nav[aria-label="Choose a timeline"]'));
 }
 for(const s of [...selectors,...numbered])assert.equal(doc.querySelectorAll(s).length,0,route+': no named or numbered control contribution '+s);
}
function beforeEmmaInventory(inventory,validated,routes,read){
 withoutAdamsCanonical(routes,read);
 assert.deepEqual([...validated].sort(),[owner,landing].sort(),'Both exact source and landing validated once');
 assert.equal(inventory.canonical_pages,138);
 for(const entry of Object.values(inventory.selectors))assert(!entry.pages.includes(owner)&&!entry.pages.includes(landing),'Unexpected Adams/landing named controls');
 for(const key of Object.keys(inventory.numbered_navigation))assert(![owner,landing].some(p=>key.startsWith(p+' ')),'Unexpected Adams/landing numbered controls');
 const result=JSON.parse(JSON.stringify(inventory));result.canonical_pages-=1;return result;
}
module.exports={owner,landing,numbered,validate,beforeEmmaInventory};
