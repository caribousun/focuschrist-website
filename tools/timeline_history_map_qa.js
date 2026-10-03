const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{JSDOM}=require('jsdom');
const root=path.join(__dirname,'..'),html=fs.readFileSync(path.join(root,'timelines/latter-day-saint-church-history-timeline.html'),'utf8');
for(const provider of [true,false]) for(const reduced of [true,false]){
 const dom=new JSDOM(html,{url:'https://focuschrist.com/timelines/latter-day-saint-church-history-timeline.html',runScripts:'outside-only'}),w=dom.window,d=w.document;
 w.matchMedia=q=>({matches:q.includes('prefers-reduced-motion')?reduced:true,addEventListener(){}});w.HTMLElement.prototype.scrollIntoView=function(){};
 const layers=new Set(),handlers={},tile={},views=[];let popup=null,popupOpens=0;
 let center={lat:38,lng:-70},zoom=3;const camera=[];function update(p,z){center={lat:p[0],lng:p[1]};zoom=z;}
 const map={stop(){camera.push({method:'stop'});return this},getCenter(){return center},getZoom(){return zoom},distance(a,b){const r=Math.PI/180,x=(b[1]-a.lng)*r*Math.cos((a.lat+b[0])*r/2),y=(b[0]-a.lat)*r;return 6371000*Math.hypot(x,y)},flyTo(p,z,o){camera.push({method:'flyTo',p,z,o});update(p,z);return this},flyToBounds(b,o){camera.push({method:'flyToBounds',b,o});return this},setView(p,z,o){camera.push({method:'setView',p,z,o});update(p,z);views.push({p,z});return this},latLngToContainerPoint(p){return{x:p[1]*2,y:p[0]*2}},removeLayer(l){layers.delete(l)},fitBounds(b,o){camera.push({method:'fitBounds',b,o});views.push({bounds:b});return this},closePopup(){popup=null;},on(n,f){handlers[n]=f;return this},invalidateSize(){}};
 function layer(coords,opts){return{coords,opts,popup:null,handlers:{},bindPopup(p){this.popup=p;return this},addTo(){layers.add(this);return this},on(n,f){this.handlers[n]=f;return this},setIcon(i){this.opts.icon=i;return this}}}
 if(provider)w.L={map:()=>map,tileLayer:()=>({addTo(){return this},on(n,f){tile[n]=f;return this}}),divIcon:o=>o,latLngBounds:p=>p,marker:layer,rectangle:layer,popup:()=>({setLatLng(){return this},setContent(p){this.content=p;return this},openOn(){popup=this.content;popupOpens++;return this}})};
 w.eval([...d.scripts].find(s=>s.textContent.includes('var EVENTS')).textContent);
 w.eval(fs.readFileSync(path.join(root,'timeline-history-locations.js'),'utf8'));
 d.querySelector('#eventDirectory button').click();assert.equal(w.HistoryTimeline.selectedIndex,0,'Directory can be selected before deferred map initializes');
 w.eval(fs.readFileSync(path.join(root,'timeline-history-map.js'),'utf8'));assert.equal(w.HistoryTimelineMap.selectedIndex,0,'Deferred map consumes preexisting selection');assert.equal(d.querySelector('#history-event-0 .card').classList.contains('open'),true,'Map initialization preserves opened story');
 const api=w.HistoryTimeline,data=w.HISTORY_LOCATIONS;assert.equal(api.events.length,51);assert.equal(data.events.length,51);
 let observed=null;w.addEventListener('timeline:select',e=>{observed=e.detail.index;assert.equal(d.querySelector('#history-event-'+observed+' .card').classList.contains('open'),true,'Selection event follows opened story');});
 for(let i=0;i<51;i++){assert.equal(data.events[i].expectedTitle,api.events[i].title);assert.equal(api.select(i),true);assert.equal(observed,i);assert.equal(d.querySelectorAll('#timeline .event:not([hidden])').length,1);assert.equal(d.querySelector('#history-event-'+i).hidden,false);assert(d.querySelector('#history-event-'+i+' .timeline-event-navigation-slot'));assert.equal(w.TimelineNavigationAdapter.current(),i);assert.equal(w.HistoryTimelineMap.selectedIndex,i);assert.equal(d.querySelector('#historyMapSelection strong').textContent,api.events[i].title);}
 assert(data.events.filter(r=>r.kind==='worldwide').every(r=>r.places.length===0));assert(data.events.some(r=>r.places.length>1));assert(data.events.some(r=>r.kind==='region'));
 let staleChoice=null;
 if(provider){
  const singles=data.events.filter(e=>e.places.length===1&&e.kind!=='worldwide'&&e.kind!=='region'),a=singles[0],place=data.places[a.places[0]],target=[place.lat,place.lng];
  map.setView([0,0],3);camera.length=0;api.select(a.index);assert.equal(camera[0].method,'stop');assert.equal(camera.at(-1).method,reduced?'setView':'flyTo');assert.deepEqual(Array.from(camera.at(-1).p),target);assert.equal(camera.at(-1).z,10);
  camera.length=0;api.select(a.index);assert(!camera.some(c=>c.method==='flyTo'||c.method==='flyToBounds'),'Repeated same place never makes artificial flight');
  map.setView([place.lat+.05,place.lng],9);camera.length=0;api.select(a.index);assert.equal(camera.at(-1).z,9,'Nearby selection preserves useful zoom');
  for(const kind of ['region','worldwide']){const event=data.events.find(e=>e.kind===kind);camera.length=0;api.select(event.index);assert.equal(camera[0].method,'stop');assert.equal(camera.at(-1).method,kind==='region'?(reduced?'fitBounds':'flyToBounds'):(reduced?'setView':'flyTo'));if(kind==='worldwide')assert.equal(camera.at(-1).z,2);}
  const multi=data.events.find(e=>e.places.length>1&&e.kind!=='region');camera.length=0;api.select(multi.index);assert.equal(camera.at(-1).method,reduced?'fitBounds':'flyToBounds');assert.equal(camera.at(-1).b.length,multi.places.length,'All multi-place extents retained');
  camera.length=0;w.HistoryTimelineMap.showMatching();assert.equal(camera[0].method,'stop','Reset cancels pending camera');assert.equal(camera.at(-1).method,'fitBounds');
  for(let n=0;n<3;n++)tile.tileerror();assert.match(d.getElementById('historyMapStatus').textContent,/imagery is unavailable/);tile.tileload();assert.doesNotMatch(d.getElementById('historyMapStatus').textContent,/imagery is unavailable/);
  let choices=null;w.TimelineWorkspace={showChoices(title,items,onSelect){choices={title,items,onSelect};return true;}};
  for(const width of [390,1366]){
   w.innerWidth=width;handlers.zoomend();let exercised=0;
   for(const l of [...layers]){choices=null;l.handlers.click({latlng:[40,-90]});assert.equal(popupOpens,0,'No map popups at any width');if(!choices)continue;exercised++;const active=choices;assert(active.items.length>1);assert(active.items.every(c=>c.label===api.events[c.index].date+' \u2014 '+api.events[c.index].title),'Exact index/title/encoded labels');
    handlers.zoomend();const target=active.items.at(-1).index;active.onSelect(target);assert.equal(api.selectedIndex,target,'Visible choices remain usable after benign map redraw');staleChoice=active;break;
   }
   assert(exercised>0,'Multi-event chooser exercised at '+width);
  }
 }
 const search=d.getElementById('search');search.value='Kirtland';search.dispatchEvent(new w.Event('input'));
 const visible=Array.from(api.visibleIndices());assert(visible.length>0&&visible.length<51);assert.deepEqual(Array.from(w.HistoryTimelineMap.visibleIndices),visible);
 const before=api.selectedIndex;assert.equal(api.select(50),false);w.HistoryTimelineMap.select(50);assert.equal(api.selectedIndex,before);assert.equal(api.selectedIndex,visible[0]);assert.equal(w.HistoryTimelineMap.selectedIndex,visible[0]);assert.equal(w.TimelineNavigationAdapter.current(),visible[0]);assert.deepEqual(Array.from(w.TimelineNavigationAdapter.visibleIndices()),visible);
 if(provider){const before=api.selectedIndex;staleChoice.onSelect(staleChoice.items[0].index);assert.equal(api.selectedIndex,before,'Detached choices are rejected after filter change even if event still matches');}
 else {assert.equal(d.getElementById('historyMapCanvas').hidden,true);assert.equal(d.getElementById('historyMapReset').hidden,true);}
 search.value='no-such-event-zzzz';search.dispatchEvent(new w.Event('input'));assert.equal(api.visibleIndices().length,0);if(provider)assert.equal(layers.size,0);assert(d.querySelector('#eventDirectory [role="status"]')?.textContent.includes('No events match'),'Empty Events pane explains search result');assert.equal(d.querySelectorAll('#eventDirectory button').length,0);search.value='';search.dispatchEvent(new w.Event('input'));assert.equal(d.querySelector('#eventDirectory [role="status"]'),null,'Clear search removes stale empty message');assert.equal(d.querySelectorAll('#eventDirectory button').length,51,'Clear search restores all event controls');
 w.dispatchEvent(new w.Event('pagehide'));dom.window.close();
}
console.log('PASS: all 51 exact event selections, geographic kinds, clustered chooser callbacks, filter synchronization, empty results and unavailable-library access. Provider pixels remain separate.');
