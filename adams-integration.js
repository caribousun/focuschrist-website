/* Measure only the existing canonical header; retain the original chart engine. */
(function () {
 'use strict';
 function init() {
  if (!document.body.classList.contains('fc-adams-chart-page')) return;
  const header=document.querySelector('nav[data-focuschrist-header="standard"]');
  if (!header) return;
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
