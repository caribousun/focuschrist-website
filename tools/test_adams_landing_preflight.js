'use strict';
// Static JSDOM source preflight only; chart rendering is checked by the hosted suite.
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {validateLanding}=require('./adams_chart_browser_qa');
const root=path.resolve(__dirname,'..'),source=fs.readFileSync(path.join(root,'timeline.html'),'utf8');
const actual=validateLanding(root);assert.equal(actual.path,'timeline.html');assert.equal(actual.validation,'current Timeline source semantics; rendered behavior checked separately');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'adams-landing-'));
try{
 const manifest='docs/owner-integration-contract/source-manifest.json';
 fs.mkdirSync(path.join(temp,path.dirname(manifest)),{recursive:true});fs.copyFileSync(path.join(root,manifest),path.join(temp,manifest));
 const check=content=>{fs.writeFileSync(path.join(temp,'timeline.html'),content);return validateLanding(temp);};
 assert.doesNotThrow(()=>check(source+' '));
 const layout=source.replace('fc-timeline-choice__body','fc-timeline-choice__body layout-v2');
 assert.notEqual(layout,source);assert.doesNotThrow(()=>check(layout));
 for(const [old,value] of [
  ['latter-day-saint-church-history-timeline.html','wrong.html'],
  ['church-history-grove.webp','wrong.webp'],
  ['Explore the story of the Restoration.','Changed copy.'],
  ['id="adams-1881"','id="wrong"']
 ]){assert(source.includes(old));assert.throws(()=>check(source.replace(old,value)),assert.AssertionError);}
 const archived=fs.readFileSync(path.join(root,'docs/timeline-selector/historical-c910.txt'),'utf8');
 assert.throws(()=>check(archived),assert.AssertionError);
 const manifestPath=path.join(temp,manifest);fs.appendFileSync(manifestPath,' ');
 assert.throws(()=>check(source),assert.AssertionError);
}finally{fs.rmSync(temp,{recursive:true,force:true});}
console.log('PASS current landing preflight, layout tolerance and link/asset/copy/anchor/historical/manifest negatives');
