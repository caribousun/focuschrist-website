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
const TELL_MY_STORY_URL = 'https://focuschrist.com/tell-my-story-too.txt';
const SOURCE_INTEGRITY_FALLBACK = 'I could not verify a reliable answer from the available authoritative sources just now. Please try again, rephrase the question, or continue in the official Gospel Library at ChurchofJesusChrist.org.';
const GENERAL_ANSWER_FALLBACK = 'I could not complete that general answer just now. Please try again or rephrase the question.';
const SOURCE_POLICY_VERSION = '2026-09-01.6';
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
const REVIEWED_COLOR_CORRECTION = 'No. Doctrine and Covenants 76:31-34 does not mention red, white, black, or golden lights and does not assign colors to degrees of glory. Those verses discuss people who know God\'s power and then deny it. Doctrine and Covenants 18:15 teaches the joy of helping bring one soul to Jesus Christ; it does not describe colors or degrees of glory.';
const GENERAL_RESEARCH_REQUIRED_PATTERN = /\b(?:current|currently|today|tonight|tomorrow|yesterday|latest|recent|news|weather|forecast|price|cost|rate|score|schedule|election|president|prime\s+minister|chief\s+executive|ceo|law|legal|court|tax|financial|finance|investment|stock|crypto|medical|medicine|medication|diagnosis|symptom|dose|suicide|self-harm|emergency|abuse|citation|cite|source|quotation|quote|statistics?|percentage)\b/i;

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

