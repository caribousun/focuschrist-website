/* CI-only rendered sanity check. Static contracts and owner visual review remain separate. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const root = path.resolve(__dirname, '..');
const pages = [...new Set([...fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)]
    .map(match => new URL(match[1]).pathname.slice(1) || 'index.html'))];
const profiles = [{name:'desktop',width:1366,scale:1},{name:'phone',width:390,scale:1},{name:'narrow-large-text',width:320,scale:2}];

function inspectPresentation() {
    function rendered(node) {
        if (!node.getClientRects().length || node.closest('[hidden],template')) return false;
        for (let parent = node; parent; parent = parent.parentElement) {
            const style = getComputedStyle(parent);
            if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
        }
        // Accessibility hiding is not visual hiding. A painted aria-hidden box
        // still contributes to overflow. Fully clipped/offcanvas controls do not.
        const rect=node.getBoundingClientRect();
        for(let parent=node.parentElement;parent;parent=parent.parentElement){
            const style=getComputedStyle(parent),box=parent.getBoundingClientRect();
            if(['hidden','clip','auto','scroll'].includes(style.overflowX) && (rect.right<=box.left || rect.left>=box.right))return false;
            if(['hidden','clip','auto','scroll'].includes(style.overflowY) && (rect.bottom<=box.top || rect.top>=box.bottom))return false;
        }
        return true;
    }
    const identity = node => ({tag:node.tagName.toLowerCase(),id:node.id,className:String(node.className).slice(0,180),text:(node.textContent || node.getAttribute('aria-label') || '').trim().slice(0,110)});
    const controls = [...document.querySelectorAll('a[href],button,input:not([type="hidden"]),select,textarea,summary')].filter(rendered);
    const clippedControls = controls.flatMap(node => {
        const rect = node.getBoundingClientRect(), style = getComputedStyle(node);
        const cropX = ['hidden','clip'].includes(style.overflowX) && node.clientWidth > 0 && node.scrollWidth > node.clientWidth + 3;
        const cropY = ['hidden','clip'].includes(style.overflowY) && node.clientHeight > 0 && node.scrollHeight > node.clientHeight + 3;
        // Inputs scroll their editable text by design; inspect their outer box only.
        const croppedText = !['INPUT','TEXTAREA','SELECT'].includes(node.tagName) && (cropX || cropY);
        const outside = rect.left < -3 || rect.right > innerWidth + 3;
        const clippedBy=[];
        for(let parent=node.parentElement;parent && parent!==document.body && parent!==document.documentElement;parent=parent.parentElement){
            const parentStyle=getComputedStyle(parent),box=parent.getBoundingClientRect();
            const clipX=['hidden','clip'].includes(parentStyle.overflowX) && (rect.left<box.left-3 || rect.right>box.right+3);
            const clipY=['hidden','clip'].includes(parentStyle.overflowY) && (rect.top<box.top-3 || rect.bottom>box.bottom+3);
            if(clipX || clipY)clippedBy.push({...identity(parent),clipX,clipY});
        }
        return croppedText || outside || clippedBy.length ? [{...identity(node),rect:{left:rect.left,right:rect.right,width:rect.width,height:rect.height},croppedText,outside,clippedBy}] : [];
    });
    const images = [...document.images].filter(rendered);
    return {
        horizontalOverflow:Math.max(0,document.documentElement.scrollWidth-innerWidth),
        overflowingElements:[...document.querySelectorAll('main *,header *,footer *')].filter(rendered).filter(n => n.getBoundingClientRect().right > innerWidth+3 || n.getBoundingClientRect().left < -3).slice(0,12).map(identity),
        clippedControls,
        visibleH1:[...document.querySelectorAll('h1')].filter(rendered).map(n=>n.textContent.trim()).filter(Boolean),
        visibleControls:controls.length,
        loadedImages:images.filter(n=>n.complete && n.naturalWidth>0).length,
        brokenLoadedImages:images.filter(n=>n.complete && n.currentSrc && !n.naturalWidth).map(n=>({src:n.currentSrc,alt:n.alt})),
        pendingImages:images.filter(n=>!n.complete).map(n=>n.currentSrc || n.src),
        pendingLocalImages:images.filter(n=>!n.complete && new URL(n.currentSrc || n.src,location.href).origin===location.origin).map(n=>n.currentSrc || n.src),
    };
}

async function main() {
    if (process.env.CI !== 'true') throw new Error('Run this browser gate in CI; local GUI/browser execution is not authorized.');
    const {chromium} = require('playwright');
    let server;
    let origin = process.env.PRESENTATION_ORIGIN;
    if (!origin) {
        server = http.createServer((req,res)=>{
            const route = decodeURIComponent(new URL(req.url,'http://localhost').pathname);
            const file = path.resolve(root,'.'+(route.endsWith('/')?route+'index.html':route));
            if (!file.startsWith(root+path.sep)) {res.writeHead(403).end();return;}
            const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.woff2':'font/woff2'};
            fs.readFile(file,(error,data)=>error?res.writeHead(404).end():res.writeHead(200,{'Content-Type':types[path.extname(file)] || 'application/octet-stream'}).end(data));
        });
        await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
        origin='http://127.0.0.1:'+server.address().port;
    }
    const browser=await chromium.launch({headless:true});
    const results=[];
    const deadline=Date.now()+12*60*1000;
    try {
        const page=await browser.newPage();
        profileLoop: for (const profile of profiles) {
            await page.setViewportSize({width:profile.width,height:1000});
            for (const route of pages) {
                if(Date.now()>deadline){results.push({route,profile:profile.name,failures:['overall-time-budget-exhausted']});break profileLoop;}
                const local404=[];
                const onResponse=response=>{if(response.status()===404 && new URL(response.url()).origin===new URL(origin).origin)local404.push(response.url());};
                page.on('response',onResponse);
                try {
                    const response=await page.goto(origin+'/'+route,{waitUntil:'load',timeout:30000});
                    await page.evaluate(scale=>{document.documentElement.style.fontSize=100*scale+'%';},profile.scale);
                    // Force local lazy images to complete without hundreds of scroll screenshots.
                    await page.evaluate(async()=>{
                        const local=[...document.images].filter(n=>new URL(n.src,location.href).origin===location.origin);
                        local.forEach(n=>{n.loading='eager';});
                        await Promise.race([Promise.all(local.map(n=>n.decode().catch(()=>{}))),new Promise(resolve=>setTimeout(resolve,10000))]);
                        await Promise.race([document.fonts.ready,new Promise(resolve=>setTimeout(resolve,5000))]);
                    });
                    const measured=await page.evaluate(inspectPresentation);
                    const failures=[];
                    if(!response || response.status()>=400)failures.push('document-status');
                    if(measured.horizontalOverflow>3)failures.push('horizontal-overflow');
                    if(measured.clippedControls.length)failures.push('clipped-visible-control');
                    if(!measured.visibleH1.length)failures.push('missing-visible-h1');
                    if(measured.brokenLoadedImages.length)failures.push('broken-loaded-image');
                    if(measured.pendingLocalImages.length)failures.push('local-image-timeout');
                    if(local404.length)failures.push('local-404');
                    results.push({route,profile:profile.name,status:response?.status(),...measured,local404,failures});
                    console.log((failures.length?'FAIL ':'PASS ')+route+' '+profile.name+(failures.length?' '+failures.join(', '):''));
                } catch(error) {results.push({route,profile:profile.name,failures:['navigation-or-measurement-error'],error:String(error),local404});}
                finally {page.off('response',onResponse);}
            }
        }
    } finally {
        await browser.close();
        if(server)await new Promise(resolve=>server.close(resolve));
        const output=process.env.PRESENTATION_REPORT || '.qa-artifacts/canonical-presentation.json';
        fs.mkdirSync(path.dirname(output),{recursive:true});
        fs.writeFileSync(output,JSON.stringify({origin,pages:pages.length,profiles,checks:results.length,failures:results.filter(r=>r.failures.length).length,results},null,2)+'\n');
    }
    if(results.length!==pages.length*profiles.length || results.some(r=>r.failures.length))process.exitCode=1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
