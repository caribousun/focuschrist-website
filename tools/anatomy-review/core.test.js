const assert = require('node:assert/strict');
const { validate, buildPrompt } = require('./core');
function sample() {
  return {version:1,candidate:{sha256:'a'.repeat(64)},reference:{description:'Two complete posed arms',source:'Owner reference'},reviewer:'Independent reviewer',decision:'pending',ownerApproval:{status:'pending',evidence:''},contacts:[{from:'peter-left',to:'christ-right',target:'forearm',description:'Wraps the other forearm; separate wrists'}],checks:Object.fromEntries(['whole_chain','hand_ownership','digits_and_thumb','contact_and_overlap','identity_preserved','reference_compared'].map(k=>[k,true])),limbs:['peter-left','christ-right'].map((id,i)=>({id,person:i?'Christ':'Peter',side:i?'right':'left',surface:'dorsal',occluded:{},points:{shoulder:{x:.1,y:.9},elbow:{x:.2,y:.65},wrist:{x:.3,y:.4},index_mcp:{x:.4,y:.25},little_mcp:{x:.2,y:.25},thumb_base:{x:.42,y:.34}}}))};
}
assert.equal(validate(sample()).status,'ready_for_visual_review');
assert.equal(validate(sample(),['a'.repeat(64)]).status,'blocked');
let r=sample();r.limbs[0].points.thumb_base.x=.12;assert.match(validate(r).errors.join(' '),/little-finger side/);
r=sample();r.limbs[0].side='screen-left';assert.match(validate(r).errors.join(' '),/anatomical left or right/);
r=sample();r.limbs[0].points.wrist={...r.limbs[0].points.elbow};assert.match(validate(r).errors.join(' '),/same point/);
r=sample();delete r.limbs[0].points.thumb_base;assert.equal(validate(r).status,'blocked');r.limbs[0].occluded.thumb_base='Behind the other wrist; pose reference establishes attachment';assert.equal(validate(r).status,'ready_for_visual_review');assert.ok(validate(r).warnings.some(x=>x.includes('occluded')));
r=sample();r.contacts[0].to='missing';assert.equal(validate(r).status,'blocked');
r=sample();r.contacts[0].to=r.contacts[0].from;assert.match(validate(r).errors.join(' '),/same limb/);
r=sample();r.decision='rejected';assert.equal(validate(r).status,'blocked');
r=sample();r.ownerApproval={status:'approved',evidence:''};assert.equal(validate(r).status,'blocked');
r=sample();r.limbs[0].points.wrist.x=1.5;assert.equal(validate(r).status,'blocked');
r=sample();r.checks.hand_ownership=false;assert.equal(validate(r).status,'blocked');
console.log('PASS: review completeness, wrong thumb-side annotation, anatomical laterality, separate joints/contact ownership, occlusion, rejection hashes and owner-evidence boundaries. Not a pixel anatomy certification.');

// Hash case does not let a renamed, rejected image become a new candidate.
r=sample();r.candidate.sha256='A'.repeat(64);assert.equal(validate(r,['a'.repeat(64)]).status,'blocked');
assert.equal(validate(sample(),[{sha256:'A'.repeat(64)}]).status,'blocked');
r=sample();r.limbs[0]=null;assert.equal(validate(r).status,'blocked');
r=sample();r.contacts[0]=null;assert.equal(validate(r).status,'blocked');
// A leg uses its own complete chain and cannot generate an arm-only prompt.
r=sample();r.contacts=[];r.limbs=[{id:'walker-left',person:'Walker',side:'left',type:'leg',points:{hip:{x:.4,y:.2},knee:{x:.4,y:.45},ankle:{x:.45,y:.75},heel:{x:.4,y:.8},big_toe:{x:.55,y:.86},little_toe:{x:.48,y:.89}},occluded:{}}];
assert.equal(validate(r).status,'ready_for_visual_review');
assert.match(buildPrompt(r),/anatomical left leg/);assert.match(buildPrompt(r),/hip → knee/);assert.doesNotMatch(buildPrompt(r),/Trace shoulder/);
r.limbs[0].points.ankle={...r.limbs[0].points.knee};assert.match(validate(r).errors.join(' '),/distinct leg joints/);
r.limbs[0].points.ankle={x:.45,y:.75};delete r.limbs[0].points.heel;assert.equal(validate(r).status,'blocked');
r.limbs[0].occluded.heel='Hidden by the shoe; full pose reference still requires visual inspection';assert.equal(validate(r).status,'ready_for_visual_review');
assert.ok(validate(r).warnings.some(w=>w.includes('cannot certify')));
console.log('PASS: hash-case rejection, malformed annotation handling and leg-specific joints, occlusion and prompts.');
