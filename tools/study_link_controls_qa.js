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
// Source tokens stay rounded only inside picture-panel action groups. The inherited
// token resolves the existing !important source rule without changing main-page rows.
const pictureCss=read('artwork-actions.css');
const pictureSelector='.fc-site :is(.fc-artwork-detail-actions, .fc-missionary-detail-actions, .fc-art-study-links)';
const pictureRule=pictureCss.slice(pictureCss.indexOf(pictureSelector)+pictureSelector.length).split('}')[0];
assert(pictureRule.includes('--fc-study-control-radius: 999px;'),'Picture sources must use standard fully rounded pills');
assert(css.includes('--fc-study-control-radius: 10px;'),'Unrelated owner control radius must remain unchanged');
const pictureFixture=new JSDOM(`<body class="fc-site cfm-page"><main><div class="cfm-jump"><a id="cfm-row">Week</a></div><p><a id="prose-source">John 20</a></p></main><dialog class="fc-topic-artwork-detail"><div class="fc-artwork-detail-actions"><a id="topic-source" data-topic-art-source class="fc-button">Read Doctrine and Covenants 109:7–9, 22–23</a></div></dialog><dialog class="fc-hero-detail-dialog"><div class="fc-artwork-detail-actions"><a id="hero-source" class="fc-button fc-button--primary">John 20</a></div></dialog><dialog><div class="fc-artwork-detail-actions"><a id="legacy-source" class="fc-button">John 10</a></div></dialog><div class="fc-missionary-detail-actions"><a id="mission-source">Source</a></div><div class="fc-art-study-links"><a id="gallery-source">Source</a></div></body>`).window.document;
for(const id of ['topic-source','hero-source','legacy-source','mission-source','gallery-source'])assert(pictureFixture.getElementById(id).closest(pictureSelector),`Picture source missing radius scope: ${id}`);
for(const id of ['cfm-row','prose-source'])assert(!pictureFixture.getElementById(id).closest(pictureSelector),`Unrelated control entered picture radius scope: ${id}`);
const fixture=new JSDOM(`<body class="fc-site"><p><a id="prose" class="fc-inline-scripture">John 3:16</a></p><a id="home" class="fc-button">Home</a><div class="fc-study-visual-sources"><a id="source">Mark 7:24–30</a><a id="primary" class="fc-button--primary">Study</a></div><a id="internal" class="source-link source-link--internal">Ask</a><a id="external" class="source-link">Source</a><nav class="jj-local-nav fc-study-nav"><a id="chapter">Chapter</a></nav><nav class="watch-topic-index"><a id="watch"><span>02</span>Book of Mormon</a></nav></body>`).window.document;
for(const id of ['prose','home','primary','internal','chapter'])assert(!selectors.some(s=>fixture.getElementById(id).matches(s)),`Unwanted control ${id}`);
for(const id of ['source','external','watch'])assert(selectors.some(s=>fixture.getElementById(id).matches(s)),`Uncovered control ${id}`);
function assertNoLooseSourceSeparators(doc){
 for(const group of doc.querySelectorAll('.fc-study-visual-sources'))
  assert(![...group.childNodes].some(n=>n.nodeType===3&&n.textContent.includes('·')),'Loose separator between source pills');
}
const sourceSeparatorFixture=new JSDOM('<p class="fc-study-visual-sources"><a>John 17</a> · <a>Moses 1</a></p>').window.document;
assert.throws(()=>assertNoLooseSourceSeparators(sourceSeparatorFixture),/Loose separator/);
assertNoLooseSourceSeparators(new JSDOM('<p class="fc-study-visual-sources"><a>John 17</a> <a>Moses 1</a></p><p>Speaker · Date</p>').window.document);
// The existing CFM prayer reference now exposes its scripture in the named source family.
function assertCfmPrayerSource(doc){
 const card=doc.querySelector('figure[data-linked-picture-reference="modern-prayer"]');
 assert(card,'Missing CFM prayer reference');
 const source=card.querySelector('.fc-study-visual-sources a');
 assert(source&&source.textContent.trim()==='Matthew 6:6–8','Missing CFM prayer source pill');
 assert(source.getAttribute('href')==='https://www.churchofjesuschrist.org/study/scriptures/nt/matt/6?lang=eng&id=p6-p8#p6','Changed CFM prayer source destination');
 assert(selectors.some(s=>source.matches(s)),'CFM prayer source outside named control coverage');
}
const cfmFixture=new JSDOM(read('come-follow-me.html'));
assertCfmPrayerSource(cfmFixture.window.document);
const cfmSource=cfmFixture.window.document.querySelector('[data-linked-picture-reference="modern-prayer"] .fc-study-visual-sources');
cfmSource.classList.remove('fc-study-visual-sources');
assert.throws(()=>assertCfmPrayerSource(cfmFixture.window.document),/Missing CFM prayer source pill/);
cfmSource.classList.add('fc-study-visual-sources');
cfmSource.querySelector('a').setAttribute('href','https://example.com/wrong');
assert.throws(()=>assertCfmPrayerSource(cfmFixture.window.document),/Changed CFM prayer source destination/);
cfmFixture.window.close();
const urls=[...read('sitemap.xml').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname.slice(1)||'index.html');
assert.equal(new Set(urls).size,urls.length,'Duplicate sitemap route');
const pages=[...new Set(urls)].sort();
const emmaControls=require('./emma_study_link_controls');
const emmaValidated=[];
const adamsControls=require('./adams_study_link_controls'),adamsValidated=[];
const integration=require('./owner_integration_navigation');
const retirementNav=require('./emma_retirement_navigation_successor');
const retirementControls=require('./emma_retirement_study_controls_successor');
const currentRoutes=urls.map(p=>p==='index.html'?'/':'/'+p);
retirementNav.assertCurrent(currentRoutes,read,JSDOM);
// These fixtures are explicit historical inputs, never current UI evidence.
const priorRead=retirementNav.priorReader(read),pastRead=integration.historicalRead(priorRead);
const predecessorRoutes=[...currentRoutes,'/history/emma-elect-lady.html'];
require('./test_owner_integration_navigation').selfTest(predecessorRoutes,priorRead,JSDOM);
require('./test_adams_study_link_controls')(JSDOM,pastRead,selectors,predecessorRoutes.filter(p=>p!=='/'+integration.intro));
require('./test_emma_study_link_controls')(JSDOM,pastRead,selectors);
// Six frozen artwork figures add exactly five named source controls. The Stand
// scripture links remain inline prose. Validate these additions before taking
// their exact inverse for the unchanged control-coverage baseline.
const readingFigures=[
 ['answers/stand-forever.html','stand-john6-remain','3a3794ddbf07c82b27a2b09ddbad64d51aa13d458cf8c2b0f39a1e204625ee98',0],
 ['answers/stand-forever.html','stand-john7-do-his-will','3d7597e5e76688fb4b98f1289d13d99fb969a52f2ef38cc3e50f9a8d9c556f1a',0],
 ['answers/why-latter-day-saints-build-temples.html','temple-tribute','25f1d649fea86b0125d7d9eeb9592e26c6ac6e63fba2b68d5cf304111f4b6cf7',1],
 ['church-history.html','history-friendship','73b3051254c835af71afa0744fc79df405ecd84c0ae5d9f1e0ee5a9475bfbc51',2],
 ['pioneers.html','pioneers-traveler','5dc82e47c2feb44a4f0b6d2b2bbe13d0ef0ece1faadcf8cd9bd2b1cf9e114102',1],
 ['timelines/willie-and-martin-handcart-map.html','handcart-supplies','075ff37c51fa2162a5ab37baf6bde5a3eb9a97220358a49ad4fe18e9e0976881',1]
];
const digest=s=>require('crypto').createHash('sha256').update(s).digest('hex');
function invertReadingFigures(doc,route){
 let added=0;
 for(const [owner,key,sha,count] of readingFigures){
  const figures=[...doc.querySelectorAll('figure')].filter(f=>f.getAttribute('data-topic-art')===key||f.outerHTML.includes(key+'-960.webp')||f.outerHTML.includes(key+'-full.webp'));
  assert.equal(figures.length,owner===route?1:0,route+': missing, duplicate or wrong-owner reading figure '+key);
  if(owner!==route)continue;
  const figure=figures[0];assert.equal(digest(figure.outerHTML),sha,route+': reviewed reading figure changed '+key);
  assert.equal(figure.querySelectorAll(selectors[0]).length,count,key+': exact added source-control count');
  for(const selector of selectors.slice(1))assert.equal(figure.querySelectorAll(selector).length,0,key+': unrelated control family entered inverse');
  added+=count;figure.remove();
 }
 return added;
}
for(const route of new Set(readingFigures.map(row=>row[0]))){
 const original=JSDOM.fragment(read(route));
 const fixtureHtml=readingFigures.filter(row=>row[0]===route).map(row=>original.querySelector('figure[data-topic-art="'+row[1]+'"]').outerHTML).join('');
 for(const row of readingFigures.filter(row=>row[0]===route))for(const kind of ['missing','duplicate','key','href','caption','wrong-owner']){
  const doc=JSDOM.fragment(fixtureHtml),figure=doc.querySelector('figure[data-topic-art="'+row[1]+'"]');
  if(kind==='missing')figure.remove();
  if(kind==='duplicate')doc.append(figure.cloneNode(true));
  if(kind==='key')figure.setAttribute('data-topic-art','unknown');
  if(kind==='href')figure.querySelector('a').setAttribute('href','unknown.webp');
  if(kind==='caption')figure.querySelector('figcaption').append('Changed');
  assert.throws(()=>invertReadingFigures(doc,kind==='wrong-owner'?'unreviewed.html':route),assert.AssertionError,kind+': '+row[1]);
 }
 const extra=JSDOM.fragment(fixtureHtml+'<p class="fc-study-visual-sources"><a href="unexpected">Extra control</a></p>');
 invertReadingFigures(extra,route);
 assert.equal(extra.querySelectorAll(selectors[0]).length,1,'Unrelated source control must remain visible to baseline coverage');
}
// The two reviewed seasonal figures add one source pill each. Validate their
// exact current DOM and owner before taking this narrow baseline inverse.
const seasonalFigures=[
 ['birth-of-christ.html','christ-christmas-light','c242de105262e87b1f3476c48faf7b3a26246733785bca189753d85c742fc196'],
 ['answers/why-families-are-important.html','christ-winter-laughter','247279f2f731ef3653baa95887e391669b9b7e572fb886828c89fe6aab6e0b6b']
];
function invertSeasonalFigures(doc,route){
 let added=0;
 for(const [owner,key,sha] of seasonalFigures){
  const figures=[...doc.querySelectorAll('figure')].filter(f=>f.getAttribute('data-exclusive-artwork')===key||f.outerHTML.includes(key+'-960.webp')||f.outerHTML.includes(key+'-full.webp'));
  assert.equal(figures.length,owner===route?1:0,route+': missing, duplicate or wrong-owner seasonal figure '+key);
  if(owner!==route)continue;
  const figure=figures[0];assert.equal(digest(figure.outerHTML),sha,route+': reviewed seasonal figure changed '+key);
  assert.equal(figure.querySelectorAll(selectors[0]).length,1,key+': exact added source-control count');
  for(const selector of selectors.slice(1))assert.equal(figure.querySelectorAll(selector).length,0,key+': unrelated control family entered inverse');
  added++;figure.remove();
 }
 return added;
}
for(const [route,key] of seasonalFigures){
 const original=JSDOM.fragment(read(route));
 const fixtureHtml=original.querySelector('figure[data-exclusive-artwork="'+key+'"]').outerHTML;
 for(const kind of ['missing','duplicate','key','href','caption','wrong-owner']){
  const doc=JSDOM.fragment(fixtureHtml),figure=doc.querySelector('figure');
  if(kind==='missing')figure.remove();
  if(kind==='duplicate')doc.append(figure.cloneNode(true));
  if(kind==='key')figure.setAttribute('data-exclusive-artwork','unknown');
  if(kind==='href')figure.querySelector('a').setAttribute('href','unknown.webp');
  if(kind==='caption')figure.querySelector('figcaption').append('Changed');
  assert.throws(()=>invertSeasonalFigures(doc,kind==='wrong-owner'?'unreviewed.html':route),assert.AssertionError,kind+': '+key);
 }
 const extra=JSDOM.fragment(fixtureHtml+'<p class="fc-study-visual-sources"><a href="unexpected">Extra control</a></p>');
 invertSeasonalFigures(extra,route);
 assert.equal(extra.querySelectorAll(selectors[0]).length,1,'Unrelated source control must remain visible to baseline coverage');
}
// Four reviewed modern scenes add one source pill each. Validate their
// exact current DOM and owner before taking this narrow baseline inverse.
const fourSceneFigures=[["answers/divorce-and-faith.html","christ-moving-day","e6639c1434c7e4e0eec978713e9f980361cc0eb69dd22ec1472f621cff449e57"],["answers/are-latter-day-saints-christian.html","christ-food-pantry","9d74f0c4cd3087dafa449c50a18936c7dc77853bba06eb7b98d02b52a55862c1"],["answers/faith-in-jesus-christ-during-trials.html","christ-homecoming-celebration","62e321283bae68213588662eb0f5d64d6326f3ca1b7f17ec31e5feb396717df2"],["art-study/suffer-the-little-children.html","christ-children-colorful-day","9a969d6e1b71f584830214510d70d204151e729d052f4e5495dd2ffe58258ee3"]];
function invertFourSceneFigures(doc,route){
 let added=0;
 for(const [owner,key,sha] of fourSceneFigures){
  const figures=[...doc.querySelectorAll('figure')].filter(f=>f.getAttribute('data-exclusive-artwork')===key||f.outerHTML.includes(key+'-960.webp')||f.outerHTML.includes(key+'-full.webp'));
  assert.equal(figures.length,owner===route?1:0,route+': missing, duplicate or wrong-owner four-scene figure '+key);
  if(owner!==route)continue;
  const figure=figures[0];assert.equal(digest(figure.outerHTML),sha,route+': reviewed four-scene figure changed '+key);
  assert.equal(figure.querySelectorAll(selectors[0]).length,1,key+': exact added source-control count');
  for(const selector of selectors.slice(1))assert.equal(figure.querySelectorAll(selector).length,0,key+': unrelated control family entered inverse');
  added++;figure.remove();
 }
 return added;
}
for(const [route,key] of fourSceneFigures){
 const original=JSDOM.fragment(read(route));
 const fixtureHtml=original.querySelector('figure[data-exclusive-artwork="'+key+'"]').outerHTML;
 for(const kind of ['missing','duplicate','key','href','caption','wrong-owner']){
  const doc=JSDOM.fragment(fixtureHtml),figure=doc.querySelector('figure');
  if(kind==='missing')figure.remove();
  if(kind==='duplicate')doc.append(figure.cloneNode(true));
  if(kind==='key')figure.setAttribute('data-exclusive-artwork','unknown');
  if(kind==='href')figure.querySelector('a').setAttribute('href','unknown.webp');
  if(kind==='caption')figure.querySelector('figcaption').append('Changed');
  assert.throws(()=>invertFourSceneFigures(doc,kind==='wrong-owner'?'unreviewed.html':route),assert.AssertionError,kind+': '+key);
 }
 const extra=JSDOM.fragment(fixtureHtml+'<p class="fc-study-visual-sources"><a href="unexpected">Extra control</a></p>');
 invertFourSceneFigures(extra,route);
 assert.equal(extra.querySelectorAll(selectors[0]).length,1,'Unrelated source control must remain visible to baseline coverage');
}
// Six reviewed modern scenes add one source pill each. Validate their
// exact current DOM and owner before taking this narrow baseline inverse.
const sixSceneFigures=[["art-study/the-living-christ.html","christ-under-countless-stars","49a8777db8bddc718f6c6136e2fa5d82c110b1ba610c26249bb923ca63b38f66"],["missionary.html","christ-earthquake-community","3a248e5070c02de28562239f30d4670676c90b1514dddd58fcd31909bee1d404"],["jesus-christ/miracles-and-compassion.html","christ-hospital-corridor","1b9e10369492cc5f48ff33b9fcc95a459e0f232ce45ad36b9363890595872f0a"],["art-study/be-still.html","christ-caregiver-night","e4ab54a25a54b6118547e7f7e9102d83268297f22e382dd20af8f4195242f0b0"],["art-study/the-good-shepherd.html","christ-last-bus","00690fe0c2d0c6544ecc75dcd0af53b46e744465d869264f6f6e48652b11c05b"],["jesus-christ/parables/good-samaritan.html","christ-responder-rest","a2fa5906fa8d753d10b2de95f55146a565b0ac83bf2d95f8f2527a55b3e2724d"]];
function invertSixSceneFigures(doc,route){
 let added=0;
 for(const [owner,key,sha] of sixSceneFigures){
  const figures=[...doc.querySelectorAll('figure')].filter(f=>f.getAttribute('data-exclusive-artwork')===key||f.outerHTML.includes(key+'-960.webp')||f.outerHTML.includes(key+'-full.webp'));
  assert.equal(figures.length,owner===route?1:0,route+': missing, duplicate or wrong-owner six-scene figure '+key);
  if(owner!==route)continue;
  const figure=figures[0];assert.equal(digest(figure.outerHTML),sha,route+': reviewed six-scene figure changed '+key);
  assert.equal(figure.querySelectorAll(selectors[0]).length,1,key+': exact added source-control count');
  for(const selector of selectors.slice(1))assert.equal(figure.querySelectorAll(selector).length,0,key+': unrelated control family entered inverse');
  added++;figure.remove();
 }
 return added;
}
for(const [route,key] of sixSceneFigures){
 const original=JSDOM.fragment(read(route));
 const fixtureHtml=original.querySelector('figure[data-exclusive-artwork="'+key+'"]').outerHTML;
 for(const kind of ['missing','duplicate','key','href','caption','wrong-owner']){
  const doc=JSDOM.fragment(fixtureHtml),figure=doc.querySelector('figure');
  if(kind==='missing')figure.remove();
  if(kind==='duplicate')doc.append(figure.cloneNode(true));
  if(kind==='key')figure.setAttribute('data-exclusive-artwork','unknown');
  if(kind==='href')figure.querySelector('a').setAttribute('href','unknown.webp');
  if(kind==='caption')figure.querySelector('figcaption').append('Changed');
  assert.throws(()=>invertSixSceneFigures(doc,kind==='wrong-owner'?'unreviewed.html':route),assert.AssertionError,kind+': '+key);
 }
 const extra=JSDOM.fragment(fixtureHtml+'<p class="fc-study-visual-sources"><a href="unexpected">Extra control</a></p>');
 invertSixSceneFigures(extra,route);
 assert.equal(extra.querySelectorAll(selectors[0]).length,1,'Unrelated source control must remain visible to baseline coverage');
}
let sixSceneSourceControls=0;
let fourSceneSourceControls=0;
let seasonalSourceControls=0;
let readingSourceControls=0;
const inventory={canonical_pages:pages.length,selectors:{},numbered_navigation:{}};
for(const s of selectors)inventory.selectors[s]={count:0,pages:[]};
for(const page of pages){
 const dom=new JSDOM(read(page)),doc=dom.window.document;
 assertNoLooseSourceSeparators(doc);
 if([adamsControls.owner,adamsControls.landing].includes(page)){const old=new JSDOM(pastRead(page));try{adamsControls.validate(old.window.document,page,selectors,pastRead(page),pastRead);adamsValidated.push(page);}finally{old.window.close();}}
 readingSourceControls+=invertReadingFigures(doc,page);
 seasonalSourceControls+=invertSeasonalFigures(doc,page);
 fourSceneSourceControls+=invertFourSceneFigures(doc,page);
 sixSceneSourceControls+=invertSixSceneFigures(doc,page);
 if(retirementControls.CURRENT.includes(page)){
  retirementControls.validate(doc,page,selectors,read(page),read('docs/emma-study-link-additions.json'));
  const old=new JSDOM(pastRead(page));try{emmaControls.validate(old.window.document,page,selectors,pastRead(page));emmaValidated.push(page);}finally{old.window.close();}
 }
 for(const s of selectors){const nodes=[...doc.querySelectorAll(s)];if(nodes.length){inventory.selectors[s].count+=nodes.length;inventory.selectors[s].pages.push(page);for(const n of nodes)assert.equal(n.tagName,'A');}}
 for(const s of ['.watch-topic-index a','nav[aria-label="Pioneer study sections"] a','.bom-story-directory a']){
  const nodes=[...doc.querySelectorAll(s)];if(nodes.length)inventory.numbered_navigation[page+' '+s]=nodes.map(n=>({href:n.getAttribute('href'),label:n.textContent.trim().replace(/\s+/g,' ')}));
 }
 if(page==='watch.html')assert.deepEqual([...doc.querySelectorAll('.watch-topic-index a > span')].map(n=>n.textContent.trim()),['01','02','03','04','05','06','07']);
 dom.window.close();
}
assert.equal(readingSourceControls,5,'Exactly five named source controls in six reviewed reading figures');
assert.equal(seasonalSourceControls,2,'Exactly two named source controls in two reviewed seasonal figures');
assert.equal(fourSceneSourceControls,4,'Exactly four source controls in four reviewed modern figures');
assert.equal(sixSceneSourceControls,6,'Exactly six source controls in six reviewed modern figures');
console.log('PASS: six exact current figures, six added controls;36 negative mutations and6 unrelated-control retention fixtures.');
console.log('PASS: two exact seasonal figures, unchanged legacy inventory;12 negative mutations and2 unrelated-control retention fixtures.');
for(const [s,a] of Object.entries(inventory.selectors))if(!a.count){const runtime=config.runtime_selectors[s];assert(runtime,`Unused selector ${s}`);assert(read(runtime.source).includes(runtime.marker));}
// Invert only five independently validated contributions; keep full current scan intact.
// Validate and project the actual retired-route successor before invoking
// unchanged historical inventory checks; no old DOM is labeled current.
const retired='history/emma-elect-lady.html',retiredOld=new JSDOM(pastRead(retired));
try{emmaControls.validate(retiredOld.window.document,retired,selectors,pastRead(retired));emmaValidated.push(retired);}finally{retiredOld.window.close();}
const beforeIntegration=retirementNav.historicProjection(inventory,currentRoutes,selectors,adamsControls.numbered,read,priorRead,JSDOM,integration);
const beforeEmma=adamsControls.beforeEmmaInventory(beforeIntegration,adamsValidated,predecessorRoutes.filter(p=>p!=='/'+integration.intro),pastRead);
const historicalInventory=emmaControls.historicalInventory(beforeEmma,emmaValidated);
const file=path.join(root,'docs/study-link-control-inventory.json');
assert.deepEqual(historicalInventory,JSON.parse(fs.readFileSync(file,'utf8')),'Historical control coverage changed; review inventory');
// Never overwrite or present a predecessor projection as a current inventory.
// A separately reviewed current inventory producer remains required.
if(process.argv.includes('--write-inventory'))throw new Error('Historical projection is read-only; a reviewed current inventory successor is required');
console.log(`PASS: ${pages.length} canonical pages, ${selectors.length} named control families; protected prose/primary/Home/chapter fixtures; numbered link destinations recorded.`);
console.log('PASS: six exact reading figures, five added source controls, unchanged legacy inventory;36 negative figure mutations and5 unrelated-control retention fixtures.');

