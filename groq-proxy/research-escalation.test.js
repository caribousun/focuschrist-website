import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import worker, { isAllowedResearchFetchUrl, hydrateResearchEvidence, SOURCE_UNAVAILABLE_MESSAGE } from './src/index.js';

// Synthetic transport fixtures exercise retrieval and verification, not doctrine.
// No provider or official site is contacted and no mocked verdict proves a claim.
const topics = [
  ['forgiveness', 'How can forgiveness help someone rebuild trust?'],
  ['prayer', 'How can prayer help someone rebuild trust?'],
  ['Kirtland Temple', 'How did the Kirtland Temple community rebuild trust?']
];
const discoveredUrl = 'https://www.churchofjesuschrist.org/study/general-conference/2025/04/offline-escalation-fixture?lang=eng';
const answer = 'Rebuilding trust takes time and involves more than a statement of good intentions. A person can begin by listening carefully, acknowledging harm, and choosing actions that show responsibility. The explanation should distinguish an inward desire to change from the work of repairing a relationship with someone else. It should also respect the other person’s freedom to decide when a relationship feels dependable. Shared expectations can give both people a clearer understanding of what comes next. Patience matters because confidence develops through experience over time. These ideas describe a process of restoration rather than an immediate result guaranteed by a single decision.';
const json = value => new Response(JSON.stringify(value), {headers:{'Content-Type':'application/json'}});
const originalFetch = globalThis.fetch;
assert.equal(isAllowedResearchFetchUrl(discoveredUrl), true);
for (const denied of [
  'http://www.churchofjesuschrist.org/study/general-conference/article',
  'https://www.churchofjesuschrist.org.evil.example/study/article',
  'https://user:password@www.churchofjesuschrist.org/study/article',
  'https://www.churchofjesuschrist.org:8443/study/article',
  'https://www.churchofjesuschrist.org/study/search/article',
  'https://www.churchofjesuschrist.org/study/article?token=secret',
  'https://www.churchofjesuschrist.org/study/article?lang=spa'
]) assert.equal(isAllowedResearchFetchUrl(denied), false, `Unsafe or unsupported fetch URL: ${denied}`);

