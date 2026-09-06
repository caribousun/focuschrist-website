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
assert.equal(run('').context,undefined);
console.log('Watch context runtime QA PASSED: section returns, external/invalid URL rejection, safe text, retained question, artwork regression, no automatic submission.');
