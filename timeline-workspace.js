/* Measure the actual menu and keep selection scrolling inside the event pane. */
(function(){
  'use strict';
  var workspace=document.querySelector('[data-timeline-workspace]');
  if(!workspace)return;
  var header=document.querySelector('[data-focuschrist-header="standard"]');
  var map=document.getElementById('map')||document.getElementById('historyMapCanvas');
  var breakpoint=Number(workspace.getAttribute('data-mobile-breakpoint'))||900;
  var wide=window.matchMedia('(min-width:'+(breakpoint+1)+'px)');
  var events=workspace.querySelector('[data-timeline-pane="events"]');
  // Chromium can retain wheel scrolling in History's nested directory at its edge.
  // Handoff only after every containing scroll pane has exhausted this direction.
  if(events&&workspace.classList.contains('history-workspace'))events.addEventListener('wheel',function(event){
    if(!wide.matches||event.ctrlKey||event.shiftKey||!event.deltaY||Math.abs(event.deltaX)>Math.abs(event.deltaY))return;
    var down=event.deltaY>0;
    for(var node=event.target;node&&node!==document.body&&node!==document.documentElement;node=node.parentElement){
      var style=getComputedStyle(node),remaining=down?node.scrollHeight-node.clientHeight-node.scrollTop:node.scrollTop;
      if(/^(auto|scroll)$/.test(style.overflowY)&&remaining>1)return;
    }
    var delta=event.deltaY*(event.deltaMode===1?parseFloat(getComputedStyle(events).lineHeight)||16:event.deltaMode===2?window.innerHeight:1);
    event.preventDefault();window.scrollBy({top:delta,left:0,behavior:'instant'});
  },{passive:false});
  var story=workspace.querySelector('[data-timeline-pane="detail"],[data-timeline-pane="timeline"]');
  var choicePanel=null,previousEventScroll=0,group=null,groupNav=null;
  function clearChoices(){if(!choicePanel)return;choicePanel.remove();choicePanel=null;events.classList.remove('timeline-choice-mode');events.scrollTop=previousEventScroll;}
  function clearGroup(){clearChoices();group=null;if(groupNav)groupNav.remove();groupNav=null;workspace.classList.remove('timeline-group-active');}
  function selectGroup(index,context){if(group!==context||!context.choices.some(function(c){return c.index===index;}))return;clearChoices();context.onSelect(index);}
  function stepGroup(direction){if(!group)return false;var at=group.choices.findIndex(function(c){return c.index===group.selected;}),next=at+direction;if(at>=0&&next>=0&&next<group.choices.length)selectGroup(group.choices[next].index,group);return true;}
  function renderGroupNav(){
    var focusedAction=groupNav&&groupNav.contains(document.activeElement)?document.activeElement.getAttribute('data-group-action'):null;
    if(groupNav)groupNav.remove();groupNav=null;if(!group||!Number.isInteger(group.selected))return;
    var context=group,at=context.choices.findIndex(function(c){return c.index===context.selected;});if(at<0)return;
    var host=story;if(window.HistoryTimeline)host=document.getElementById('history-event-'+context.selected)||story;if(!host)return;
    groupNav=document.createElement('nav');groupNav.className='timeline-group-nav';groupNav.setAttribute('aria-label','Events at this map pin');
    var label=document.createElement('p');label.textContent=context.title+' · '+(at+1)+' of '+context.choices.length;groupNav.appendChild(label);
    var back=document.createElement('button');back.type='button';back.textContent="Back to this pin’s events";back.setAttribute('data-group-action','back');back.addEventListener('click',function(){if(group===context)renderChoices(context);});groupNav.appendChild(back);
    [-1,1].forEach(function(direction){var button=document.createElement('button');button.type='button';button.textContent=direction<0?'Previous event':'Next event';button.setAttribute('data-group-action',direction<0?'previous':'next');button.disabled=at+direction<0||at+direction>=context.choices.length;button.addEventListener('click',function(){if(group===context)stepGroup(direction);});groupNav.appendChild(button);});host.prepend(groupNav);if(focusedAction){var focusTarget=groupNav.querySelector('[data-group-action="'+focusedAction+'"]');(focusTarget&&!focusTarget.disabled?focusTarget:back).focus({preventScroll:true});}
  }
  function renderChoices(context){
    if(group!==context)return;clearChoices();previousEventScroll=events.scrollTop;
    choicePanel=document.createElement('div');choicePanel.className='timeline-place-choices';
    var heading=document.createElement('h3');heading.textContent=context.title;heading.tabIndex=-1;choicePanel.appendChild(heading);
    var back=document.createElement('button');back.type='button';back.className='timeline-choices-back';back.textContent='Back to all matching events';back.addEventListener('click',function(){if(group===context)clearGroup();});choicePanel.appendChild(back);
    context.choices.forEach(function(choice){var button=document.createElement('button');button.type='button';button.textContent=choice.label;if(choice.index===context.selected)button.setAttribute('aria-current','true');button.addEventListener('click',function(){selectGroup(choice.index,context);});choicePanel.appendChild(button);});
    events.classList.add('timeline-choice-mode');events.appendChild(choicePanel);showView('events');events.scrollTop=0;heading.focus({preventScroll:true});revealReader();
  }
  function showChoices(title,choices,onSelect){
    if(!events)return false;clearGroup();group={title:title,choices:choices.map(function(c){return {index:c.index,label:c.label};}),onSelect:onSelect,selected:null};workspace.classList.add('timeline-group-active');renderChoices(group);return true;
  }
  var tabs=document.createElement('div');
  tabs.className='timeline-mobile-tabs';tabs.setAttribute('aria-label','Study view');
  tabs.innerHTML='<button type="button" data-study-view="events" aria-pressed="true">Events</button><button type="button" data-study-view="story" aria-pressed="false">Story</button><button type="button" class="timeline-map-toggle" aria-expanded="true">Collapse map</button>';
  var mapPane=workspace.querySelector('[data-timeline-pane="map"]');
  var dock=document.createElement('div');dock.className='timeline-map-dock';
  if(mapPane){mapPane.before(dock);dock.appendChild(mapPane);}else workspace.appendChild(dock);
  var interact=document.createElement('button');interact.type='button';interact.className='timeline-map-interact';interact.textContent='Interact with map';interact.setAttribute('aria-pressed','false');dock.appendChild(interact);dock.appendChild(tabs);
  var interacting=false;
  function mapInteraction(enabled){interacting=!wide.matches&&enabled;interact.textContent=interacting?'Done moving map':'Interact with map';interact.setAttribute('aria-pressed',String(interacting));dock.classList.toggle('timeline-map-passive',!wide.matches&&!interacting);if(map)map.dispatchEvent(new CustomEvent('timeline:map-interaction',{detail:{enabled:wide.matches||interacting}}));}
  interact.addEventListener('click',function(){mapInteraction(!interacting);});
  var notes=document.createElement('details');notes.className='timeline-map-notes';notes.innerHTML='<summary>Map information</summary>';dock.after(notes);
  var noteItems=mapPane?Array.from(mapPane.querySelectorAll('.history-map-copy,.legend,.map-pin-note')).map(function(node){var placeholder=document.createComment('map information position');node.before(placeholder);return {node:node,placeholder:placeholder};}):[];
  var controls=workspace.querySelector('.controls'),filters=null;
  if(controls){filters=document.createElement('details');filters.className='timeline-filter-disclosure';var filterSummary=document.createElement('summary');filterSummary.textContent=workspace.classList.contains('history-workspace')?'Search and filter events':'Filter journey';filters.appendChild(filterSummary);controls.before(filters);filters.appendChild(controls);}
  function syncLayout(){workspace.classList.toggle('timeline-mobile',!wide.matches);clearChoices();renderGroupNav();if(filters)filters.open=wide.matches;notes.hidden=wide.matches||!noteItems.length;noteItems.forEach(function(item){if(wide.matches)item.placeholder.after(item.node);else notes.appendChild(item.node);});mapInteraction(false);schedule();}
  function revealReader(){if(wide.matches)return;requestAnimationFrame(function(){var target=workspace.dataset.mobileView==='story'?story:events;if(!target)return;if(target===story&&window.HistoryTimeline){target=document.getElementById('history-event-'+window.HistoryTimeline.selectedIndex)||target;}var headerHeight=header?header.getBoundingClientRect().height:0;var dockHeight=getComputedStyle(dock).position==='sticky'?dock.getBoundingClientRect().height:0;window.scrollTo({top:scrollY+target.getBoundingClientRect().top-headerHeight-dockHeight-12,behavior:'instant'});});}

  workspace.setAttribute('data-mobile-view','events');
  function showView(view){
    if(view==='story')clearChoices();
    workspace.setAttribute('data-mobile-view',view);
    tabs.querySelectorAll('[data-study-view]').forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-study-view')===view));});
    if(wide.matches&&view==='story'&&story&&story.getAttribute('data-timeline-pane')==='detail')story.scrollTop=0;
  }
  tabs.querySelectorAll('[data-study-view]').forEach(function(b){b.addEventListener('click',function(){if(b.getAttribute('data-study-view')==='events'&&group)renderChoices(group);else{showView(b.getAttribute('data-study-view'));revealReader();}});});
  var mapToggle=tabs.querySelector('.timeline-map-toggle');
  function collapseMap(collapsed){workspace.classList.toggle('timeline-map-collapsed',collapsed);mapToggle.textContent=collapsed?'Show map':'Collapse map';if(collapsed)mapInteraction(false);mapToggle.setAttribute('aria-expanded',String(!collapsed));schedule();}
  mapToggle.addEventListener('click',function(){collapseMap(!workspace.classList.contains('timeline-map-collapsed'));});
  if(window.innerHeight<560)collapseMap(true);
  window.addEventListener('timeline:select',function(e){if(group){if(e.detail&&group.choices.some(function(c){return c.index===e.detail.index;})){group.selected=e.detail.index;renderGroupNav();}else clearGroup();}if(!wide.matches&&(!e.detail||e.detail.showStory!==false)){showView('story');revealReader();}});
  window.addEventListener('timeline:filter',function(){clearGroup();if(!wide.matches)showView('events');});
  var previousMapSize='',wasUnavailable=false;
  var pending=false;
  function fitHeader(){
    if(!header)return;
    var logo=header.querySelector('.nav-logo'),controls=header.querySelector('.hamburger-wrap');
    if(!logo||!controls)return;
    var narrow=window.matchMedia('(max-width:1020px)').matches;
    var style=getComputedStyle(header),available=header.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
    // Intrinsic wordmark width remains independent of the wrapped layout.
    var textRange=document.createRange();textRange.selectNodeContents(logo);
    var needed=textRange.getBoundingClientRect().width+controls.scrollWidth+12;
    header.classList.toggle('timeline-header-wrap',narrow&&needed>available);
  }
  function measure(){
    pending=false;
    fitHeader();
    var height=header?header.getBoundingClientRect().height:0;
    workspace.style.setProperty('--timeline-menu-height',Math.ceil(height)+'px');workspace.style.setProperty('--timeline-dock-height',Math.ceil(dock.getBoundingClientRect().height)+'px');
    if(map){
      var unavailable=map.hidden||!!map.querySelector('.map-fallback')||!!(document.getElementById('mapFallback')&&!document.getElementById('mapFallback').hidden&&getComputedStyle(document.getElementById('mapFallback')).display!=='none');dock.classList.toggle('timeline-map-unavailable',unavailable);if(unavailable&&!wasUnavailable&&!wide.matches&&noteItems.length)notes.open=true;wasUnavailable=unavailable;var rect=map.getBoundingClientRect();
      var size=rect.width+':'+rect.height;
      if(size!==previousMapSize){
        previousMapSize=size;
        map.dispatchEvent(new Event('timeline:map-resize'));
        // Hatch's renderer listens to browser resize; Leaflet uses the event above.
        window.dispatchEvent(new Event('resize'));
      }
    }
  }
  function schedule(){if(!pending){pending=true;requestAnimationFrame(measure);}}
  function alignEntry(){
    var ready=document.fonts ? document.fonts.ready : Promise.resolve();
    ready.then(function(){
      requestAnimationFrame(function(){requestAnimationFrame(function(){
        measure();
        var offset=(header?header.getBoundingClientRect().height:0)+12;
        window.scrollTo({top:window.scrollY+workspace.getBoundingClientRect().top-offset,behavior:'instant'});
        // A final layout frame includes map sizing without following later selections.
        requestAnimationFrame(function(){
          var remaining=workspace.getBoundingClientRect().top-((header?header.getBoundingClientRect().height:0)+12);
          if(Math.abs(remaining)>1)window.scrollTo({top:window.scrollY+remaining,behavior:'instant'});
        });
      });});
    });
  }
  document.querySelectorAll('a[href="#'+workspace.id+'"]').forEach(function(anchor){
    anchor.addEventListener('click',function(event){
      if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
      event.preventDefault();
      if(location.hash!=='#'+workspace.id)history.pushState(null,'','#'+workspace.id);
      alignEntry();
    });
  });
  if(window.ResizeObserver){var observer=new ResizeObserver(schedule);if(header){observer.observe(header);var logo=header.querySelector('.nav-logo');if(logo)observer.observe(logo);}observer.observe(workspace);if(map)observer.observe(map);}
  window.addEventListener('resize',schedule);
  wide.addEventListener('change',syncLayout);
  if(window.visualViewport)window.visualViewport.addEventListener('resize',schedule);
  window.TimelineWorkspace={showChoices:showChoices,clearChoices:clearGroup,clearGroup:clearGroup,stepGroup:stepGroup,showStory:function(){clearChoices();if(!wide.matches)showView('story');},showEvents:function(){if(group)renderChoices(group);else{clearChoices();showView('events');}},scrollRow:function(row){
    var pane=row.closest('[data-timeline-pane="events"]');
    if(!pane||!wide.matches){row.scrollIntoView({block:'nearest'});return;}
    var p=pane.getBoundingClientRect(),r=row.getBoundingClientRect();
    if(r.top<p.top)pane.scrollTop-=p.top-r.top+3;
    else if(r.bottom>p.bottom)pane.scrollTop+=r.bottom-p.bottom+3;
  }};
  if(window.MutationObserver&&mapPane)new MutationObserver(schedule).observe(mapPane,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});
  syncLayout();
  if(!wide.matches&&window.HistoryTimeline&&Number.isInteger(window.HistoryTimeline.selectedIndex))showView('story');
})();
