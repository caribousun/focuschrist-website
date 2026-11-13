/* Measure frame cadence before steady-state motion checks; never infer smooth
 * startup from this readiness measurement or relax motion/settling assertions. */
'use strict';
async function waitForFrameCadence(page){
 const result=await page.evaluate(()=>new Promise(resolve=>{
  const start=performance.now(),gaps=[];let previous=start,consecutive=0,done=false;
  const snapshot=ready=>({ready,elapsed:performance.now()-start,gaps,stableFrames:consecutive,maximumGap:gaps.length?Math.max(...gaps):null});
  const timeout=setTimeout(()=>{done=true;resolve(snapshot(false));},10000);
  function frame(){
   if(done)return;
   const now=performance.now(),gap=now-previous;previous=now;gaps.push(gap);
   consecutive=gap<=50?consecutive+1:0;
   if(consecutive>=12){done=true;clearTimeout(timeout);resolve(snapshot(true));return;}
   requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
 }));
 if(!result.ready){
  const error=new Error('Browser never supplied 12 consecutive frames within 50ms; motion sampling unavailable');
  error.readiness=result;throw error;
 }
 return result;
}
module.exports={waitForFrameCadence};
