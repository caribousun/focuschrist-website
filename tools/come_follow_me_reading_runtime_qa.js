const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {readingParts,weeks}=require('../come-follow-me.js');
class Node{
 constructor(tag,text=''){this.tag=tag;this.children=[];this.attrs={};this._text=text;this.classList={contains:()=>false};}
 set textContent(text){this._text=text;this.children=[];}
 get textContent(){return this._text+this.children.map(n=>n.textContent).join('');}
 setAttribute(key,value){this.attrs[key]=value;}
 append(...nodes){this.children.push(...nodes);}
 appendChild(node){this.append(node);return node;}
 replaceChildren(...nodes){this._text='';this.children=nodes;}
 *walk(){yield this;for(const n of this.children)yield* n.walk();}
}
const reading=new Node('div'),schedule=new Node('div');
const document={querySelector:s=>s==='[data-cfm-current-reading]'?reading:s==='[data-cfm-schedule]'?schedule:null,querySelectorAll:()=>[],createElement:t=>new Node(t),createTextNode:t=>new Node('#text',t)};
const NativeDate=Date;
class ReviewDate extends NativeDate{constructor(...args){super(...(args.length?args:['2026-09-08T12:00:00']));}}
vm.runInNewContext(fs.readFileSync(require.resolve('../come-follow-me.js'),'utf8'),{document,Date:ReviewDate,location:{}});
const current=[...reading.walk()];
assert.equal(current.filter(n=>n.tag==='details').length,4);
assert.equal(reading.attrs['role'],'group');
assert.equal(reading.attrs['aria-label'],'Scripture reading: '+weeks[36][3]);
assert.match(fs.readFileSync(require.resolve('../come-follow-me.css'),'utf8'),/\[data-cfm-current-reading\],\.cfm-schedule-reading\{display:flex;flex-wrap:wrap;gap:8px/);
assert.ok(!reading.children.some(n=>n.tag==='#text'&&n.textContent.includes(';')),'No stranded separators');
assert.equal(current.filter(n=>n.tag==='a').length,13);
assert.equal(current.find(n=>n.textContent==='Proverbs 2'&&n.tag==='a').href,'https://www.churchofjesuschrist.org/study/scriptures/ot/prov/2?lang=eng');
assert.equal(current.find(n=>n.textContent==='Proverbs 22'&&n.tag==='a').attrs['aria-label'],'Read Proverbs 22');
assert.deepEqual(readingParts('Psalms 102–3; 110; 116–19; 127–28; 135–39; 146–50').map(p=>p.chapters),[[102,103],[110],[116,117,118,119],[127,128],[135,136,137,138,139],[146,147,148,149,150]]);
for(const week of weeks){
 const parts=readingParts(week[3]);assert.equal(parts.map(p=>p.label).join('; '),week[3]);
 for(const part of parts){if(!['Easter','Christmas','Introduction to the Old Testament'].includes(part.label))assert.ok(part.key,part.label+' must resolve to scripture');}
}
const all=[...schedule.walk()];
assert.equal(all.filter(n=>n.tag==='li').length,52);
const lessons=all.filter(n=>n.tag==='a'&&n.href.includes('/study/manual/'));
assert.equal(lessons.length,52);
for(const a of all.filter(n=>n.tag==='a'))assert.equal([...a.walk()].filter(n=>n.tag==='a').length,1,'No nested scripture/lesson anchors');
for(const lesson of lessons)assert.ok(![...lesson.walk()].some(n=>n.className==='cfm-schedule-reading'),'Reading controls must be separate from lesson links');
console.log('PASS: 52 unchanged assignments, exact chapter choices, abbreviated Psalms ranges, accessible inherited book labels, separate lesson links, no nested anchors.');
// The evergreen initial HTML must still become the right weekly lesson at rollover.
for(const [day,lesson] of [['2026-09-27','39'],['2026-09-28','40']]){
 const date=new Node('span'),title=new Node('h2'),assignment=new Node('div');
 const links=[new Node('a'),new Node('a')], ask=new Node('a');
 const nodes={'.cfm-week a[href^="ask.html"]':ask,'[data-cfm-current-date]':date,'[data-cfm-current-title]':title,'[data-cfm-current-reading]':assignment};
 const doc={querySelector:s=>nodes[s]||null,querySelectorAll:s=>s==='[data-cfm-current-lesson]'?links:[],createElement:t=>new Node(t),createTextNode:t=>new Node('#text',t)};
 class RolloverDate extends NativeDate{constructor(...args){super(...(args.length?args:[day+'T12:00:00']));}}
 vm.runInNewContext(fs.readFileSync(require.resolve('../come-follow-me.js'),'utf8'),{document:doc,Date:RolloverDate,location:{}});
 const week=weeks.find(w=>w[4]===lesson);
 const askURL=new URL(ask.href,'https://focuschrist.com/');
 assert.equal(askURL.searchParams.get('return'),'/come-follow-me.html#this-week');
 assert.equal(askURL.hash,'#ask-question');
 assert.ok(askURL.searchParams.get('topic').includes(week[3]));
 assert.equal(date.textContent,week[2]);
 assert.ok(title.textContent && !title.textContent.includes('Find this week'));
 assert.equal(assignment.attrs['aria-label'],'Scripture reading: '+week[3]);
 for(const link of links)assert.equal(link.href,'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-old-testament-2026/'+lesson+'?lang=eng');
}
console.log('PASS: Sunday/Monday weekly rollover updates both official lesson routes and the reading.');

const fallback=fs.readFileSync(require.resolve('../come-follow-me.html'),'utf8');
assert.ok(fallback.includes('&amp;return=%2Fcome-follow-me.html%23this-week#ask-question'));
console.log('PASS: weekly Ask preserves current reading and returns to this-week; composer anchor retained.');

require('./cfm_palette_contract.test.js');
