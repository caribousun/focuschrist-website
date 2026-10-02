/* Execute the production inline adapter against a deterministic Leaflet boundary; no browser/provider claims. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{JSDOM}=require('jsdom');
const html=fs.readFileSync(path.join(__dirname,'../timelines/willie-and-martin-handcart-map.html'),'utf8');
function setup(provider=true){
 const dom=new JSDOM(html,{url:'https://focuschrist.com/timelines/willie-and-martin-handcart-map.html',runScripts:'outside-only'}),w=dom.window,d=w.document;
 w.HTMLElement.prototype.scrollIntoView=function(){};w.matchMedia=()=>({matches:true});
 const state={markers:[],routes:[],events:[],filters:[],shows:0,invalidations:0,removed:0,fits:[],flies:[],layers:new Set(),handlers:{},tile:{},popup:null};
 w.TimelineWorkspace={showStory(){state.shows++;},scrollRow(){}};
 w.addEventListener('timeline:select',e=>state.events.push(e.detail));w.addEventListener('timeline:filter',e=>state.filters.push(e.detail));
 const map={setView(){return this;},on(names,fn){names.split(' ').forEach(n=>state.handlers[n]=fn);return this;},getZoom(){return 5;},flyTo(coords,zoom){state.flies.push({coords,zoom});return this;},fitBounds(coords,options){state.fits.push({coords,options});return this;},latLngToContainerPoint(coords){return {x:coords[1]*5,y:coords[0]*5};},hasLayer(m){return state.layers.has(m);},removeLayer(m){state.layers.delete(m);},closePopup(){state.popup=null;},invalidateSize(){state.invalidations++;},remove(){state.removed++;}};
 if(provider)w.L={map(renderer){state.renderer=renderer;state.child=d.createElement('div');renderer.appendChild(state.child);return map;},tileLayer(url){state.url=url;return {on(n,fn){state.tile[n]=fn;return this;},addTo(){return this;}};},geoJSON(data,options){state.routes.push({data,options});return {addTo(){return this;}};},divIcon:o=>o,latLngBounds:x=>x,marker(coords,options){const element=d.createElement('div');element.innerHTML=options.icon.html;const m={coords,options,handlers:{},element,on(n,fn){this.handlers[n]=fn;return this;},addTo(){state.layers.add(this);return this;},setIcon(icon){this.options.icon=icon;element.innerHTML=icon.html;return this;},getElement(){return element;}};state.markers.push(m);return m;},popup(){return {setLatLng(){return this;},setContent(content){this.content=content;return this;},openOn(){state.popup=this.content;return this;}};}};
 w.eval([...d.scripts].find(s=>s.textContent.includes('var STOPS =')).textContent);
 w.eval(fs.readFileSync(path.join(__dirname,'../timeline-images.js'),'utf8'));
 return {dom,w,d,state,close(){w.dispatchEvent(new w.Event('pagehide'));dom.window.close();}};
}
const t=setup(),{w,d,state:s}=t,original=s.markers.filter(m=>m.options.title.startsWith('Stop '));
assert.equal(original.length,33);assert.equal(s.routes.length,4);assert.equal(s.url,'https://tile.openstreetmap.org/{z}/{x}/{y}.png');
const coordinates=original.map(m=>JSON.stringify(m.coords));assert.equal(coordinates[0],'[53.4084,-2.9916]');
assert.equal(w.HandcartTimeline.current,0);assert.equal(s.events.at(-1).showStory,false);assert.equal(s.shows,0);
const titles=new Map([...d.querySelectorAll('.stop-card')].map(c=>[Number(c.dataset.stopIndex),c.querySelector('h3').textContent]));
function selected(i){assert.equal(w.HandcartTimeline.current,i);assert.equal(d.querySelector('#detail-title').textContent,titles.get(i));assert(d.querySelector('#detail-kicker').textContent.startsWith('Stop '+(i+1)+' of 33'));assert.equal(s.events.at(-1).index,i);}
for(const filter of ['all','willie','martin','shared','sea']){
 d.querySelector('[data-filter="'+filter+'"]').click();const cards=[...d.querySelectorAll('.stop-card')],visible=cards.map(c=>Number(c.dataset.stopIndex));
 assert.deepEqual(Array.from(s.filters.at(-1).indices),visible);assert.equal(s.events.at(-1).showStory,false);
 const firstImage=w.TimelineImages.registry.handcart[visible[0]],figure=d.querySelector('[data-timeline-image]');assert.equal(!!figure,!!firstImage,'Filter clears old image before selecting its first new story');if(firstImage){assert.equal(Number(figure.dataset.timelineImage),visible[0]);assert.equal(figure.querySelector('img').getAttribute('src'),firstImage.src);}
 for(const c of cards){const i=Number(c.dataset.stopIndex);assert.equal(Number(c.querySelector('.stop-num').textContent),i+1);original[i].handlers.click();selected(i);assert.equal(s.events.at(-1).showStory,true);}
 const hidden=original.findIndex((_,i)=>!visible.includes(i));if(hidden>=0){const before=w.HandcartTimeline.current;original[hidden].handlers.click();assert.equal(w.HandcartTimeline.current,before);}
 cards[0].click();const i=Number(cards[0].dataset.stopIndex);selected(i);assert.equal(JSON.stringify(s.flies.at(-1).coords),coordinates[i]);assert(s.flies.at(-1).zoom>=6);
 s.handlers.zoomend();assert.deepEqual(original.map(m=>JSON.stringify(m.coords)),coordinates);
}
d.querySelector('[data-filter="all"]').click();
const cluster=[...s.layers].find(m=>m.options.title.includes('nearby'));assert(cluster);assert.equal(cluster.options.icon.iconSize[0],44);cluster.handlers.click();
let popup=s.popup;assert(popup);const choice=popup.querySelector('button'),index=Number(choice.textContent.match(/^\d+/)[0])-1;choice.click();selected(index);
// Detached popup and old cluster callbacks cannot select or zoom after a filter rebuild.
const liveCluster=[...s.layers].find(m=>m.options.title.includes('nearby'));liveCluster.handlers.click();popup=s.popup;const staleButtons=[...popup.querySelectorAll('button')];
d.querySelector('[data-filter="willie"]').click();const before=w.HandcartTimeline.current,fitCount=s.fits.length;staleButtons.forEach(b=>b.click());liveCluster.handlers.click();assert.equal(w.HandcartTimeline.current,before);assert.equal(s.fits.length,fitCount);assert.equal(s.popup,null);
const visibleNow=[...d.querySelectorAll('.stop-card')].map(c=>Number(c.dataset.stopIndex));const hiddenIndex=original.findIndex((_,i)=>!visibleNow.includes(i));assert(hiddenIndex>=0);w.HandcartTimeline.select(hiddenIndex);selected(hiddenIndex);assert.equal(d.querySelector('[data-filter="all"]').getAttribute('aria-pressed'),'true');
// On phones, the production cluster delegates exact numbered choices to the lower reader.
let mobileChoices=null;w.TimelineWorkspace.showChoices=(title,choices,select)=>{mobileChoices={title,choices,select};return true;};
d.querySelector('[data-filter="all"]').click();let phoneCluster=[...s.layers].find(m=>m.options.title.includes('nearby'));phoneCluster.handlers.click();assert(mobileChoices);assert.equal(s.popup,null,'Phone uses lower reader chooser, not clipped map popup');
const firstChoice=mobileChoices.choices[0];assert.equal(firstChoice.label,(firstChoice.index+1)+'. '+titles.get(firstChoice.index));s.handlers.zoomend();mobileChoices.select(firstChoice.index);selected(firstChoice.index);assert.equal(w.HandcartTimeline.current,firstChoice.index,'Visible chooser survives benign map zoom');
phoneCluster=[...s.layers].find(m=>m.options.title.includes('nearby'));phoneCluster.handlers.click();const staleChoice=mobileChoices;d.querySelector('[data-filter="martin"]').click();const selectionBeforeStale=w.HandcartTimeline.current;staleChoice.select(staleChoice.choices[0].index);assert.equal(w.HandcartTimeline.current,selectionBeforeStale,'Detached phone chooser ignores stale selection');
for(let n=0;n<4;n++)s.tile.tileerror();assert.equal(d.querySelectorAll('.map-fallback').length,1);assert(s.renderer.hidden);assert.equal(s.child.parentNode,s.renderer);
d.querySelector('[data-filter="martin"]').click();assert.equal(s.removed,0);assert.equal(s.markers.filter(m=>m.options.title.startsWith('Stop ')).length,33);assert.equal(d.querySelectorAll('.map-fallback').length,1);
s.tile.tileload();assert.equal(d.querySelectorAll('.map-fallback').length,0);assert(!s.renderer.hidden);assert(s.invalidations>0);
const invalidations=s.invalidations;d.querySelector('#map').dispatchEvent(new w.Event('timeline:map-resize'));assert.equal(s.invalidations,invalidations+1);
t.close();assert.equal(s.removed,1);s.tile.tileerror();s.tile.tileload();assert.equal(s.removed,1);
const absent=setup(false);assert.equal(absent.d.querySelectorAll('.map-fallback').length,1);assert.equal(absent.d.querySelectorAll('.stop-card').length,33);absent.d.querySelector('[data-filter="sea"]').click();assert(absent.d.querySelectorAll('.stop-card').length>0);absent.w.HandcartTimeline.select(32);assert.equal(absent.w.HandcartTimeline.current,32);assert(absent.d.querySelector('#detail-body').textContent.length>100);assert.equal(absent.d.querySelectorAll('.map-fallback').length,1);absent.close();
console.log('PASS: persistent Leaflet ownership, all 33 immutable pin/story identities through filters/zoom, cluster choices and stale-callback rejection, row recentering, selection events, provider failure/recovery and library-absent reading.');
