const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),cp=require('node:child_process');
const root=path.join(__dirname,'..'),file='timelines/life-of-christ-journey-map.html';
function data(html){const context={};vm.runInNewContext(html.match(/var STOPS = \[[\s\S]*?\n\];/)[0],context);return JSON.parse(JSON.stringify(context.STOPS));}
const current=data(fs.readFileSync(path.join(root,file),'utf8')),original=data(cp.execFileSync('git',['show','c1f3c2d4f984d23cd6df60269c77163be66034a3:'+file],{cwd:root,encoding:'utf8'}));
assert.equal(current.length,38);assert.deepEqual(current.slice(0,29),original.slice(0,29),'First29 source records remain exact');
for(const i of [29,30]){assert.equal(current[i].desc,original[i].desc);assert.equal(current[i].lat,null);assert.equal(current[i].lng,null);assert.equal(current[i].unlocated,true);}
const added=current.slice(31);assert(added.every(s=>s.phase==='restoration'&&s.witnessLocation&&s.source.startsWith('https://')));assert.deepEqual(added.map(s=>s.date),['Spring 1820','16 February 1832','18 March 1833','21 January 1836','3 April 1836','1898','3 October 1918']);
assert(added[2].desc.includes('1883')&&added[2].desc.includes('contemporary minutes'),'Later recollection attribution preserved');assert(added[5].desc.includes('LeRoi')&&added[5].desc.includes('Allie'),'Snow transmission attributed');assert(added[6].desc.includes('not a new earthly visit')&&added[6].desc.includes('body lay in the tomb'),'Vision date differs from ministry witnessed');
console.log('PASS38 Life records: original29 unchanged, Americas unlocated with narratives intact,7 sourced/dated/attributed witness experiences. Rendering and internal Americas map remain separate.');
