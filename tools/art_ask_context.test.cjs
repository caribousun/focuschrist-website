const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('jsdom');
const code = fs.readFileSync(require('node:path').resolve(__dirname, '../art-ask-context.js'), 'utf8');
function open(query, draft = '') {
  const dom = new JSDOM('<!doctype html><html><head></head><body><form class="ask-study-card"><textarea id="userInput"></textarea></form></body></html>', { url:'https://focuschrist.com/ask.html?' + query, runScripts:'outside-only' });
  dom.actions = { submit:0, fetch:0, send:0 };
  dom.window.document.querySelector('form').addEventListener('submit',e=>{e.preventDefault();dom.actions.submit++;});
  dom.window.fetch = () => { dom.actions.fetch++; return Promise.resolve({}); };
  dom.window.sendMessage = () => { dom.actions.send++; };
  dom.window.document.querySelector('textarea').value = draft;
  dom.window.setTimeout = () => 0;
  dom.window.eval(code);
  dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded'));
  return dom;
}
function values(dom) {const d=dom.window.document;return {value:d.querySelector('textarea').value,link:d.querySelector('[data-focuschrist-art-return]')?.getAttribute('href'),label:d.querySelector('[data-focuschrist-art-return]')?.textContent,context:d.querySelector('aside')?.textContent,float:!!d.querySelector('[data-focuschrist-art-return-float]')};}
test('CFM topic is visible, editable, returns to CFM, and never submits',()=>{
 const dom=open('topic=Isaiah+40-49&return=%2Fcome-follow-me.html');const v=values(dom);
 assert.match(v.value,/Isaiah 40-49/);assert.match(v.context,/Continuing your study/);assert.equal(v.link,'/come-follow-me.html');assert.equal(v.label,'Return to your study');assert.equal(v.float,false);
 const input=dom.window.document.querySelector('textarea');input.value='My own question';assert.equal(input.value,'My own question');assert.deepEqual(dom.actions,{submit:0,fetch:0,send:0});dom.window.close();
});
test('explicit q and already typed draft take precedence',()=>{
 for(const [q,draft,want] of [['topic=Isaiah&q=My+question','','My question'],['topic=Isaiah&q=URL+question','Typed draft','Typed draft'],['topic=Isaiah&search-question=Search+question','','Search question'],['topic=Isaiah&search-question=Search+question','Search question','Search question']]){const d=open(q,draft);assert.equal(values(d).value,want);d.window.close();}
});
test('returns allow known pages and plain fragments, drop queries and reject unsafe paths',()=>{
 for(const [raw,want] of [['/church-history.html#guided-reflections','/church-history.html#guided-reflections'],['/come-follow-me.html?x=secret#reading','/come-follow-me.html#reading'],['https://evil.example/come-follow-me.html','/answers.html'],['//evil.example/come-follow-me.html','/answers.html'],['/unknown.html','/answers.html'],['/come-follow-me.html#bad%20fragment','/come-follow-me.html'],['javascript:alert(1)','/answers.html']]){const d=open('topic=Study&return='+encodeURIComponent(raw));assert.equal(values(d).link,want);d.window.close();}
});
test('topic without return offers accurate fallback; empty topic does not create context',()=>{
 let d=open('topic=Faith');assert.equal(values(d).label,'Browse study topics');assert.equal(values(d).link,'/answers.html');d.window.close();
 d=open('topic=+++');assert.equal(values(d).context,undefined);d.window.close();
});