// Source row contract and deliberately broken style fixtures.
{
const base='body.fc-site:not(.cfm-page) :is(.fc-study-visual-sources, .pioneer-source-links)';
const child=base+' > a:not(.fc-button--primary):not([hidden])';
function check(css){
 assert(css.includes('> a[hidden] {\n    display: none !important;'),'hidden source must remain hidden');
 const part=css.slice(css.indexOf('/* Related source controls share each row'));
 assert(part.includes(base+' {\n    align-items: stretch;'),'missing group stretch');
 assert(part.includes(child+' {\n    flex: 1 1 16rem;\n    margin: 0;'),'missing equal grow basis');
 assert(part.includes(child+':only-child {\n    flex: 0 1 auto;'),'single rule loses specificity or protected scope');
 assert(part.includes('@media (max-width: 600px)'),'missing phone boundary');
 assert(part.includes(child+' {\n        flex-basis: 100%;\n        width: 100%;'),'missing phone full width');
}
const css=read('site-system.css');check(css);
const mutations=[css.replace('> a[hidden] {\n    display: none !important;', '> a[hidden] {\n    display: inline-flex;'),css.replace('flex: 1 1 16rem','flex: 0 1 auto'),css.replace('flex-basis: 100%','flex-basis: auto'),css.replace('width: 100%;\n    }\n}', 'width: auto;\n    }\n}'),css.replace(child+':only-child',base+' > a:only-child'),css.replaceAll(':not(.cfm-page)',''),css.replaceAll(':not([hidden])',''),css.replaceAll(':not(.fc-button--primary)','')];
mutations.forEach(x=>assert.throws(()=>check(x)));
const fixture=new JSDOM('<body class="fc-site"><p><a id="prose">Text</a></p><nav class="fc-study-nav"><a id="nav">Nav</a></nav><p class="fc-study-visual-sources"><a id="normal">Source</a><a id="hidden" hidden>Hidden</a><a id="primary" class="fc-button--primary">Primary</a><span><a id="nested">Nested</a></span></p><p class="pioneer-source-links"><a id="single">Single</a></p></body>').window.document;
for(const id of ['normal','single'])assert(fixture.getElementById(id).matches(child));
for(const id of ['prose','nav','hidden','primary','nested'])assert(!fixture.getElementById(id).matches(child));
assert(fixture.getElementById('single').matches(child+':only-child'));
fixture.body.classList.add('cfm-page');assert.equal(fixture.querySelectorAll(child).length,0);
console.log('PASS source group structural contract;8negative CSS mutations;positive/negative direct-child,CFM,primary,hidden,prose,navigation fixtures. Rendered geometry still requires native review.');

}
