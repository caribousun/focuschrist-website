const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {assertCurrentRootControllers,assertRootControllerContracts,discoverCriticalAssets}=require('./live_production_ask_qa.js');
const roots=()=>Object.fromEntries(['ask.html','pioneers.html','church-history.html'].map(p=>[p,fs.readFileSync(p,'utf8')]));
test('actual release roots satisfy production controller contract before deployment',()=>{
 const graph=discoverCriticalAssets();
 assert(graph.assets.includes('ask-experience.js'));
 const live=roots();assertRootControllerContracts(live);
 const ref=live['ask.html'].match(/ask-experience\.js\?v=[^"']+/)[0];
 assert(graph.canonicalTargets.some(t=>t.path==='ask-experience.js'&&t.url===ref));
});
test('future release version is derived while the previously deployed revision is rejected',()=>{
 const old='<script src="ask-experience.js?v=old-release"></script>';
 const next='<script src="ask-experience.js?v=next-approved-release"></script>';
 assertCurrentRootControllers(next,'ask.html',['ask-experience.js'],next);
 assert.throws(()=>assertCurrentRootControllers(old,'ask.html',['ask-experience.js'],next),/production does not load/);
});
test('missing, additional stale, substituted and unversioned controllers fail closed',()=>{
 const expected='<script src="ask-experience.js?v=current"></script>';
 for(const actual of ['',expected+'<script src="ask-experience.js?v=stale"></script>',
  '<script src="art-ask-context.js?v=current"></script>','<script src="ask-experience.js"></script>']) {
  assert.throws(()=>assertCurrentRootControllers(actual,'ask.html',['ask-experience.js'],expected),/production does not load/);
 }
 assert.throws(()=>assertCurrentRootControllers(expected,'ask.html',['ask-experience.js'],''),/release root missing/);
 assert.throws(()=>assertCurrentRootControllers(expected,'ask.html',['ask-experience.js'],'<script src="ask-experience.js"></script>'),/release root missing/);
});
test('all required root controller identities remain mandatory',()=>{
 for(const [page,name] of [['ask.html','reviewed-ask-knowledge.js'],['ask.html','ask-experience.js'],['pioneers.html','pioneer-experience.js'],['church-history.html','church-history-experience.js']]) {
  const live=roots();live[page]=live[page].replaceAll(name,'missing-controller.js');
  assert.throws(()=>assertRootControllerContracts(live),/production does not load/);
 }
});
