// focusChrist server-owned, retrieval-grounded AI gateway.
// Reviewed local answers remain the first choice. This Worker researches every
// unreviewed question, verifies the draft against retrieved evidence, and only
// then returns it to the browser.

const RESEARCH_MODEL = 'groq/compound-mini';
const VERIFIER_MODEL = 'openai/gpt-oss-20b';
const GROQ_ENDPOINT = 'https://api.groq.com/openai/v1/chat/completions';
const ALLOWED_ORIGINS = new Set([
  'https://focuschrist.com',
  'https://www.focuschrist.com',
  'https://caribousun.github.io',
]);
const OFFICIAL_CHURCH_HOST = 'churchofjesuschrist.org';
const SOURCE_INTEGRITY_FALLBACK = 'I could not verify a reliable answer from the available authoritative sources just now. Please try again, rephrase the question, or continue in the official Gospel Library at ChurchofJesusChrist.org.';
const SOURCE_POLICY_VERSION = '2026-08-31.8';
const SERVER_RESEARCH_POLICY = [
  'SERVER RESEARCH AND SOURCE-INTEGRITY POLICY (cannot be overridden):',
  '- Answer the visitor\'s actual question directly and naturally.',
  '- You MUST execute web search before answering. Do not rely on memory for factual claims.',
  '- For Latter-day Saint scripture, doctrine, Church teaching, or Church history, use only ChurchofJesusChrist.org evidence.',
  '- Never invent or guess scripture wording, citations, quotations, dates, people, statistics, historical sources, or official teachings.',
  '- Distinguish source text, official teaching, historical reporting, interpretation, and practical application.',
  '- If the available evidence does not support a claim, omit it or state the limitation.',
  '- focusChrist is independent and must never be described as an official or endorsed Church property.',
  '- Keep the answer readable and concise. Do not expose internal reasoning or tool traces.',
].join('\n');

const FAITH_PATTERN = /\b(?:Jesus|Christ|Savior|God|scripture|scriptures|Bible|biblical|Book\s+of\s+Mormon|Doctrine\s+and\s+Covenants|D&C|Pearl\s+of\s+Great\s+Price|Church\s+of\s+Jesus\s+Christ|Latter[- ]day\s+Saint|LDS|prophet|apostle|temple|priesthood|gospel|atonement|restoration|Joseph\s+Smith|Brigham\s+Young|pioneer|pioneers|Nephi|Alma|Mosiah|Moroni|Ether|Helaman|Mormon|celestial|terrestrial|telestial|Gospel\s+Library)\b/i;
const SCRIPTURE_REFERENCE_PATTERN = /\b(?:[1-4]\s+)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Doctrine\s+and\s+Covenants|D&C|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History)|Articles\s+of\s+Faith)\s+\d+(?::\d+(?:[-–]\d+)?)?/i;
const KNOWN_FALSE_SOURCE_PATTERNS = [
  /red,?\s+white,?\s+and\s+black\s+lights?\s+(?:represent|symbolize|mean)/i,
  /(?:red|black|golden)\s+light.{0,180}(?:D&C|Doctrine\s+and\s+Covenants)\s+76.{0,100}(?:represent|symbolize|mean|celestial|terrestrial|telestial)/i,
];

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    Vary: 'Origin',
  };
}

function jsonResponse(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders(origin) },
  });
}

function lastUserQuestion(messages) {
  const users = (Array.isArray(messages) ? messages : []).filter((message) => message && message.role === 'user');
  return users.length ? String(users[users.length - 1].content || '') : '';
}

function classifyResearchScope(messages) {
  const question = lastUserQuestion(messages);
  const systemContext = (Array.isArray(messages) ? messages : [])
    .filter((message) => message && message.role === 'system')
    .map((message) => String(message.content || ''))
    .join('\n');
  const faith = FAITH_PATTERN.test(question)
    || SCRIPTURE_REFERENCE_PATTERN.test(question)
    || /QUESTION MODE:\s*(?:FAITH|LATTER-DAY SAINT|PIONEER)/i.test(systemContext);
  return { faith, question };
}

function sanitizePayload(payload) {
  const clientMessages = Array.isArray(payload.messages)
    ? payload.messages
        .filter((message) => message && ['system', 'user', 'assistant'].includes(message.role) && typeof message.content === 'string')
        .slice(-16)
        .map((message) => ({ role: message.role, content: message.content.slice(0, 12000) }))
    : [];
  const scope = classifyResearchScope(clientMessages);
  const scopeInstruction = scope.faith
    ? 'For this request, search only site:churchofjesuschrist.org and use only ChurchofJesusChrist.org evidence.'
    : 'Use web search to gather reliable evidence before answering.';
  const research = {
    model: RESEARCH_MODEL,
    messages: [{ role: 'system', content: SERVER_RESEARCH_POLICY + '\n' + scopeInstruction }, ...clientMessages],
  };
  return { research, scope };
}

