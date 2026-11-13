'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm');
const {waitForFrameCadence}=require('./continue_motion_sampling');
function fakePage(gaps){return {evaluate:fn=>{
 let now=0,timer=null,cleared=false,used=0;
 const context={performance:{now:()=>now},setTimeout:callback=>{timer=callback;return 1},clearTimeout:()=>{cleared=true},requestAnimationFrame:callback=>{
  queueMicrotask(()=>{if(used<gaps.length){now+=gaps[used++];callback()}else if(!cleared&&timer)timer()});
 },Promise,Math,Error};
 return vm.runInNewContext('('+fn.toString()+')()',context);
}}}
(async()=>{
 const stable=await waitForFrameCadence(fakePage(Array(12).fill(16)));assert.equal(stable.stableFrames,12);assert.equal(stable.elapsed,192);
 const busy=await waitForFrameCadence(fakePage([103,255,100,...Array(6).fill(16),100,...Array(12).fill(16)]));
 assert.equal(busy.stableFrames,12);assert.equal(busy.gaps.length,22);assert.equal(busy.maximumGap,255);
 await assert.rejects(()=>waitForFrameCadence(fakePage(Array(30).fill(100))),error=>{assert.match(error.message,/sampling unavailable/);assert.equal(error.readiness.ready,false);assert.equal(error.readiness.gaps.length,30);assert.equal(error.readiness.maximumGap,100);assert.equal(error.readiness.elapsed,3000);return true;});
 await assert.rejects(()=>waitForFrameCadence(fakePage([])),error=>{assert.equal(error.readiness.gaps.length,0);assert.equal(error.readiness.maximumGap,null);return true;});
 console.log('PASS: stable frames required; stalls reset streak; persistent stall fails; diagnostic gaps preserved');
})().catch(e=>{console.error(e);process.exitCode=1});
