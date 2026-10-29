'use strict';
// Actual current 138 routes first; predecessor tests use only explicitly named
// exact historical files and old canonical projection, never live UI claims.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const s=require('./emma_retirement_navigation_successor'),old=require('./test_owner_integration_navigation');
const routes=[...read('sitemap.xml').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname);
s.assertCurrent(routes,read,JSDOM);
const prior=s.priorReader(read),predecessorRoutes=[...routes,'/history/emma-elect-lady.html'];
old.selfTest(predecessorRoutes,prior,JSDOM);
assert.throws(()=>s.assertCurrent([...routes,routes[0]],read,JSDOM));
assert.throws(()=>s.assertCurrent([...routes,'/history/emma-elect-lady.html'],read,JSDOM));
assert.throws(()=>s.assertCurrent(routes.map((x,i)=>i===0?'/unknown.html':x),read,JSDOM));
for(const route of Object.keys(s.CURRENT))assert.throws(()=>s.assertCurrent(routes,p=>read(p)+(p===route?' ':'') ,JSDOM));
console.log('PASS: actual 138-route/source successor; unchanged owner navigation tests ran against exact prior fixtures only. Browser/release approval remains separate.');