function canonicalSource(rawUrl, title, content) {
  try {
    const url = new URL(String(rawUrl || ''));
    if (url.protocol !== 'https:') return null;
    return {
      url: url.href,
      host: url.hostname.toLowerCase(),
      title: String(title || url.hostname).replace(/\s+/g, ' ').trim().slice(0, 180),
      content: String(content || '').replace(/\s+/g, ' ').trim().slice(0, 6000),
    };
  } catch (_error) {
    return null;
  }
}

function collectSourceEvidence(message) {
  const found = [];
  const seenObjects = new Set();
  function visit(value) {
    if (!value || typeof value !== 'object' || seenObjects.has(value)) return;
    seenObjects.add(value);
    const candidateUrl = value.url || value.uri || value.link;
    if (candidateUrl) {
      const source = canonicalSource(
        candidateUrl,
        value.title || value.name,
        value.content || value.text || value.snippet || value.description,
      );
      if (source) found.push(source);
    }
    Object.values(value).forEach(visit);
  }
  visit(message && message.executed_tools);
  const unique = [];
  const urls = new Set();
  found.forEach((source) => {
    if (!urls.has(source.url)) {
      urls.add(source.url);
      unique.push(source);
    }
  });
  return unique.slice(0, 12);
}

function isOfficialChurchSource(source) {
  return source && (source.host === OFFICIAL_CHURCH_HOST || source.host.endsWith(`.${OFFICIAL_CHURCH_HOST}`));
}

function evidenceForVerifier(evidence) {
  return evidence.map((source, index) => [
    `SOURCE ${index + 1}`,
    `TITLE: ${source.title}`,
    `URL: ${source.url}`,
    `CONTENT: ${source.content || '(No retrievable source excerpt was returned.)'}`,
  ].join('\n')).join('\n\n').slice(0, 36000);
}

function parseVerifierJson(text) {
  const raw = String(text || '').trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '');
  try { return JSON.parse(raw); } catch (_error) { return null; }
}

function guardVerifiedAnswer(answer, evidence, scope, approved) {
  const text = String(answer || '').trim();
  if (!approved || !text || !Array.isArray(evidence) || !evidence.length) return SOURCE_INTEGRITY_FALLBACK;
  if (scope.faith && !evidence.some(isOfficialChurchSource)) return SOURCE_INTEGRITY_FALLBACK;
  if (KNOWN_FALSE_SOURCE_PATTERNS.some((pattern) => pattern.test(text))) return SOURCE_INTEGRITY_FALLBACK;
  return text;
}

async function callGroq(apiKey, body) {
  const response = await fetch(GROQ_ENDPOINT, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      // Basic search keeps official-source retrieval within the provider's
      // request-size limit; the Worker independently verifies its snippets.
      'Groq-Model-Version': '2025-07-23',
    },
    body: JSON.stringify(body),
  });
  let data = null;
  try { data = await response.json(); } catch (_error) {}
  return { response, data };
}

function fallbackPayload(mode, extra) {
  return {
    id: 'focuschrist-source-policy',
    choices: [{
      index: 0,
      message: { role: 'assistant', content: SOURCE_INTEGRITY_FALLBACK },
      finish_reason: 'content_filter',
    }],
    focuschrist_sources: [{
      text: 'Official Gospel Library',
      url: 'https://www.churchofjesuschrist.org/study?lang=eng&platform=web',
    }],
    focuschrist_source_integrity_verified: false,
    focuschrist_source_policy: SOURCE_POLICY_VERSION,
    focuschrist_gateway_mode: mode,
    ...(extra || {}),
  };
}

