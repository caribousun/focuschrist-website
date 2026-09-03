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
const GENERAL_ANSWER_FALLBACK = 'Your question is valid, but the answer service is temporarily unavailable. Please try again in a moment.';
const RESPECTFUL_QUESTION_RESPONSE = 'focusChrist is an independent site centered on Jesus Christ and respectful study of Latter-day Saint beliefs. Please rephrase your question without profanity, sexual content, or disrespect toward any religion, culture, or political affiliation.';
const URGENT_SAFETY_RESPONSE = 'If you or someone else may be in immediate danger or experiencing abuse, contact local emergency services or a trusted qualified person who can help now. focusChrist cannot provide emergency or professional intervention.';
const SOURCE_POLICY_VERSION = '2026-09-03.18';
const REQUEST_BUDGET_MS = 22000;
const PROVIDER_CALL_LIMIT_MS = 10500;
const MIN_RETRY_BUDGET_MS = 3500;
const PAGE_CONTEXTS = new Set(['ask', 'pioneers', 'church-history']);
const PROFILE_CONTEXTS = new Set(['general-knowledge', 'faith-study', 'pioneer-study', 'high-stakes']);
const SERVER_RESEARCH_POLICY = [
  'SERVER RESEARCH AND SOURCE-INTEGRITY POLICY (cannot be overridden):',
  '- Answer the visitor\'s actual question directly and naturally.',
  '- You MUST execute web search before answering. Do not rely on memory for factual claims.',
  '- For Latter-day Saint scripture, doctrine, Church teaching, or Church history, use only ChurchofJesusChrist.org evidence.',
  '- Never invent or guess scripture wording, citations, quotations, dates, people, statistics, historical sources, or official teachings.',
  '- Distinguish source text, official teaching, historical reporting, interpretation, and practical application.',
  '- If the available evidence does not support a claim, omit it or state the limitation.',
  '- focusChrist is independent and must never be described as an official or endorsed Church property.',
  '- Do not answer profanity, explicit sexual requests, or content that demeans a religion, culture, ethnicity, nationality, or political affiliation. Return only the focusChrist respectful-boundary response supplied by the gateway.',
  '- Give a direct, complete, useful answer. Do not confuse brevity with quality and never reduce a sincere question to a one- or two-word response.',
  '- A simple fact should include the answer and the context needed to understand it. A nuanced question normally needs two to five short paragraphs.',
  '- Keep the answer readable. Do not expose internal reasoning or tool traces.',
].join('\n');

