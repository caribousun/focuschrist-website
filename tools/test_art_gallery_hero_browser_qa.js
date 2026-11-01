/* Synthetic boundary tests; no browser or external network is used. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {safeReadAt,assertHosted}=require('./art_gallery_hero_browser_qa');
const base=fs.mkdtempSync(path.join(os.tmpdir(),'gallery-diagnostic-boundary-'));
try{
 fs.writeFileSync(path.join(base,'public.txt'),'public');fs.mkdirSync(path.join(base,'nested'));fs.symlinkSync(path.join(base,'public.txt'),path.join(base,'nested','link'));
 const allowed=new Set(['/public.txt','/.git/config','/../outside','/nested/link']);
 assert.equal(safeReadAt(base,allowed,'public.txt').toString(),'public');
 for(const name of ['.git/config','../outside','nested/link','unknown.txt'])assert.throws(()=>safeReadAt(base,allowed,name));
 const hosted={GITHUB_ACTIONS:'true',GITHUB_EVENT_NAME:'pull_request',GITHUB_HEAD_REF:'albert/art-gallery-hero-20261030',GITHUB_RUN_ID:'123'};
 assert.doesNotThrow(()=>assertHosted(hosted));
 for(const [key,value] of [['GITHUB_ACTIONS','false'],['GITHUB_EVENT_NAME','push'],['GITHUB_HEAD_REF','other'],['GITHUB_RUN_ID','not-a-run']])assert.throws(()=>assertHosted({...hosted,[key]:value}));
 console.log('Gallery diagnostic boundary and hosted-scope synthetic tests PASS');
}finally{fs.rmSync(base,{recursive:true,force:true});}
