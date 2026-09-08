/* Run after images settle on the rendered topic page. Geometry detects stretched boxes even with object-fit containment. */
(() => {
 const main=document.querySelector('main');
 if(!main) throw new Error('A rendered topic page is required');
 const images=[...main.querySelectorAll('figure img,.fc-marriage-era img')].filter(im=>!im.closest('.fc-resource-card,dialog,.fc-topic-opening,.gc-intro'));
 const failures=[],measurements=[],distinct=new Set(),sections=new Set();
 for(const im of images){
  const r=im.getBoundingClientRect(),hint=getComputedStyle(im).getPropertyValue('--study-image-ratio').trim().split('/').map(Number);
  const nativeRatio=im.naturalWidth?im.naturalWidth/im.naturalHeight:(hint.length===2?hint[0]/hint[1]:Number(im.width)/Number(im.height));
  if(r.width<=0 || r.height<=0){failures.push({src:im.src,error:'Artwork has no reserved box before load'});continue;}
  const error=Math.abs((r.width/r.height)/nativeRatio-1);
  measurements.push({src:im.currentSrc,native:[im.naturalWidth,im.naturalHeight],rendered:[r.width,r.height],ratioError:error});
  if(error>.01) failures.push({src:im.currentSrc,error:'Rendered image box distorts intrinsic aspect ratio',ratioError:error});
  if(r.right>innerWidth+1 || r.left < -1) failures.push({src:im.currentSrc,error:'Image exceeds viewport'});
  const fig=im.closest('figure,.fc-marriage-era'),section=im.closest('section');
  if(fig?.textContent.trim()){
   const placement=fig.id || 'reading-'+[...main.querySelectorAll('figure,.fc-marriage-era')].indexOf(fig);
   const identity=new URL(im.getAttribute('src'),location.href).pathname.replace(/-(320|640|800|900|1200|1536|2048)(?=\.[^.]+$)/,'');
   if(!distinct.has(identity)){distinct.add(identity);sections.add(placement);}
  }
 }
 if(distinct.size<5) failures.push({error:'Fewer than five distinct contextual body pictures',count:distinct.size});
 if(sections.size<3) failures.push({error:'Body pictures are not distributed through three reading locations',count:sections.size});
 return {page:location.pathname,viewport:[innerWidth,innerHeight],pass:!failures.length,distinct:distinct.size,sections:sections.size,failures,measurements};
})();
