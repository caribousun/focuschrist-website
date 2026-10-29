'use strict';
// Validate actual viewport screenshot samples against the decoded image at the
// same screen coordinates. This checks painting, not likeness or composition.
const assert=require('node:assert/strict');
function inspect(samples){
 assert(Array.isArray(samples)&&samples.length>=36,'insufficient unobscured image pixels');
 let error=0,lo=255,hi=0;
 for(const sample of samples){
  assert(Array.isArray(sample)&&sample.length===6&&sample.every(n=>Number.isFinite(n)&&n>=0&&n<=255),'invalid screenshot sample');
  for(let i=0;i<3;i++){error+=Math.abs(sample[i]-sample[i+3]);lo=Math.min(lo,sample[i]);hi=Math.max(hi,sample[i]);}
 }
 const meanAbsoluteError=error/(samples.length*3);
 assert(hi-lo>=12,'source samples lack enough contrast to establish painting');
 assert(meanAbsoluteError<=40,`captured pixels differ from decoded image: mean absolute error ${meanAbsoluteError.toFixed(2)}`);
 return {samples:samples.length,sourceRange:hi-lo,meanAbsoluteError:Number(meanAbsoluteError.toFixed(3))};
}
module.exports={inspect};
