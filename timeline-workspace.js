/* Measure the actual menu and keep selection scrolling inside the event pane. */
(function(){
  'use strict';
  var workspace=document.querySelector('[data-timeline-workspace]');
  if(!workspace)return;
  var header=document.querySelector('[data-focuschrist-header="standard"]');
  var map=document.getElementById('map');
  var wide=window.matchMedia('(min-width:901px)');
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
  if(window.ResizeObserver){var observer=new ResizeObserver(schedule);if(header)observer.observe(header);observer.observe(workspace);if(map)observer.observe(map);}
  window.addEventListener('resize',schedule);
  if(window.visualViewport)window.visualViewport.addEventListener('resize',schedule);
  window.TimelineWorkspace={scrollRow:function(row){
    var pane=row.closest('[data-timeline-pane="events"]');
    if(!wide.matches||!pane){row.scrollIntoView({block:'nearest'});return;}
    var p=pane.getBoundingClientRect(),r=row.getBoundingClientRect();
    if(r.top<p.top)pane.scrollTop-=p.top-r.top+3;
    else if(r.bottom>p.bottom)pane.scrollTop+=r.bottom-p.bottom+3;
  }};
  schedule();
})();
