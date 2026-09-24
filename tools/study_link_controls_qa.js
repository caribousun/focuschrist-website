/* Named study controls: DOM coverage plus positive/negative selector fixtures. */
const fs=require('fs'),path=require('path'),assert=require('assert');
const {JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const config=JSON.parse(read('docs/study-link-controls.json'));
const selectors=[...config.chip_selectors,...config.navigation_surface_selectors];
const css=read('site-system.css').split('/* BEGIN OWNER STUDY LINK CONTROLS')[1].split('/* END OWNER STUDY LINK CONTROLS */')[0];
for(const s of selectors) assert(css.includes('body.fc-site '+s),`Missing surface ${s}`);
for(const s of config.number_badges) assert(css.includes('body.fc-site '+s),`Missing number protection ${s}`);
assert(css.includes('--fc-study-control-min-height: 44px'));
assert(css.includes('white-space: nowrap;')&&css.includes('flex: 0 0 2.2em;'));
assert(css.includes('flex: 1 1 210px;')&&css.includes('flex-wrap: wrap;'));
assert(!/body\.fc-site\s+a\s*\{/.test(css),'Bare-anchor treatment prohibited');
const fixture=new JSDOM(`<body class="fc-site"><p><a id="prose" class="fc-inline-scripture">John 3:16</a></p><a id="home" class="fc-button">Home</a><div class="fc-study-visual-sources"><a id="source">Mark 7:24–30</a><a id="primary" class="fc-button--primary">Study</a></div><a id="internal" class="source-link source-link--internal">Ask</a><a id="external" class="source-link">Source</a><nav class="jj-local-nav fc-study-nav"><a id="chapter">Chapter</a></nav><nav class="watch-topic-index"><a id="watch"><span>02</span>Book of Mormon</a></nav></body>`).window.document;
for(const id of ['prose','home','primary','internal','chapter'])assert(!selectors.some(s=>fixture.getElementById(id).matches(s)),`Unwanted control ${id}`);
for(const id of ['source','external','watch'])assert(selectors.some(s=>fixture.getElementById(id).matches(s)),`Uncovered control ${id}`);
const urls=[...read('sitemap.xml').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname.slice(1)||'index.html');
const pages=[...new Set(urls)].sort();
const inventory={canonical_pages:pages.length,selectors:{},numbered_navigation:{}};
for(const s of selectors)inventory.selectors[s]={count:0,pages:[]};
for(const page of pages){
 const dom=new JSDOM(read(page)),doc=dom.window.document;
 for(const s of selectors){const nodes=[...doc.querySelectorAll(s)];if(nodes.length){inventory.selectors[s].count+=nodes.length;inventory.selectors[s].pages.push(page);for(const n of nodes)assert.equal(n.tagName,'A');}}
 for(const s of ['.watch-topic-index a','nav[aria-label="Pioneer study sections"] a','.bom-story-directory a']){
  const nodes=[...doc.querySelectorAll(s)];if(nodes.length)inventory.numbered_navigation[page+' '+s]=nodes.map(n=>({href:n.getAttribute('href'),label:n.textContent.trim().replace(/\s+/g,' ')}));
 }
 if(page==='watch.html')assert.deepEqual([...doc.querySelectorAll('.watch-topic-index a > span')].map(n=>n.textContent.trim()),['01','02','03','04','05','06','07']);
 dom.window.close();
}
for(const [s,a] of Object.entries(inventory.selectors))if(!a.count){const runtime=config.runtime_selectors[s];assert(runtime,`Unused selector ${s}`);assert(read(runtime.source).includes(runtime.marker));}
const file=path.join(root,'docs/study-link-control-inventory.json');
if(process.argv.includes('--write-inventory'))fs.writeFileSync(file,JSON.stringify(inventory,null,2)+'\n');
else assert.deepEqual(inventory,JSON.parse(fs.readFileSync(file,'utf8')),'Control coverage changed; review inventory');
console.log(`PASS: ${pages.length} canonical pages, ${selectors.length} named control families; protected prose/primary/Home/chapter fixtures; numbered link destinations recorded.`);
