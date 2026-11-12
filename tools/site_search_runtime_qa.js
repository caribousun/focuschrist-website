'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM,VirtualConsole}=require('jsdom');
const domErrors=[],virtualConsole=new VirtualConsole();virtualConsole.on('jsdomError',error=>domErrors.push(error.message));
const root=path.resolve(__dirname,'..');
const search=require('../site-search.js');
const data=require('../site-search-index.json');
const top=q=>search.rank(data.records,q).slice(0,5).map(r=>r.url);
assert.deepEqual(top('priesthood restoration').slice(0,2),['/answers/aaronic-priesthood-restoration.html','/answers/melchizedek-priesthood-restoration.html']);
assert.equal(top('Restoration')[0],'/answers/restored-church-of-jesus-christ.html');
assert.equal(top('Joseph Smith death mask')[0],'/joseph-smith-portrait-research.html#portrait-section-4');
assert.equal(top('D&C 6:36')[0],'/answers/look-unto-me-doctrine-and-covenants-6-36.html');
assert.equal(top('grief')[0],'/answers/grief-and-faith.html');
for (const query of ['Settle Your Heart','Settle This in Your Hearts','Neil Andersen']) assert.equal(search.groupMatches(data.records,query).best[0].url,'/answers/settle-this-in-your-hearts.html');
assert.equal(search.rank(data.records,'zzzxxyy').length,0);
for(const q of ['','   ','???','how do I'])assert.equal(search.rank(data.records,q).length,0);
for(const url of ['javascript:alert(1)','//evil.test','/../private','https://evil.test'])assert.equal(search.localURL(url),false);
const source=fs.readFileSync(path.join(root,'site-search.js'),'utf8');
function loadBank(w){
    for(const file of ['site-common.js','answer-bank-data.js','answer-bank-matcher.js','answer-bank-guards.js'])w.eval(fs.readFileSync(path.join(root,file),'utf8'));
}
function mergedRecords(w){return data.records.concat(search.reviewedBankRecords(w.FocusChristAnswerBankData,w.FocusChristAnswerBank,w.FocusChristAnswerBankGuards,w.focusChristQuestionSafety));}
const tick=()=>new Promise(r=>setTimeout(r,0));
async function run(){
    const dom=new JSDOM(fs.readFileSync(path.join(root,'search.html'),'utf8'),{url:'https://focuschrist.com/search.html?q=priesthood+restoration',runScripts:'outside-only',pretendToBeVisual:true,virtualConsole});
    const w=dom.window,d=w.document;let fails=false,calls=0;
    w.fetch=async()=>{calls++;if(fails)throw Error('offline');return {ok:true,json:async()=>data};};
    w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};
    w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'));};
    loadBank(w);const merged=mergedRecords(w);
    const loaded=w.FocusChristAnswerBank.loadBank(w.FocusChristAnswerBankData.records,{assignments:w.FocusChristAnswerBankData.assignments,guards:w.FocusChristAnswerBankGuards});
    const matcher=w.FocusChristAnswerBank.createMatcher(loaded.bank,{evaluateSafety:r=>w.focusChristQuestionSafety.evaluate(r.question_text)});
    const nursery=matcher.answer({question_text:'At what age do children start nursery?',profile:'ask'});
    assert.equal(nursery.status,'serve');assert.equal(nursery.record_id,'ask-what-does-a-nursery-leader-do');assert.match(nursery.answer,/18 months/);assert.match(nursery.answer,/December 31/);
    assert.equal(matcher.answer({question_text:'At what age do children start nursery? I want to kill myself',profile:'ask'}).status,'safety');
    assert.ok(merged.every(r=>search.localURL(r.url)));
    w.eval(source);await tick();await tick();
    assert.equal(d.querySelector('[data-search-results] h2 a').getAttribute('href'),top('priesthood restoration')[0]);
    assert.match(d.getElementById('fc-search-status').textContent,/best match/);
    const submit=q=>{d.getElementById('fc-results-query').value=q;d.getElementById('fc-results-search-form').dispatchEvent(new w.Event('submit',{cancelable:true,bubbles:true}));};
    assert.deepEqual(new Set(search.groupMatches(data.records,'priesthood').best.map(r=>r.url)),new Set(['/answers/aaronic-priesthood-restoration.html','/answers/melchizedek-priesthood-restoration.html','/answers/race-priesthood-and-temple-blessings.html']));
    submit('priesthood');await tick();assert.equal(d.querySelector('[data-search-results]').children.length,Math.min(12,search.groupMatches(merged,'priesthood').best.length));assert.equal(d.querySelector('.fc-search-supporting').open,false);assert.equal(d.getElementById('fc-search-more').hidden,search.groupMatches(merged,'priesthood').best.length<=12);d.querySelector('.fc-search-supporting summary').click();assert.equal(d.querySelector('.fc-search-supporting').open,true);assert.ok(d.querySelector('.fc-search-supporting ol').children.length>0);
    submit('grief');await tick();assert.equal(new URL(w.location).searchParams.get('q'),'grief');
    assert.equal(d.querySelector('[data-search-results] h2 a').getAttribute('href'),top('grief')[0]);
    const ask=new URL(d.getElementById('fc-search-ask').href);assert.equal(ask.searchParams.get('search-question'),'grief');assert.equal(ask.hash,'#ask-question');
    submit('<img src=x onerror=alert(1)>');await tick();assert.equal(d.querySelectorAll('#fc-search-status img').length,0);assert.match(d.getElementById('fc-search-status').textContent,/No matching/);
    submit('');await tick();assert.equal(d.querySelector('[data-search-results]').children.length,0);
    w.history.replaceState(null,'','?q=Restoration');w.dispatchEvent(new w.PopStateEvent('popstate'));await tick();assert.equal(d.getElementById('fc-results-query').value,'Restoration');
    submit('Christ');await tick();const count=d.querySelector('[data-search-results]').children.length;assert.equal(count,12);d.getElementById('fc-results-query').value='unsubmitted edit';d.getElementById('fc-search-more').click();assert.equal(d.querySelector('[data-search-results]').children.length,24);assert.match(d.getElementById('fc-search-status').textContent,/for “Christ”/);
    const trigger=d.querySelector('[data-site-search-trigger]');trigger.click();assert.equal(d.getElementById('fc-search-dialog').open,true);assert.equal(d.activeElement.id,'fc-header-search');d.querySelector('.fc-search-close').click();assert.equal(d.activeElement,trigger);
    w.dispatchEvent(new w.HashChangeEvent('hashchange'));assert.equal(d.querySelectorAll('[data-site-search-trigger]').length,1);assert.equal(calls,1);
    for (const [query,id] of [['nursery','ask-what-does-a-nursery-leader-do'],['Korihor','ask-who-was-korihor-in-the-book-of-mormon']]){
        submit(query);await tick();
        const record=search.groupMatches(merged,query).best.find(r=>r.bankRecordId===id);assert.ok(record);
        const link=[...d.querySelectorAll('[data-search-results] h2 a')].find(a=>a.getAttribute('href')===record.url);assert.ok(link,query+' must appear as a clickable answer');
        assert.ok(link.textContent);assert.equal(new URL(link.href).pathname,'/ask.html');
    }
    dom.window.close();
    const bad=new JSDOM(fs.readFileSync(path.join(root,'search.html'),'utf8'),{url:'https://focuschrist.com/search.html?q=faith',runScripts:'outside-only',pretendToBeVisual:true,virtualConsole});
    let fail=true;bad.window.fetch=async()=>{if(fail)throw Error('offline');return {ok:true,json:async()=>data};};loadBank(bad.window);bad.window.eval(source);await tick();await tick();assert.equal(bad.window.document.getElementById('fc-search-retry').hidden,false);
    fail=false;bad.window.document.getElementById('fc-search-retry').click();await tick();await tick();assert.match(bad.window.document.getElementById('fc-search-status').textContent,/best match/);bad.window.close();
    const missing=new JSDOM(fs.readFileSync(path.join(root,'search.html'),'utf8'),{url:'https://focuschrist.com/search.html?q=grief',runScripts:'outside-only',pretendToBeVisual:true,virtualConsole});
    missing.window.fetch=async()=>({ok:true,json:async()=>data});missing.window.eval(source);await tick();await tick();
    assert.equal(missing.window.document.querySelector('[data-search-results] h2 a').getAttribute('href'),top('grief')[0]);
    assert.match(missing.window.document.getElementById('fc-search-status').textContent,/Some Ask answers could not load/);
    assert.equal(missing.window.document.getElementById('fc-search-retry').hidden,false);missing.window.close();
    const askDOM=new JSDOM('<input id="userInput">',{url:'https://focuschrist.com/ask.html?search-question=priesthood#ask-question',runScripts:'outside-only',pretendToBeVisual:true,virtualConsole});askDOM.window.eval(source);await tick();assert.equal(askDOM.window.document.getElementById('userInput').value,'priesthood');askDOM.window.close();
    assert.deepEqual(domErrors,[], 'No uncaught DOM errors');
    console.log('SEARCH RUNTIME PASS: reviewed-bank nursery/Korihor discovery, relevance, safe text, pagination, history, dialog focus, empty/error/retry and Ask prefill');
}
run().catch(e=>{console.error(e);process.exitCode=1;});

