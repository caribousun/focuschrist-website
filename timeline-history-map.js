/* Geographic context for chronology: no invented continuous journey. */
(function(){
  'use strict';
  var api=window.HistoryTimeline,data=window.HISTORY_LOCATIONS;
  var canvas=document.getElementById('historyMapCanvas'),status=document.getElementById('historyMapStatus'),summary=document.getElementById('historyMapSelection');
  if(!api||!data||!canvas)return;
  if(data.events.length!==api.events.length||data.events.some(function(r,i){return r.index!==i||r.expectedTitle!==api.events[i].title;})){
    status.textContent='Geographic context is unavailable. The complete event timeline remains usable.';return;
  }
  var map=null,layers=[],indices=api.visibleIndices(),selected=null,groups=[],generation=0,tileLoaded=false,tileFailed=false,tileTimer=null;
  function description(index){
    var record=data.events[index];summary.replaceChildren();
    var heading=document.createElement('strong');heading.textContent=api.events[index].title;summary.appendChild(heading);
    var note=document.createElement('p');note.textContent=record.note;summary.appendChild(note);
    record.sources.forEach(function(url,i){var a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent='Church location source'+(record.sources.length>1?' '+(i+1):'');summary.appendChild(a);});
  }
  function choose(index){if(indices.indexOf(index)<0)return;api.select(index);if(map)map.closePopup();}
  function chooser(title,eventIndices){
    var captured=generation;
    var box=document.createElement('div');box.className='history-map-choices';
    var strong=document.createElement('strong');strong.textContent=title;box.appendChild(strong);
    eventIndices.forEach(function(index){var button=document.createElement('button');button.type='button';button.dataset.historyEvent=index;button.textContent=api.events[index].date+' â€” '+api.events[index].title;button.addEventListener('click',function(){if(captured===generation)choose(index);});box.appendChild(button);});
    return box;
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
      var popup=chooser(title,eventIndices);
      if(keys.length>1){var zoom=document.createElement('button');zoom.type='button';zoom.textContent='Zoom to these places';zoom.addEventListener('click',function(){if(captured!==generation)return;map.fitBounds(L.latLngBounds(keys.map(function(key){var p=data.places[key];return[p.lat,p.lng];})),{padding:[35,35],maxZoom:13});});popup.prepend(zoom);}
      var marker=L.marker([place.lat,place.lng],{icon:icon(group),keyboard:true,title:title+': '+eventIndices.length+' events; approximate context'});
      marker.bindPopup(popup,{maxHeight:240,maxWidth:300});
      marker.on('click',function(){if(captured!==generation)return;if(eventIndices.length===1)choose(eventIndices[0]);});
      marker.addTo(map);group.marker=marker;layers.push(marker);
    });
    // Regional extents remain visibly different from approximate place pins.
    var regionGroups={};
    indices.forEach(function(index){var r=data.events[index];if(r.kind==='region'){var key=r.region.label;(regionGroups[key]||(regionGroups[key]={region:r.region,indices:[]})).indices.push(index);}});
    Object.keys(regionGroups).forEach(function(key){var g=regionGroups[key],box=L.rectangle(g.region.bounds,{color:'#b87d24',weight:2,dashArray:'5 5',fillOpacity:.09});box.bindPopup(chooser(g.region.label+' â€” regional context',g.indices),{maxHeight:240});box.addTo(map);layers.push(box);});
    var worldwide=indices.filter(function(i){return data.events[i].kind==='worldwide';}).length;
    status.textContent=(tileFailed?'Map imagery is unavailable here. Geographic markers and event descriptions remain usable. ':'')+indices.length+' matching events. '+Object.keys(byPlace).length+' approximate places; '+Object.keys(regionGroups).length+' contextual regions; '+worldwide+' worldwide events without pins.';
  }
  function focus(index){
    var r=data.events[index];selected=index;description(index);
    if(!map)return;
    groups.forEach(function(g){g.marker.setIcon(icon(g));});
    if(r.kind==='worldwide'){map.setView([20,0],2);return;}
    if(r.kind==='region'){map.fitBounds(r.region.bounds,{padding:[24,24],maxZoom:7});return;}
    var points=r.places.map(function(key){var p=data.places[key];return[p.lat,p.lng];});
    if(points.length)map.fitBounds(L.latLngBounds(points),{padding:[30,30],maxZoom:10});
  }
  function showMatching(){
    if(!map)return;
    var points=[];indices.forEach(function(i){var r=data.events[i];r.places.forEach(function(key){var p=data.places[key];points.push([p.lat,p.lng]);});if(r.region)points.push.apply(points,r.region.bounds);});
    if(points.length)map.fitBounds(L.latLngBounds(points),{padding:[24,24],maxZoom:8});else map.setView([20,0],2);
  }
  window.addEventListener('timeline:select',function(event){if(Number.isInteger(event.detail.index)&&data.events[event.detail.index])focus(event.detail.index);});
  window.addEventListener('timeline:filter',function(event){indices=event.detail.indices.slice();if(indices.indexOf(selected)<0){selected=null;summary.textContent='Choose an event or a map location to explore its geographic context.';}draw();showMatching();});
  document.getElementById('historyMapReset').addEventListener('click',showMatching);
  try{
    if(!window.L)throw new Error('Leaflet unavailable');
    map=L.map(canvas,{scrollWheelZoom:false}).setView([38,-70],3);
    var tileErrors=0;
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'}).on('tileload',function(){var recovering=tileFailed;tileLoaded=true;tileFailed=false;clearTimeout(tileTimer);if(recovering)draw();}).on('tileerror',function(){if(++tileErrors>=3&&!tileLoaded){tileFailed=true;draw();}}).addTo(map);
    tileTimer=setTimeout(function(){if(!tileLoaded){tileFailed=true;draw();}},10000);
    window.addEventListener('pagehide',function(){clearTimeout(tileTimer);});
    map.on('zoomend',draw);
    draw();showMatching();
    canvas.addEventListener('timeline:map-resize',function(){map.invalidateSize({pan:false});});
    if(window.ResizeObserver)new ResizeObserver(function(){map.invalidateSize({pan:false});}).observe(canvas);
  }catch(error){canvas.hidden=true;status.textContent='The map could not load. Every event and its geographic explanation remain available in the timeline and event list.';}
  window.HistoryTimelineMap={select:choose,showMatching:showMatching,get visibleIndices(){return indices.slice();},get selectedIndex(){return selected;}};
})();
