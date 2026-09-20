/* Real DOM source association without provider calls. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<div id="chatBox"></div>', { url: 'https://focuschrist.com/pioneers.html', runScripts: 'outside-only' });
const w = dom.window, d = w.document, box = d.getElementById('chatBox');
w.eval(fs.readFileSync('study-source-router.js', 'utf8'));
d.dispatchEvent(new w.Event('DOMContentLoaded'));
const pause = () => new Promise(resolve => setTimeout(resolve, 120));
function pair(question, pending = false) {
 const q = d.createElement('div'); q.className='user-message'; q.textContent=question;
 const a = d.createElement('div'); a.className='bot-message'; a.textContent='Reviewed answer.';
 if(pending) a.setAttribute('data-scripture-pending','true');
 box.append(q,a); return {q,a};
}
(async()=>{
 const old=pair('Who was Elizabeth Crook Panting?'); await pause();
 assert.equal(old.a.querySelector('[data-focuschrist-answer-source]').getAttribute('href'),'https://focuschrist.com/pioneers.html#elizabeth-crook-panting');
 const next=pair('Tell me about Winter Quarters',true);
 box.prepend(next.q,next.a); await pause();
 assert.equal(next.a.querySelector('[data-focuschrist-answer-source]'),null,'Pending answer must not receive source enhancements');
 next.a.removeAttribute('data-scripture-pending');
 next.a.append(d.createTextNode(' Complete.')); await pause();
 assert.equal(next.a.querySelector('[data-focuschrist-answer-source]').getAttribute('href'),'https://focuschrist.com/pioneers.html#pioneer-departure-heading');
 assert.equal(old.a.querySelectorAll('[data-focuschrist-answer-source]').length,1);
 assert.match(old.a.querySelector('[data-focuschrist-answer-source]').href,/elizabeth-crook-panting$/);
 const irrelevant=pair('Why is the sky blue?'); box.prepend(irrelevant.q,irrelevant.a); await pause();
 assert.equal(irrelevant.a.querySelector('[data-focuschrist-answer-source]'),null);
 const router=w.focusChristSourceRouter;
 for(const q of ['Steve Martin movies','Elizabeth Taylor films','Willie Nelson songs']) assert.equal(router.answerStudySourceForQuestion(q),null,q);
 const html=fs.readFileSync('pioneers.html','utf8');
 for(const q of ['Brigham Young','Nauvoo','Winter Quarters','Willie handcart company','Martin company','pioneer rescue','Elizabeth Crook Panting']){
  const r=router.answerStudySourceForQuestion(q);assert(r,q);assert(html.includes('id="'+r.url.split('#')[1]+'"'),q);
 }
 assert.equal(router.answerStudySourceForQuestion('Who is Jesus Christ?').url,'answers/jesus-christ-latter-day-saint-beliefs.html');
 dom.window.close();console.log('Pioneer related study PASS: verified anchors, pending guard, repeated/top-promoted exchanges, unrelated names, existing Answers route.');
})().catch(e=>{dom.window.close();console.error(e);process.exitCode=1;});
