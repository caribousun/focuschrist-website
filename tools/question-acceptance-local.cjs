/* Run the real local page scripts and DOM against an explicitly isolated AI
 * preview. No answer/provider mocks. jsdom cannot prove visual layout; the
 * companion browser review must check scrolling and presentation separately. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {JSDOM, ResourceLoader, VirtualConsole} = require('jsdom');
const root = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const option = (name, fallback) => args.includes(name) ? args[args.indexOf(name)+1] : fallback;
const endpoint = option('--endpoint', '');
const expectedPolicy = fs.readFileSync(path.join(root,'groq-proxy/src/index.js'),'utf8').match(/const SOURCE_POLICY_VERSION = '([^']+)'/)[1];
const selectedPage = option('--page', 'all');
const output = path.resolve(option('--output', path.join(root, '../../outputs/question-acceptance')));
const limit = Number(option('--limit', '100'));
const providerGapMs = Number(option('--provider-gap-ms', '6500'));
if (!Number.isFinite(providerGapMs) || providerGapMs < 0) throw new Error('--provider-gap-ms must be a nonnegative number.');
const ids = option('--ids', '').split(',').filter(Boolean);
if (endpoint && !/^https:\/\/[a-z0-9-]+-focuschrist-groq-proxy\.caribousun\.workers\.dev\/?$/.test(endpoint)) throw new Error('Only an isolated Worker preview endpoint is allowed.');
fs.mkdirSync(output, {recursive:true});
if(fs.existsSync(path.join(output,'results.jsonl')))throw new Error('Output already contains results.jsonl; choose a fresh run directory to preserve distinct evidence.');
const pause = ms => new Promise(resolve=>setTimeout(resolve,ms));
const localOrigin = 'http://127.0.0.1:4188';
const sourceFallback = 'focusChrist is here to help you learn of Jesus Christ and draw closer to Him.';
const allowedHosts = new Set(['rsc.byu.edu','scriptures.byu.edu','speeches.byu.edu','eom.byu.edu','www.byui.edu']);
let lastProviderStart = 0;
const networkFetch = global.fetch;
function localPath(url) {
  const target = path.resolve(root, '.'+decodeURIComponent(new URL(url,localOrigin).pathname));
  if (!target.startsWith(root+path.sep)) throw new Error('Local resource escaped repository');
  return target;
}
class LocalResources extends ResourceLoader {
  constructor(errors) { super(); this.errors=errors; }
  fetch(url) {
    const parsed = new URL(url);
    if (parsed.origin !== localOrigin || !/\.(js|css)$/.test(parsed.pathname)) return null;
    try { return Promise.resolve(fs.readFileSync(localPath(url))); } catch(error) { this.errors.push('Missing local page resource: '+parsed.pathname+' ('+error.message+')'); return null; }
  }
}
async function ready(predicate, description, timeout=15000) {
  const start=Date.now();
  while (!predicate()) { if(Date.now()-start>timeout) throw new Error('Timed out: '+description); await pause(20); }
}
async function pageContext(page) {
  const calls=[], messages=[], errors=[];
  const console = new VirtualConsole();
  console.on('jsdomError',error=>{if(!/CSS stylesheet|navigation|HTMLMediaElement/.test(error.message)) errors.push(error.message);});
  const dom=new JSDOM(fs.readFileSync(path.join(root,page+'.html'),'utf8'),{
    url:localOrigin+'/'+page+'.html',runScripts:'dangerously',resources:new LocalResources(errors),pretendToBeVisual:true,virtualConsole:console,
    beforeParse(w) {
      w.__acceptanceLifecycle={domContentLoadedObserved:0,duplicateDomContentLoadedSuppressed:0,normalization:'jsdom duplicate DOMContentLoaded suppressed to match real-browser one-event lifecycle'};
      w.document.addEventListener('DOMContentLoaded',event=>{
        w.__acceptanceLifecycle.domContentLoadedObserved++;
        if(w.__acceptanceLifecycle.domContentLoadedObserved>1){w.__acceptanceLifecycle.duplicateDomContentLoadedSuppressed++;event.stopImmediatePropagation();}
      },true);
      Object.assign(w,{TextEncoder,TextDecoder,Response,Request,Headers,AbortController});
      Object.defineProperty(w,'crypto',{value:crypto.webcrypto});
      w.matchMedia=()=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
      w.scrollTo=()=>{}; w.HTMLElement.prototype.scrollTo=function(){};w.HTMLElement.prototype.scrollIntoView=function(){};
      w.ResizeObserver=class{observe(){} unobserve(){} disconnect(){}};
      w.IntersectionObserver=class{observe(){} unobserve(){} disconnect(){}};
      w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};
      w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'));};
      w.fetch=async (url,options={})=>{
        const parsed=new URL(String(url),w.location.href);
        if(parsed.hostname==='focuschrist-groq-proxy.caribousun.workers.dev') {
          const call={request:options.body?JSON.parse(options.body):null,status:null,durationMs:0,payload:null,error:null}; calls.push(call);
          if(!endpoint) {call.error='Isolated AI endpoint not configured; remote case NOT TESTED';throw new Error(call.error);}
          await pause(Math.max(0,providerGapMs-(Date.now()-lastProviderStart)));lastProviderStart=Date.now();
          const start=Date.now();
          try {
          const response=await networkFetch(endpoint,{...options,headers:{...options.headers,Origin:'https://focuschrist.com'},signal:AbortSignal.timeout(70000)});
          const payload=await response.clone().json();
          Object.assign(call,{status:response.status,durationMs:Date.now()-start,payload});
          if(payload.focuschrist_source_policy!==expectedPolicy) throw new Error('Candidate policy mismatch: '+payload.focuschrist_source_policy);
          return response;
          } catch(error) {call.error=error.message;call.durationMs=Date.now()-start;throw error;}
        }
        if(parsed.origin===localOrigin || parsed.hostname==='focuschrist.com') {
          try { const file=localPath(parsed.href);return new Response(fs.readFileSync(file),{headers:{'Content-Type':file.endsWith('.json')?'application/json':'text/plain'}}); }
          catch{return new Response('',{status:404});}
        }
        throw new Error('Unexpected page network request: '+parsed.origin);
      };
    }
  });
  const w=dom.window;
  try {
    await ready(()=>w.document.documentElement.getAttribute('data-focuschrist-study-intelligence-version')==='3'&&w.focusChristScriptureLibrary&&w.document.readyState!=='loading'&&typeof w.sendMessage==='function'&&typeof w.addMessage==='function'&&(page!=='pioneers'||w.focusChristRunPioneerDisclosure),'local page controllers');
  } catch(error) {
    const detail={version:w.document.documentElement.getAttribute('data-focuschrist-study-intelligence-version'),library:!!w.focusChristScriptureLibrary,ready:w.document.readyState,errors};
    dom.window.close();throw new Error(error.message+' '+JSON.stringify(detail));
  }
  const add=w.addMessage;
  w.addMessage=function(text,isUser,sources){messages.push({text,isUser,sources:sources||[]});return add.apply(this,arguments);};
  return {dom,w,calls,messages,errors};
}
async function submit(ctx,question) {
  const {w}=ctx; const before=ctx.calls.length; const messageBefore=ctx.messages.length; const nodesBefore=new Set(w.document.querySelectorAll('#chatBox .bot-message')); const start=Date.now();
  const input=w.document.getElementById('userInput');input.value=question;
  await w.sendMessage();
  await ready(()=>!w.document.querySelector('#chatBox .loading, #chatBox [data-scripture-pending]'),'final scripture-checked answer',32000);
  await pause(90);
  const node=[...w.document.querySelectorAll('#chatBox .bot-message')].filter(n=>!nodesBefore.has(n)).at(-1);
  const raw=ctx.messages.slice(messageBefore).reverse().find(m=>!m.isUser);
  return {question,displayedAnswerText:node?[...node.querySelectorAll(':scope > p')].map(p=>p.textContent).join('\n\n'):'',answer:raw?.text||'',sources:raw?.sources||[],displayedText:node?.textContent||'',html:node?.outerHTML||'',durationMs:Date.now()-start,providerCalls:ctx.calls.slice(before)};
}
function normalizedDisplayText(text) {
 return String(text||'').normalize('NFKC').replace(/[“”]/g,'"').replace(/[‘’]/g,"'").replace(/[–—]/g,'-').replace(/¶/g,'').replace(/\s+/g,' ').trim();
}
function outcome(result) {
  if ((result.providerCalls || []).some(c => c.error || c.status < 200 || c.status >= 300
    || /unavailable|rate-limited|timeout|transport-failure/i.test(c.payload?.focuschrist_gateway_mode || '')
    || Number(c.payload?.focuschrist_provider_status) === 429 || Number(c.payload?.focuschrist_provider_status) >= 500)) return 'unavailable';
  const text=result.answer;
  if(/unable to check|temporarily unavailable|try again|could not complete/i.test(text)) return 'unavailable';
  if(text.startsWith(sourceFallback)||/could not confirm|cannot verify|could not verify/i.test(text)) return 'unsupported';
  if(/^(?:Which |Please (?:name|specify|provide|tell)|I found (?:several|more than))/i.test(text)||/choose.*pioneer|select.*pioneer/i.test(text))return 'clarify';
  return text.trim()?'answer':'empty';
}
function allowedSource(source) {
  try {const u=new URL(source.url);return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&(u.hostname==='churchofjesuschrist.org'||u.hostname.endsWith('.churchofjesuschrist.org')||allowedHosts.has(u.hostname)||(u.hostname==='focuschrist.com'&&u.pathname==='/tell-my-story-too.txt'));}catch{return false;}
}
const escape=text=>String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function report(results) {
  const rows=results.map(r=>`<details><summary>${escape(r.id)} · ${escape(r.automatedStatus)} · ${escape(r.question)}</summary><p>Expected ${escape(r.expectedOutcome)}; observed ${escape(r.observedOutcome)}. Semantic review pending.</p><p>${escape(r.issues.join('; '))}</p><h3>Answer</h3><div class="answer">${escape(r.answer)}</div><h3>Sources</h3><ul>${r.sources.map(s=>`<li><a href="${escape(s.url)}">${escape(s.text||s.url)}</a></li>`).join('')}</ul><h3>Review cues</h3><p>${escape(r.reviewNotes)}</p></details>`).join('');
  fs.writeFileSync(path.join(output,'review.html'),`<!doctype html><meta charset="utf-8"><title>200-question prepublication review</title><style>body{max-width:1100px;margin:40px auto;background:#f8f3e9;color:#17353f;font:18px/1.6 system-ui;padding:20px}details{border:1px solid #a89b73;padding:18px;margin:12px 0;border-radius:12px;background:white}summary{cursor:pointer;font-weight:bold}.answer{white-space:pre-wrap}a{color:#175d71}</style><h1>Local question acceptance review</h1><p>${results.length} cases recorded. This report separates automatic checks from pending semantic review. Isolated service: ${escape(endpoint||'not configured')}.</p>${rows}`);
}
(async()=>{
  const all=['ask','pioneer'].flatMap(name=>JSON.parse(fs.readFileSync(path.join(root,'tools/fixtures',name+'-100-questions.json'),'utf8')));
  for(const page of ['ask','pioneers']) {const set=all.filter(t=>t.page===page);if(set.length!==100||new Set(set.map(t=>t.question.toLowerCase())).size!==100)throw new Error(page+' corpus must contain100uniquequestions');}
  const selected=all.filter(t=>(selectedPage==='all'||t.page===selectedPage)&&(!ids.length||ids.includes(t.id))).filter((t,index,arr)=>arr.slice(0,index).filter(x=>x.page===t.page).length<limit);
  const results=[];
  const manifest={harnessLifecyclePolicy:'Suppress and record duplicate jsdom DOMContentLoaded; matches observed real browser single-event lifecycle. Earlier round1 display snapshots are invalid due to double initialization, while raw answers remain separate evidence.',startedAt:new Date().toISOString(),endpoint,providerGapMs,localCodeHash:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'groq-proxy/src/index.js'))).digest('hex'),cases:selected.length};
  fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2));
  for(const test of selected) {
    let ctx; let record={...test,issues:[],prerequisites:[],answer:'',sources:[],observedOutcome:'error',semanticReview:'pending'};
    try {
      ctx=await pageContext(test.page);
      for(const question of test.priorUserQuestions||[]) {
        const prerequisite=await submit(ctx,question);record.prerequisites.push(prerequisite);
        if(!prerequisite.displayedText||['unavailable','empty'].includes(outcome(prerequisite))||prerequisite.providerCalls.some(c=>c.error||c.status<200||c.status>=300))record.issues.push('Prior question did not complete successfully: '+question);
      }
      const result=await submit(ctx,test.question);Object.assign(record,result);
      record.observedOutcome=outcome(result);
      if(record.observedOutcome==='unavailable'||record.observedOutcome==='empty')record.issues.push('No completed answer: '+record.observedOutcome);
      if(test.expectedOutcome==='answer'&&record.observedOutcome!=='answer')record.issues.push('Expected supported answer; got '+record.observedOutcome);
      if(test.expectedOutcome==='clarify'&&record.observedOutcome!=='clarify')record.issues.push('Expected clarification; review actual response');
      if(result.sources.some(s=>!allowedSource(s)))record.issues.push('Unapproved source exposed');
      if(record.observedOutcome==='answer'&&!result.sources.length)record.issues.push('Answer has no supporting source');
      if(result.providerCalls.some(c=>c.error||c.status<200||c.status>=300))record.issues.push('Provider request incomplete or failed; not an accepted unsupported answer');
      if(result.providerCalls.some(c=>c.payload&&c.payload.focuschrist_source_policy!==expectedPolicy))record.issues.push('Wrong candidate policy');
      if(result.providerCalls.length&&record.observedOutcome==='answer'&&!result.providerCalls.at(-1).payload?.focuschrist_source_integrity_verified)record.issues.push('AI answer lacks verified source receipt');
      if(!result.displayedText)record.issues.push('No answer displayed');
      if(/Checking scripture sources|Seeking divine guidance/i.test(result.displayedText))record.issues.push('Answer still displays a loading placeholder');
      const rawNormalized=normalizedDisplayText(result.answer), renderedNormalized=normalizedDisplayText(result.displayedAnswerText);
      const guardTransformed=/could not (?:confirm|verify)|cannot verify|scripture verification is temporarily unavailable/i.test(result.displayedAnswerText);
      record.displayGuardTransformed=guardTransformed&&rawNormalized!==renderedNormalized;
      if(!renderedNormalized)record.issues.push('No completed answer paragraph rendered');
      else if(rawNormalized!==renderedNormalized&&!guardTransformed)record.issues.push('Rendered answer paragraphs do not match the recorded raw answer');
      if(record.displayGuardTransformed&&test.expectedOutcome==='answer')record.issues.push('Display guard did not deliver expected supported answer');
      if(/could not confirm/i.test(result.displayedText)&&!/could not confirm/i.test(result.answer))record.issues.push('Display scripture guard rejected raw answer');
      record.lifecycleDiagnostics=ctx.w.__acceptanceLifecycle;
      record.runtimeErrors=ctx.errors;
      if(ctx.errors.length)record.issues.push('Local page runtime errors');
    }catch(error){record.issues.push(error.message);}
    finally {if(ctx)ctx.dom.window.close();}
    record.automatedStatus=record.issues.length?'FAIL':'PASS';results.push(record);
    fs.appendFileSync(path.join(output,'results.jsonl'),JSON.stringify(record)+'\n');
    report(results);
    console.log(JSON.stringify({id:test.id,status:record.automatedStatus,outcome:record.observedOutcome,issues:record.issues,completed:results.length,total:selected.length}));
  }
  const summary={...manifest,completedAt:new Date().toISOString(),completed:results.length,automaticPass:results.filter(r=>r.automatedStatus==='PASS').length,automaticFail:results.filter(r=>r.automatedStatus==='FAIL').length,semanticReviewsPending:results.length};
  fs.writeFileSync(path.join(output,'summary.json'),JSON.stringify(summary,null,2));console.log(JSON.stringify(summary));
})().catch(error=>{console.error(error);process.exitCode=1;});
