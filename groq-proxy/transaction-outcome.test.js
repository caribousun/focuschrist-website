import assert from 'node:assert/strict';
import { unsupportedJoinedTransactionOutcomes as check } from './src/transaction-outcome.js';
const evidence = content => [{content}];
const source = 'Church leaders attempted to sell the Nauvoo Temple and other Church properties to help the poor, but they were unable to find a buyer for the temple.';
const regression = 'Church members covenanted to help poorer migrants, and leaders tried unsuccessfully to sell the Nauvoo Temple and other Church properties for that purpose.';
assert.deepEqual(check(regression,evidence(source)),[{transaction:'sale',unsupportedObjects:['other Church properties']}]);
assert.deepEqual(check('Their efforts to sell the Nauvoo Temple and other Church properties were unsuccessful.',evidence(source)),[{transaction:'sale',unsupportedObjects:['other Church properties']}]);
assert.deepEqual(check('They were unable to sell the Nauvoo Temple and other Church properties.',evidence(source)),[{transaction:'sale',unsupportedObjects:['other Church properties']}]);
assert.deepEqual(check('They attempted to sell the Nauvoo Temple and other Church properties, but could not find a buyer for the temple.',evidence(source)),[]);
assert.deepEqual(check('They tried unsuccessfully to sell the Nauvoo Temple.',evidence(source)),[]);
assert.deepEqual(check(regression,evidence('They were unable to find a buyer for the temple and other Church properties.')),[]);
assert.deepEqual(check(regression,evidence('They failed to sell the temple. Other Church properties remained unsold.')),[]);
assert.deepEqual(check(regression,evidence(source+' They were unable to buy other Church properties.')),[{transaction:'sale',unsupportedObjects:['other Church properties']}]);
assert.deepEqual(check(regression,evidence(source+' The other Church properties were damaged by fire.')),[{transaction:'sale',unsupportedObjects:['other Church properties']}]);
for (const denied of ['It is false that they failed to sell the other Church properties.', 'They were not unable to sell the other Church properties.']) assert.deepEqual(check(regression,evidence(source+' '+denied)),[{transaction:'sale',unsupportedObjects:['other Church properties']}]);
assert.deepEqual(check('It is false that they failed to sell the temple and other Church properties.',evidence(source)),[]);
assert.deepEqual(check('They were not unable to sell the temple and other Church properties.',evidence(source)),[]);
assert.deepEqual(check('They could not purchase the blue wagon and red wagon.',evidence('They failed to purchase the blue wagon. They purchased the red wagon.')),[{transaction:'purchase',unsupportedObjects:['red wagon']}]);
assert.deepEqual(check('They could not purchase the blue wagon and red wagon.',evidence('They failed to purchase the blue wagon and red wagon.')),[]);
console.log('PASS: joined transaction failures require separate outcome support, preserve attempted lists, specific failures, supported joins and distinct transaction types.');

// Exercise the real approval -> audit -> repair -> audit -> final gate. Even
// two provider approvals cannot publish the original overextended predicate.
const {default:worker}=await import('./src/index.js');
const savedFetch=globalThis.fetch;
const broken=regression+' Church leaders directed that effort.';
const corrected='Church leaders organized the effort to raise money through property sales for poorer travelers. The account names the temple among their offerings and specifically reports that no purchaser was secured for that building.';
try {
  for(const repaired of [true,false]) {
    let calls=0;
    globalThis.fetch=async(url,options={})=>{
      if(String(url).endsWith('/chat/completions')) {
        calls++;
        const prompt=JSON.parse(options.body).messages.map(message=>message.content).join('\n');
        if(calls===3) {
          assert(prompt.includes('deterministic transaction-outcome check'));
          assert(prompt.includes('other Church properties'));
        }
        const answer=repaired&&calls>=3?corrected:broken;
        return new Response(JSON.stringify({choices:[{message:{content:JSON.stringify({approved:true,answer,source_indexes:[1]})}}]}),{headers:{'Content-Type':'application/json'}});
      }
      assert(!String(url).endsWith('/responses'));
      return new Response('<p>Between February and September 1846, thousands of Latter-day Saints departed Nauvoo, Illinois. The previous fall, Church leaders had developed plans for a large exodus. Church members covenanted to assist the poor among them to make the trek. '+source+' Most evacuees made their way to Council Bluffs in western Iowa, while many remained scattered in the surrounding area for months or years. The pioneer exodus began in February 1846.</p>',{headers:{'Content-Type':'text/html'}});
    };
    const response=await worker.fetch(new Request('https://worker.test',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'pioneers',focuschrist_profile:'faith-study',messages:[{role:'user',content:'When did the pioneer exodus begin?'},{role:'assistant',content:'We were discussing the departure from Nauvoo.'},{role:'user',content:'When did it end?'}]})}),{OPENAI_API_KEY:'offline-fixture'});
    const payload=await response.json();
    assert.equal(calls,repaired?4:3,JSON.stringify(payload));
    assert.equal(payload.focuschrist_source_integrity_verified,repaired,JSON.stringify(payload));
    if(repaired) assert.equal(payload.choices[0].message.content,corrected);
    else assert.equal(payload.focuschrist_verifier_publication_failure,'unsupported-joined-transaction-outcome');
  }
}finally{globalThis.fetch=savedFetch;}
console.log('PASS: joined-outcome repair stays within four provider calls; unchanged unsupported answer fails final publication.');