test('Holy Ghost study, supporting artwork and hero return to the exact approved route',()=>{
 for(const [query,raw,want] of [
  ['study=Holy+Ghost&topic=learning+to+recognize+the+Holy+Ghost','/answers/holy-ghost.html#holy-ghost-or-me','/answers/holy-ghost.html#holy-ghost-or-me'],
  ['art=The+Father+the+Son+and+the+Spirit','/answers/holy-ghost.html#picture-hg-baptism','/answers/holy-ghost.html#picture-hg-baptism'],
  ['art=Holy+Ghost+hero','/answers/holy-ghost.html?hero=1&discard=yes','/answers/holy-ghost.html?hero=1']
 ]) {const d=open(query+'&return='+encodeURIComponent(raw));assert.equal(values(d).link,want);assert.ok(values(d).value.length);assert.deepEqual(d.actions,{submit:0,fetch:0,send:0});d.window.close();}
 for(const raw of ['https://evil.example/answers/holy-ghost.html#holy-ghost-or-me','/answers/holy-ghost-other.html#holy-ghost-or-me','/answers/holy-ghost.html/extra']) {
  const d=open('topic=Holy+Ghost&return='+encodeURIComponent(raw));assert.equal(values(d).link,'/answers.html');d.window.close();
 }
 const d=open('topic=Holy+Ghost&q=My+own+question&return=%2Fanswers%2Fholy-ghost.html%23holy-ghost-or-me');assert.equal(values(d).value,'My own question');d.window.close();
});
test('Plan of Salvation study, supporting artwork and hero return to the exact approved route',()=>{
 for(const [query,raw,want] of [
  ['study=Plan+of+Salvation&topic=learning+to+recognize+the+Plan+of+Salvation','/answers/plan-of-salvation.html#today','/answers/plan-of-salvation.html#today'],
  ['art=The+Father+the+Son+and+the+Spirit','/answers/plan-of-salvation.html#picture-pos-belong','/answers/plan-of-salvation.html#picture-pos-belong'],
  ['art=Plan+of+Salvation+hero','/answers/plan-of-salvation.html?hero=1&discard=yes','/answers/plan-of-salvation.html?hero=1']
 ]) {const d=open(query+'&return='+encodeURIComponent(raw));assert.equal(values(d).link,want);assert.ok(values(d).value.length);assert.deepEqual(d.actions,{submit:0,fetch:0,send:0});d.window.close();}
 for(const raw of ['https://evil.example/answers/plan-of-salvation.html#today','/answers/plan-of-salvation-other.html#today','/answers/plan-of-salvation.html/extra']) {
  const d=open('topic=Plan+of+Salvation&return='+encodeURIComponent(raw));assert.equal(values(d).link,'/answers.html');d.window.close();
 }
 const d=open('topic=Plan+of+Salvation&q=My+own+question&return=%2Fanswers%2Fplan-of-salvation.html%23today');assert.equal(values(d).value,'My own question');d.window.close();
});
test('Emma topic returns to her reflection without submitting and rejects unsafe destinations',()=>{
 for(const [raw,want] of [
  ['/history/emma-hale-smith.html#reflect','/history/emma-hale-smith.html#reflect'],
  ['/history/emma-hale-smith.html?discard=yes#reflect','/history/emma-hale-smith.html#reflect'],
  ['/history/emma-hale-smith.html#bad%20fragment','/history/emma-hale-smith.html'],
  ['https://evil.example/history/emma-hale-smith.html#reflect','/answers.html'],
  ['/history/emma-hale-smith-other.html#reflect','/answers.html']
 ]) {
  const d=open('topic=Emma+Hale+Smith&return='+encodeURIComponent(raw));
  const v=values(d);assert.equal(v.link,want);assert.match(v.context,/Emma Hale Smith/);
  assert.equal(v.label,want==='/answers.html'?'Browse study topics':'Return to your study');
  assert.deepEqual(d.actions,{submit:0,fetch:0,send:0});d.window.close();
 }
});
test('existing artwork, Watch, evidences and covenant contracts remain intact',()=>{
 for(const [q,label,pattern,float] of [['art=The+Sower&topic=Faith','Return to this artwork',/artwork "The Sower"/,true],['watch=Prayer&topic=Prayer','Return to Watch study',/What do the scriptures/,false],['study=Book+of+Mormon+Evidences&topic=Witnesses','Return to Evidences study',/scholarly interpretations/,false],['study=Abrahamic+Covenant&topic=Abraham','Return to Covenant study',/Help me understand/,false]]){const d=open(q);const v=values(d);assert.equal(v.label,label);assert.match(v.value,pattern);assert.equal(v.float,float);d.window.close();}
});
