/* Synthetic classification only; it does not run a browser or prove providers. */
'use strict';
const assert=require('node:assert/strict'),{classify}=require('./world_provider_browser_diagnostic');
const ok={denied:false,pageErrors:0,failedRequests:0,badResponses:0,openfreemapResponses:1,mapterhornResponses:1,sourcesLoaded:true,rendererLoaded:true,statusHidden:true,canvasVisible:true};
assert.equal(classify(ok),'PASS');
for(const field of ['sourcesLoaded','rendererLoaded','statusHidden','canvasVisible','openfreemapResponses','mapterhornResponses'])assert.equal(classify({...ok,[field]:false}),'FAIL',field);
for(const field of ['pageErrors','failedRequests','badResponses'])assert.equal(classify({...ok,[field]:1}),'FAIL',field);
assert.equal(classify({...ok,error:'failure'}),'FAIL');assert.equal(classify({...ok,denied:true}),'DENIED');assert.equal(classify({}),'FAIL');
console.log('PASS: synthetic provider-report classification, including incomplete, errors and denial.');
