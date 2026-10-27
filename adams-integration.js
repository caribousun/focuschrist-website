/* Measure only the existing canonical header; retain the original chart engine. */
(function () {
 'use strict';
 function init() {
  if (!document.body.classList.contains('fc-adams-chart-page')) return;
  const header=document.querySelector('nav[data-focuschrist-header="standard"]');
  if (!header) return;
  // Reuse the engine's existing status node; the toolbar observer measures its row.
  const progress=document.getElementById('progress');
  const toolbar=document.getElementById('toolbar');
  // Keep an explicitly restored map below a reflowing toolbar.
  function syncToolbarHeight() {
   if(toolbar)document.documentElement.style.setProperty('--adams-toolbar-height',toolbar.getBoundingClientRect().height+'px');
  }
  if(toolbar && window.ResizeObserver)new ResizeObserver(syncToolbarHeight).observe(toolbar);
  window.addEventListener('resize',syncToolbarHeight,{passive:true});
  syncToolbarHeight();
  const originalParent=progress&&progress.parentNode;
  const originalNext=progress&&progress.nextSibling;
  const compact=window.matchMedia('(max-width:899px) and (max-height:700px)');
  function placeProgress() {
   if(!progress||!toolbar||!originalParent)return;
   const target=compact.matches?toolbar:originalParent;
   if(progress.parentNode===target)return;
   if(compact.matches)toolbar.appendChild(progress);
   else originalParent.insertBefore(progress,originalNext&&originalNext.parentNode===originalParent?originalNext:null);
   window.dispatchEvent(new Event('resize'));
  }
  compact.addEventListener('change',placeProgress);
  placeProgress();
  let last=0,frame=0;
  function sync() {
   cancelAnimationFrame(frame);
   frame=requestAnimationFrame(function () {
    const height=Math.ceil(header.getBoundingClientRect().height);
    if(height<=0||height===last)return;
    last=height;document.documentElement.style.setProperty('--adams-header-height',height+'px');
    window.dispatchEvent(new Event('resize'));
   });
  }
  if(window.ResizeObserver)new ResizeObserver(sync).observe(header);
  window.addEventListener('resize',sync,{passive:true});
  if(document.fonts)document.fonts.ready.then(sync);
  sync();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
}());