try {
  for (const [topic, question, rejectAgain, articleUnavailable] of [...topics, [...topics[0], true], [...topics[0], false, true]]) {
    const events = [];
    let researchCalls = 0;
    let verifierCalls = 0;
    globalThis.fetch = async (url, options = {}) => {
      const address = String(url);
      if (address.startsWith('https://focuschrist.com/scripture-data/')) {
        return new Response(readFileSync(new URL('..' + new URL(address).pathname, import.meta.url)));
      }
      if (address.includes('api.groq.com')) {
        researchCalls++;
        events.push('research');
        const body = JSON.parse(options.body);
        assert.ok(body.messages.some(message => message.content.includes(question)), 'research must retain current question');
        return json({choices:[{message:{content:'A newly discovered article addresses the requested relationship.', executed_tools:[{search_results:[{
          url:discoveredUrl, title:'Additional study about rebuilding trust',
          content:`${topic} and rebuilding trust are discussed in this search result. Search metadata only; retrieve the article to verify its fuller account.`
        }]}]}}]});
      }
      if (address === discoveredUrl) {
        events.push('hydrated');
        assert.equal(options.redirect, 'manual', 'discovered source fetch must never follow redirects');
        if (articleUnavailable) return new Response('', {status:503});
        return new Response(`<article><p>${topic} can be discussed in relation to rebuilding trust. FETCHED_NEW_EVIDENCE identifies an independently retrieved article, not the search excerpt. Restoring confidence requires sustained responsible conduct, willingness to acknowledge injuries, careful attention to another person's boundaries, and patience. Reconciliation cannot be demanded or promised on a fixed timetable. An honest discussion distinguishes a personal intention from the experience of those affected.</p></article>`, {headers:{'Content-Type':'text/html'}});
      }
      if (address.startsWith('https://www.churchofjesuschrist.org/')) {
        events.push('indexed');
        return new Response(`<article><p>${topic} is the named subject of this introductory study. Rebuild trust appears as a topic for further investigation. INDEXED_INTRODUCTION_ONLY describes the broad subject but provides no explanation of the relationship requested by the visitor. This source is deliberately insufficient for the first verifier to approve an answer.</p></article>`, {headers:{'Content-Type':'text/html'}});
      }
      throw new Error('Unexpected offline fixture request: ' + address);
    };
    const response = await worker.fetch(new Request('https://worker.test', {method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'ask',focuschrist_profile:'faith-study',messages:[{role:'user',content:question}]})}), {
      GROQ_KEY_NEW:'offline-fixture',
      AI:{run:async (_model, body) => {
        verifierCalls++;
        events.push('verify');
        const prompt = body.messages[0].content;
        assert.ok(prompt.includes(question));
        assert.ok(prompt.includes('For a scripture quotation, use [[SCRIPTURE:Book chapter:verse]]'));
        if (verifierCalls === 1) return {response:{approved:false,answer:'The introduction does not establish the requested relationship.',source_indexes:[]}};
        assert.ok(prompt.includes('FETCHED_NEW_EVIDENCE'), 'second verifier must receive newly fetched article text');
        if (rejectAgain) return {response:{approved:false,answer:'The additional source still does not establish a responsible answer.',source_indexes:[]}};
        return {response:{approved:true,answer,source_indexes:[1]}};
      }}
    });
    const payload = await response.json();
    assert.equal(researchCalls, 1, `${topic}: rejected local evidence must cause exactly one external research pass`);
    if (articleUnavailable) {
      assert.equal(verifierCalls, 1, 'unavailable new evidence must not trigger another verdict on old rejected text');
      assert.equal(payload.choices[0].message.content, SOURCE_UNAVAILABLE_MESSAGE);
      assert.equal(payload.focuschrist_gateway_mode, 'research-unavailable');
      assert.notEqual(payload.focuschrist_source_integrity_verified, true);
      continue;
    }
    assert.equal(verifierCalls, 2, `${topic}: evidence escalation must use the same verifier once more`);
    assert.ok(events.indexOf('research') > events.indexOf('verify'), 'local verification precedes research escalation');
    assert.ok(events.indexOf('hydrated') > events.indexOf('research'), 'discovered article must be fetched after discovery');
    if (rejectAgain) {
      assert.notEqual(payload.focuschrist_source_integrity_verified, true, 'second rejection must remain closed with no third research pass');
      continue;
    }
    assert.equal(payload.focuschrist_source_integrity_verified, true, JSON.stringify(payload));
    assert.equal(payload.focuschrist_scripture_validated, true);
    assert.ok(payload.focuschrist_sources.some(source => source.url === discoveredUrl));
  }
  for (const question of ['How can forgiveness help someone rebuild trust?', 'Is God the same in the Old Testament and New Testament?']) {
    let failedArticles = 0;
    globalThis.fetch = async url => {
      if (String(url).includes('api.groq.com')) return json({choices:[{message:{content:'No supported article was found.',executed_tools:[]}}]});
      assert.ok(String(url).includes('churchofjesuschrist.org'), 'initial retrieval fixture must only fetch approved articles');
      failedArticles++;
      return new Response('', {status:503});
    };
    const response = await worker.fetch(new Request('https://worker.test', {method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'ask',focuschrist_profile:'faith-study',messages:[{role:'user',content:question}]})}), {GROQ_KEY_NEW:'offline-fixture'});
    const payload = await response.json();
    assert.ok(failedArticles > 0);
    assert.equal(payload.focuschrist_source_transport_failures, failedArticles, 'initial indexed and paired article failures must all propagate without resetting the count');
    assert.equal(payload.focuschrist_gateway_mode, 'research-unavailable');
    assert.equal(payload.choices[0].message.content, SOURCE_UNAVAILABLE_MESSAGE);
  }
  let redirectCalls = 0;
  globalThis.fetch = async (_url, options) => {
    redirectCalls++;
    assert.equal(options.redirect, 'manual');
    return new Response('', {status:302, headers:{Location:'https://unapproved.example/article'}});
  };
  const hydrated = await hydrateResearchEvidence([{url:discoveredUrl,host:'www.churchofjesuschrist.org',title:'Search metadata',content:'A bounded search excerpt.'}], 'forgiveness rebuild trust', Date.now()+10000);
  assert.equal(redirectCalls, 1, 'source hydration must not follow a redirect');
  assert.ok(hydrated.every(source=>source.url !== 'https://unapproved.example/article'));
  for (const failure of ['429','503','network','timeout','deadline','404','content','unrelated']) {
    const diagnostic = {};
    globalThis.fetch = async () => {
      if (failure === 'network') throw new TypeError('network unavailable');
      if (failure === 'timeout') throw new DOMException('The operation was aborted', 'AbortError');
      if (failure === 'deadline') throw new Error('expired deadline must not fetch');
      if (failure === 'content') return new Response('{}', {headers:{'Content-Type':'application/json'}});
      if (failure === 'unrelated') return new Response('<p>These fixtures discuss unrelated decorative buildings and contain no requested concepts.</p>', {headers:{'Content-Type':'text/html'}});
      return new Response('', {status:Number(failure)});
    };
    const result = await hydrateResearchEvidence([{url:discoveredUrl,host:'www.churchofjesuschrist.org',title:'Source fixture',content:'Search snippets cannot establish article claims.'}], 'forgiveness rebuild trust', Date.now()+(failure === 'deadline' ? -1 : 10000), diagnostic);
    assert.deepEqual(result, [], 'failed or unrelated article text must not admit a search snippet');
    assert.equal(Number(diagnostic.focuschrist_source_transport_failures || 0), ['429','503','network','timeout','deadline'].includes(failure) ? 1 : 0,
      failure + ' must be classified as transport unavailability or unsupported content accurately');
  }
} finally { globalThis.fetch = originalFetch; }
console.log('Research escalation QA PASS: three topics, one research escalation, fetched official text, closed second rejection, URL boundaries and no redirects.');
