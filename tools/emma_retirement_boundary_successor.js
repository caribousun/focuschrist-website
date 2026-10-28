'use strict';
// Candidate successor: separate current-route partition; historical inputs are
// still verified exactly. No historical test or evidence record is rewritten.
const assert=require('node:assert/strict');
const CURRENT=Object.freeze(['/history/emma-hymns.html','/history/emma-winter-crossing.html','/history/emma-relief-society.html','/history/emma-last-testimony.html']);
const RETIRED='/history/emma-elect-lady.html';
function historicalBoundaryRoutes(routes,historicalRoutes){
 assert.equal(routes.length,136,'132 established plus four current story routes');assert.equal(new Set(routes).size,136,'duplicate route');
 assert(!routes.includes(RETIRED),'compatibility route is not canonical');for(const route of CURRENT)assert(routes.includes(route),'missing current '+route);
 const historical=routes.filter(route=>!CURRENT.includes(route));assert.equal(historical.length,132);
 assert.equal(historicalRoutes.length,130);assert.equal(new Set(historicalRoutes).size,130);
 assert.deepEqual(historical.map(p=>p==='/'?'index.html':p.replace(/^\//,'')).sort(),[...historicalRoutes,'history/emma-hale-smith.html','timelines/world-and-scripture-timeline.html'].sort(),'all unrelated and reviewed hub/timeline routes exact');
 return historical;
}
module.exports={CURRENT,RETIRED,historicalBoundaryRoutes};
