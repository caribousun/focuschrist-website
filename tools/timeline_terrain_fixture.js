/* Hosted Leaflet tests simulate pixels while retaining the production credit row. */
'use strict';
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm'), assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../timeline-terrain.js'), 'utf8');
const context = {URL, document: {currentScript: {src: 'https://focuschrist.com/timeline-terrain.js'}}, window: {}};
vm.runInNewContext(source, context);
let credit;
context.window.FCTerrainLayer().addTo({attributionControl: {addAttribution(value) { credit = value; }}});
assert.equal(typeof credit, 'string', 'Fixture retains the actual facade attribution');
for (const url of ['https://openfreemap.org/', 'https://www.openmaptiles.org/', 'https://www.openstreetmap.org/copyright', 'https://mapterhorn.com/attribution/']) {
  assert(credit.includes('href="' + url + '"'), 'Production credit includes ' + url);
}
module.exports = "window.FCTerrainLayer=function(){return L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:" + JSON.stringify(credit) + "});};";