const FAITH_PATTERN = /\b(?:Jesus|Christ|Savior|God|scripture|scriptures|Bible|biblical|Book\s+of\s+Mormon|Doctrine\s+and\s+Covenants|D&C|Pearl\s+of\s+Great\s+Price|Church\s+of\s+Jesus\s+Christ|Latter[- ]day\s+Saint|LDS|prophet|apostle|temple|priesthood|gospel|atonement|restoration|Joseph\s+Smith|Brigham\s+Young|pioneer|pioneers|Nephi|Alma|Mosiah|Moroni|Ether|Helaman|Mormon|celestial|terrestrial|telestial|Gospel\s+Library)\b/i;
const KNOWN_CHURCH_PERSON_PHRASES = [
  'hyrum smith', 'lucy mack smith', 'emma smith', 'oliver cowdery', 'brigham young',
  'eliza r snow', 'lorenzo snow', 'wilford woodruff', 'john taylor', 'heber c kimball',
  'parley p pratt', 'orson pratt', 'david whitmer', 'martin harris', 'sidney rigdon',
  'joseph f smith', 'joseph fielding smith', 'harold b lee', 'spencer w kimball',
  'ezra taft benson', 'howard w hunter', 'gordon b hinckley', 'thomas s monson',
  'russell m nelson', 'dallin h oaks', 'henry b eyring', 'jeffrey r holland',
];
const SCRIPTURE_REFERENCE_PATTERN = /\b(?:[1-4]\s+)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Doctrine\s+and\s+Covenants|D&C|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History)|Articles\s+of\s+Faith)\s+\d+(?::\d+(?:[-–]\d+)?)?/i;
const SCRIPTURE_BOOK_TOPIC_PATTERN = /(?:\b(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History))\b.{0,100}\b(?:says?|states?|teach(?:es)?|declares?|records?|promises?|describes?|means?|about)\b|\babout\s+(?:the\s+)?(?:book\s+of\s+)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History))\b)/i;
const CASELESS_CANON_NAME_PERSON_QUESTION_PATTERN = /(\bwho\s+(?:is|was)\s+)(?:Joshua|Ruth|Samuel|Ezra|Nehemiah|Esther|Job|Isaiah|Jeremiah|Ezekiel|Daniel|Hosea|Joel|Amos|Jonah|Micah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Timothy|Titus|Philemon|James|Peter|Jude|Nephi|Jacob|Enos|Mosiah|Alma|Helaman|Ether|Moroni|Moses|Abraham)\s+(?!the\b|and\b|or\b)[\p{L}'’.-]{2,}(?:\s+[\p{L}'’.-]{2,}){0,1}(?=\s*[?.!]*$)/giu;
const CASELESS_CANON_NAME_PERSON_ACTION_PATTERN = /(\b(?:what|when|where|why|how)\s+(?:did|does|is|was)\s+)(?:Joshua|Ruth|Samuel|Ezra|Nehemiah|Esther|Job|Isaiah|Jeremiah|Ezekiel|Daniel|Hosea|Joel|Amos|Jonah|Micah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Timothy|Titus|Philemon|James|Peter|Jude|Nephi|Jacob|Enos|Mosiah|Alma|Helaman|Ether|Moroni|Moses|Abraham)\s+(?!the\b|and\b|or\b)[\p{L}'’.-]{2,}(?:\s+[\p{L}'’.-]{2,}){0,1}(?=\s+(?:act(?:ed|ing)?|became|become|composed?|did|died?|lived?|made|make|said|say|served?|spoke|talked?|writes?|wrote)\b)/giu;
const CASELESS_CANON_NAME_PERSON_ABOUT_PATTERN = /(\btell\s+me\s+about\s+)(?:Joshua|Ruth|Samuel|Ezra|Nehemiah|Esther|Job|Isaiah|Jeremiah|Ezekiel|Daniel|Hosea|Joel|Amos|Jonah|Micah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Timothy|Titus|Philemon|James|Peter|Jude|Nephi|Jacob|Enos|Mosiah|Alma|Helaman|Ether|Moroni|Moses|Abraham)\s+(?!the\b|and\b|or\b|faith\b|sermon\b|story\b|account\b|creation\b|teachings?\b|prophecy\b|vision\b|chapter\b|book\b|gospel\b|loyalty\b)[\p{L}'’.-]{2,}(?:\s+[\p{L}'’.-]{2,}){0,1}(?=\s*[?.!]*$)/giu;
const KNOWN_FALSE_SOURCE_PATTERNS = [
  /red,?\s+white,?\s+and\s+black\s+lights?\s+(?:represent|symbolize|mean)/i,
  /(?:red|black|golden)\s+light.{0,180}(?:D&C|Doctrine\s+and\s+Covenants)\s+76.{0,100}(?:represent|symbolize|mean|celestial|terrestrial|telestial)/i,
];
const REVIEWED_COLOR_CORRECTION = 'No. Doctrine and Covenants 76:31-34 does not mention red, white, black, or golden lights and does not assign colors to degrees of glory. Those verses discuss people who know God\'s power and then deny it. Doctrine and Covenants 18:15 teaches the joy of helping bring one soul to Jesus Christ; it does not describe colors or degrees of glory.';
const GENERAL_RESEARCH_REQUIRED_PATTERN = /\b(?:current|currently|today|tonight|tomorrow|yesterday|latest|recent|news|weather|forecast|price|cost|rate|score|schedule|election|president|prime\s+minister|chief\s+executive|ceo|law|legal|court|tax|financial|finance|investment|stock|crypto|medical|medicine|medication|diagnosis|symptom|dose|suicide|self-harm|emergency|abuse|citation|cite|source|quotation|quote|statistics?|percentage)\b/i;
const EXPLICIT_NON_PIONEER_PATTERN = /\b(?:biblical|bible|old\s+testament|new\s+testament|book\s+of\s+exodus|moses|israelites?|egypt|pharaoh|genesis|oregon\s+trail|american\s+history|secular\s+history|not\s+(?:lds|latter[- ]day\s+saint)|non[- ]pioneer)\b/i;

