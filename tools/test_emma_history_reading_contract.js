'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM}=require('jsdom'),contract=require('./emma_history_reading_contract');
const root=path.resolve(__dirname,'..');let positive=0,negative=0;
for(const owner of contract.owners){
 const dom=new JSDOM(fs.readFileSync(path.join(root,owner),'utf8')),parsed=contract.inspect(dom.window.document);contract.validate(owner,parsed);positive++;
 for(const [key,value] of [['history',false],['readingFirst',false],['heroes',1],['openings',0],['openings',2],['bodies',0],['directories',0],['summaries',2]]){const bad={...parsed,[key]:value};assert.throws(()=>contract.validate(owner,bad),assert.AssertionError);negative++;}
 for(const file of ['connected-study.css','history-stories.css'])for(const kind of ['missing','duplicate','version']){const bad=JSON.parse(JSON.stringify(parsed)),i=bad.links.findIndex(x=>x.includes(file));if(kind==='missing')bad.links.splice(i,1);if(kind==='duplicate')bad.links.push(bad.links[i]);if(kind==='version')bad.links[i]=bad.links[i].replace(/\?v=.*/,'?v=unknown');assert.throws(()=>contract.validate(owner,bad),assert.AssertionError);negative++;}
 assert.throws(()=>contract.validate('history/unknown.html',parsed),assert.AssertionError);negative++;dom.window.close();
}
const old=['history/eleazer-miller.html','history/emma-hale-smith.html','history/john-rowe-moyle.html','history/john-tanner.html'],all=[...old,...contract.owners];assert.deepEqual(contract.partition(all,contract.owners),old);positive++;
for(const [histories,validated] of [[all.slice(0,-1),contract.owners],[[...all,all[0]],contract.owners],[all,contract.owners.slice(1)],[all,[...contract.owners,contract.owners[0]]]]){assert.throws(()=>contract.partition(histories,validated),assert.AssertionError);negative++;}
assert.notDeepEqual(contract.partition([...all,'history/unknown.html'],contract.owners).sort(),[...old].sort(),'Unknown owner remains visible to unchanged old exact-set assertion');negative++;
console.log(`PASS reading-first history contract: ${positive} positives/${negative} negative fixtures; actual five parsed source documents`);
