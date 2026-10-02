const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'timeline-images.js'),'utf8');
for(const [route,kind,count] of [['life-of-christ-journey-map.html','life',18],['willie-and-martin-handcart-map.html','handcart',7],['latter-day-saint-church-history-timeline.html','history',8]]){
 const dom=new JSDOM('<div data-timeline-pane="detail"><p id="story">Original narrative</p></div>'+Array.from({length:51},(_,i)=>'<article id="history-event-'+i+'"><div class="detail"><p>Original story '+i+'</p></div></article>').join(''),{url:'https://focuschrist.com/timelines/'+route,runScripts:'outside-only'}),w=dom.window,d=w.document;w.eval(source);
 const registry=w.TimelineImages.registry[kind];assert.equal(Object.keys(registry).length,count);assert.equal(d.querySelectorAll('[data-timeline-image]').length,kind==='history'?0:1);assert.equal(new Set(Object.values(registry).map(r=>r.src)).size,count);
 for(const [index,entry] of Object.entries(registry)){
  w.dispatchEvent(new w.CustomEvent('timeline:select',{detail:{index:Number(index)}}));const figures=d.querySelectorAll('[data-timeline-image]');assert.equal(figures.length,1);const f=figures[0];assert.equal(f.dataset.timelineImage,index);assert.equal(f.querySelector('img').getAttribute('src'),entry.src);assert.equal(f.querySelector('a').getAttribute('href'),entry.href);assert.equal(d.getElementById('story').textContent,'Original narrative');if(kind==='history')assert.equal(f.parentElement.parentElement.id,'history-event-'+index);
  assert(fs.existsSync(path.join(root,entry.src)));if(entry.href.startsWith('/')){const [page,anchor]=entry.href.slice(1).split('#');assert(fs.readFileSync(path.join(root,page),'utf8').includes('id="'+anchor+'"'));}
 }
 w.dispatchEvent(new w.CustomEvent('timeline:select',{detail:{index:999}}));assert.equal(d.querySelectorAll('[data-timeline-image]').length,0);
 w.TimelineImages.render(0);w.dispatchEvent(new w.CustomEvent('timeline:filter',{detail:{indices:[]}}));assert.equal(d.querySelectorAll('[data-timeline-image]').length,0);dom.window.close();
}
console.log('PASS33 image references unique per experience, assets/anchors valid, exact selected container, initial selection rules, stale image removal, narrative retained.');
