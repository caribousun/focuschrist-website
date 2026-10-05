/* Geographic context for chronology: no invented continuous journey. */
(function(){
  'use strict';
  var api=window.HistoryTimeline,data=window.HISTORY_LOCATIONS;
  var canvas=document.getElementById('historyMapCanvas'),status=document.getElementById('historyMapStatus'),summary=document.getElementById('historyMapSelection');
  if(!api||!data||!canvas)return;
  if(data.events.length!==api.events.length||data.events.some(function(r,i){return r.index!==i||r.expectedTitle!==api.events[i].title;})){
    status.textContent='Geographic context is unavailable. The complete event timeline remains usable.';return;
  }
  var map=null,layers=[],indices=api.visibleIndices(),selected=null,groups=[],generation=0,filterGeneration=0,tileLoaded=false,tileFailed=false,tileTimer=null;
  function description(index){
    var record=data.events[index];summary.replaceChildren();
    var heading=document.createElement('strong');heading.textContent=api.events[index].title;summary.appendChild(heading);
    var note=document.createElement('p');note.textContent=record.note;summary.appendChild(note);
    record.sources.forEach(function(url,i){var a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent='Church location source'+(record.sources.length>1?' '+(i+1):'');summary.appendChild(a);});
  }
  function choose(index){if(indices.indexOf(index)<0)return;api.select(index);if(map)map.closePopup();}
  function lowerChoices(title,eventIndices){
    var filterCaptured=filterGeneration;
    var workspace=window.TimelineWorkspace;
    if(!workspace||typeof workspace.showChoices!=='function')return false;
    var handled=workspace.showChoices(title,eventIndices.map(function(index){return {index:index,label:api.events[index].date+' \u2014 '+api.events[index].title};}),function(index){if(filterCaptured===filterGeneration&&eventIndices.indexOf(index)>=0)choose(index);});
    if(handled&&map)map.closePopup();return handled;
  }
  function icon(group){return L.divIcon({className:'history-map-icon',html:'<span class="history-map-pin'+(group.indices.indexOf(selected)>=0?' is-selected':'')+'">'+group.indices.length+'<small>'+(group.indices.length===1?'event':'events')+'</small></span>',iconSize:[58,44],iconAnchor:[29,22]});}
  function draw(){
    if(!map)return;
    generation++;
    layers.forEach(function(layer){map.removeLayer(layer);});layers=[];groups=[];
    var byPlace={};
    indices.forEach(function(index){data.events[index].places.forEach(function(key){(byPlace[key]||(byPlace[key]=[])).push(index);});});
    var candidates=Object.keys(byPlace).map(function(key){var p=data.places[key];return {key:key,point:map.latLngToContainerPoint([p.lat,p.lng])};});
    var clusters=[];
    candidates.forEach(function(candidate){
      var touching=clusters.filter(function(cluster){return cluster.some(function(member){return Math.hypot(member.point.x-candidate.point.x,member.point.y-candidate.point.y)<68;});});
      var cluster=[candidate];touching.forEach(function(old){cluster=cluster.concat(old);clusters.splice(clusters.indexOf(old),1);});clusters.push(cluster);
    });
    clusters.forEach(function(cluster){
      var keys=cluster.map(function(c){return c.key;}),eventIndices=[];
      keys.forEach(function(key){byPlace[key].forEach(function(i){if(eventIndices.indexOf(i)<0)eventIndices.push(i);});});eventIndices.sort(function(a,b){return a-b;});
      var place=data.places[keys[0]],group={keys:keys,indices:eventIndices};groups.push(group);
      var captured=generation;
      var title=keys.length===1?place.label:keys.length+' nearby places';
      var marker=L.marker([place.lat,place.lng],{icon:icon(group),keyboard:true,title:title+': '+eventIndices.length+' events; approximate context'});
      marker.on('click',function(){if(captured!==generation)return;if(eventIndices.length===1){if(window.TimelineWorkspace&&window.TimelineWorkspace.clearGroup)window.TimelineWorkspace.clearGroup();choose(eventIndices[0]);return;}lowerChoices(title,eventIndices);});
      marker.addTo(map);group.marker=marker;layers.push(marker);
    });
    // Regional extents remain visibly different from approximate place pins.
    var regionGroups={};
    indices.forEach(function(index){var r=data.events[index];if(r.kind==='region'){var key=r.region.label;(regionGroups[key]||(regionGroups[key]={region:r.region,indices:[]})).indices.push(index);}});
    Object.keys(regionGroups).forEach(function(key){var g=regionGroups[key],box=L.rectangle(g.region.bounds,{color:'#b87d24',weight:2,dashArray:'5 5',fillOpacity:.09});var captured=generation,title=g.region.label+' \u2014 regional context';box.on('click',function(event){if(captured!==generation)return;if(g.indices.length===1){if(window.TimelineWorkspace&&window.TimelineWorkspace.clearGroup)window.TimelineWorkspace.clearGroup();choose(g.indices[0]);return;}lowerChoices(title,g.indices);});box.addTo(map);layers.push(box);});
    var worldwide=indices.filter(function(i){return data.events[i].kind==='worldwide';}).length;
    status.textContent=(tileFailed?'Map imagery is unavailable here. Geographic markers and event descriptions remain usable. ':'')+indices.length+' matching events. '+Object.keys(byPlace).length+' approximate places; '+Object.keys(regionGroups).length+' contextual regions; '+worldwide+' worldwide events without pins.';
  }
  function reducedMotion(){return window.matchMedia('(prefers-reduced-motion: reduce)').matches;}
  function focus(index){
    var r=data.events[index];selected=index;description(index);
    if(!map)return;
    map.stop();
    groups.forEach(function(g){g.marker.setIcon(icon(g));});
    var immediate=reducedMotion();
    if(r.kind==='worldwide'){
      if(immediate)map.setView([20,0],2,{animate:false});else map.flyTo([20,0],2,{duration:.6});
      return;
    }
    if(r.kind==='region'){
      var regionOptions={padding:[24,24],maxZoom:7,animate:!immediate,duration:.8};
      if(immediate)map.fitBounds(r.region.bounds,regionOptions);else map.flyToBounds(r.region.bounds,regionOptions);
      return;
    }
    var points=r.places.map(function(key){var p=data.places[key];return[p.lat,p.lng];});
    if(points.length===1){
      var distance=map.distance(map.getCenter(),points[0]),zoom=map.getZoom();
      // These are approximate place locations: retain a nearby area view, never street-level precision.
      var targetZoom=distance<75000&&zoom>=8?Math.min(zoom,10):10;
      if(distance<25&&Math.abs(zoom-targetZoom)<.01)return;
      if(immediate)map.setView(points[0],targetZoom,{animate:false});else map.flyTo(points[0],targetZoom,{duration:.6});
    }else if(points.length){
      var options={padding:[30,30],maxZoom:10,animate:!immediate,duration:.8};
      if(immediate)map.fitBounds(L.latLngBounds(points),options);else map.flyToBounds(L.latLngBounds(points),options);
    }
  }
  function showMatching(){
    if(!map)return;
    map.stop();
    var points=[];indices.forEach(function(i){var r=data.events[i];r.places.forEach(function(key){var p=data.places[key];points.push([p.lat,p.lng]);});if(r.region)points.push.apply(points,r.region.bounds);});
    if(points.length)map.fitBounds(L.latLngBounds(points),{padding:[24,24],maxZoom:8,animate:false});else map.setView([20,0],2,{animate:false});
  }
  window.addEventListener('timeline:select',function(event){if(Number.isInteger(event.detail.index)&&data.events[event.detail.index])focus(event.detail.index);});
  window.addEventListener('timeline:filter',function(event){filterGeneration++;indices=event.detail.indices.slice();if(indices.indexOf(selected)<0){selected=null;summary.textContent='Choose an event or a map location to explore its geographic context.';}draw();showMatching();});
  document.getElementById('historyMapReset').addEventListener('click',showMatching);
  try{
    if(!window.L)throw new Error('Leaflet unavailable');
    map=L.map(canvas,{scrollWheelZoom:false,maxZoom:19}).setView([38,-70],3);
  // Keep live provider credits visible outside the interactive map canvas.
  if(map.attributionControl&&map.attributionControl.getContainer){var attribution=map.attributionControl.getContainer();attribution.classList.add('timeline-map-attribution');canvas.after(attribution);}
    var tileErrors=0;
    FCTerrainLayer().on('tileload',function(){var recovering=tileFailed;tileLoaded=true;tileFailed=false;clearTimeout(tileTimer);if(recovering)draw();}).on('tileerror',function(){tileLoaded=false;if(++tileErrors>=3){tileFailed=true;draw();}}).addTo(map);
    tileTimer=setTimeout(function(){if(!tileLoaded){tileFailed=true;draw();}},10000);
    window.addEventListener('pagehide',function(){clearTimeout(tileTimer);});
    map.on('zoomend',draw);
    draw();showMatching();
    canvas.addEventListener('timeline:map-resize',function(){map.invalidateSize({pan:false});});
    canvas.addEventListener('timeline:map-interaction',function(event){['dragging','touchZoom','doubleClickZoom'].forEach(function(name){var handler=map[name];if(handler)handler[event.detail.enabled?'enable':'disable']();});});
    if(window.ResizeObserver)new ResizeObserver(function(){map.invalidateSize({pan:false});}).observe(canvas);
  }catch(error){canvas.hidden=true;document.getElementById('historyMapReset').hidden=true;status.textContent='The map could not load. Every event and its geographic explanation remain available in the timeline and event list.';}
  if(Number.isInteger(api.selectedIndex))focus(api.selectedIndex);
  window.HistoryTimelineMap={select:choose,showMatching:showMatching,get visibleIndices(){return indices.slice();},get selectedIndex(){return selected;}};
})();
