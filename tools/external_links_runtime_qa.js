const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('site-common.js','utf8');
const fn = source.slice(source.indexOf('    function initExternalLinks()'),source.indexOf("    document.addEventListener('DOMContentLoaded', function () {\n        initExternalLinks();"));
function link(href) { const a={href}; return {getAttribute:k=>a[k]||null,setAttribute:(k,v)=>a[k]=v,matches:()=>true,querySelectorAll:()=>[],a}; }
const external=link('https://www.churchofjesuschrist.org/study/scriptures/nt/john/3');
const internal=link('atonement.html');const mail=link('mailto:test@example.org');const same=link('https://focuschrist.com/ask.html');const lookalike=link('https://focuschrist.com.example.org/');
const events={};let observer;
const document={body:{},querySelectorAll:()=>[external,internal,mail,same,lookalike],addEventListener:(t,fn)=>events[t]=fn};
vm.runInNewContext(fn+'initExternalLinks();',{URL,document,window:{location:{href:'https://focuschrist.com/atonement.html',origin:'https://focuschrist.com'}},MutationObserver:class{constructor(fn){observer=fn}observe(){}}});
assert.equal(external.a.target,'_blank');assert.match(external.a.rel,/noopener/);assert.match(external.a.rel,/noreferrer/);assert.equal(lookalike.a.target,'_blank');
for(const a of [internal,mail,same])assert.equal(a.a.target,undefined);
const dynamic=link('https://example.org/resource');observer([{type:'childList',addedNodes:[dynamic]}]);assert.equal(dynamic.a.target,'_blank');
const changed=link('https://example.org/changed');observer([{type:'attributes',target:changed}]);assert.equal(changed.a.target,'_blank');
const clicked=link('https://example.org/click');let prevented=false;events.click({target:{closest:()=>clicked},preventDefault:()=>prevented=true});assert.equal(clicked.a.target,'_blank');assert.equal(prevented,false,'Do not interfere with scripture/art dialogs');
console.log('EXTERNAL LINK QA PASS: static/dynamic links, changed href, native navigation and reader compatibility');
