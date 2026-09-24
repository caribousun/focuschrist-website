/* DOM measurement fixtures; no browser is launched. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {JSDOM}=require('jsdom');
const source=fs.readFileSync(require('node:path').join(__dirname,'canonical_presentation_browser_qa.js'),'utf8');
const measure=source.slice(source.indexOf('function inspectPresentation()'),source.indexOf('\nasync function main()'));
function inspect(html){
    const dom=new JSDOM('<h1>Study</h1><main>'+html+'</main>',{runScripts:'outside-only',url:'https://focuschrist.com/test.html'});
    const w=dom.window;
    const box=node=>({left:0,top:0,right:Number(node.dataset.right || 300),bottom:1000,width:Number(node.dataset.right || 300),height:1000});
    for(const node of w.document.querySelectorAll('*')){
        node.getBoundingClientRect=()=>box(node);
        node.getClientRects=()=>[box(node)];
        Object.defineProperty(node,'scrollWidth',{value:999,configurable:true});
        Object.defineProperty(node,'clientWidth',{value:300});
    }
    Object.defineProperty(w,'innerWidth',{value:320});
    Object.defineProperty(w.document.documentElement,'scrollWidth',{value:320});
    w.getComputedStyle=node=>({display:'block',visibility:'visible',opacity:'1',overflowX:node.dataset.clip || 'visible',overflowY:'visible'});
    w.document.createRange=()=>({selectNodeContents(text){this.node=text.parentElement;},getClientRects(){return [{left:0,right:Number(this.node.dataset.textRight || 100),top:0,bottom:20}];}});
    w.eval(measure+'\nwindow.measure=inspectPresentation;');
    const result=w.measure();dom.window.close();return result;
}
assert.equal(inspect('<a href="art.webp" data-clip="hidden"><img alt="Artwork"></a>').clippedControls.length,0,'Image scroll overflow is not a clipped text label');
assert.equal(inspect('<a href="#study" data-clip="hidden" data-text-right="400">Long visible label</a>').clippedControls.length,1,'Actual clipped label remains rejected');
assert.equal(inspect('<a href="#study" aria-hidden="true" data-right="350">Painted control</a>').clippedControls.length,1,'Painted aria-hidden controls remain measured');
assert.equal(inspect('<details><summary>Month</summary><a href="#study" data-right="350">Closed content</a></details>').clippedControls.length,0,'Native closed details content is not visible');
assert.equal(inspect('<details open><summary>Month</summary><a href="#study" data-right="350">Open content</a></details>').clippedControls.length,1,'Open details content remains measured');
console.log('Canonical presentation measurement PASS: painted controls, real text clipping, image-only overflow, closed/open disclosures.');
