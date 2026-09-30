/* Owner-requested reading balance, using unchanged original images and prose. */
const assert=require('node:assert/strict');
module.exports=async function(page,origin){
  const records=[];
  for(const [width,enlarged] of [[320,false],[390,false],[1366,false],[1920,false],[390,true],[1366,true]]){
    await page.setViewportSize({width,height:1000});
    for(const route of ['atonement.html','answers/bible-and-book-of-mormon-together.html']){
      await page.goto(origin+'/'+route,{waitUntil:'load'});
      await page.locator('.fc-unified-continue').waitFor({state:'visible'});
      if(enlarged)await page.evaluate(()=>document.documentElement.style.fontSize='200%');
      await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
      const data=await page.evaluate(()=>{
        const box=n=>{const r=n.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};};
        const hero=document.querySelector('.fc-visual-hero');const before=box(hero);
        const style=document.querySelector('link[href*="study-reading-balance.css"]');const original=before;
        const result={viewport:document.documentElement.clientWidth,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,hero:before,originalHero:original,
          welcome:[...document.querySelectorAll('.atonement-welcome > p:not(.fc-eyebrow)')].map(n=>({box:box(n),max:parseFloat(getComputedStyle(n).maxWidth)})),
          scenes:[...document.querySelectorAll('.fc-bible-scene')].map(n=>{const f=n.querySelector('figure'),r=n.querySelector('.fc-bible-scene-reading'),i=f.querySelector('img'),c=f.querySelector('figcaption');return {id:n.id,figure:box(f),reading:box(r),image:box(i),caption:box(c),columns:getComputedStyle(f).gridTemplateColumns.split(' ').length,ratio:Number(i.getAttribute('width'))/Number(i.getAttribute('height')),clipped:[r,c].some(x=>x.scrollWidth>x.clientWidth+1)};})};
        style.disabled=true;result.originalHero=box(hero);style.disabled=false;return result;
      });
      assert(!data.overflow,route+' horizontal overflow '+width);
      assert.deepEqual(data.hero,data.originalHero,route+' reading rules must not alter hero');
      if(route==='atonement.html'){
        assert.equal(data.welcome.length,3);
        for(const p of data.welcome){assert(Number.isFinite(p.max)&&p.box.width<=p.max+1,'Welcome readable line length');assert(Math.abs((p.box.left+p.box.right)/2-data.viewport/2)<2,'Welcome paragraphs centered');}
      }else{
        assert.equal(data.scenes.length,13,'All thirteen related scene cards reviewed');
        for(const s of data.scenes){
          assert.equal(s.columns,width>800?2:1,s.id+' responsive picture/caption layout');
          assert(s.reading.top>=s.figure.bottom-1&&s.reading.top<=s.figure.bottom+1,s.id+' reading follows complete picture row without blank parallel column');
          assert(!s.clipped&&s.reading.left>=-1&&s.reading.right<=data.viewport+1,s.id+' readable contained text');
          assert(Math.abs(s.image.width/s.image.height-s.ratio)<.02,s.id+' original image aspect preserved');
        }
      }
      records.push({route,width,enlarged,...data});
    }
  }
  console.log('PASS reading balance:13 Bible cards across6 profiles,3 Atonement paragraphs, original hero/image geometry');
  return records;
};
