'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),binding=require('./timeline_51_destination_bindings');
const raw=fs.readFileSync(path.join(__dirname,'../docs/reviews/timeline-51-destination-bindings.json'));
const rows=binding.read(raw);assert.equal(rows.length,51);
// Changing a target along with its associated row must not make a cross-event
// swap appear valid merely because the destination section exists.
for(const mutate of [r=>{[r[0].target,r[1].target]=[r[1].target,r[0].target];},r=>{r[0].event='Different event';},r=>{r.pop();},r=>{r[0].original_source='https://example.invalid/';}]){
 const changed=JSON.parse(raw);mutate(changed);assert.throws(()=>binding.read(Buffer.from(JSON.stringify(changed,null,2)+'\n')),/Unreviewed event destination bindings/);
}
console.log('PASS: exact 51-event bindings reject target swaps and altered identities, source records, and coverage.');
