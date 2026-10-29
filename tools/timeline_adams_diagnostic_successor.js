'use strict';
// Exact source projection only; this is not a review or release approval.
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const digest=value=>crypto.createHash('sha256').update(value).digest('hex');
const BEFORE='b90c19dd9f77c3966843b41d514319816a194deee86b87235909f6b2c742130c';
const AFTER='43f19fc23f4fd17e1c9fdb54003feab2885565c97b1a98abc6aefb092ec06944';
const MANIFEST='docs/timeline-controls-successor/adams-source-delta.json';
const MANIFEST_SHA='25cb8c9ca50d607f1bcef7dfb84ed560732397810dbea889a4d62c6fd9c2e4cb';
function restore(source,read){
 const raw=read(MANIFEST);assert.equal(digest(raw),MANIFEST_SHA,'Adams successor manifest changed');
 const record=JSON.parse(raw);assert.equal(record.schema,1);assert.equal(record.path,'timelines/adams-1881-chart.html');
 assert.equal(record.before_sha256,BEFORE);assert.equal(record.after_sha256,AFTER);assert.equal(digest(source),AFTER,'Unreviewed Adams successor source');
 assert.equal(record.changes.length,4);let bytes=Buffer.from(source);
 for(const item of [...record.changes].reverse()){
  const old=Buffer.from(item.before_b64,'base64'),next=Buffer.from(item.after_b64,'base64');
  assert(!old.equals(next));const offset=bytes.indexOf(next);assert(offset>=0);assert.equal(bytes.indexOf(next,offset+1),-1,'Adams successor context changed');
  bytes=Buffer.concat([bytes.subarray(0,offset),old,bytes.subarray(offset+next.length)]);
 }
 assert.equal(digest(bytes),BEFORE,'Adams predecessor mismatch');return bytes.toString('utf8');
}
module.exports={restore,BEFORE,AFTER};
