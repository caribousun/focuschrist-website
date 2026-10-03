/* DOM measurement fixtures; no browser is launched. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {JSDOM}=require('jsdom');
const source=fs.readFileSync(require('node:path').join(__dirname,'canonical_presentation_browser_qa.js'),'utf8');
const measure=source.slice(source.indexOf('function inspectPresentation()'),source.indexOf('\nasync function main()'));
function inspect(html,documentWidth=320){
    const dom=new JSDOM('<h1>Study</h1><main>'+html+'</main>',{runScripts:'outside-only',url:'https://focuschrist.com/test.html'});
    const w=dom.window;
    const box=node=>{const left=Number(node.dataset.left || 0),top=Number(node.dataset.top || 0),right=Number(node.dataset.right || 300),bottom=Number(node.dataset.bottom || 1000);return {left,top,right,bottom,width:right-left,height:bottom-top};};
    for(const node of w.document.querySelectorAll('*')){
        node.getBoundingClientRect=()=>box(node);
        node.getClientRects=()=>[box(node)];
        Object.defineProperty(node,'scrollWidth',{value:Number(node.dataset.scrollWidth || 999),configurable:true});
        Object.defineProperty(node,'scrollHeight',{value:Number(node.dataset.scrollHeight || 60),configurable:true});
        Object.defineProperty(node,'clientHeight',{value:Number(node.dataset.clientHeight || 60),configurable:true});
        Object.defineProperty(node,'clientWidth',{value:300});
    }
    Object.defineProperty(w,'innerWidth',{value:320});
    Object.defineProperty(w.document.documentElement,'scrollWidth',{value:documentWidth});
    w.getComputedStyle=node=>({display:node.dataset.display || 'block',visibility:'visible',opacity:'1',overflowX:node.dataset.clip || 'visible',overflowY:node.dataset.clipY || 'visible'});
    w.document.createRange=()=>({selectNodeContents(text){this.node=text.parentElement;},getClientRects(){const left=Number(this.node.dataset.textLeft || 0),right=Number(this.node.dataset.textRight || 100),top=Number(this.node.dataset.textTop || 0),bottom=Number(this.node.dataset.textBottom || 20);return [{left,right,top,bottom,width:right-left,height:bottom-top}];}});
    w.eval(measure+'\nwindow.measure=inspectPresentation;');
    const result=w.measure();dom.window.close();return result;
}
assert.equal(inspect('<a href="art.webp" data-clip="hidden"><img alt="Artwork"></a>').clippedControls.length,0,'Image scroll overflow is not a clipped text label');
assert.equal(inspect('<a href="#study" data-clip="hidden" data-text-right="400">Long visible label</a>').clippedControls.length,1,'Actual clipped label remains rejected');
assert.equal(inspect('<a href="#study" aria-hidden="true" data-right="350">Painted control</a>').clippedControls.length,1,'Painted aria-hidden controls remain measured');
assert.equal(inspect('<details><summary>Month</summary><a href="#study" data-right="350">Closed content</a></details>').clippedControls.length,0,'Native closed details content is not visible');
assert.equal(inspect('<details open><summary>Month</summary><a href="#study" data-right="350">Open content</a></details>').clippedControls.length,1,'Open details content remains measured');
console.log('Canonical presentation measurement PASS: painted controls, real text clipping, image-only overflow, closed/open disclosures.');

assert.equal(inspect('<input id="userInput" value="Long question" data-scroll-width="999">').clippedControls.length,1,'Single-line question clipping must fail even without page overflow');
assert.equal(inspect('<textarea id="userInput" data-scroll-width="300" data-scroll-height="180" data-client-height="60">Long question</textarea>').clippedControls.length,1,'Hidden textarea rows must fail even without page overflow');
assert.equal(inspect('<textarea id="userInput" data-scroll-width="300" data-scroll-height="180" data-client-height="180">Long question</textarea>').clippedControls.length,0,'Fully visible growing question passes');

assert.equal(inspect('<figure data-left="16" data-right="359" data-clip="hidden"><figcaption data-left="358" data-right="700"><p data-left="358" data-right="700" data-text-left="358" data-text-right="700">Study explanation</p></figcaption></figure>').clippedCaptions.length,1,'CFM partial caption outside hidden figure fails without document overflow');
assert.equal(inspect('<figure data-right="300" data-clip="hidden"><figcaption data-left="400" data-right="700"><a href="#source" data-left="400" data-right="700" data-text-left="400" data-text-right="650">Scripture source</a></figcaption></figure>').clippedCaptions.length,1,'Wholly clipped caption and source pill cannot disappear from measurement');
assert.equal(inspect('<figure data-bottom="60" data-clip-y="clip"><figcaption><p data-text-top="55" data-text-bottom="95">Lower caption line</p></figcaption></figure>').clippedCaptions.length,1,'Vertically clipped caption fails');
assert.equal(inspect('<figure data-clip="hidden"><figcaption><p data-text-right="280">Wrapped readable caption</p></figcaption></figure>').clippedCaptions.length,0,'Contained caption passes');
assert.equal(inspect('<details><summary>Study</summary><figure data-clip="hidden"><figcaption><p data-text-right="700">Closed caption</p></figcaption></figure></details>').clippedCaptions.length,0,'Closed native disclosure caption is excluded');
assert.equal(inspect('<section hidden><figure data-clip="hidden"><figcaption><p data-text-right="700">Hidden chapter caption</p></figcaption></figure></section>').clippedCaptions.length,0,'Hidden chapter caption is excluded');
assert.equal(inspect('<section data-display="none"><figure data-clip="hidden"><figcaption><p data-text-right="700">Inactive panel caption</p></figcaption></figure></section>').clippedCaptions.length,0,'CSS-hidden panel caption is excluded');
assert.equal(inspect('<figure data-clip="hidden"><a href="art.webp"><img data-right="700" alt="Intentionally cropped art"></a><figcaption><p>Readable caption</p></figcaption></figure>').clippedCaptions.length,0,'Decorative image cropping does not fail caption text measurement');
console.log('Caption ancestor clipping PASS: partial/full/vertical negatives; contained, closed, hidden and image-crop positives.');

// Text enlargement must settle before measurement; actual persistent overflow still fails.
const scaleAt=source.indexOf("document.documentElement.style.fontSize=100*scale+'%'");
const settleAt=source.indexOf('await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))');
const measureAt=source.indexOf('const measured=await page.evaluate(inspectPresentation)');
assert(scaleAt>=0&&settleAt>scaleAt&&measureAt>settleAt,'Font scaling settles two frames before presentation measurement');
assert(source.includes("if(measured.horizontalOverflow>3)failures.push('horizontal-overflow')"),'Persistent overflow threshold remains unchanged');

assert.equal(inspect('<p>Persistent overflow</p>',371).horizontalOverflow,51,'Settling cannot hide actual 51px document overflow');
