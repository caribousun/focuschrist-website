'use strict';
const assert = require('node:assert/strict');
const {EMMA_ROUTES, historicalBoundaryRoutes} = require('./emma_content_boundary_routes');
function selfTest(routes, historicalRoutes) {
  const before = JSON.stringify([routes, historicalRoutes]);
  const actual = historicalBoundaryRoutes(routes, historicalRoutes);
  assert.equal(actual.length,132);
  for (const route of EMMA_ROUTES) {
    assert.throws(()=>historicalBoundaryRoutes(routes.filter(p=>p!==route),historicalRoutes));
    assert.throws(()=>historicalBoundaryRoutes([...routes,route],historicalRoutes));
    assert.throws(()=>historicalBoundaryRoutes(routes.map(p=>p===route?route+'?drift=1':p),historicalRoutes));
  }
  assert.throws(()=>historicalBoundaryRoutes([...routes,'/unknown.html'],historicalRoutes));
  assert.throws(()=>historicalBoundaryRoutes(routes.map(p=>p===EMMA_ROUTES[0]?'/unknown.html':p),historicalRoutes));
  const old = actual.find(p=>p!=='/');
  assert.throws(()=>historicalBoundaryRoutes(routes.filter(p=>p!==old),historicalRoutes));
  assert.throws(()=>historicalBoundaryRoutes(routes.map(p=>p===old?'/old-owner-drift.html':p),historicalRoutes));
  assert.throws(()=>historicalBoundaryRoutes(routes,[...historicalRoutes.slice(1),historicalRoutes[1]]));
  assert.throws(()=>historicalBoundaryRoutes(routes,historicalRoutes.map((p,i)=>i===0?'unknown-old.html':p)));
  assert.equal(JSON.stringify([routes,historicalRoutes]),before,'Inputs unchanged');
  return {positive:1,negative:21};
}
module.exports = {selfTest};
if (require.main===module) {
  const fs=require('node:fs'),path=require('node:path');
  const root=path.resolve(__dirname,'..');
  const routes=[...fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname);
  const historical=JSON.parse(fs.readFileSync(path.join(root,'docs/unified-opening-inventory.json'),'utf8')).pages.map(p=>p.path);
  console.log(JSON.stringify(selfTest(routes,historical)));
}
