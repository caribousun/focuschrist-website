/* Independent real Chromium comparison: original native panels versus gallery. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'art-gallery.json')));
const base = process.env.GALLERY_QA_BASE || 'http://localhost:4187';
const out = path.resolve(root, '../gallery-qa');
fs.mkdirSync(out, {recursive:true});
const limit = Number(process.env.GALLERY_QA_LIMIT || Infinity);
const selectors = {hero:'#heroDetailDialog', artwork:'#artworkDetailDialog', topic:'#topicArtworkDetailDialog', missionary:'#missionaryDetailDialog', legacy:'#imageModal', full:'.fc-full-image-viewer'};
const report = {base, started:new Date().toISOString(), results:[], failures:[]};
function capture({selector}) {
    const panel = document.querySelector(selector);
    const normalize = s => (s || '').replace(/\s+/g,' ').trim();
    const style = el => {
        if (!el) return null;
        const s = getComputedStyle(el);
        return Object.fromEntries(['fontFamily','fontSize','fontWeight','color','backgroundColor','backgroundImage','borderColor','borderRadius'].map(k=>[k,s[k]]));
    };
    const cleanURL = value => {
        if (!value) return '';
        const url = new URL(value,location.href); url.searchParams.delete('gallery-embed');
        return url.href;
    };
    const title = panel.querySelector('h2,h3');
    const image = panel.querySelector('img');
    const copy = panel.querySelector('.fc-artwork-detail-copy,.fc-missionary-detail-copy,.fc-art-study-drawer');
    const copyClone=copy?.cloneNode(true);
    copyClone?.querySelectorAll('[data-gallery-original],[data-gallery-share]').forEach(el=>el.remove());
    const visible = el => {
        if(!el)return false;
        const r=el.getBoundingClientRect(),s=getComputedStyle(el);
        return s.visibility==='visible'&&s.display!=='none'&&Number(s.opacity)>0&&r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.left<innerWidth&&r.top<innerHeight;
    };
    const pills = [...panel.querySelectorAll('.fc-artwork-detail-actions > a,.fc-artwork-detail-actions > button,.fc-missionary-detail-actions > a,.fc-missionary-detail-actions > button,.fc-art-study-links > a,.fc-art-study-links > button')]
        .filter(el=>!el.hasAttribute('data-gallery-original')&&!el.hasAttribute('data-gallery-share')&&!el.hidden)
        .map(el=>({label:normalize(el.textContent),href:cleanURL(el.getAttribute('href')),style:style(el)}));
    return {width:innerWidth,title:normalize(title?.textContent),image:cleanURL(image?.src),copyText:normalize(copyClone?.textContent),
        panelVisible:visible(panel),imageVisible:visible(image),imageLoaded:!!(image?.complete&&image.naturalWidth),
        titleStyle:style(title),copyStyle:style(copy),panelStyle:style(panel),pills};
}
async function ready(pageOrFrame, source) {
    await pageOrFrame.waitForFunction(id=>document.documentElement.dataset.galleryArtworkReady===id || !!document.documentElement.dataset.galleryArtworkError, source.id, {timeout:18000});
    const error=await pageOrFrame.evaluate(()=>document.documentElement.dataset.galleryArtworkError);
    if(error) throw Error(error);
    await pageOrFrame.evaluate(()=>document.fonts.ready);
    if(source.kind==='legacy') {
        const drawer=pageOrFrame.locator('[data-focuschrist-art-study-drawer]');
        if(!await drawer.evaluate(el=>el.classList.contains('open')))await pageOrFrame.locator('[data-focuschrist-art-study-button]').click();
    }
    await pageOrFrame.waitForFunction(selector=>{const img=document.querySelector(selector)?.querySelector('img');return img?.complete&&img.naturalWidth>0;},selectors[source.kind],{timeout:18000});
}
(async()=>{
    const browser = await chromium.launch({channel:'chrome',headless:true});
    try {
        for(const viewport of [{width:1440,height:1000},{width:390,height:844}]) {
            const context=await browser.newContext({viewport});
            const original=await context.newPage(), gallery=await context.newPage();
            await gallery.goto(base+'/art-gallery.html',{waitUntil:'domcontentloaded'});
            await gallery.locator('[data-gallery-card]').first().waitFor();
            let checked=0;
            for(const art of catalog.artworks) {
                for(let index=0;index<art.occurrences.length;index++) {
                    if(checked>=limit)break;
                    const source=art.occurrences[index];
                    const result={width:viewport.width,artwork:art.id,source:source.id,kind:source.kind,page:source.page};
                    try {
                        await original.goto(base+source.page+'?gallery-art='+source.id,{waitUntil:'domcontentloaded'});
                        await ready(original,source);
                        await original.mouse.move(0,0);
                        await original.waitForTimeout(220);
                        const native=await original.evaluate(capture,{selector:selectors[source.kind]});
                        const card=gallery.locator('[data-gallery-card="'+art.id+'"]');
                        if(index===0)await card.locator('.fc-gallery-picture').click();
                        else {
                            await card.locator('details').evaluate(el=>el.open=true);
                            await card.locator('details a').nth(index-1).click();
                        }
                        await gallery.locator('#artGalleryFrame').waitFor({state:'visible',timeout:18000});
                        const frame=await gallery.locator('#artGalleryFrame').elementHandle().then(el=>el.contentFrame());
                        await ready(frame,source);
                        await gallery.mouse.move(0,0);
                        await gallery.waitForTimeout(220);
                        const embedded=await frame.evaluate(capture,{selector:selectors[source.kind]});
                        if(!native.panelVisible||!native.imageVisible||!native.imageLoaded||!embedded.panelVisible||!embedded.imageVisible||!embedded.imageLoaded) {
                            result.native=native;result.embedded=embedded;
                            throw Error('Panel/image not visibly rendered or loaded');
                        }
                        if(JSON.stringify(native)!==JSON.stringify(embedded)) {
                            result.differences=Object.keys(native).filter(k=>JSON.stringify(native[k])!==JSON.stringify(embedded[k]));
                            result.native=native; result.embedded=embedded;
                            throw Error('Native/embedded mismatch: '+result.differences.join(', '));
                        }
                        const controls=await frame.locator('[data-gallery-original]').count();
                        if(!controls)throw Error('Missing View in Original Study control');
                        result.pills=native.pills.length;
                        result.pass=true;
                        if(checked<2)await gallery.screenshot({path:path.join(out,viewport.width+'-'+source.kind+'-'+checked+'.png')});
                    } catch(error) {
                        result.pass=false; result.error=error.message;
                        report.failures.push(result);
                    }
                    report.results.push(result); checked++;
                    await gallery.evaluate(()=>{const d=document.getElementById('artGalleryDialog');if(d.open)d.close();});
                    if(checked%20===0) {
                        fs.writeFileSync(path.join(out,'art-gallery-browser-progress.json'),JSON.stringify(report,null,2));
                        console.log(viewport.width+': '+checked+' checked, '+report.failures.length+' failures');
                    }
                }
                if(checked>=limit)break;
            }
            await context.close();
        }
    } finally {
        await browser.close(); report.finished=new Date().toISOString();
        fs.writeFileSync(path.join(out,'art-gallery-browser-results.json'),JSON.stringify(report,null,2));
    }
    console.log(JSON.stringify({checked:report.results.length,failures:report.failures.length,evidence:out}));
    process.exitCode=report.failures.length?1:0;
})().catch(error=>{console.error(error);process.exitCode=1;});
