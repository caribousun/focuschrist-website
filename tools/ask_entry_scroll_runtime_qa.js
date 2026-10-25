const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM}=require('jsdom');

// Scenario A: addMessage in ask.html brings the top of each newly
// appended conversation entry into view (the append choke point every
// send path uses), instead of forcing the transcript to its bottom.
const askHtml=fs.readFileSync(path.join(__dirname,'../ask.html'),'utf8');
const sliceStart=askHtml.indexOf('    function bringEntryIntoView(');
const sliceEnd=askHtml.indexOf('    async function sendMessage()');
assert(sliceStart>=0 && sliceEnd>sliceStart,'the entry scroll helper and addMessage must be present in ask.html');
const domA=new JSDOM('<div class="chat-box ask-chat-box" id="chatBox"></div>',{runScripts:'outside-only'});
const wA=domA.window, boxA=wA.document.getElementById('chatBox');
const viewed=[];
wA.Element.prototype.scrollIntoView=function (options){ viewed.push({node:this,options}); };
Object.defineProperty(boxA,'scrollHeight',{value:999,configurable:true});
wA.eval(askHtml.slice(sliceStart,sliceEnd)+'\n;window.__addMessage=addMessage;');
assert.equal(typeof wA.__addMessage,'function','addMessage must be defined by the ask.html slice');
wA.__addMessage('Who is Jesus Christ?',true,[]);
wA.__addMessage('Jesus Christ is the Son of God.',false,[]);
assert.equal(boxA.children.length,2,'both conversation entries are appended');
assert.equal(viewed.length,2,'every appended entry is brought into view');
assert.equal(viewed[0].node,boxA.children[0],'the user entry is scrolled into view on its append');
assert.equal(viewed[1].node,boxA.children[1],'the answer entry is scrolled into view on its append');
assert.equal(viewed[1].options.block,'start','the entry top is the alignment target');
assert.notEqual(boxA.scrollTop,999,'an append no longer forces the transcript to its bottom');
domA.window.close();

// Scenario B: the follow-up follow in ask-experience.js anchors the
// newly appended exchange when the latest-first marker is already set.
// That is the chip-click state: no promotion runs for the new exchange,
// so anchoring to the first user message in the box (the old behavior)
// scrolls the transcript back to the first exchange instead.
const code=fs.readFileSync(path.join(__dirname,'../ask-experience.js'),'utf8');
const domB=new JSDOM('<header class="nav" data-focuschrist-header="standard" style="position:fixed"></header><aside id="askFollowupDock" aria-hidden="true"></aside><div id="chatBox" data-focuschrist-latest-first="true"><div class="user-message">First question</div><div class="bot-message">First answer</div><div class="user-message">Follow-up question</div><div class="bot-message">Follow-up answer</div></div>',{runScripts:'outside-only'});
const w=domB.window, d=w.document, box=d.getElementById('chatBox');
const users=box.querySelectorAll('.user-message'), answers=box.querySelectorAll('.bot-message');
const firstUser=users[0], firstAnswer=answers[0], newUser=users[1], newAnswer=answers[1];
Object.defineProperties(w,{innerHeight:{value:900,configurable:true},innerWidth:{value:1366,configurable:true}});
d.querySelector('header').getBoundingClientRect=()=>({height:52});
let pageY=0, innerY=0;
Object.defineProperty(w,'scrollY',{get:()=>pageY});
w.scrollTo=({top})=>{pageY=top;};
w.matchMedia=()=>({matches:true});
const boxDocumentTop=300;
const contentTop=new Map([[firstUser,0],[firstAnswer,76],[newUser,592],[newAnswer,668]]);
const heights=new Map([[firstUser,60],[firstAnswer,500],[newUser,60],[newAnswer,500]]);
box.getBoundingClientRect=()=>({top:boxDocumentTop-pageY,height:500,bottom:boxDocumentTop-pageY+500});
for (const el of [firstUser,firstAnswer,newUser,newAnswer]) {
    el.getBoundingClientRect=()=>({top:boxDocumentTop-pageY+(contentTop.get(el)-innerY),height:heights.get(el),bottom:boxDocumentTop-pageY+(contentTop.get(el)-innerY)+heights.get(el)});
}
Object.defineProperties(box,{scrollHeight:{value:1400},clientHeight:{value:500},scrollTop:{get:()=>innerY}});
box.scrollTo=({top})=>{innerY=top;};
w.eval(code.slice(code.indexOf('    function preferredScrollBehavior('),code.indexOf('    function ensureAskEntryStyles(')));
w.eval(code.slice(code.indexOf('    function focusLatestAnswer('),code.indexOf('    function submitQuestion(')));
w.focusLatestAnswer(newAnswer);
assert.equal(innerY,574,'the transcript scrolls to the new exchange top (592 - 18), not the first exchange (0)');
assert.equal(pageY,224,'the page scrolls so the transcript begins below the fixed header');
w.focusLatestAnswerSettled(newAnswer);
assert.equal(innerY,574,'the settled pass re-anchors the same new exchange');
domB.window.close();
console.log('PASS: appended entries are brought into view at append time, and the chip-path follow anchors the new exchange, not the first.');