function normalizeQuestionSafetyText(value) {
  return String(value || '')
    .normalize('NFKD')
    .toLowerCase()
    .replace(/[013457@$]/g, (character) => ({ '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '@': 'a', '$': 's' })[character] || character)
    .replace(/([a-z])\1{2,}/g, '$1$1')
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function evaluateQuestionSafety(value) {
  const normalized = normalizeQuestionSafetyText(value);
  const compact = normalized.replace(/\s+/g, '');
  if (/\b(?:sexual abuse|sexually abused|rape|raped|molest|molested|assaulted|immediate danger|being threatened|threatening me|hurt me|hurting me|kill me|being abused)\b/.test(normalized)) {
    return { allowed: false, kind: 'urgent-safety', response: URGENT_SAFETY_RESPONSE };
  }
  const profanity = /\b(?:fuck|fucking|fucked|motherfucker|shit|bullshit|bitch|bastard|ass|asshole|whore|slut|piss|dick|cock|pussy|faggot|nigger|retard|damn|crap|wtf|stfu)\b/.test(normalized)
    || /f+u+c+k+|s+h+i+t+|b+i+t+c+h+/.test(compact);
  const explicitSexual = /\b(?:sex|sexual|porn|pornography|nude|nudes|naked|intercourse|masturbate|masturbation|masturbating|orgasm|genital|genitals|explicit sex|sexual act|sexual fantasy|have sex|having sex)\b/.test(normalized);
  const protectedGroup = /\b(?:religion|religions|religious|faith|faiths|church|churches|christian|christians|catholic|catholics|protestant|protestants|latter day saint|latter day saints|lds|mormon|mormons|jewish|jews|muslim|muslims|islam|hindu|hindus|buddhist|buddhists|culture|cultures|cultural|ethnicity|ethnicities|ethnic|race|races|racial|nationality|nationalities|immigrant|immigrants|democrat|democrats|republican|republicans|liberal|liberals|conservative|conservatives|political party|political parties|political affiliation|political affiliations)\b/.test(normalized);
  const derogatory = /\b(?:stupid|idiot|idiots|evil|inferior|worthless|disgusting|trash|vermin|subhuman|hate|hateful|scum|moron|morons|should die|should be killed|deserve to die)\b/.test(normalized);
  const groupAttack = protectedGroup && derogatory
    && (/\b(?:why|are|is|all|those|these|people|followers|members|believers)\b/.test(normalized)
      || /\b(?:should die|should be killed|deserve to die|subhuman|vermin)\b/.test(normalized));
  const structuredGroupAttack = /\b(?:why are|all|those|these)\s+[a-z-]{3,30}(?:\s+people)?\s+(?:are\s+|is\s+)?(?:stupid|idiots?|evil|inferior|worthless|disgusting|trash|vermin|subhuman|scum|morons?|hateful)\b/.test(normalized);
  if (profanity || explicitSexual || groupAttack || structuredGroupAttack) {
    return { allowed: false, kind: 'respect-boundary', response: RESPECTFUL_QUESTION_RESPONSE };
  }
  return { allowed: true, kind: 'allowed', response: '' };
}

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

function classifyResearchScope(messages, requestedPage, requestedProfile) {
  const question = lastUserQuestion(messages);
  const normalizedQuestion = question.toLowerCase().replace(/[^a-z0-9\s'-]/g, ' ').replace(/\s+/g, ' ').trim();
  const scriptureTopicQuestion = question
    .replace(CASELESS_CANON_NAME_PERSON_QUESTION_PATTERN, '$1')
    .replace(CASELESS_CANON_NAME_PERSON_ACTION_PATTERN, '$1')
    .replace(CASELESS_CANON_NAME_PERSON_ABOUT_PATTERN, '$1');
  const page = PAGE_CONTEXTS.has(requestedPage) ? requestedPage : 'ask';
  const profile = PROFILE_CONTEXTS.has(requestedProfile) ? requestedProfile : '';
  const faith = page === 'pioneers'
    || page === 'church-history'
    || profile === 'faith-study'
    || profile === 'pioneer-study'
    || KNOWN_CHURCH_PERSON_PHRASES.some((name) => normalizedQuestion.includes(name))
    || FAITH_PATTERN.test(scriptureTopicQuestion)
    || SCRIPTURE_REFERENCE_PATTERN.test(question)
    || SCRIPTURE_BOOK_TOPIC_PATTERN.test(scriptureTopicQuestion);
  const selectedPioneerName = extractSelectedPioneerName(messages);
  return { faith, question, page, profile, selectedPioneer: Boolean(selectedPioneerName), selectedPioneerName };
}

function sanitizePayload(payload) {
  const clientMessages = Array.isArray(payload.messages)
    ? payload.messages
        .filter((message) => message && ['system', 'user', 'assistant'].includes(message.role) && typeof message.content === 'string')
        .slice(-16)
        .map((message) => ({ role: message.role, content: message.content.slice(0, 12000) }))
    : [];
  const scope = classifyResearchScope(clientMessages, payload.focuschrist_page, payload.focuschrist_profile);
  const conversationMessages = clientMessages
    .filter((message) => message.role === 'user' || message.role === 'assistant')
    .slice(-8)
    .map((message) => ({ role: message.role, content: message.content.slice(0, 3000) }));
  let scopeInstruction;
  if (scope.selectedPioneer) {
    scopeInstruction = `The visitor selected the pioneer ${scope.selectedPioneerName}. Search only site:churchofjesuschrist.org to corroborate that exact person's identity, company, dates, and journey. The gateway will separately supply the selected Tell My Story, Too biography.`;
  } else if (scope.page === 'pioneers' && EXPLICIT_NON_PIONEER_PATTERN.test(scope.question)) {
    scopeInstruction = 'This request comes from the Pioneers page, but the visitor explicitly requested a biblical or non-pioneer subject. Answer that explicit subject directly. Use only ChurchofJesusChrist.org evidence for biblical or Latter-day Saint claims.';
  } else if (scope.page === 'pioneers') {
    scopeInstruction = 'This request comes from the focusChrist Pioneers page. Interpret ambiguous labels in Latter-day Saint pioneer and Church-history context. In particular, an unqualified Exodus means the 1846 exodus from Nauvoo, not the biblical Exodus. Search only site:churchofjesuschrist.org and distinguish established fact from recollection, tradition, and interpretation.';
  } else if (scope.page === 'church-history') {
    scopeInstruction = 'This request comes from the focusChrist Church History page. Interpret ambiguous questions and follow-ups within Latter-day Saint Church history. Search only site:churchofjesuschrist.org and prefer the official Church History and Saints source family.';
  } else if (scope.faith) {
    scopeInstruction = 'For this request, search only site:churchofjesuschrist.org and use only ChurchofJesusChrist.org evidence.';
  } else {
    scopeInstruction = 'Use web search to gather reliable evidence before answering.';
  }
  const research = {
    model: RESEARCH_MODEL,
    // Browser prompts are presentation hints, not server-owned source policy.
    // Keeping them out of the research request prevents an Ask-page keyword
    // from inheriting Pioneer scope and sharply reduces provider token use.
    messages: [{ role: 'system', content: SERVER_RESEARCH_POLICY + '\n' + scopeInstruction }, ...conversationMessages],
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
      content: String(content || '').replace(/\s+/g, ' ').trim().slice(0, 700),
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
  return unique.slice(0, 4);
}

function isOfficialChurchSource(source) {
  return source && (source.host === OFFICIAL_CHURCH_HOST || source.host.endsWith(`.${OFFICIAL_CHURCH_HOST}`));
}

function identityTokens(question) {
  const value = String(question || '').toLowerCase().replace(/[^a-z0-9' -]/g, ' ').replace(/\s+/g, ' ').trim();
  const match = value.match(/^(?:who\s+(?:is|was)|tell\s+me\s+about)\s+(.+?)(?:\s*[?.!]|$)/);
  if (!match) return [];
  return match[1].split(/\s+/).filter((token) => token.length >= 2).slice(0, 5);
}

function withinOneEdit(left, right) {
  if (left === right) return true;
  if (Math.abs(left.length - right.length) > 1 || Math.max(left.length, right.length) < 4) return false;
  let row = Array.from({ length: right.length + 1 }, (_, index) => index);
  for (let i = 1; i <= left.length; i += 1) {
    const next = [i];
    for (let j = 1; j <= right.length; j += 1) {
      next[j] = Math.min(
        next[j - 1] + 1,
        row[j] + 1,
        row[j - 1] + (left[i - 1] === right[j - 1] ? 0 : 1),
      );
    }
    row = next;
  }
  return row[right.length] <= 1;
}

function isOfficialChurchIdentityEvidence(question, evidence) {
  const requested = identityTokens(question);
  if (requested.length < 2) return false;
  return (Array.isArray(evidence) ? evidence : []).some((source) => {
    if (!isOfficialChurchSource(source)) return false;
    let pathname = '';
    try { pathname = new URL(source.url).pathname.toLowerCase(); } catch (_error) {}
    const historyContext = source.host.startsWith('history.')
      || /\/(?:study\/)?(?:church-history|history)(?:\/|$)/.test(pathname)
      || /\b(?:church history|latter-day saint|the church of jesus christ)\b/i.test(`${source.title} ${source.content}`);
    if (!historyContext) return false;
    const evidenceTokens = String(`${source.title} ${source.url}`)
      .toLowerCase()
      .replace(/[^a-z0-9' -]/g, ' ')
      .split(/\s+/)
      .filter(Boolean);
    return requested.every((token) => evidenceTokens.some((candidate) => withinOneEdit(token, candidate)));
  });
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

async function fetchTellMyStoryEvidence(selectedName, deadline) {
  if (!selectedName) return null;
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const available = deadline ? remainingBudget(deadline) : 4000;
  if (available < 250) return null;
  const timer = controller ? setTimeout(() => controller.abort(), Math.max(200, Math.min(4000, available - 50))) : null;
  try {
    const response = await fetch(TELL_MY_STORY_URL, {
      headers: { Accept: 'text/plain' },
      signal: controller ? controller.signal : undefined,
    });
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
  } finally {
    if (timer) clearTimeout(timer);
  }
}

function evidenceForVerifier(evidence) {
  return evidence.map((source, index) => [
    `SOURCE ${index + 1}`,
    `SOURCE CLASS: ${source.sourceClass || (isOfficialChurchSource(source) ? 'official-church' : 'web')}`,
    `TITLE: ${source.title}`,
    `URL: ${source.url}`,
    `CONTENT: ${source.content || '(No retrievable source excerpt was returned.)'}`,
  ].join('\n')).join('\n\n').slice(0, 5000);
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
  if (!answerMeetsSubstanceContract(text, scope)) return SOURCE_INTEGRITY_FALLBACK;
  return text;
}

function answerSubstanceRequirements(scope) {
  if (scope && scope.selectedPioneer) return { minimumWords: 90, minimumSentences: 3, minimumParagraphs: 2 };
  if (scope && scope.faith) return { minimumWords: 70, minimumSentences: 3, minimumParagraphs: 1 };
  return { minimumWords: 45, minimumSentences: 2, minimumParagraphs: 1 };
}

function answerMeetsSubstanceContract(answer, scope) {
  const text = String(answer || '').replace(/\s+/g, ' ').trim();
  const original = String(answer || '').trim();
  const requirements = answerSubstanceRequirements(scope);
  const words = text ? text.split(' ').filter(Boolean).length : 0;
  const sentences = countCompleteSentences(text);
  const paragraphs = original ? original.split(/\n\s*\n/).filter((value) => value.trim()).length : 0;
  return words >= requirements.minimumWords
    && sentences >= requirements.minimumSentences
    && paragraphs >= requirements.minimumParagraphs;
}

function countCompleteSentences(answer) {
  const text = String(answer || '').replace(/\s+/g, ' ').trim();
  if (!text) return 0;
  const segments = typeof Intl !== 'undefined' && typeof Intl.Segmenter === 'function'
    ? Array.from(new Intl.Segmenter('en', { granularity: 'sentence' }).segment(text), (item) => item.segment)
    : (text
        .replace(/\b(?:Mr|Mrs|Ms|Dr|Prof|Rev|Sr|Jr|St|Mt|Gen|Gov|Pres|No|vs|etc)\./gi, (value) => value.slice(0, -1))
        .replace(/\b[ap]\.m\./gi, (value) => value.replace(/\./g, ''))
        .match(/[^.!?]+[.!?][”"')\]]?/g) || []);
  return segments.filter((segment) => {
    const value = segment.trim();
    const sentenceWords = value.match(/[\p{L}\p{N}]+(?:['’][-\p{L}\p{N}]+)*/gu) || [];
    return sentenceWords.length >= 3 && /[.!?][”"')\]]?$/.test(value);
  }).length;
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

function needsIdentityClarification(question) {
  const value = String(question || '').toLowerCase().replace(/[^a-z0-9\s'-]/g, ' ').replace(/\s+/g, ' ').trim();
  if (!/\b(?:when|year|die|died|death|killed|martyred|martyrdom|murdered)\b/.test(value)) return false;
  if (/\bjoseph\s+smith\b/.test(value)) return false;
  const bare = value.match(/\bjoseph(?:\s+([a-z'-]+))?/);
  if (!bare) return false;
  if (!bare[1]) return true;
  return ['was', 'is', 'did', 'die', 'died', 'death', 'killed', 'martyred', 'martyrdom', 'murdered', 'get', 'got', 'be'].includes(bare[1]);
}

function remainingBudget(deadline) {
  return Math.max(0, Number(deadline || 0) - Date.now());
}

function providerFailure(status, code) {
  return {
    response: new Response(JSON.stringify({ error: { code } }), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
    data: { error: { code } },
  };
}

async function callGroq(apiKey, body, deadline, mayRetry = true) {
  const available = remainingBudget(deadline);
  if (available < 250) return providerFailure(504, 'timeout');
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timeoutMs = Math.max(200, Math.min(PROVIDER_CALL_LIMIT_MS, available - 50));
  const timer = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;
  let response;
  try {
    response = await fetch(GROQ_ENDPOINT, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        // Basic search keeps official-source retrieval within the provider's
        // request-size limit; the Worker independently verifies its snippets.
        'Groq-Model-Version': '2025-07-23',
      },
      body: JSON.stringify(body),
      signal: controller ? controller.signal : undefined,
    });
  } catch (error) {
    return providerFailure(error && error.name === 'AbortError' ? 504 : 503,
      error && error.name === 'AbortError' ? 'timeout' : 'service_unavailable');
  } finally {
    if (timer) clearTimeout(timer);
  }
  let data = null;
  try { data = await response.json(); } catch (_error) {}
  if (response.status === 429 && mayRetry && remainingBudget(deadline) >= MIN_RETRY_BUDGET_MS) {
    const message = data && data.error ? String(data.error.message || '') : '';
    const messageDelay = message.match(/try again in\s+([\d.]+)s/i);
    const retrySeconds = Number.parseFloat(response.headers.get('retry-after') || (messageDelay ? messageDelay[1] : '2'));
    const requestedWait = Number.isFinite(retrySeconds) ? (retrySeconds * 1000) + 100 : 500;
    const waitMs = Math.min(5000, Math.max(250, requestedWait), Math.max(0, remainingBudget(deadline) - MIN_RETRY_BUDGET_MS));
    await new Promise((resolve) => setTimeout(resolve, waitMs));
    return callGroq(apiKey, body, deadline, false);
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
    focuschrist_resolved_profile: scope && scope.faith ? 'faith-study' : (scope && scope.profile || 'general-knowledge'),
    focuschrist_classification_mode: scope && scope.classificationMode || 'request-scope',
    ...(extra || {}),
  };
}

async function produceLowRiskGeneralAnswer(apiKey, scope, draft, deadline) {
  const diagnostic = { focuschrist_low_risk_stage: 'started' };
  scope.lowRiskDiagnostic = diagnostic;
  if (requiresExternalGeneralResearch(scope.question)) {
    diagnostic.focuschrist_low_risk_stage = 'ineligible';
    return null;
  }
  const prompt = [
    'You are the final checker for a low-risk, stable general-knowledge answer. Return one JSON object only.',
    'This path is never for current events, weather, prices, schedules, politics, medical, legal, financial, safety, statistics, quotations, citations, or source-specific questions.',
    'Decide whether the question is ordinary, stable, low-risk general knowledge that can be answered accurately without live retrieval.',
    'If it is, answer directly or correct the draft if one is supplied, then set approved true. Give at least 45 words and two complete sentences: state the direct answer first, then add useful context that explains the fact. Keep it direct, nonreligious unless the user asked about religion, and free of invented citations or links.',
    'If it requires current or specialized evidence, set approved false and return an empty answer.',
    'Schema: {"approved":boolean,"answer":string}',
    '',
    `QUESTION:\n${scope.question}`,
    '',
    `DRAFT:\n${draft || '(No draft was available. Write the answer directly from stable general knowledge.)'}`,
  ].join('\n');
  const result = await callGroq(apiKey, {
    model: VERIFIER_MODEL,
    messages: [{ role: 'user', content: prompt }],
    temperature: 0,
    max_tokens: 700,
    response_format: { type: 'json_object' },
  }, deadline);
  if (!result.response.ok) {
    Object.assign(diagnostic, providerDiagnostic(result));
    diagnostic.focuschrist_low_risk_stage = 'initial-provider-error';
    return null;
  }
  const content = result.data && result.data.choices && result.data.choices[0]
    ? result.data.choices[0].message.content
    : '';
  let verdict = parseVerifierJson(content);
  diagnostic.focuschrist_low_risk_stage = 'initial-verdict';
  diagnostic.focuschrist_low_risk_initial_approved = Boolean(verdict && verdict.approved === true);
  diagnostic.focuschrist_low_risk_initial_words = String(verdict && verdict.answer || '').split(/\s+/).filter(Boolean).length;
  diagnostic.focuschrist_low_risk_initial_sentences = countCompleteSentences(verdict && verdict.answer);
  if (verdict && verdict.approved === true
    && !answerMeetsSubstanceContract(verdict.answer, scope)) {
    const requirements = answerSubstanceRequirements(scope);
    if (remainingBudget(deadline) < 4500) {
      diagnostic.focuschrist_low_risk_stage = 'expansion-skipped-deadline';
      return null;
    }
    const expansionResult = await callGroq(apiKey, {
      model: VERIFIER_MODEL,
      messages: [{ role: 'user', content: [
        prompt,
        '',
        'Your previous approved answer was too brief.',
        `Rewrite it using at least ${requirements.minimumWords} words and ${requirements.minimumSentences} complete sentences.`,
        'State the direct answer first, then add useful stable context. Do not pad, repeat, invent a citation, or add current, high-stakes, or specialized claims.',
        `PREVIOUS ANSWER:\n${String(verdict.answer || '').trim()}`,
        'Return the complete JSON object again with approved and answer.',
      ].join('\n') }],
      temperature: 0,
      max_tokens: 900,
      response_format: { type: 'json_object' },
    }, deadline, false);
    if (expansionResult.response.ok) {
      const expansionContent = expansionResult.data && expansionResult.data.choices && expansionResult.data.choices[0]
        ? expansionResult.data.choices[0].message.content
        : '';
      const expansionVerdict = parseVerifierJson(expansionContent);
      if (expansionVerdict) verdict = expansionVerdict;
      diagnostic.focuschrist_low_risk_stage = 'expanded-verdict';
      diagnostic.focuschrist_low_risk_expanded_approved = Boolean(expansionVerdict && expansionVerdict.approved === true);
      diagnostic.focuschrist_low_risk_expanded_words = String(expansionVerdict && expansionVerdict.answer || '').split(/\s+/).filter(Boolean).length;
      diagnostic.focuschrist_low_risk_expanded_sentences = countCompleteSentences(expansionVerdict && expansionVerdict.answer);
    } else {
      Object.assign(diagnostic, providerDiagnostic(expansionResult));
      diagnostic.focuschrist_low_risk_stage = 'expansion-provider-error';
    }
  }
  const answer = String(verdict && verdict.answer || '').trim();
  if (!verdict || verdict.approved !== true || !answer || hasKnownFalseClaim(answer)
    || !answerMeetsSubstanceContract(answer, scope)) {
    diagnostic.focuschrist_low_risk_stage = `${diagnostic.focuschrist_low_risk_stage}-rejected`;
    return null;
  }
  diagnostic.focuschrist_low_risk_stage = 'accepted';
  return answer;
}

function generalAnswerPayload(answer, mode) {
  return {
    id: 'focuschrist-general-ai-answer',
    choices: [{
      index: 0,
      message: { role: 'assistant', content: answer },
      finish_reason: 'stop',
    }],
    focuschrist_sources: [],
    focuschrist_source_integrity_verified: false,
    focuschrist_source_policy: SOURCE_POLICY_VERSION,
    focuschrist_gateway_mode: mode,
    focuschrist_answer_word_count: String(answer || '').split(/\s+/).filter(Boolean).length,
  };
}

function providerDiagnostic(result) {
  const error = result && result.data && result.data.error ? result.data.error : {};
  const rawCode = String(error.code || error.type || '');
  const publicCodes = new Set([
    'rate_limit_exceeded', 'json_validate_failed', 'failed_generation',
    'invalid_api_key', 'invalid_request_error', 'context_length_exceeded',
    'server_error', 'service_unavailable', 'timeout',
  ]);
  const safeCode = publicCodes.has(rawCode) ? rawCode : (rawCode ? 'provider_error' : '');
  return {
    focuschrist_provider_status: result && result.response ? result.response.status : 0,
    focuschrist_provider_code: safeCode,
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
    const safety = evaluateQuestionSafety(sanitized.scope.question);
    if (!safety.allowed) {
      return jsonResponse({
        id: 'focuschrist-question-boundary',
        choices: [{ index: 0, message: { role: 'assistant', content: safety.response }, finish_reason: 'content_filter' }],
        focuschrist_sources: [],
        focuschrist_source_integrity_verified: false,
        focuschrist_source_policy: SOURCE_POLICY_VERSION,
        focuschrist_gateway_mode: safety.kind,
        focuschrist_resolved_profile: 'local-boundary',
        focuschrist_classification_mode: 'server-question-safety',
      }, 200, origin);
    }
    if (!sanitized.scope.faith && needsIdentityClarification(sanitized.scope.question)) {
      return jsonResponse(generalAnswerPayload(
        'Which Joseph do you mean? Please include the last name or a little more context.',
        'general-identity-clarification',
      ), 200, origin);
    }
    if (isReviewedColorRegression(sanitized.scope.question)) {
      return jsonResponse(reviewedColorPayload(), 200, origin);
    }
    if (!env || !env.GROQ_KEY_NEW) {
      return jsonResponse(fallbackPayload('research-unavailable', null, sanitized.scope), 200, origin);
    }

    const deadline = Date.now() + REQUEST_BUDGET_MS;
    try {
      const tellMyStoryEvidence = sanitized.scope.selectedPioneer
        ? await fetchTellMyStoryEvidence(sanitized.scope.selectedPioneerName, deadline)
        : null;
      const researchResult = await callGroq(env.GROQ_KEY_NEW, sanitized.research, deadline);
      if (!researchResult.response.ok && !tellMyStoryEvidence) {
        if (!sanitized.scope.faith && !sanitized.scope.selectedPioneer) {
          const directGeneralAnswer = await produceLowRiskGeneralAnswer(env.GROQ_KEY_NEW, sanitized.scope, '', deadline);
          if (directGeneralAnswer) {
            return jsonResponse(generalAnswerPayload(directGeneralAnswer, 'general-ai-low-risk'), 200, origin);
          }
        }
        const limited = researchResult.response.status === 429;
        return jsonResponse(fallbackPayload(
          limited ? 'research-rate-limited' : 'research-provider-error',
          { ...providerDiagnostic(researchResult), ...(sanitized.scope.lowRiskDiagnostic || {}) },
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
      if (!sanitized.scope.faith && isOfficialChurchIdentityEvidence(sanitized.scope.question, allEvidence)) {
        sanitized.scope.faith = true;
        sanitized.scope.profile = 'faith-study';
        sanitized.scope.classificationMode = 'official-church-identity-evidence';
      }
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
        : (sanitized.scope.faith ? allEvidence.filter(isOfficialChurchSource) : allEvidence).slice(0, 2);
      if (draft && !evidence.length && !sanitized.scope.faith && !sanitized.scope.selectedPioneer) {
        const generalAnswer = await produceLowRiskGeneralAnswer(env.GROQ_KEY_NEW, sanitized.scope, draft, deadline);
        if (generalAnswer) {
          return jsonResponse(generalAnswerPayload(generalAnswer, 'general-ai-consensus'), 200, origin);
        }
      }
      if (!draft || !evidence.length) {
        return jsonResponse(fallbackPayload(
          'research-insufficient-evidence',
          sanitized.scope.lowRiskDiagnostic || null,
          sanitized.scope,
        ), 200, origin);
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
        'Repair the draft into a direct, complete answer using the evidence. Remove unsupported detail and correct contradictions, but preserve useful supported explanation. Do not add facts from memory.',
        'For a simple general fact, give at least 45 words and two complete sentences. For a faith or Church-history question, give at least 70 words and three complete sentences. A nuanced question normally needs two to five short paragraphs. Put the direct answer first, then explain the context supported by the evidence. Never return a one-line fact fragment, a one- or two-word answer, or padded repetition.',
        'For a Latter-day Saint question, reject any evidence outside ChurchofJesusChrist.org.',
        'Set approved true whenever the evidence supports a useful answer, even if unsupported parts of the draft must be removed. Set approved false only when the evidence is empty, unrelated, or cannot support a responsible answer. source_indexes must list the 1-based evidence sources that directly support the final answer.',
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
      let verifierResult = await callGroq(env.GROQ_KEY_NEW, verifierBody, deadline);
      if (!verifierResult.response.ok && isJsonValidationFailure(verifierResult)
        && remainingBudget(deadline) >= 4500) {
        await new Promise((resolve) => setTimeout(resolve, Math.min(250, remainingBudget(deadline))));
        verifierResult = await callGroq(env.GROQ_KEY_NEW, {
          ...verifierBody,
          messages: [{ role: 'user', content: `${verifierPrompt}\n\nReturn the JSON object as plain text with no markdown fence.` }],
          max_tokens: sanitized.scope.selectedPioneer ? 1200 : 1800,
          response_format: undefined,
        }, deadline, false);
      }
      if (!verifierResult.response.ok) {
        return jsonResponse(fallbackPayload('verification-provider-error', providerDiagnostic(verifierResult), sanitized.scope), 200, origin);
      }
      const verifierContent = verifierResult.data && verifierResult.data.choices && verifierResult.data.choices[0]
        ? verifierResult.data.choices[0].message.content
        : '';
      let verdict = parseVerifierJson(verifierContent);
      let indexes = verdict && Array.isArray(verdict.source_indexes)
        ? verdict.source_indexes.filter((index) => Number.isInteger(index) && index >= 1 && index <= evidence.length)
        : [];
      if (verdict && verdict.approved === true && indexes.length
        && !answerMeetsSubstanceContract(verdict.answer, sanitized.scope)
        && remainingBudget(deadline) >= 4500) {
        const requirements = answerSubstanceRequirements(sanitized.scope);
        const expansionPrompt = [
          verifierPrompt,
          '',
          'Your previous approved answer did not meet the required answer depth.',
          `Rewrite it using at least ${requirements.minimumWords} words, ${requirements.minimumSentences} complete sentences, and ${requirements.minimumParagraphs} paragraph(s).`,
          'State the direct answer first. Add only useful explanatory context supported by the supplied evidence; do not pad, repeat, speculate, or add facts from memory.',
          `PREVIOUS ANSWER:\n${String(verdict.answer || '').trim()}`,
          'Return the complete JSON object again with approved, answer, and source_indexes.',
        ].join('\n');
        const expansionResult = await callGroq(env.GROQ_KEY_NEW, {
          ...verifierBody,
          messages: [{ role: 'user', content: expansionPrompt }],
          max_tokens: sanitized.scope.selectedPioneer ? 1400 : 1800,
        }, deadline, false);
        if (expansionResult.response.ok) {
          const expansionContent = expansionResult.data && expansionResult.data.choices && expansionResult.data.choices[0]
            ? expansionResult.data.choices[0].message.content
            : '';
          const expansionVerdict = parseVerifierJson(expansionContent);
          if (expansionVerdict) {
            verdict = expansionVerdict;
            indexes = Array.isArray(verdict.source_indexes)
              ? verdict.source_indexes.filter((index) => Number.isInteger(index) && index >= 1 && index <= evidence.length)
              : [];
          }
        }
      }
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
        focuschrist_resolved_profile: sanitized.scope.faith ? 'faith-study' : (sanitized.scope.profile || 'general-knowledge'),
        focuschrist_classification_mode: sanitized.scope.classificationMode || 'request-scope',
        focuschrist_answer_word_count: answer.split(/\s+/).filter(Boolean).length,
      }, 200, origin);
    } catch (_error) {
      return jsonResponse(fallbackPayload('research-exception', null, sanitized.scope), 200, origin);
    }
  },
};

export {
  GENERAL_ANSWER_FALLBACK,
  PROVIDER_CALL_LIMIT_MS,
  REQUEST_BUDGET_MS,
  SOURCE_INTEGRITY_FALLBACK,
  answerMeetsSubstanceContract,
  answerSubstanceRequirements,
  callGroq,
  classifyResearchScope,
  collectSourceEvidence,
  extractSelectedPioneerName,
  extractTellMyStoryEntry,
  evaluateQuestionSafety,
  fetchTellMyStoryEvidence,
  guardVerifiedAnswer,
  hasKnownFalseClaim,
  isReviewedColorRegression,
  isOfficialChurchSource,
  isOfficialChurchIdentityEvidence,
  isJsonValidationFailure,
  isTellMyStorySource,
  needsIdentityClarification,
  parseVerifierJson,
  providerDiagnostic,
  remainingBudget,
  requiresExternalGeneralResearch,
  sanitizePayload,
};