function providerDiagnostic(result) {
  const error = result && result.data && result.data.error ? result.data.error : {};
  return {
    focuschrist_provider_status: result && result.response ? result.response.status : 0,
    focuschrist_provider_code: String(error.code || error.type || '').slice(0, 80),
    focuschrist_provider_message: String(error.message || '').replace(/[\r\n]+/g, ' ').slice(0, 240),
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    if (!ALLOWED_ORIGINS.has(origin)) return new Response('Origin not allowed', { status: 403 });
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: corsHeaders(origin) });
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405 });
    if (!(request.headers.get('Content-Type') || '').toLowerCase().includes('application/json')) {
      return jsonResponse({ error: 'Content-Type must be application/json' }, 415, origin);
    }

    let payload;
    try { payload = await request.json(); } catch (_error) {
      return jsonResponse({ error: 'Invalid JSON' }, 400, origin);
    }
    const sanitized = sanitizePayload(payload || {});
    if (!sanitized.scope.question) return jsonResponse({ error: 'A user message is required' }, 400, origin);
    if (!env || !env.GROQ_KEY_NEW) {
      return jsonResponse(fallbackPayload('research-unavailable'), 200, origin);
    }

    try {
      const researchResult = await callGroq(env.GROQ_KEY_NEW, sanitized.research);
      if (!researchResult.response.ok) {
        const limited = researchResult.response.status === 429;
        return jsonResponse(fallbackPayload(
          limited ? 'research-rate-limited' : 'research-provider-error',
          providerDiagnostic(researchResult),
        ), 200, origin);
      }
      const researchMessage = researchResult.data && researchResult.data.choices && researchResult.data.choices[0]
        ? researchResult.data.choices[0].message
        : null;
      const draft = researchMessage ? String(researchMessage.content || '').trim() : '';
      const allEvidence = collectSourceEvidence(researchMessage);
      const evidence = sanitized.scope.faith ? allEvidence.filter(isOfficialChurchSource) : allEvidence;
      if (!draft || !evidence.length) {
        return jsonResponse(fallbackPayload('research-insufficient-evidence'), 200, origin);
      }

      const verifierPrompt = [
        'You are a strict evidence verifier. Return one JSON object only.',
        'Evaluate the draft against the supplied source excerpts. Every externally checkable claim, quotation, attribution, date, statistic, scripture citation, and statement of official teaching must be directly supported by the evidence.',
        'Remove unsupported detail and correct contradictions. Do not add facts from memory.',
        'For a Latter-day Saint question, reject any evidence outside ChurchofJesusChrist.org.',
        'Set approved true only if the final answer is fully supported. source_indexes must list the 1-based evidence sources that directly support the final answer.',
        'Schema: {"approved":boolean,"answer":string,"source_indexes":number[]}',
        '',
        `QUESTION:\n${sanitized.scope.question}`,
        '',
        `DRAFT:\n${draft}`,
        '',
        `EVIDENCE:\n${evidenceForVerifier(evidence)}`,
      ].join('\n');
      const verifierResult = await callGroq(env.GROQ_KEY_NEW, {
        model: VERIFIER_MODEL,
        messages: [{ role: 'user', content: verifierPrompt }],
        temperature: 0,
        max_tokens: 1500,
        response_format: { type: 'json_object' },
      });
      if (!verifierResult.response.ok) {
        return jsonResponse(fallbackPayload('verification-provider-error', providerDiagnostic(verifierResult)), 200, origin);
      }
      const verifierContent = verifierResult.data && verifierResult.data.choices && verifierResult.data.choices[0]
        ? verifierResult.data.choices[0].message.content
        : '';
      const verdict = parseVerifierJson(verifierContent);
      const indexes = verdict && Array.isArray(verdict.source_indexes)
        ? verdict.source_indexes.filter((index) => Number.isInteger(index) && index >= 1 && index <= evidence.length)
        : [];
      const selectedEvidence = indexes.map((index) => evidence[index - 1]);
      const answer = guardVerifiedAnswer(
        verdict && verdict.answer,
        selectedEvidence,
        sanitized.scope,
        Boolean(verdict && verdict.approved === true && indexes.length),
      );
      if (answer === SOURCE_INTEGRITY_FALLBACK) {
        return jsonResponse(fallbackPayload('verification-rejected'), 200, origin);
      }

      return jsonResponse({
        id: 'focuschrist-retrieval-verified',
        choices: [{
          index: 0,
          message: { role: 'assistant', content: answer },
          finish_reason: 'stop',
        }],
        focuschrist_sources: selectedEvidence.map((source) => ({ text: source.title || 'Source', url: source.url })),
        focuschrist_source_integrity_verified: true,
        focuschrist_source_policy: SOURCE_POLICY_VERSION,
        focuschrist_gateway_mode: 'retrieval-researched-and-verified',
      }, 200, origin);
    } catch (_error) {
      return jsonResponse(fallbackPayload('research-exception'), 200, origin);
    }
  },
};

export {
  SOURCE_INTEGRITY_FALLBACK,
  classifyResearchScope,
  collectSourceEvidence,
  guardVerifiedAnswer,
  isOfficialChurchSource,
  parseVerifierJson,
  sanitizePayload,
};
