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
  document.querySelectorAll('a[href="#journeyWorkspace"]').forEach(function(anchor){
    anchor.addEventListener('click',function(event){
      if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
      event.preventDefault();
      if(location.hash!=='#journeyWorkspace')history.pushState(null,'','#journeyWorkspace');
      alignEntry();
    });
  });
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
