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
  var story=workspace.querySelector('[data-timeline-pane="detail"],[data-timeline-pane="timeline"]');
  var choicePanel=null,previousEventScroll=0;
  function clearChoices(){if(!choicePanel)return;choicePanel.remove();choicePanel=null;events.classList.remove('timeline-choice-mode');events.scrollTop=previousEventScroll;}
  function showChoices(title,choices,onSelect){
    if(wide.matches||!events)return false;
    clearChoices();previousEventScroll=events.scrollTop;
    choicePanel=document.createElement('div');choicePanel.className='timeline-place-choices';
    var heading=document.createElement('h3');heading.textContent=title;heading.tabIndex=-1;choicePanel.appendChild(heading);
    var back=document.createElement('button');back.type='button';back.className='timeline-choices-back';back.textContent='Back to all matching events';back.addEventListener('click',function(){clearChoices();});choicePanel.appendChild(back);
    choices.forEach(function(choice){var button=document.createElement('button');button.type='button';button.textContent=choice.label;button.addEventListener('click',function(){clearChoices();onSelect(choice.index);});choicePanel.appendChild(button);});
    events.classList.add('timeline-choice-mode');events.appendChild(choicePanel);showView('events');events.scrollTop=0;heading.focus({preventScroll:true});return true;
  }
  var tabs=document.createElement('div');
  tabs.className='timeline-mobile-tabs';tabs.setAttribute('aria-label','Study view');
  tabs.innerHTML='<button type="button" data-study-view="events" aria-pressed="true">Events</button><button type="button" data-study-view="story" aria-pressed="false">Story</button><button type="button" class="timeline-map-toggle" aria-expanded="true">Collapse map</button>';
  workspace.appendChild(tabs);
  workspace.setAttribute('data-mobile-view','events');
  function showView(view){
    if(view==='story')clearChoices();
    workspace.setAttribute('data-mobile-view',view);
    tabs.querySelectorAll('[data-study-view]').forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-study-view')===view));});
    if(view==='story'&&story&&story.getAttribute('data-timeline-pane')==='detail')story.scrollTop=0;
  }
  tabs.querySelectorAll('[data-study-view]').forEach(function(b){b.addEventListener('click',function(){showView(b.getAttribute('data-study-view'));});});
  var mapToggle=tabs.querySelector('.timeline-map-toggle');
  function collapseMap(collapsed){workspace.classList.toggle('timeline-map-collapsed',collapsed);mapToggle.textContent=collapsed?'Show map':'Collapse map';mapToggle.setAttribute('aria-expanded',String(!collapsed));schedule();}
  mapToggle.addEventListener('click',function(){collapseMap(!workspace.classList.contains('timeline-map-collapsed'));});
  if(window.innerHeight<560)collapseMap(true);
  window.addEventListener('timeline:select',function(e){if(!wide.matches&&(!e.detail||e.detail.showStory!==false))showView('story');});
  window.addEventListener('timeline:filter',function(){clearChoices();if(!wide.matches)showView('events');});
  var previousMapSize='';
  var pending=false;
  function measure(){
    pending=false;
    var height=header?header.getBoundingClientRect().height:0;
    workspace.style.setProperty('--timeline-menu-height',Math.ceil(height)+'px');
    if(map){
      var rect=map.getBoundingClientRect();
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
  if(window.ResizeObserver){var observer=new ResizeObserver(schedule);if(header)observer.observe(header);observer.observe(workspace);if(map)observer.observe(map);}
  window.addEventListener('resize',schedule);
  wide.addEventListener('change',clearChoices);
  if(window.visualViewport)window.visualViewport.addEventListener('resize',schedule);
  window.TimelineWorkspace={showChoices:showChoices,clearChoices:clearChoices,showStory:function(){clearChoices();if(!wide.matches)showView('story');},showEvents:function(){clearChoices();showView('events');},scrollRow:function(row){
    var pane=row.closest('[data-timeline-pane="events"]');
    if(!pane){row.scrollIntoView({block:'nearest'});return;}
    var p=pane.getBoundingClientRect(),r=row.getBoundingClientRect();
    if(r.top<p.top)pane.scrollTop-=p.top-r.top+3;
    else if(r.bottom>p.bottom)pane.scrollTop+=r.bottom-p.bottom+3;
  }};
  schedule();
})();
