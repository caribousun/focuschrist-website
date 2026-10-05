const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),cp=require('node:child_process');
const root=path.join(__dirname,'..'),file='timelines/life-of-christ-journey-map.html';
function data(html){const context={};vm.runInNewContext(html.match(/var STOPS = \[[\s\S]*?\n\];/)[0],context);return JSON.parse(JSON.stringify(context.STOPS));}
const current=data(fs.readFileSync(path.join(root,file),'utf8')),original=data(cp.execFileSync('git',['show','c1f3c2d4f984d23cd6df60269c77163be66034a3:'+file],{cwd:root,encoding:'utf8'}));
// Exact independently reviewed Life19 source/prose corrections; all other original fields stay frozen.
const approvedCorrections = [
  [
    0,
    "scripture",
    "Luke 1:26 to 38",
    "Luke 1:26 to 38; Matthew 1:18 to 25"
  ],
  [
    2,
    "scripture",
    "Luke 2:1 to 20; Matthew 1:18 to 25",
    "Luke 2:1 to 20; Matthew 1:18 to 25; Matthew 2:1 to 12"
  ],
  [
    3,
    "scripture",
    "Luke 2:21 to 38",
    "Luke 2:21 to 38; Leviticus 12:2 to 8"
  ],
  [
    5,
    "scripture",
    "Luke 2:39 to 40, 51 to 52",
    "Luke 2:39 to 40, 51 to 52; Matthew 2:19 to 23"
  ],
  [
    11,
    "scripture",
    "Luke 4:16 to 30",
    "Luke 4:16 to 31; Matthew 4:13 to 16"
  ],
  [
    12,
    "scripture",
    "Matthew 4:13 to 16; Mark 1:21 to 34",
    "Matthew 4:13 to 22; Matthew 8:5 to 15; Mark 1:21 to 34"
  ],
  [
    14,
    "scripture",
    "John 6:1 to 14; Matthew 14:13 to 21",
    "Luke 9:10 to 17; John 6:1 to 35; Matthew 14:13 to 21"
  ],
  [
    15,
    "scripture",
    "Matthew 16:13 to 20",
    "Matthew 16:13 to 21"
  ],
  [
    17,
    "scripture",
    "Luke 18:35 to 43; Luke 19:1 to 10",
    "Mark 10:46 to 52; Luke 18:35 to 43; Luke 19:1 to 10"
  ],
  [
    17,
    "desc",
    "Entering and passing through Jericho, Jesus heals blind Bartimaeus who cries, Son of David, have mercy on me. He also calls Zacchaeus down from the sycamore tree and brings salvation to his house.",
    "At Jericho, Jesus heals blind Bartimaeus, who cries, Son of David, have mercy on me. He also calls Zacchaeus down from the sycamore tree and brings salvation to his house."
  ],
  [
    18,
    "scripture",
    "John 11:1 to 44",
    "John 11:1 to 53"
  ],
  [
    19,
    "scripture",
    "Matthew 21:1 to 11; Luke 19:28 to 44",
    "Matthew 21:1 to 11; Luke 19:28 to 44; John 12:12 to 15"
  ],
  [
    20,
    "scripture",
    "Matthew 21:12 to 17; Matthew 23",
    "Matthew 21:12 to 17; Matthew 23; Luke 19:47 to 48"
  ],
  [
    23,
    "scripture",
    "John 19:16 to 37; Luke 23:33 to 46",
    "John 18:12 to 40; John 19:1 to 37; Luke 23:1 to 46"
  ],
  [
    24,
    "scripture",
    "John 19:38 to 42; John 20:1 to 18; Matthew 28:1 to 10",
    "Matthew 27:57 to 60; John 19:38 to 42; John 20:1 to 18; Matthew 28:1 to 10; Mark 16:9"
  ],
  [
    26,
    "desc",
    "Jesus appears among His Apostles in a locked room, shows His hands and side, and breathes the Holy Ghost upon them. A week later He appears again for Thomas, who declares, My Lord and my God.",
    "Jesus appears among His Apostles in a locked room, shows His hands and side, and breathes on them, inviting them to receive the Holy Ghost. A week later He appears again for Thomas, who declares, My Lord and my God."
  ],
  [
    28,
    "scripture",
    "Luke 24:50 to 53; Acts 1:9 to 11",
    "Luke 24:50 to 53; Acts 1:3 to 12"
  ],
  [
    29,
    "scripture",
    "3 Nephi 11",
    "3 Nephi 8:5 to 23; 3 Nephi 11"
  ],
  [
    30,
    "scripture",
    "3 Nephi 12 to 26; 3 Nephi 17; 3 Nephi 19",
    "3 Nephi 12 to 26; 4 Nephi 1:1 to 5"
  ]
];
const reviewed=JSON.parse(JSON.stringify(original));
for(const [index,field,before,after] of approvedCorrections){assert.equal(reviewed[index][field],before,`Frozen baseline for stop ${index+1} ${field}`);reviewed[index][field]=after;}
assert.equal(current.length,38);assert.deepEqual(current.slice(0,29),reviewed.slice(0,29),'First29 source records match exact reviewed corrections; every other field remains frozen');
for(const i of [29,30]){assert.equal(current[i].desc,original[i].desc);assert.equal(current[i].scripture,reviewed[i].scripture);assert.equal(current[i].lat,null);assert.equal(current[i].lng,null);assert.equal(current[i].unlocated,true);}
const added=current.slice(31);assert(added.every(s=>s.phase==='restoration'&&s.witnessLocation&&s.source.startsWith('https://')));assert.deepEqual(added.map(s=>s.date),['Spring 1820','16 February 1832','18 March 1833','21 January 1836','3 April 1836','1898','3 October 1918']);
assert(added[2].desc.includes('1883')&&added[2].desc.includes('contemporary minutes'),'Later recollection attribution preserved');assert(added[5].desc.includes('LeRoi')&&added[5].desc.includes('Allie'),'Snow transmission attributed');assert(added[6].desc.includes('not a new earthly visit')&&added[6].desc.includes('body lay in the tomb'),'Vision date differs from ministry witnessed');
console.log('PASS38 Life records: original29 match reviewed source/prose corrections, Americas unlocated with narratives and reviewed sources intact,7 sourced/dated/attributed witness experiences. Rendering and internal Americas map remain separate.');
