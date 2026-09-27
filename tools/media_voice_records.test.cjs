const {test}=require('node:test');
const assert=require('node:assert/strict');
const {extractRecords}=require('./media_voice_records.js');
test('audit includes later assigned dialog paragraphs without running page code',()=>{
 const s=`    const records = {one:{title:'First',paragraphs:['A person listens.']}};
 Object.assign(records,{two:{title:'Second',paragraphs:['Let this imagined encounter teach you.']}});
    const script = document.currentScript;
 throw new Error('Visitor runtime must not execute');`;
 const records=extractRecords(s);assert.equal(Object.keys(records).length,2);
 assert.equal(records.two.paragraphs[0],'Let this imagined encounter teach you.');
});
test('changed record boundary fails closed',()=>assert.throws(()=>extractRecords('const renamed={};'),/boundaries changed/));
test('malformed record fails closed',()=>assert.throws(()=>extractRecords(`    const records = {one:{title:'First'}};
    const script = document.currentScript;`),/Incomplete public hero record/));
