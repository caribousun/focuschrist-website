'use strict';
const assert = require('node:assert/strict');
const EMMA_ROUTES = Object.freeze([
  '/history/emma-elect-lady.html', '/history/emma-hymns.html',
  '/history/emma-winter-crossing.html', '/history/emma-relief-society.html',
  '/history/emma-last-testimony.html'
]);
function historicalBoundaryRoutes(routes, historicalRoutes) {
  assert.equal(routes.length, 137, '132 historical routes plus five Emma stories');
  assert.equal(new Set(routes).size, 137, 'No duplicate current routes');
  for (const route of EMMA_ROUTES) assert(routes.includes(route), 'Missing exact Emma route: '+route);
  const historical = routes.filter(route => !EMMA_ROUTES.includes(route));
  assert.equal(historical.length, 132);
  assert.equal(historicalRoutes.length, 130);
  assert.equal(new Set(historicalRoutes).size, 130);
  assert.deepEqual(historical.map(p=>p==='/'?'index.html':p.replace(/^\//,'')).sort(),
    [...historicalRoutes,'history/emma-hale-smith.html','timelines/world-and-scripture-timeline.html'].sort(),
    'Exact historical routes plus reviewed Emma hub and World and Scripture additions');
  return historical;
}
module.exports = {EMMA_ROUTES, historicalBoundaryRoutes};
