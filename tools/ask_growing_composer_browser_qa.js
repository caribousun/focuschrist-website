/* CI-only real layout regression, called by the existing interaction browser gate. */
const assert=require('node:assert/strict');
module.exports=async function checkGrowingComposer(page,origin){
 const results=[];
 const long='I am studying prayer and personal revelation. How can I recognize guidance while giving a difficult question enough time, and how can I bring what I learn into daily life? '.repeat(5);
 const measure=()=>[...document.querySelectorAll('#userInput,#followupInput')].filter(n=>n.getClientRects().length).map(n=>({id:n.id,tag:n.tagName,value:n.value,height:n.clientHeight,scrollHeight:n.scrollHeight,width:n.clientWidth,scrollWidth:n.scrollWidth,rect:{left:n.getBoundingClientRect().left,right:n.getBoundingClientRect().right},viewport:document.documentElement.clientWidth}));
 for(const profile of [{width:1366,scale:1},{width:390,scale:1},{width:320,scale:2}]){
  await page.setViewportSize({width:profile.width,height:1000});
  await page.goto(origin+'/ask.html?topic=Prayer&return=%2Fanswers%2Fprayer-and-personal-revelation.html',{waitUntil:'load'});
  await page.evaluate(scale=>{document.documentElement.style.fontSize=scale*100+'%';window.sendMessage=()=>{window.__testSends=(window.__testSends||0)+1;};},profile.scale);
  assert((await page.locator('#userInput').inputValue()).includes('Prayer'),'Incoming study context should prefill');
  await page.locator('#userInput').fill(long);await page.waitForTimeout(100);
  await page.evaluate(value=>{document.querySelector('#followupInput').value=value;const dock=document.querySelector('#askFollowupDock');dock.classList.add('visible');dock.setAttribute('aria-hidden','false');},long);
  await page.waitForTimeout(100);
  let rows=await page.evaluate(measure);assert.equal(rows.length,2);
  for(const r of rows){assert.equal(r.tag,'TEXTAREA');assert.equal(r.value,long);assert(r.scrollHeight<=r.height+3,r.id+' clips rows');assert(r.scrollWidth<=r.width+3,r.id+' clips horizontally');assert(r.rect.left>=-1&&r.rect.right<=r.viewport+1,r.id+' leaves viewport');}
  await page.locator('#userInput').press('End');await page.locator('#userInput').press('Shift+Enter');
  assert((await page.locator('#userInput').inputValue()).includes('\n'));assert.equal(await page.evaluate(()=>window.__testSends||0),0);
  await page.evaluate(()=>{for(const id of ['userInput','followupInput'])document.getElementById(id).dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',isComposing:true,bubbles:true,cancelable:true}));});
  assert.equal(await page.evaluate(()=>window.__testSends||0),0,'IME composition must not send');
  await page.locator('#followupInput').press('Shift+Enter');
  assert((await page.locator('#followupInput').inputValue()).includes('\n'));assert.equal(await page.evaluate(()=>window.__testSends||0),0);
  await page.locator('#userInput').press('Enter');assert.equal(await page.evaluate(()=>window.__testSends),1);
  await page.locator('#followupInput').press('Enter');assert.equal(await page.evaluate(()=>window.__testSends),2);
  // Negative control: reproduces hidden rows without causing document overflow.
  await page.locator('#userInput').fill(long);await page.waitForTimeout(100);
  await page.addStyleTag({content:'#userInput{height:48px!important;min-height:0!important;overflow:hidden!important}'});
  const negative=(await page.evaluate(measure)).find(r=>r.id==='userInput');assert(negative.scrollHeight>negative.height+3,'Clipping negative must be detectable');
  results.push({profile,composers:rows,clippingNegativeDetected:true,keyboardPassed:true});
 }
 return results;
};