function extractSelectedPioneerName(messages) {
  const content = (Array.isArray(messages) ? messages : [])
    .filter((message) => message && ['system', 'user'].includes(message.role))
    .map((message) => String(message.content || ''))
    .join('\n');
  const match = content.match(/(?:Selected pioneer|Selected name):\s*([^\n\r]{2,120})/i);
  if (!match) return '';
  const name = match[1].replace(/[^A-Za-zÀ-ÖØ-öø-ÿ0-9 .,'’()&-]/g, '').replace(/\s+/g, ' ').trim();
  return name.length >= 2 && name.length <= 120 ? name : '';
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
  const selectedPioneerName = extractSelectedPioneerName(messages);
  return { faith, question, selectedPioneer: Boolean(selectedPioneerName), selectedPioneerName };
}

function sanitizePayload(payload) {
  const clientMessages = Array.isArray(payload.messages)
    ? payload.messages
        .filter((message) => message && ['system', 'user', 'assistant'].includes(message.role) && typeof message.content === 'string')
        .slice(-16)
        .map((message) => ({ role: message.role, content: message.content.slice(0, 12000) }))
    : [];
  const scope = classifyResearchScope(clientMessages);
  const scopeInstruction = scope.selectedPioneer
    ? `The visitor selected the pioneer ${scope.selectedPioneerName}. Search only site:churchofjesuschrist.org to corroborate that exact person's identity, company, dates, and journey. The gateway will separately supply the selected Tell My Story, Too biography.`
    : scope.faith
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
      content: String(content || '').replace(/\s+/g, ' ').trim().slice(0, 1800),
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
  return unique.slice(0, 6);
}

function isOfficialChurchSource(source) {
  return source && (source.host === OFFICIAL_CHURCH_HOST || source.host.endsWith(`.${OFFICIAL_CHURCH_HOST}`));
}

function isTellMyStorySource(source) {
  return Boolean(source && source.sourceClass === 'tell-my-story-too' && source.url === TELL_MY_STORY_URL);
}

function extractTellMyStoryEntry(bookText, selectedName) {
  const name = String(selectedName || '').replace(/\s+/g, ' ').trim();
  if (!name) return '';
  const lines = String(bookText || '').replace(/\r/g, '').split('\n');
  const normalizedName = name.toUpperCase();
  const start = lines.findIndex((line) => line.replace(/\s+/g, ' ').trim().toUpperCase() === normalizedName);
  if (start < 0) return '';

  let end = lines.length;
  for (let index = start + 1; index < lines.length; index += 1) {
    const candidate = lines[index].replace(/\s+/g, ' ').trim();
    if (!/^[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ0-9 .,'’()&-]{3,119}$/.test(candidate)) continue;
    if (candidate.toUpperCase() === normalizedName || candidate.includes(`(${normalizedName} - PAGE`)) continue;
    const nearby = lines.slice(index + 1, index + 9).join('\n');
    if (/\bBorn:\s*/i.test(nearby) && /\bAge:\s*/i.test(nearby)) {
      end = index;
      break;
    }
  }

  return lines.slice(start, end).join('\n')
    .replace(/--- PAGE \d+ ---/g, '')
    .replace(/This biographical sketch comes from the 8th edition of the book Tell My Story, Too:[\s\S]*?non-commercial purposes\./g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
    .slice(0, 14000);
}

async function fetchTellMyStoryEvidence(selectedName) {
  if (!selectedName) return null;
  try {
    const response = await fetch(TELL_MY_STORY_URL, { headers: { Accept: 'text/plain' } });
    if (!response.ok) return null;
    const entry = extractTellMyStoryEntry(await response.text(), selectedName);
    if (!entry) return null;
    return {
      url: TELL_MY_STORY_URL,
      host: 'focuschrist.com',
      title: `Tell My Story, Too — ${selectedName}`,
      content: entry,
      sourceClass: 'tell-my-story-too',
    };
  } catch (_error) {
    return null;
  }
}

function evidenceForVerifier(evidence) {
  return evidence.map((source, index) => [
    `SOURCE ${index + 1}`,
    `SOURCE CLASS: ${source.sourceClass || (isOfficialChurchSource(source) ? 'official-church' : 'web')}`,
    `TITLE: ${source.title}`,
    `URL: ${source.url}`,
    `CONTENT: ${source.content || '(No retrievable source excerpt was returned.)'}`,
  ].join('\n')).join('\n\n').slice(0, 18000);
}

function parseVerifierJson(text) {
  const raw = String(text || '').trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '');
  try { return JSON.parse(raw); } catch (_error) { return null; }
}

function isJsonValidationFailure(result) {
  const error = result && result.data && result.data.error ? result.data.error : {};
  return Boolean(result && result.response && result.response.status === 400
    && /json[_ -]?validate|failed_generation/i.test(`${error.code || ''} ${error.type || ''} ${error.message || ''}`));
}

function guardVerifiedAnswer(answer, evidence, scope, approved) {
  const text = String(answer || '').trim();
  if (!approved || !text || !Array.isArray(evidence) || !evidence.length) return SOURCE_INTEGRITY_FALLBACK;
  if (scope.selectedPioneer && !evidence.some(isTellMyStorySource)) return SOURCE_INTEGRITY_FALLBACK;
  if (scope.faith && !scope.selectedPioneer && !evidence.some(isOfficialChurchSource)) return SOURCE_INTEGRITY_FALLBACK;
  if (hasKnownFalseClaim(text)) return SOURCE_INTEGRITY_FALLBACK;
  return text;
}

function hasKnownFalseClaim(text) {
  const value = String(text || '');
  if (!KNOWN_FALSE_SOURCE_PATTERNS.some((pattern) => pattern.test(value))) return false;
  const explicitCorrection = /\b(?:does\s+not|do\s+not|doesn't|don't|is\s+not|are\s+not|never|no\s+such)\b.{0,180}\b(?:red|white|black|golden)\b/i.test(value)
    || /\b(?:red|white|black|golden)\b.{0,180}\b(?:does\s+not|do\s+not|is\s+not|are\s+not|never)\b/i.test(value);
  return !explicitCorrection;
}

function isReviewedColorRegression(question) {
  const value = String(question || '');
  return /(?:D&C|Doctrine\s+and\s+Covenants)\s*(?:18|76)/i.test(value)
    && /\b(?:red|white|black|golden|color|colors|light|lights|degrees?\s+of\s+glory)\b/i.test(value);
}

function reviewedColorPayload() {
  return {
    id: 'focuschrist-reviewed-color-correction',
    choices: [{ index: 0, message: { role: 'assistant', content: REVIEWED_COLOR_CORRECTION }, finish_reason: 'stop' }],
    focuschrist_sources: [
      { text: 'Doctrine and Covenants 76:31-34', url: 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/76?id=p31-p34&lang=eng' },
      { text: 'Doctrine and Covenants 18:15', url: 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/18?id=p15&lang=eng' },
    ],
    focuschrist_source_integrity_verified: true,
    focuschrist_source_policy: SOURCE_POLICY_VERSION,
    focuschrist_gateway_mode: 'reviewed-local-correction',
  };
}

function requiresExternalGeneralResearch(question) {
  return GENERAL_RESEARCH_REQUIRED_PATTERN.test(String(question || ''));
}

async function callGroq(apiKey, body, mayRetry = true) {
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
  if (response.status === 429 && mayRetry) {
    const message = data && data.error ? String(data.error.message || '') : '';
    const messageDelay = message.match(/try again in\s+([\d.]+)s/i);
    const retrySeconds = Number.parseFloat(response.headers.get('retry-after') || (messageDelay ? messageDelay[1] : '2'));
    const waitMs = Math.min(30000, Math.max(1000, Number.isFinite(retrySeconds) ? (retrySeconds * 1000) + 500 : 2500));
    await new Promise((resolve) => setTimeout(resolve, waitMs));
    return callGroq(apiKey, body, false);
  }
  return { response, data };
}

function fallbackPayload(mode, extra, scope) {
  const general = scope && !scope.faith && !scope.selectedPioneer;
  return {
    id: 'focuschrist-source-policy',
    choices: [{
      index: 0,
      message: { role: 'assistant', content: general ? GENERAL_ANSWER_FALLBACK : SOURCE_INTEGRITY_FALLBACK },
      finish_reason: 'content_filter',
    }],
    focuschrist_sources: general ? [] : [{
      text: 'Official Gospel Library',
      url: 'https://www.churchofjesuschrist.org/study?lang=eng&platform=web',
    }],
    focuschrist_source_integrity_verified: false,
    focuschrist_source_policy: SOURCE_POLICY_VERSION,
    focuschrist_gateway_mode: mode,
    ...(extra || {}),
  };
}

async function produceLowRiskGeneralAnswer(apiKey, scope, draft) {
  if (!draft || requiresExternalGeneralResearch(scope.question)) return null;
  const prompt = [
    'You are the final checker for a low-risk, stable general-knowledge answer. Return one JSON object only.',
    'This path is never for current events, weather, prices, schedules, politics, medical, legal, financial, safety, statistics, quotations, citations, or source-specific questions.',
    'Decide whether the question is ordinary, stable, low-risk general knowledge that can be answered accurately without live retrieval.',
    'If it is, correct the draft if necessary and set approved true. Keep the answer concise, direct, nonreligious unless the user asked about religion, and free of invented citations or links.',
    'If it requires current or specialized evidence, set approved false and return an empty answer.',
    'Schema: {"approved":boolean,"answer":string}',
    '',
    `QUESTION:\n${scope.question}`,
    '',
    `DRAFT:\n${draft}`,
  ].join('\n');
  const result = await callGroq(apiKey, {
    model: VERIFIER_MODEL,
    messages: [{ role: 'user', content: prompt }],
    temperature: 0,
    max_tokens: 700,
    response_format: { type: 'json_object' },
  });
  if (!result.response.ok) return null;
  const content = result.data && result.data.choices && result.data.choices[0]
    ? result.data.choices[0].message.content
    : '';
  const verdict = parseVerifierJson(content);
  const answer = String(verdict && verdict.answer || '').trim();
  if (!verdict || verdict.approved !== true || !answer || hasKnownFalseClaim(answer)) return null;
  return answer;
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
    if (isReviewedColorRegression(sanitized.scope.question)) {
      return jsonResponse(reviewedColorPayload(), 200, origin);
    }
    if (!env || !env.GROQ_KEY_NEW) {
      return jsonResponse(fallbackPayload('research-unavailable', null, sanitized.scope), 200, origin);
    }

    try {
      const tellMyStoryEvidence = sanitized.scope.selectedPioneer
        ? await fetchTellMyStoryEvidence(sanitized.scope.selectedPioneerName)
        : null;
      const researchResult = await callGroq(env.GROQ_KEY_NEW, sanitized.research);
      if (!researchResult.response.ok && !tellMyStoryEvidence) {
        const limited = researchResult.response.status === 429;
        return jsonResponse(fallbackPayload(
          limited ? 'research-rate-limited' : 'research-provider-error',
          providerDiagnostic(researchResult),
          sanitized.scope,
        ), 200, origin);
      }
      const researchMessage = researchResult.response.ok && researchResult.data && researchResult.data.choices && researchResult.data.choices[0]
        ? researchResult.data.choices[0].message
        : null;
      const researchDraft = researchMessage ? String(researchMessage.content || '').trim() : '';
      const draft = researchDraft || (tellMyStoryEvidence
        ? `Write a concise, accurate biographical summary of ${sanitized.scope.selectedPioneerName} from the supplied Tell My Story, Too entry.`
        : '');
      const allEvidence = collectSourceEvidence(researchMessage);
      const officialEvidence = [];
      const officialUrls = new Set();
      allEvidence.filter(isOfficialChurchSource).forEach((source) => {
        const key = source.url.split('?')[0];
        if (!officialUrls.has(key) && officialEvidence.length < 2) {
          officialUrls.add(key);
          officialEvidence.push(source);
        }
      });
      const evidence = sanitized.scope.selectedPioneer
        ? [tellMyStoryEvidence].filter(Boolean)
        : (sanitized.scope.faith ? allEvidence.filter(isOfficialChurchSource) : allEvidence);
      if (draft && !evidence.length && !sanitized.scope.faith && !sanitized.scope.selectedPioneer) {
        const generalAnswer = await produceLowRiskGeneralAnswer(env.GROQ_KEY_NEW, sanitized.scope, draft);
        if (generalAnswer) {
          return jsonResponse({
            id: 'focuschrist-general-ai-consensus',
            choices: [{
              index: 0,
              message: { role: 'assistant', content: generalAnswer },
              finish_reason: 'stop',
            }],
            focuschrist_sources: [],
            focuschrist_source_integrity_verified: false,
            focuschrist_source_policy: SOURCE_POLICY_VERSION,
            focuschrist_gateway_mode: 'general-ai-consensus',
          }, 200, origin);
        }
      }
      if (!draft || !evidence.length) {
        return jsonResponse(fallbackPayload('research-insufficient-evidence', null, sanitized.scope), 200, origin);
      }

      const verifierPrompt = sanitized.scope.selectedPioneer ? [
        'You are writing a source-grounded biographical summary. Return one JSON object only.',
        `The visitor selected ${sanitized.scope.selectedPioneerName}. The evidence below is that person's permitted Tell My Story, Too entry.`,
        'Write a concise two-to-four paragraph answer using only facts in that entry. Do not use the optional research draft or add facts from memory.',
        'Attribute diary material, descendant recollections, family histories, traditions, and miraculous accounts to the people or source traditions named in the entry. Do not present them as official Church declarations.',
        'Do not reproduce long passages. Paraphrase the biography and preserve meaningful uncertainty words such as apparently, probably, recalled, reported, or according to the entry.',
        'If the entry contains usable biographical information for the selected person, set approved true and source_indexes to [1]. Set approved false only if the evidence is empty or belongs to a different person.',
        'Schema: {"approved":boolean,"answer":string,"source_indexes":number[]}',
        '',
        `EVIDENCE:\n${evidenceForVerifier(evidence)}`,
      ].join('\n') : [
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
      const verifierBody = {
        model: VERIFIER_MODEL,
        messages: [{ role: 'user', content: verifierPrompt }],
        temperature: 0,
        max_tokens: sanitized.scope.selectedPioneer ? 1000 : 1500,
        response_format: { type: 'json_object' },
      };
      let verifierResult = await callGroq(env.GROQ_KEY_NEW, verifierBody);
      if (!verifierResult.response.ok && isJsonValidationFailure(verifierResult)) {
        await new Promise((resolve) => setTimeout(resolve, 12000));
        verifierResult = await callGroq(env.GROQ_KEY_NEW, {
          ...verifierBody,
          messages: [{ role: 'user', content: `${verifierPrompt}\n\nReturn the JSON object as plain text with no markdown fence.` }],
          max_tokens: sanitized.scope.selectedPioneer ? 1200 : 1800,
          response_format: undefined,
        });
      }
      if (!verifierResult.response.ok) {
        return jsonResponse(fallbackPayload('verification-provider-error', providerDiagnostic(verifierResult), sanitized.scope), 200, origin);
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
        return jsonResponse(fallbackPayload('verification-rejected', {
          focuschrist_verifier_approved: Boolean(verdict && verdict.approved === true),
          focuschrist_verifier_source_indexes: verdict && Array.isArray(verdict.source_indexes)
            ? verdict.source_indexes.slice(0, 6)
            : [],
          focuschrist_verifier_answer_length: verdict ? String(verdict.answer || '').length : 0,
        }, sanitized.scope), 200, origin);
      }

      return jsonResponse({
        id: 'focuschrist-retrieval-verified',
        choices: [{
          index: 0,
          message: { role: 'assistant', content: answer },
          finish_reason: 'stop',
        }],
        focuschrist_sources: [
          ...selectedEvidence,
          ...(sanitized.scope.selectedPioneer ? officialEvidence : []),
        ].map((source) => ({
          text: source.title || 'Source',
          url: source.url,
        })),
        focuschrist_source_integrity_verified: true,
        focuschrist_source_policy: SOURCE_POLICY_VERSION,
        focuschrist_gateway_mode: 'retrieval-researched-and-verified',
      }, 200, origin);
    } catch (_error) {
      return jsonResponse(fallbackPayload('research-exception', null, sanitized.scope), 200, origin);
    }
  },
};

export {
  GENERAL_ANSWER_FALLBACK,
  SOURCE_INTEGRITY_FALLBACK,
  classifyResearchScope,
  collectSourceEvidence,
  extractSelectedPioneerName,
  extractTellMyStoryEntry,
  fetchTellMyStoryEvidence,
  guardVerifiedAnswer,
  hasKnownFalseClaim,
  isReviewedColorRegression,
  isOfficialChurchSource,
  isJsonValidationFailure,
  isTellMyStorySource,
  parseVerifierJson,
  requiresExternalGeneralResearch,
  sanitizePayload,
};
