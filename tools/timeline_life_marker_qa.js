/* Exercise actual Life of Christ marker callbacks after zoom/filter changes without a tile provider. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{JSDOM}=require('jsdom');
const html=fs.readFileSync(path.join(__dirname,'../timelines/life-of-christ-journey-map.html'),'utf8');
for(const narrow of [false,true]){
 const dom=new JSDOM(html,{url:'https://focuschrist.com/timelines/life-of-christ-journey-map.html',runScripts:'outside-only'}),w=dom.window,d=w.document;w.matchMedia=()=>({matches:narrow});w.HTMLElement.prototype.scrollIntoView=function(){};
 const layers=new Set(),markers=[],events={},tiles={};let zoom=8;const project=coords=>({x:(coords[1]+180)/360*(narrow?320:800),y:(90-coords[0])/180*500});
 const map={setView(){return this},on(names,fn){names.split(' ').forEach(n=>events[n]=fn);return this},getSize(){return {x:narrow?320:800,y:500}},latLngToContainerPoint:project,containerPointToLatLng(p){return {lng:p[0]/(narrow?320:800)*360-180,lat:90-p[1]/500*180}},scrollWheelZoom:{enable(){},disable(){}},hasLayer(x){return layers.has(x)},removeLayer(x){layers.delete(x)},getZoom(){return zoom},flyTo(coords,z){zoom=z;return this},fitBounds(){return this},flyToBounds(){return this},invalidateSize(){},zoomIn(){zoom++;if(events.zoomend)events.zoomend();return this}};
 w.L={map(){return map},tileLayer(){return {addTo(){return this},on(n,f){tiles[n]=f;return this}}},divIcon(v){return v},latLngBounds(){return {pad(){return this}}},polyline(){return {addTo(){return this},bringToBack(){}}},marker(coords,options){const el=d.createElement('div');el.innerHTML=options.icon.html;const m={coords,options,el,handlers:{},on(name,fn){this.handlers[name]=fn;return this},addTo(){layers.add(this);return this},getElement(){return el},setIcon(icon){this.options.icon=icon;el.innerHTML=icon.html;return this},setZIndexOffset(){return this}};markers.push(m);return m}};
 const source=[...d.scripts].find(s=>s.textContent.includes('var STOPS ='));assert(source);w.eval(source.textContent);assert.equal(markers.filter(m=>m.el.querySelector('.pin')).length,36);assert.equal(w.STOPS.length,38);assert(w.STOPS.slice(29,31).every(s=>s.lat===null&&s.lng===null&&s.unlocated),'Americas have no asserted geographic coordinates');assert(markers.every(m=>Number.isFinite(m.coords[0])&&Number.isFinite(m.coords[1])),'No null coordinate coerced into map pin');tiles.tileerror();tiles.tileerror();tiles.tileerror();const warning=[...d.querySelectorAll('.map-pin-note')].find(n=>n.getAttribute('role')==='status');assert(warning&&!warning.hidden&&warning.textContent.includes('imagery is unavailable'));assert.notEqual(d.getElementById('map').style.display,'none','Tile failure retains selectable geographic markers');tiles.tileload();assert(warning.hidden,'Recovered tiles clear warning');
 for(const phase of ['all','beginnings','ministry','final','risen','americas','restoration']){
  d.querySelector('#filters [data-filter="'+phase+'"]').click();map.zoomIn().zoomIn();
  const expected=w.STOPS.map((s,i)=>({s,i})).filter(x=>!x.s.unlocated&&(phase==='all'||x.s.phase===phase)).map(x=>x.i);
  const nativeExpected=Array.from(expected);
  assert.deepEqual(Array.from(w.LifeTimeline.mappedGroups).flat().sort((a,b)=>a-b),nativeExpected,'Every mapped index appears exactly once across singles and groups');
  let choices;w.TimelineWorkspace={scrollRow(){},showChoices(title,items,callback){choices={items,callback};},clearGroup(){},showStory(){}};
  for(const i of nativeExpected){
   const marker=markers.find(m=>layers.has(m)&&(m.lifeIndices?m.lifeIndices.includes(i):Number(m.el.querySelector('.pin')?.textContent)-1===i));assert(marker,'Every mapped event has a visible singleton or group');
   if(!marker.lifeIndices){assert.equal(marker.coords[0],w.STOPS[i].lat);assert.equal(marker.coords[1],w.STOPS[i].lng);marker.handlers.click();}else{marker.handlers.click();const saved=choices;assert(saved.items.some(x=>x.index===i));map.zoomIn();choices=null;marker.handlers.click();assert.equal(choices,null,'Detached marker callback is ignored after redraw');saved.callback(i);choices=saved;}
   assert.equal(w.LifeTimeline.current,i,'Every original mapped index selects exact story after zoom');assert.equal(d.querySelector('#dTitle').textContent,w.STOPS[i].title);
  }

  if(choices){const saved=choices;d.querySelector('#filters [data-filter="beginnings"]').click();const before=w.LifeTimeline.current;saved.callback(saved.items[0].index);assert.equal(w.LifeTimeline.current,before,'Filter invalidates detached choices');}

 }
 w.TimelineWorkspace=null;d.querySelector('#filters [data-filter="all"]').click();d.querySelector('#nextBtn').click();assert.equal(d.querySelector('#dNum').textContent,'2');d.querySelector('#prevBtn').click();assert.equal(d.querySelector('#dNum').textContent,'1');dom.window.close();
}
console.log('PASS: all36 geographic marker numbers across38 stories map to exact stories after zoom and every phase filter, desktop and phone callback paths. Provider rendering remains separate.');
