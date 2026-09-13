const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync(require('node:path').join(__dirname, '../pioneer-experience.js'), 'utf8');

function scenario({height=720, fieldTop=678.825, fieldHeight=60.8, rowHeight=fieldHeight, keyboard=null}={}) {
    let pageY=1000, focused=null;
    const listeners={};
    const rect=(top,h)=>({top:1000+top-pageY,bottom:1000+top-pageY+h,height:h});
    const row={getBoundingClientRect:()=>rect(fieldTop,rowHeight)};
    const input={disabled:false,isConnected:true,value:'',focus(){focused=input;},setAttribute(){},setSelectionRange(){},closest(){return row;},getBoundingClientRect:()=>rect(fieldTop,fieldHeight)};
    const document={get activeElement(){return focused;},querySelector(){return {getBoundingClientRect:()=>({height:72})};}};
    const window={innerHeight:height,get scrollY(){return pageY;},scrollTo({top}){pageY=top;},getComputedStyle(){return {position:'fixed'};},addEventListener(type,fn){listeners[type]=fn;},visualViewport:keyboard?{...keyboard,addEventListener(type,fn){listeners['visual-'+type]=fn;}}:null};
    const context=vm.createContext({window,document,userInput:()=>input,chatBox:()=>null});
    vm.runInContext(code.slice(code.indexOf('    function preferredScrollBehavior('),code.indexOf('    function ensurePioneerEntryStyles(')),context);
    return {context,input,row,window,listeners,get pageY(){return pageY;},blur(){focused=null;}};
}
const desktop=scenario();
vm.runInContext('focusPioneerInput()',desktop.context);
assert.equal(desktop.input.getBoundingClientRect().bottom,708,'observed 739.625px clipped desktop field must finish inside 720px viewport with margin');
assert(desktop.input.getBoundingClientRect().top>=96,'fixed header must not cover the focused field');
const stable=desktop.pageY;
vm.runInContext('focusPioneerInput()',desktop.context);
assert.equal(desktop.pageY,stable,'already visible completion must not drift on repeated answer-ready events');
const phone=scenario({height:844,fieldTop:627.275,rowHeight:205});
vm.runInContext('focusPioneerInput()',phone.context);
assert(phone.row.getBoundingClientRect().bottom<=832,'phone control stack including buttons remains usable');
assert(phone.input.getBoundingClientRect().top>=96);
const short=scenario({height:720,fieldTop:678.825,rowHeight:205,keyboard:{offsetTop:40,height:240}});
vm.runInContext('focusPioneerInput()',short.context);
assert(short.input.getBoundingClientRect().bottom<=268.01,'keyboard viewport prioritizes the field when the whole row cannot fit');
assert(short.input.getBoundingClientRect().top>=96);
short.window.visualViewport.height=200;
short.listeners['visual-resize']();
assert(short.input.getBoundingClientRect().bottom<=228.01,'keyboard resizing must recheck the actual visible viewport');
short.blur();const blurredY=short.pageY;
short.window.visualViewport.height=160;short.listeners['visual-resize']();
assert.equal(short.pageY,blurredY,'resizing must not move the page after focus leaves the composer');
const above=scenario({fieldTop:40});vm.runInContext('focusPioneerInput()',above.context);
assert.equal(above.input.getBoundingClientRect().top,96,'field above the header is moved below it');
console.log('PASS: Pioneer focused composer geometry at desktop720, phone844, keyboard resize, header occlusion, repeated completion and inactive focus.');


// The transcript and composer share actual flow geometry: reducing chat height
// moves the controls upward. Simulate native selection scrolling on EVERY
// follow-up, including a field already near the viewport top.
for (const [height,rowHeight] of [[720,60.8],[844,205],[400,205]]) {
    let pageY=1600, focused=null;
    const top=1000, gap=50;
    const box={style:{},querySelector:()=>({}),getBoundingClientRect(){const h=Math.min(560,parseFloat(this.style.maxHeight)||560);return {top:top-pageY,bottom:top-pageY+h,height:h};}};
    const row={getBoundingClientRect(){const start=box.getBoundingClientRect().bottom+gap;return {top:start,bottom:start+rowHeight,height:rowHeight};}};
    const input={disabled:false,isConnected:true,value:'',focus(){focused=input;},setAttribute(){},closest:()=>row,setSelectionRange(){pageY+=this.getBoundingClientRect().top-20;},getBoundingClientRect(){const start=row.getBoundingClientRect().top;return {top:start,bottom:start+60.8,height:60.8};}};
    const document={get activeElement(){return focused;},querySelector(){return {getBoundingClientRect:()=>({height:72})};}};
    const window={innerHeight:height,get scrollY(){return pageY;},scrollTo({top}){pageY=top;},getComputedStyle(element){return element===box?{maxHeight:'560px',minHeight:'210px'}:{position:'fixed'};},addEventListener(){}};
    const context=vm.createContext({window,document,userInput:()=>input,chatBox:()=>box});
    vm.runInContext(code.slice(code.indexOf('    function preferredScrollBehavior('),code.indexOf('    function ensurePioneerEntryStyles(')),context);
    for(let turn=0;turn<3;turn++){
        vm.runInContext('focusPioneerInput()',context);
        assert.equal(box.getBoundingClientRect().top,96,'each completion restores the transcript below the header even after native selection scroll');
        assert(box.getBoundingClientRect().height>=120,'a useful answer beginning stays on screen');
        assert(box.getBoundingClientRect().top+120<=height-12);
        assert(input.getBoundingClientRect().bottom<=height-12+.01,'input and answer jointly fit the viewport');
        if(height>400)assert(row.getBoundingClientRect().bottom<=height-12+.01,'desktop/phone controls fit alongside transcript');
    }
}
console.log('PASS: three successive answer completions preserve BOTH answer and composer after native selection scroll at desktop, phone and short viewport.');
