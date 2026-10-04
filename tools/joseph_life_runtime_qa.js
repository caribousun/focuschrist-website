const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..');
const dom=new JSDOM(fs.readFileSync(path.join(root,'answers/who-was-joseph-smith.html'),'utf8'),{url:'https://focuschrist.com/answers/who-was-joseph-smith.html',runScripts:'outside-only',pretendToBeVisual:true});
const w=dom.window,d=w.document;w.HTMLElement.prototype.scrollIntoView=function(){this.dataset.qaScrolled='true';};
w.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','');};w.HTMLDialogElement.prototype.close=function(){this.removeAttribute('open');this.dispatchEvent(new w.Event('close'));};
for(const file of ['topic-artwork-details.js','full-image-viewer.js'])w.eval(fs.readFileSync(path.join(root,file),'utf8'));
d.dispatchEvent(new w.Event('DOMContentLoaded'));const click=n=>n.dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true,button:0}));
// Native menus must work without JavaScript and lead to the beginning of real content.
for(const selector of ['.joseph-page-menu','.joseph-story-menu']){
 const menu=d.querySelector(selector);assert(menu&&menu.tagName==='DETAILS'&&!menu.open,'Compact native menu starts closed');
 assert(menu.querySelector(':scope > summary')?.textContent.trim(),'Menu has a visible keyboard-operable summary');
 const links=[...menu.querySelectorAll('a[href]')];assert(links.length>0);const ids=new Set();
 for(const link of links){const href=link.getAttribute('href');assert(/^#[a-z0-9-]+$/.test(href),'Local menu target is explicit');assert(!ids.has(href),'No duplicate menu target');ids.add(href);const target=d.getElementById(href.slice(1));assert(target&&['SECTION','ARTICLE','H2','H3'].includes(target.tagName),'Menu lands on content start');assert(target.matches('h2,h3')||target.querySelector('h2,h3'),'Target has a real visible heading');}
}
const storyTargets=[...d.querySelectorAll('.joseph-story-menu a')].map(a=>a.hash.slice(1));
assert.deepEqual(storyTargets,[...d.querySelectorAll('.joseph-life-scene,.joseph-life-closing')].map(e=>e.id),'Every shared-life scene has one menu link in narrative order');
const lucy=JSON.parse(fs.readFileSync(path.join(root,'docs/joseph-lucy-family-stories.json'),'utf8')).stories;
assert.equal(lucy.length,10,'Owner requires ten distinct Lucy stories');
const acceptedLucy=lucy.filter(s=>s.image);
if(!process.argv.includes('--allow-partial'))assert.equal(acceptedLucy.length,10,'Release requires all ten reviewed illustrations');
const triggers=[...d.querySelectorAll('.joseph-life-scene figure > a')];assert.equal(triggers.length,11+acceptedLucy.length);
for(const record of acceptedLucy)assert(d.getElementById(record.id)?.querySelector('figure > a'),'Every accepted story has a real illustration');
for(const t of triggers){
 const owner=t.closest('article.joseph-life-scene');t.focus();click(t);const panel=d.getElementById('topicArtworkDetailDialog');assert(panel.open);assert.equal(panel.querySelector('img').src,t.href);
 const expected=[...t.closest('figure').querySelectorAll('figcaption a[href]')].map(a=>a.href);
 assert.deepEqual([...panel.querySelectorAll('[data-topic-art-source]')].map(a=>a.href),expected.slice(0,3),'All actual scene source actions retained');
 const full=panel.querySelector('[data-full-image-viewer]');full.focus();click(full);const viewer=d.querySelector('.fc-full-image-viewer');assert(viewer.open);click(viewer.querySelector('button'));assert(panel.open&&!viewer.open&&d.activeElement===full);
 click(panel.querySelector('[data-topic-art-close]'));assert(d.activeElement===t);click(t);const resume=panel.querySelector('[data-topic-art-continue]');assert.equal(new URL(resume.href).hash,'#'+owner.id);click(resume);assert(!panel.open&&d.activeElement===owner&&owner.dataset.qaScrolled==='true','Continue returns to exact individual scene');
}
const archives=JSON.parse(fs.readFileSync(path.join(root,'docs/joseph-family-archival-art.json'),'utf8')).items;
assert.equal(archives.length,5);
for(const record of archives){
 const figure=[...d.querySelectorAll('#'+record.owning_section+' figure')].find(f=>new URL(f.querySelector('img').src).pathname==='/'+record.asset);
 assert(figure,'Archival image belongs to its dated family section');const t=figure.querySelector('a:has(img)');click(t);
 const panel=d.getElementById('topicArtworkDetailDialog');assert(panel.open);assert.equal(panel.querySelector('img').src,t.href);
 assert([...panel.querySelectorAll('[data-topic-art-source]')].some(a=>a.href===record.source_url),'Exact archival source survives modal');
 click(panel.querySelector('[data-topic-art-close]'));assert.equal(d.activeElement,t);
}
for(const route of ['/answers/who-was-joseph-smith.html','/joseph-smith-likeness.html','/index.html']){
 for(const record of archives){
  const good=record.source_url,bad=[good.replace('https:','http:'),good+'?unreviewed=1',good+'#other',good.replace(new URL(good).hostname,new URL(good).hostname+'.evil.example'),good+'/other'];
  const fixture=new JSDOM('<main><figure><a href="/assets/test.webp"><img src="/assets/test.webp" alt="Test"></a><figcaption><h3>Archive boundary</h3>'+[good,...bad].map(u=>'<a href="'+u+'">Source</a>').join('')+'</figcaption></figure></main>',{url:'https://focuschrist.com'+route,runScripts:'outside-only'});
  const fw=fixture.window,fd=fw.document;fw.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','');};fw.HTMLElement.prototype.scrollIntoView=function(){};
  fw.eval(fs.readFileSync(path.join(root,'topic-artwork-details.js'),'utf8'));fd.dispatchEvent(new fw.Event('DOMContentLoaded'));fd.querySelector('figure>a').dispatchEvent(new fw.MouseEvent('click',{bubbles:true,cancelable:true,button:0}));
  assert.deepEqual([...fd.querySelectorAll('[data-topic-art-source]')].map(a=>a.href),route==='/answers/who-was-joseph-smith.html'?[good]:[],'Only exact reviewed archive URL and family owner route accepted');fixture.window.close();
 }
}
w.close();console.log('PASS current family detail/fullsize/source/close paths and exact individual-scene Continue focus; five archival source paths and strict URL negatives pass; rendered geometry remains separate.');
