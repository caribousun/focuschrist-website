const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.attributes={}; this.value=''; }
  setAttribute(k,v){ this.attributes[k]=v; }
  appendChild(e){this.children.push(e);return e;}
  insertBefore(e){this.children.unshift(e);}
  querySelector(){return null;}
  focus(){this.focused=true;}
}
function run(query, existing='') {
  const card=new Element('article'), input=new Element('textarea'),body=new Element('body'), head=new Element('head');input.value=existing;
  const doc={readyState:'complete',head,body,documentElement:new Element('html'),createElement:t=>new Element(t),getElementById:id=>id==='userInput'?input:null,querySelector:s=>s==='.ask-study-card'?card:null};
  const location={href:'https://focuschrist.com/ask.html'+query,origin:'https://focuschrist.com',search:query};
  vm.runInNewContext(fs.readFileSync('art-ask-context.js','utf8'),{document:doc,window:{location,setTimeout:f=>f()},URL,URLSearchParams});
  const context=card.children[0]; return {input,body,context,back:context?.children.find(e=>e.tag==='a')};
}
for(const section of ['life-of-christ','book-of-mormon','prayer-and-revelation','hope-in-trials','restoration-and-history','temples-and-family','love-and-service']){
 const x=run('?'+new URLSearchParams({watch:'Video study',topic:'prayer',return:'/watch.html?ignored=yes#'+section}));
 assert.equal(x.back.href,'/watch.html#'+section);assert.equal(x.back.textContent,'Return to Watch study');assert(x.input.value.includes('prayer'));assert(!x.input.value.includes('artwork'));assert.equal(x.body.children.length,0,'No floating overlay for Watch');
}
for(const value of ['https://evil.example/watch.html#love-and-service','javascript:alert(1)','/art.html#love-and-service','/watch.html#missing']){
 assert.equal(run('?'+new URLSearchParams({watch:'Video',return:value})).back.href,'/watch.html#watch-topics');
}
const raw=run('?'+new URLSearchParams({watch:'<img src=x onerror=alert(1)>',topic:'prayer'}));assert.equal(raw.context.children[0].children[1].textContent,'<img src=x onerror=alert(1)>');
assert.equal(run('?watch=Video','My own question').input.value,'My own question');
const art=run('?'+new URLSearchParams({art:'Watch hero',return:'/watch.html?hero=1'}));assert.equal(art.back.href,'/watch.html?hero=1');assert.equal(art.back.textContent,'Return to this artwork');assert(art.input.value.includes('artwork'));assert.equal(art.body.children.length,1);
const birth = run('?' + new URLSearchParams({art:'Mary lays her newborn Son in a manger',topic:'The birth of Jesus Christ',return:'/birth-of-christ.html?hero=1'}));
assert.equal(birth.back.href, '/birth-of-christ.html?hero=1');
assert(birth.input.value.includes('The birth of Jesus Christ'));
assert.equal(run('?' + new URLSearchParams({art:'Birth artwork',return:'https://evil.example/birth-of-christ.html?hero=1'})).back.href, 'art.html?art=Birth%20artwork');
assert.equal(run('').context,undefined);
const heroes = JSON.parse(fs.readFileSync('docs/sitewide-artwork-review.json', 'utf8')).heroes;
assert.equal(heroes.length, 19, 'Exercise every reviewed replacement hero');
for (const hero of heroes) {
 const ask = new URL(hero.ask, 'https://focuschrist.com');
 const destination = ask.searchParams.get('return');
 assert.equal(destination, '/' + hero.page + '?hero=1');
 const result = run(ask.search);
 assert.equal(result.back.href, destination, hero.key + ': hero return must preserve its page');
 assert.equal(result.body.children[0].href, destination, hero.key + ': persistent hero return must agree');
 assert.equal(run('?' + new URLSearchParams({art:hero.title, return:'https://evil.example' + destination})).back.href, 'art.html?art=' + encodeURIComponent(hero.title));
}
for (const destination of ['/atonement.html?hero=1', '/joseph-smith-likeness.html?hero=1']) {
 assert.equal(run('?' + new URLSearchParams({art:'Existing hero',return:destination})).back.href, destination);
}
const studyReturns = [
 ['/answers/faith-in-jesus-christ-during-trials.html#scripture-study', 'Strength while the burden remains'],
 ['/answers/look-unto-me-doctrine-and-covenants-6-36.html#every-thought', 'Immediately Jesus reached for him'],
 ['/birth-of-christ.html#word-made-flesh', 'John points his disciples toward Christ'],
 ['/book-of-mormon-evidences.html#alma-36', 'Alma and Helaman'],
 ['/church-history.html#relief-society-organization', 'Practical care'],
 ['/come-follow-me.html#study-practice', 'Learning through service']
];
for (const [destination, title] of studyReturns) {
 const [pagePath, fragment] = destination.slice(1).split('#');
 assert(fs.readFileSync(pagePath, 'utf8').includes('id="' + fragment + '"'), 'Regression return must name a real study anchor');
 const result = run('?' + new URLSearchParams({art:title, topic:title, return:destination}));
 assert.equal(result.back.href, destination, 'Context card must preserve the own-page anchor');
 assert.equal(result.body.children[0].href, destination, 'Persistent return must agree');
 assert(result.input.value.includes(title));
}
for (const destination of ['https://evil.example/answers/faith-in-jesus-christ-during-trials.html#scripture-study', '//evil.example/come-follow-me.html#study-pattern', 'javascript:alert(1)', '/not-a-study.html#scripture-study', '/answers/faith-in-jesus-christ-during-trials.html#%3Cscript%3E']) {
 assert.equal(run('?' + new URLSearchParams({art:'Study', return:destination})).back.href, 'art.html?art=Study', 'Unsafe or unknown destination must fall back');
}
assert.equal(run('?' + new URLSearchParams({art:'Study',return:'/answers/faith-in-jesus-christ-during-trials.html?redirect=https://evil.example#scripture-study'})).back.href, '/answers/faith-in-jesus-christ-during-trials.html#scripture-study');
assert.equal(run('?' + new URLSearchParams({art:'Gallery',return:'/art.html?art=Gallery#art-grid'})).back.href, 'art.html?art=Gallery#art-grid', 'Keep original gallery selection and anchor');
assert.equal(run('?' + new URLSearchParams({art:'Home',return:'/index.html?artwork=home-come-and-see#study'})).back.href, '/index.html?artwork=home-come-and-see', 'Keep approved Home artwork routing');
console.log('Watch context runtime QA PASSED: section returns, external/invalid URL rejection, safe text, retained question, artwork regression, no automatic submission.');
