/* Home-derived body rails and promotion/divider clearance. Pixels still need review. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
module.exports=async function historyBodySpacing(page,origin){
  const routes=[...fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>new URL(m[1]).pathname.slice(1)||'index.html');
  const adjacency=[],histories=[],consumers=[];
  const historyVersions={'history/eleazer-miller.html':'20261009-directory-alignment-1','history/john-rowe-moyle.html':'20261009-directory-alignment-1','history/john-tanner.html':'20261009-directory-alignment-1','history/emma-hale-smith.html':'20261008-standard-body-1'};
  for(const route of routes){
    const parsed=await page.evaluate(html=>{const doc=new DOMParser().parseFromString(html,'text/html');return{matches:doc.querySelectorAll('.fc-study-promotion + .fc-study-grid').length,history:!!doc.querySelector('.fc-life-reading'),links:[...doc.querySelectorAll('link[rel="stylesheet"]')].map(n=>n.getAttribute('href'))}},fs.readFileSync(path.join(root,route),'utf8'));
    const matches=parsed.matches;
    if(matches)adjacency.push({route,matches});
    if(parsed.history)histories.push(route);
    for(const [file,version] of [['connected-study.css','20261008-promotion-spacing-1'],['history-stories.css',historyVersions[route]]]){
      const links=parsed.links.filter(n=>new URL(n,'https://focuschrist.com/'+route).pathname.endsWith('/'+file));
      if(links.length){assert(version,route+' unknown '+file+' consumer');assert.equal(links.length,1,route+' duplicate '+file);assert.equal(new URL(links[0],'https://focuschrist.com/'+route).searchParams.get('v'),version,route+' stale '+file);consumers.push({route,file});}
    }
  }
  assert.deepEqual(histories.sort(),['history/eleazer-miller.html','history/john-rowe-moyle.html','history/john-tanner.html']);
  assert(adjacency.length,'Discover actual promotion/divider consumers');
  const records=[];
  const profiles=[[320,800,1],[390,844,1],[430,932,1],[1366,900,1],[1722,1000,1],[1905,1000,1],[390,844,2],[1366,900,2]];
  async function settle(scale){await page.evaluate(async scale=>{document.documentElement.style.fontSize=100*scale+'%';await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));},scale);}
  for(const [width,height,scale]of profiles){
    await page.setViewportSize({width,height});
    await page.goto(origin+'/index.html');await settle(scale);
    const home=await page.locator('.fc-home-purpose-paths').evaluate(n=>({x:n.getBoundingClientRect().x,width:n.getBoundingClientRect().width}));
    for(const route of histories){
      await page.goto(origin+'/'+route);await page.waitForSelector('.fc-unified-continue');await settle(scale);
      const measure=()=>{const box=n=>{const r=n.getBoundingClientRect();return{x:r.x,y:r.y+scrollY,width:r.width,height:r.height}};return{overflow:document.documentElement.scrollWidth-innerWidth,hero:box(document.querySelector('.fc-life-hero')),cue:box(document.querySelector('.fc-unified-continue')),opening:box(document.querySelector('.fc-life-opening')),bodies:[...document.querySelectorAll('.fc-life-reading:not(.fc-life-opening)')].map(n=>({box:box(n),first:box(n.firstElementChild),padding:parseFloat(getComputedStyle(n).paddingTop),lastMargin:parseFloat(getComputedStyle(n.lastElementChild).marginBottom)}))};};
      const data=await page.evaluate(measure);
      assert(data.overflow<=1,route+' overflow');
      for(const b of data.bodies){assert(Math.abs(b.box.x-home.x)<1&&Math.abs(b.box.width-home.width)<1,route+' body must match Home');assert.equal(b.first.x,b.box.x,route+' no doubled gutter');assert.equal(b.lastMargin,0,route+' trailing margin stacks section gap');}
      // Recreate old narrow padded body to prove the geometry gate sees its failure.
      if(width===1722){const old=await page.addStyleTag({content:'.fc-life-story .fc-life-reading:not(.fc-life-opening){width:auto!important;max-width:860px!important;padding:30px 24px!important}'});const bad=await page.evaluate(measure);assert.notEqual(bad.bodies[0].box.width,home.width);assert.deepEqual(bad.hero,data.hero);assert.deepEqual(bad.cue,data.cue);assert.deepEqual(bad.opening,data.opening);await old.evaluate(n=>n.remove());}
      await page.locator('.fc-life-directory summary').click();assert(await page.locator('.fc-life-directory').evaluate(n=>n.open));await page.locator('.fc-life-directory summary').click();
      records.push({route,width,height,scale,home,...data});
    }
    for(const {route,matches}of adjacency){
      await page.goto(origin+'/'+route);await settle(scale);
      const grids=page.locator('.fc-study-promotion + .fc-study-grid');assert.equal(await grids.count(),matches);
      for(let i=0;i<matches;i++){
        const grid=grids.nth(i),pill=grid.locator('xpath=preceding-sibling::*[1]').locator('.fc-actions a').last();
        for(const state of ['rest','hover','focus']){
          await pill.scrollIntoViewIfNeeded();if(state==='hover')await pill.hover();if(state==='focus'){await page.mouse.move(0,0);await pill.focus();}await page.waitForTimeout(230);
          const data=await grid.evaluate(n=>{const p=n.previousElementSibling.querySelector('.fc-actions a:last-child'),r=p.getBoundingClientRect(),g=n.getBoundingClientRect(),s=getComputedStyle(p);const range=document.createRange();range.selectNodeContents(p);return{gap:g.top-r.bottom,required:parseFloat(getComputedStyle(n).marginTop),outline:parseFloat(s.outlineWidth)+parseFloat(s.outlineOffset),pill:{x:r.x,right:r.right,height:r.height},text:[...range.getClientRects()].map(x=>({left:x.left,right:x.right,top:x.top,bottom:x.bottom})),bottom:r.bottom,top:r.top,width:innerWidth};});
          assert(data.gap>=data.required-.5&&data.gap>=16,'Clearance to divider');assert(data.gap>data.outline,'Focus ring clears divider');assert(data.pill.x>=0&&data.pill.right<=width+1,'Pill within viewport');assert(data.text.every(r=>r.left>=data.pill.x-1&&r.right<=data.pill.right+1&&r.top>=data.top-1&&r.bottom<=data.bottom+1),'Wrapped label contained');records.push({route,width,height,scale,state,...data});
        }
        if(width===1722){const old=await page.addStyleTag({content:'.fc-study-promotion + .fc-study-grid{margin-block-start:0!important}'});await page.mouse.move(0,0);await page.locator('body').click({position:{x:0,y:0}});await page.waitForTimeout(230);const gap=await grid.evaluate(n=>n.getBoundingClientRect().top-n.previousElementSibling.querySelector('.fc-actions a:last-child').getBoundingClientRect().bottom);assert(gap<1,'Pre-fix touching divider must fail');await old.evaluate(n=>n.remove());}
      }
    }
  }
  console.log('PASS historical body rails and pill/divider spacing: '+records.length+' rendered states');
  return{profiles,consumers,adjacency,histories,records};
};
