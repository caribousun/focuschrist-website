import { CHURCH_SOURCE_INDEX, CHURCH_SOURCE_ROBOTS_SHA256, CHURCH_SOURCE_SITEMAP_REVISION } from './church-source-index.js';

// focusChrist server-owned, retrieval-grounded AI gateway.
// Reviewed local answers remain the first choice. This Worker retrieves
// official evidence for faith questions and independently checks every
// unreviewed answer before returning it to the browser.

const RESEARCH_MODEL = 'groq/compound-mini';
const VERIFIER_MODEL = 'openai/gpt-oss-20b';
const CLOUDFLARE_VERIFIER_MODEL = '@cf/meta/llama-3.3-70b-instruct-fp8-fast';
const CLOUDFLARE_FALLBACK_MODEL = '@cf/meta/llama-3.1-8b-instruct-fp8-fast';
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
const SOURCE_POLICY_VERSION = '2026-09-03.30';
const REQUEST_BUDGET_MS = 22000;
const PROVIDER_CALL_LIMIT_MS = 10500;
const MIN_RETRY_BUDGET_MS = 3500;
const CLOUDFLARE_VERIFIER_LIMIT_MS = 12000;
const VERIFIER_FALLBACK_RESERVE_MS = 5000;
const OFFICIAL_FETCH_LIMIT_MS = 9000;
const CLOUDFLARE_UNMETERED_CALL_NEURONS = 1000;
const OFFICIAL_HTML_BYTE_LIMIT = 1500000;
const REQUEST_BODY_BYTE_LIMIT = 65536;
const REQUEST_MESSAGE_LIMIT = 16;
const OFFICIAL_INDEX_URLS = new Set(CHURCH_SOURCE_INDEX.map((entry) => entry.url));
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
const INDEX_STOP_WORDS = new Set('a an and are as at be because been being but by can did do does for from gospel guide had has have how i in into is it its latter manual me of on or our saint saints should study tell that the their them there these they this to topics us was were what when where which who why will with would you your says said teach teaches taught meaning means mean'.split(' '));
const SCRIPTURE_ROUTES = Object.freeze({
  genesis:['ot','gen'],exodus:['ot','ex'],leviticus:['ot','lev'],numbers:['ot','num'],deuteronomy:['ot','deut'],joshua:['ot','josh'],judges:['ot','judg'],ruth:['ot','ruth'],samuel:['ot','sam'],kings:['ot','kgs'],chronicles:['ot','chr'],ezra:['ot','ezra'],nehemiah:['ot','neh'],esther:['ot','esth'],job:['ot','job'],psalm:['ot','ps'],psalms:['ot','ps'],proverbs:['ot','prov'],ecclesiastes:['ot','eccl'],isaiah:['ot','isa'],jeremiah:['ot','jer'],lamentations:['ot','lam'],ezekiel:['ot','ezek'],daniel:['ot','dan'],hosea:['ot','hosea'],joel:['ot','joel'],amos:['ot','amos'],obadiah:['ot','obad'],jonah:['ot','jonah'],micah:['ot','micah'],nahum:['ot','nahum'],habakkuk:['ot','hab'],zephaniah:['ot','zeph'],haggai:['ot','hag'],zechariah:['ot','zech'],malachi:['ot','mal'],
  matthew:['nt','matt'],mark:['nt','mark'],luke:['nt','luke'],john:['nt','john'],acts:['nt','acts'],romans:['nt','rom'],corinthians:['nt','cor'],galatians:['nt','gal'],ephesians:['nt','eph'],philippians:['nt','philip'],colossians:['nt','col'],thessalonians:['nt','thes'],timothy:['nt','tim'],titus:['nt','titus'],philemon:['nt','philem'],hebrews:['nt','heb'],james:['nt','james'],peter:['nt','pet'],jude:['nt','jude'],revelation:['nt','rev'],
  'song of solomon':['ot','song'],nephi:['bofm','ne'],jacob:['bofm','jacob'],enos:['bofm','enos'],jarom:['bofm','jarom'],omni:['bofm','omni'],'words of mormon':['bofm','w-of-m'],mosiah:['bofm','mosiah'],alma:['bofm','alma'],helaman:['bofm','hel'],mormon:['bofm','morm'],ether:['bofm','ether'],moroni:['bofm','moro'],moses:['pgp','moses'],abraham:['pgp','abr'],
});
const SCRIPTURE_CHAPTER_LIMITS = Object.freeze({
  'ot/gen':50,'ot/ex':40,'ot/lev':27,'ot/num':36,'ot/deut':34,'ot/josh':24,'ot/judg':21,'ot/ruth':4,
  'ot/1-sam':31,'ot/2-sam':24,'ot/1-kgs':22,'ot/2-kgs':25,'ot/1-chr':29,'ot/2-chr':36,'ot/ezra':10,
  'ot/neh':13,'ot/esth':10,'ot/job':42,'ot/ps':150,'ot/prov':31,'ot/eccl':12,'ot/song':8,'ot/isa':66,
  'ot/jer':52,'ot/lam':5,'ot/ezek':48,'ot/dan':12,'ot/hosea':14,'ot/joel':3,'ot/amos':9,'ot/obad':1,
  'ot/jonah':4,'ot/micah':7,'ot/nahum':3,'ot/hab':3,'ot/zeph':3,'ot/hag':2,'ot/zech':14,'ot/mal':4,
  'nt/matt':28,'nt/mark':16,'nt/luke':24,'nt/john':21,'nt/acts':28,'nt/rom':16,'nt/1-cor':16,
  'nt/2-cor':13,'nt/gal':6,'nt/eph':6,'nt/philip':4,'nt/col':4,'nt/1-thes':5,'nt/2-thes':3,
  'nt/1-tim':6,'nt/2-tim':4,'nt/titus':3,'nt/philem':1,'nt/heb':13,'nt/james':5,'nt/1-pet':5,
  'nt/2-pet':3,'nt/1-jn':5,'nt/2-jn':1,'nt/3-jn':1,'nt/jude':1,'nt/rev':22,
  'bofm/1-ne':22,'bofm/2-ne':33,'bofm/3-ne':30,'bofm/4-ne':1,'bofm/jacob':7,'bofm/enos':1,
  'bofm/jarom':1,'bofm/omni':1,'bofm/w-of-m':1,'bofm/mosiah':29,'bofm/alma':63,'bofm/hel':16,
  'bofm/morm':9,'bofm/ether':15,'bofm/moro':10,'dc-testament/dc':138,'pgp/moses':8,'pgp/abr':5,
  'pgp/js-m':1,'pgp/js-h':1,'pgp/a-of-f':1,
});
const SCRIPTURE_MAX_ORDINAL = Object.freeze({
  sam:2,kgs:2,chr:2,cor:2,thes:2,tim:2,pet:2,john:3,ne:4,
});
const SCRIPTURE_ROUTE_PATTERN = new RegExp(
  `\\b([1-4]\\s+)?(Doctrine\\s+and\\s+Covenants|D&C|Joseph\\s+Smith(?:—|-|\\s+)(?:Matthew|History)|Articles\\s+of\\s+Faith|${Object.keys(SCRIPTURE_ROUTES).sort((left, right) => right.length - left.length).join('|')})\\s+(?:chapter\\s+)?(\\d{1,3})(?::(\\d{1,3})(?:[-–](\\d{1,3}))?)?`,
  'i',
);

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
  const earlierContext = (Array.isArray(messages) ? messages : []).slice(0, -1)
    .map((message) => String(message && message.content || '').toLowerCase()).join(' ');
  const contextualSubject = KNOWN_CHURCH_PERSON_PHRASES.find((name) => earlierContext.includes(name)) || '';
  const usesConversationContext = Boolean(contextualSubject
    && /\b(?:he|him|his|she|her|hers|they|them|their|that person|this person|the leader)\b/i.test(question));
  const retrievalQuestion = usesConversationContext ? `${contextualSubject}: ${question}` : question;
  const faith = page === 'pioneers'
    || page === 'church-history'
    || profile === 'faith-study'
    || profile === 'pioneer-study'
    || KNOWN_CHURCH_PERSON_PHRASES.some((name) => normalizedQuestion.includes(name))
    || FAITH_PATTERN.test(scriptureTopicQuestion)
    || SCRIPTURE_REFERENCE_PATTERN.test(question)
    || SCRIPTURE_BOOK_TOPIC_PATTERN.test(scriptureTopicQuestion)
    || usesConversationContext;
  const selectedPioneerName = extractSelectedPioneerName(messages);
  return {
    faith, question, retrievalQuestion, page, profile,
    classificationMode: usesConversationContext ? 'conversation-context' : 'request-scope',
    selectedPioneer: Boolean(selectedPioneerName), selectedPioneerName,
  };
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
    max_tokens: 700,
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

function normalizeDiscoveryTokens(value) {
  const stem = (token) => {
    if (token.endsWith('ies') && token.length > 5) return `${token.slice(0, -3)}y`;
    if (token.endsWith('ed') && token.length > 5) return token.endsWith('ied') ? `${token.slice(0, -3)}y` : token.slice(0, -1);
    if (token.endsWith('ing') && token.length > 6) return token.slice(0, -3);
    if (token.endsWith('s') && !token.endsWith('ss') && token.length > 4) return token.slice(0, -1);
    return token;
  };
  return [...new Set(String(value || '')
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[^a-z0-9]+/g, ' ')
    .split(/\s+/)
    .filter((token) => token.length >= 3 && !INDEX_STOP_WORDS.has(token))
    .map(stem))];
}

function deterministicScriptureSource(question) {
  const match = String(question || '').match(SCRIPTURE_ROUTE_PATTERN);
  if (!match) return null;
  const ordinal = String(match[1] || '').trim();
  const rawBook = String(match[2] || '').toLowerCase().replace(/[—-]/g, ' ').replace(/\s+/g, ' ').trim();
  const chapter = Number(match[3]);
  const startVerse = match[4] ? Number(match[4]) : 0;
  const endVerse = match[5] ? Number(match[5]) : startVerse;
  if (!Number.isInteger(chapter) || chapter < 1 || chapter > 150 || endVerse > 300) return null;
  let collection;
  let slug;
  if (rawBook === 'doctrine and covenants' || rawBook === 'd&c') {
    collection = 'dc-testament'; slug = 'dc';
  } else if (rawBook === 'articles of faith') {
    collection = 'pgp'; slug = 'a-of-f';
  } else if (rawBook === 'joseph smith matthew') {
    collection = 'pgp'; slug = 'js-m';
  } else if (rawBook === 'joseph smith history') {
    collection = 'pgp'; slug = 'js-h';
  } else {
    const route = SCRIPTURE_ROUTES[rawBook];
    if (!route) return null;
    [collection, slug] = route;
    if (ordinal) {
      const number = ordinal.replace(/\s+/g, '');
      if (!SCRIPTURE_MAX_ORDINAL[slug] || Number(number) > SCRIPTURE_MAX_ORDINAL[slug]) return null;
      if (slug === 'john') slug = `${number}-jn`;
      else if (['sam','kgs','chr','cor','thes','tim','pet','ne'].includes(slug)) slug = `${number}-${slug}`;
      else return null;
    } else if (slug === 'ne') {
      return null;
    }
  }
  const chapterLimit = SCRIPTURE_CHAPTER_LIMITS[`${collection}/${slug}`];
  if (!chapterLimit || chapter > chapterLimit) return null;
  const verseQuery = startVerse ? `?id=p${startVerse}${endVerse > startVerse ? `-p${endVerse}` : ''}&lang=eng` : '?lang=eng';
  const url = `https://www.churchofjesuschrist.org/study/scriptures/${collection}/${slug}/${chapter}${verseQuery}`;
  return {
    url,
    title: `${ordinal}${ordinal ? ' ' : ''}${match[2]} ${chapter}${startVerse ? `:${startVerse}${endVerse > startVerse ? `-${endVerse}` : ''}` : ''}`,
    kind: 'canonical-scripture',
    priority: 250,
    tokens: normalizeDiscoveryTokens(`${match[2]} ${chapter} ${question}`).join(' '),
    deterministic: true,
  };
}

function rankChurchSourceCandidates(question, page) {
  const queryTokens = normalizeDiscoveryTokens(question);
  if (!queryTokens.length) return [];
  const scripture = deterministicScriptureSource(question);
  const pioneerIrrigation = page === 'pioneers'
    && /\b(?:irrigat\w*|shared\s+water|water\s+(?:management|distribution|systems?))\b/i.test(String(question || ''));
  const ranked = CHURCH_SOURCE_INDEX.map((entry) => {
    const sourceTokens = new Set(normalizeDiscoveryTokens(entry.tokens));
    const overlaps = queryTokens.filter((token) => sourceTokens.has(token));
    const titleTokens = normalizeDiscoveryTokens(entry.title);
    const titleMatch = titleTokens.length > 0 && titleTokens.every((token) => queryTokens.includes(token));
    let score = overlaps.length * 18 + Number(entry.priority || 0) / 20 + (titleMatch ? 40 : 0);
    // Prefer a focused, one-concept Gospel Topic when its complete title is
    // explicitly present in the question. This prevents broad framing topics
    // such as "Jesus Christ" from outranking the visitor's named subject, as
    // in "the grace of Jesus Christ", while preserving ordinary multi-topic
    // ranking and deterministic scripture routing.
    const focusedTopicMatch = entry.kind === 'gospel-topic'
      && titleTokens.length === 1
      && queryTokens.includes(titleTokens[0]);
    if (focusedTopicMatch) score += 60;
    if (page === 'church-history' && /history/.test(entry.kind)) score += 8;
    if (page === 'pioneers' && /pioneer|history/.test(`${entry.tokens} ${entry.kind}`)) score += 8;
    const topicPinned = pioneerIrrigation && /\/history\/topics\/pioneer-settlements/.test(entry.url);
    if (topicPinned) score += 500;
    return { ...entry, score, overlapCount: overlaps.length, titleMatch, focusedTopicMatch, topicPinned };
  }).filter((entry) => entry.topicPinned
    || entry.overlapCount >= 2
    || (entry.overlapCount >= 1 && (queryTokens.length === 1 || entry.titleMatch)));
  if (scripture) ranked.push({ ...scripture, score: 1000, overlapCount: queryTokens.length });
  return ranked.sort((left, right) => right.score - left.score || String(left.url).localeCompare(String(right.url))).slice(0, 6);
}

function isAllowedOfficialFetchUrl(rawUrl, deterministic = false) {
  try {
    const url = new URL(String(rawUrl || ''));
    if (url.protocol !== 'https:' || url.hostname !== 'www.churchofjesuschrist.org') return false;
    if (/\/(?:search|scriptures\/search)(?:\/|$)/i.test(url.pathname) || /internal-use-only/i.test(url.pathname)) return false;
    if (![...url.searchParams.keys()].every((key) => key === 'lang' || key === 'id')) return false;
    if (url.searchParams.get('lang') && url.searchParams.get('lang') !== 'eng') return false;
    return deterministic ? /^\/study\/scriptures\/(?:ot|nt|bofm|dc-testament|pgp)\//.test(url.pathname) : OFFICIAL_INDEX_URLS.has(url.href);
  } catch (_error) {
    return false;
  }
}

function decodeHtmlEntities(value) {
  return String(value || '')
    .replace(/&#(\d+);/g, (_match, code) => String.fromCodePoint(Math.min(0x10ffff, Number(code))))
    .replace(/&#x([0-9a-f]+);/gi, (_match, code) => String.fromCodePoint(Math.min(0x10ffff, Number.parseInt(code, 16))))
    .replace(/&nbsp;/gi, ' ').replace(/&amp;/gi, '&').replace(/&quot;/gi, '"')
    .replace(/&apos;|&#39;/gi, "'").replace(/&lt;/gi, '<').replace(/&gt;/gi, '>');
}

function extractVisibleParagraphs(htmlText) {
  const clean = String(htmlText || '')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<(script|style|nav|header|footer|svg|form|noscript|template|iframe)\b[\s\S]*?(?:<\/\1>|$)/gi, ' ')
    .replace(/<([a-z][a-z0-9-]*)\b[^>]*(?:\bhidden\b|\binert\b|aria-hidden\s*=\s*["']?true|style\s*=\s*(?:"[^"]*(?:display\s*:\s*none|visibility\s*:\s*hidden)[^"]*"|'[^']*(?:display\s*:\s*none|visibility\s*:\s*hidden)[^']*'|[^\s>]*(?:display\s*:\s*none|visibility\s*:\s*hidden)[^\s>]*))[^>]*>[\s\S]*?(?:<\/\1>|$)/gi, ' ');
  const paragraphs = [];
  const seen = new Set();
  let retainedCharacters = 0;
  const consider = (part) => {
    const text = decodeHtmlEntities(String(part || '').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
    if (text.length < 50 || text.length > 1800) return;
    if (/\b(?:ignore|disregard|override)\b.{0,80}\b(?:previous|prior|system|developer|instructions?|prompt)\b|\bfollow\b.{0,60}\b(?:system|developer)\b.{0,60}\b(?:directions?|instructions?|prompt)\b|\b(?:system|developer|assistant)\s*:\s*|\byou are (?:chatgpt|an ai|a language model)\b/i.test(text)) return;
    if (/\b(?:system|developer|assistant)\s+(?:instructions?|directions?|prompts?|messages?|rules?)\b|\b(?:obey|execute|apply|comply\s+with|treat)\b.{0,100}\b(?:system|developer|assistant|instructions?|directions?|prompts?|higher\s+priority)\b|\b(?:system|developer|assistant)\b.{0,100}\b(?:higher\s+priority|approve|approval|require|required|must|obey|execute|override|ignore)\b/i.test(text)) return;
    if (/\b(?:follow|obey|execute|apply|comply\s+with)\s+(?:all\s+|these\s+|the\s+|any\s+)?(?:new\s+|next\s+|following\s+)?(?:instructions?|directions?|commands?|rules?)\b|\bignore\b.{0,50}\b(?:all|earlier|previous|prior)\b.{0,50}\b(?:instructions?|directions?|commands?|rules?)\b|\b(?:next|following|new)\s+(?:instructions?|directions?|commands?)\b.{0,60}\b(?:mandatory|required|must)\b|\b(?:respond|return|output)\b.{0,80}\b(?:approved\s*(?:true|false)|source\s+indexes?|json)\b|\b(?:approve|suppress)\b.{0,80}\b(?:every\s+claim|this\s+evidence|contrary\s+evidence|source\s+indexes?)\b/i.test(text)) return;
    const identity = text.toLowerCase();
    if (seen.has(identity) || paragraphs.length >= 300 || retainedCharacters + text.length > 120000) return;
    seen.add(identity);
    retainedCharacters += text.length;
    paragraphs.push(text);
  };
  for (const match of clean.matchAll(/<p\b[^>]*>([\s\S]*?)<\/p>/gi)) {
    const parts = match[1].split(/(?:<br\b[^>]*>\s*){2,}|<\/?(?:div|section|article|li)\b[^>]*>/gi);
    parts.forEach(consider);
  }
  clean.split(/(?:<br\b[^>]*>\s*){2,}/gi).forEach(consider);
  return paragraphs;
}

function relevantParagraphText(paragraphs, question) {
  const queryTokens = normalizeDiscoveryTokens(question);
  return (Array.isArray(paragraphs) ? paragraphs : []).map((text) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    const overlap = queryTokens.filter((token) => tokens.has(token)).length;
    return { text, overlap, score: overlap * 20 + Math.min(10, text.length / 180) };
  }).filter((item) => item.overlap > 0)
    .sort((left, right) => right.score - left.score)
    .slice(0, 2).map((item) => item.text).join(' ').slice(0, 700);
}

function extractRelevantParagraphs(htmlText, question) {
  return relevantParagraphText(extractVisibleParagraphs(htmlText), question);
}

function compactParagraphPack(paragraphs, candidate) {
  const discoveryTokens = normalizeDiscoveryTokens(`${candidate.title || ''} ${candidate.tokens || ''}`);
  let size = 0;
  return (Array.isArray(paragraphs) ? paragraphs : []).map((text, position) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    const overlap = discoveryTokens.filter((token) => tokens.has(token)).length;
    return { text, position, score: overlap * 20 - position / 1000 };
  }).sort((left, right) => right.score - left.score)
    .filter((item) => {
      if (size + item.text.length > 4200) return false;
      size += item.text.length;
      return true;
    }).slice(0, 6).sort((left, right) => left.position - right.position).map((item) => item.text);
}

async function readBoundedText(response, maxBytes) {
  if (!response.body || typeof response.body.getReader !== 'function') {
    const text = await response.text();
    if (new TextEncoder().encode(text).length > maxBytes) throw new Error('official_html_too_large');
    return text;
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let size = 0;
  let text = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > maxBytes) {
      await reader.cancel();
      throw new Error('official_html_too_large');
    }
    text += decoder.decode(value, { stream: true });
  }
  return text + decoder.decode();
}

async function evidenceCacheKey(candidate, question) {
  if (!globalThis.crypto || !globalThis.crypto.subtle) return null;
  const normalized = candidate.url;
  const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(normalized));
  const hex = Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
  return new Request(`https://focuschrist-groq-proxy.caribousun.workers.dev/__official_excerpt_cache/${hex}`);
}

async function fetchOfficialSource(candidate, question, deadline, counters = null) {
  if (!isAllowedOfficialFetchUrl(candidate.url, candidate.deterministic === true)) return null;
  const available = remainingBudget(deadline);
  if (available < 300) return null;
  let cache = null;
  let cacheKey = null;
  try {
    cache = globalThis.caches && globalThis.caches.default;
    cacheKey = cache ? await evidenceCacheKey(candidate, question) : null;
    if (cache && cacheKey) {
      const cached = await cache.match(cacheKey);
      if (cached) {
        const payload = await cached.json();
        if (payload && Array.isArray(payload.paragraphs)) {
          const content = relevantParagraphText(payload.paragraphs, question);
          if (content) {
            if (counters) counters.cacheHits += 1;
            const source = canonicalSource(candidate.url, candidate.title, content);
            if (source) source.cacheStatus = 'hit';
            return source;
          }
        }
      }
    }
  } catch (_cacheError) {}
  if (counters) {
    counters.attempts += 1;
    counters.cacheMisses += 1;
  }
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timer = controller ? setTimeout(() => controller.abort(), Math.max(200, Math.min(OFFICIAL_FETCH_LIMIT_MS, available - 100))) : null;
  try {
    const response = await fetch(candidate.url, {
      redirect: 'manual',
      headers: { Accept: 'text/html', 'Accept-Language': 'en', 'User-Agent': 'focusChrist-official-source/1.0 (+https://focuschrist.com/about.html)' },
      signal: controller ? controller.signal : undefined,
    });
    if (!response.ok || response.status >= 300) return null;
    const contentType = String(response.headers.get('content-type') || '').toLowerCase();
    if (!contentType.includes('text/html')) return null;
    const paragraphs = extractVisibleParagraphs(await readBoundedText(response, OFFICIAL_HTML_BYTE_LIMIT));
    const content = relevantParagraphText(paragraphs, question);
    if (!content || normalizeDiscoveryTokens(content).filter((token) => normalizeDiscoveryTokens(question).includes(token)).length < 2) return null;
    if (cache && cacheKey) {
      try {
        await cache.put(cacheKey, new Response(JSON.stringify({ paragraphs: compactParagraphPack(paragraphs, candidate) }), {
          headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=3600' },
        }));
      } catch (_cacheError) {}
    }
    const source = canonicalSource(candidate.url, candidate.title, content);
    if (source) source.cacheStatus = 'miss';
    return source;
  } catch (_error) {
    return null;
  } finally {
    if (timer) clearTimeout(timer);
  }
}

async function retrieveIndexedChurchEvidence(question, page, deadline) {
  const candidates = rankChurchSourceCandidates(question, page);
  const counters = { attempts: 0, cacheHits: 0, cacheMisses: 0 };
  const fetched = await Promise.all(candidates.slice(0, 2).map((candidate) => fetchOfficialSource(candidate, question, deadline, counters)));
  const evidence = fetched.filter(Boolean).slice(0, 2);
  return { candidates, evidence, fetchCalls: counters.attempts, cacheHits: counters.cacheHits, cacheMisses: counters.cacheMisses };
}

function hasExcessiveSourceOverlap(answer, evidence, limit = 25) {
  const answerTokens = String(answer || '').toLowerCase().match(/[a-z0-9']+/g) || [];
  if (answerTokens.length <= limit) return false;
  return (Array.isArray(evidence) ? evidence : []).some((source) => {
    const sourceTokens = String(source.content || '').toLowerCase().match(/[a-z0-9']+/g) || [];
    const sourceText = ` ${sourceTokens.join(' ')} `;
    for (let index = 0; index + limit < answerTokens.length; index += 1) {
      if (sourceText.includes(` ${answerTokens.slice(index, index + limit + 1).join(' ')} `)) return true;
    }
    let reconstructedWords = 0;
    let sourceFloor = 0;
    for (let answerIndex = 0; answerIndex < answerTokens.length;) {
      let longest = 0;
      let longestSourceIndex = -1;
      for (let sourceIndex = sourceFloor; sourceIndex < sourceTokens.length; sourceIndex += 1) {
        let length = 0;
        while (answerTokens[answerIndex + length]
          && sourceTokens[sourceIndex + length] === answerTokens[answerIndex + length]) length += 1;
        if (length > longest) {
          longest = length;
          longestSourceIndex = sourceIndex;
        }
      }
      if (longest >= 2) {
        reconstructedWords += longest;
        answerIndex += longest;
        sourceFloor = longestSourceIndex + longest;
      } else {
        answerIndex += 1;
      }
    }
    return reconstructedWords > limit && reconstructedWords / answerTokens.length >= 0.4;
  });
}

function evidenceRelevanceReceipt(question, evidence) {
  const queryTokens = normalizeDiscoveryTokens(question);
  return (Array.isArray(evidence) ? evidence : []).map((source) => {
    const sourceTokens = new Set(normalizeDiscoveryTokens(source.content));
    const terms = queryTokens.filter((token) => sourceTokens.has(token)).slice(0, 6);
    return { url: source.url, overlap_count: terms.length, terms };
  });
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
  if (hasExcessiveSourceOverlap(text, evidence)) return SOURCE_INTEGRITY_FALLBACK;
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
  return GENERAL_RESEARCH_REQUIRED_PATTERN.test(String(question || ''))
    || /\b(?:who\s+(?:is|was)|tell\s+me\s+about)\s+[\p{L}'’.-]+(?:\s+[\p{L}'’.-]+){0,3}\b/iu.test(String(question || ''));
}

function prefersResearchFirstGeneral(question) {
  return requiresExternalGeneralResearch(question)
    || /\b(?:when|what\s+(?:date|year))\b/i.test(String(question || ''));
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
  if (!apiKey) return { ...providerFailure(503, 'service_unavailable'), callCount: 0 };
  const available = remainingBudget(deadline);
  if (available < 250) return { ...providerFailure(504, 'timeout'), callCount: 0 };
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
    return {
      ...providerFailure(error && error.name === 'AbortError' ? 504 : 503,
        error && error.name === 'AbortError' ? 'timeout' : 'service_unavailable'),
      callCount: 1,
    };
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
    const retried = await callGroq(apiKey, body, deadline, false);
    return { ...retried, callCount: 1 + Number(retried.callCount || 0) };
  }
  return { response, data, callCount: 1 };
}

function verifierContent(result) {
  return result && result.data && result.data.choices && result.data.choices[0]
    ? String(result.data.choices[0].message && result.data.choices[0].message.content || '')
    : '';
}

function isVerifierVerdictShape(value, requireSourceIndexes = false) {
  const validSourceIndexes = Array.isArray(value && value.source_indexes)
    && value.source_indexes.every((index) => Number.isInteger(index));
  return Boolean(value && typeof value === 'object' && !Array.isArray(value)
    && typeof value.approved === 'boolean'
    && typeof value.answer === 'string'
    && (requireSourceIndexes
      ? validSourceIndexes
      : (value.source_indexes === undefined || validSourceIndexes)));
}

function validateVerifierResult(result, requireSourceIndexes = false) {
  if (!result || !result.response || !result.response.ok) return result;
  const verdict = parseVerifierJson(verifierContent(result));
  if (isVerifierVerdictShape(verdict, requireSourceIndexes)) return result;
  return {
    ...result,
    ...providerFailure(502, 'invalid_verifier_response'),
    formatContract: true,
  };
}

function validateGroqVerifierResult(result, requireSourceIndexes = false) {
  return validateVerifierResult(result, requireSourceIndexes);
}

function cloudflareNeuronEstimate(usage, model) {
  const inputTokens = Number(usage && (usage.prompt_tokens || usage.input_tokens) || 0);
  const outputTokens = Number(usage && (usage.completion_tokens || usage.output_tokens) || 0);
  const rates = model === CLOUDFLARE_FALLBACK_MODEL
    ? { input: 4119, output: 34868 }
    : { input: 26668, output: 204805 };
  if (inputTokens <= 0 && outputTokens <= 0) return 0;
  return Math.ceil((inputTokens * rates.input + outputTokens * rates.output) / 1000000);
}

async function callCloudflareVerifier(ai, body, deadline, options = {}) {
  if (!ai || typeof ai.run !== 'function') return providerFailure(503, 'service_unavailable');
  const model = options.model || CLOUDFLARE_VERIFIER_MODEL;
  const reserveMs = Number.isFinite(options.reserveMs) ? Math.max(0, options.reserveMs) : VERIFIER_FALLBACK_RESERVE_MS;
  const limitMs = Number.isFinite(options.limitMs) ? Math.max(200, options.limitMs) : CLOUDFLARE_VERIFIER_LIMIT_MS;
  const enforceResponseFormat = options.enforceResponseFormat !== false;
  const available = remainingBudget(deadline);
  if (available < reserveMs + 250) return providerFailure(504, 'timeout');
  const timeoutMs = Math.max(200, Math.min(limitMs, available - reserveMs));
  let timer;
  try {
    const timeout = new Promise((resolve) => {
      timer = setTimeout(() => resolve({ focuschristTimeout: true }), timeoutMs);
    });
    const raw = await Promise.race([
      ai.run(model, {
        messages: body.messages,
        temperature: body.temperature,
        max_tokens: body.max_tokens,
        ...(enforceResponseFormat && body.response_format ? { response_format: body.response_format } : {}),
      }),
      timeout,
    ]);
    if (raw && raw.focuschristTimeout) return {
      ...providerFailure(504, 'timeout'),
      cloudflareCallCount: 1,
      cloudflareModel: model,
      cloudflareEstimatedNeurons: 0,
      cloudflareUnmeteredNeurons: CLOUDFLARE_UNMETERED_CALL_NEURONS,
    };
    let content = '';
    if (raw && raw.choices && raw.choices[0] && raw.choices[0].message) {
      content = String(raw.choices[0].message.content || '');
    } else if (raw && typeof raw.response === 'string') {
      content = raw.response;
    } else if (raw && isVerifierVerdictShape(raw.response)) {
      content = JSON.stringify(raw.response);
    }
    const estimatedNeurons = cloudflareNeuronEstimate(raw && raw.usage, model);
    if (!content.trim()) {
      return {
        ...providerFailure(502, 'service_unavailable'),
        formatContract: true,
        cloudflareCallCount: 1,
        cloudflareModel: model,
        cloudflareEstimatedNeurons: estimatedNeurons,
        cloudflareUnmeteredNeurons: estimatedNeurons > 0 ? 0 : CLOUDFLARE_UNMETERED_CALL_NEURONS,
      };
    }
    return {
      response: new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
      data: {
        choices: [{ message: { content } }],
        usage: raw && raw.usage && typeof raw.usage === 'object' ? raw.usage : {},
      },
      cloudflareCallCount: 1,
      cloudflareModel: model,
      cloudflareEstimatedNeurons: estimatedNeurons,
      cloudflareUnmeteredNeurons: estimatedNeurons > 0 ? 0 : CLOUDFLARE_UNMETERED_CALL_NEURONS,
    };
  } catch (error) {
    const status = Number(error && (error.status || error.statusCode)) || 503;
    const code = status === 429 ? 'rate_limit_exceeded'
      : (status === 504 ? 'timeout' : 'service_unavailable');
    return {
      ...providerFailure(status >= 400 && status <= 599 ? status : 503, code),
      cloudflareCallCount: 1,
      cloudflareModel: model,
      cloudflareEstimatedNeurons: 0,
      cloudflareUnmeteredNeurons: CLOUDFLARE_UNMETERED_CALL_NEURONS,
    };
  } finally {
    if (timer) clearTimeout(timer);
  }
}

function verifierRouteDiagnostic(result) {
  const usage = result && result.accumulatedUsage
    ? result.accumulatedUsage
    : (result && result.data && result.data.usage || {});
  const inputTokens = Number(usage.prompt_tokens || usage.input_tokens || 0);
  const outputTokens = Number(usage.completion_tokens || usage.output_tokens || 0);
  const diagnostic = {
    focuschrist_verifier_route: result && result.verifierRoute
      ? result.verifierRoute
      : 'cloudflare-primary',
  };
  const route = diagnostic.focuschrist_verifier_route;
  const inferredCloudflareCalls = route === 'cloudflare-primary' ? 1
    : (route === 'cloudflare-fast-fallback' ? 2
      : (route === 'groq-fallback' && !['binding-missing', 'deadline-direct'].includes(String(result && result.fallbackReason || '')) ? 1 : 0));
  const cloudflareCalls = Number(result && result.totalCloudflareVerifierCalls
    || result && result.cloudflareCallCount
    || inferredCloudflareCalls);
  const groqCalls = Number(result && result.totalGroqVerifierCalls
    || (route === 'groq-fallback' ? result && result.callCount || 0 : 0));
  diagnostic.focuschrist_cloudflare_verifier_calls = Math.max(0, cloudflareCalls);
  diagnostic.focuschrist_groq_verifier_calls = Math.max(0, groqCalls);
  diagnostic.focuschrist_verifier_primary_attempted = cloudflareCalls > 0;
  diagnostic.focuschrist_verifier_conservative_unmetered_neurons = Math.max(0, Number(
    result && (result.totalCloudflareUnmeteredNeurons
      || result.cloudflareUnmeteredNeurons) || 0,
  ));
  if (result && result.primaryDiagnostic) {
    diagnostic.focuschrist_verifier_primary_status = result.primaryDiagnostic.focuschrist_provider_status || 0;
    diagnostic.focuschrist_verifier_primary_code = result.primaryDiagnostic.focuschrist_provider_code || '';
  }
  if (result && result.fallbackReason) {
    diagnostic.focuschrist_verifier_fallback_reason = result.fallbackReason;
  }
  if (result && result.fallbackSkippedDeadline) {
    diagnostic.focuschrist_verifier_fallback_skipped_deadline = true;
  }
  if (result && Number.isFinite(result.verifierDurationMs)) {
    diagnostic.focuschrist_verifier_duration_ms = Math.max(0, Math.round(result.verifierDurationMs));
  }
  if (Number.isFinite(inputTokens) && inputTokens > 0) {
    diagnostic.focuschrist_verifier_input_tokens = Math.round(inputTokens);
  }
  if (Number.isFinite(outputTokens) && outputTokens > 0) {
    diagnostic.focuschrist_verifier_output_tokens = Math.round(outputTokens);
  }
  const measuredCloudflareNeurons = Number(result && (result.totalCloudflareEstimatedNeurons
    || result.cloudflareEstimatedNeurons) || 0);
  if (measuredCloudflareNeurons > 0) {
    diagnostic.focuschrist_verifier_estimated_neurons = Math.ceil(measuredCloudflareNeurons);
  } else if (diagnostic.focuschrist_verifier_route === 'cloudflare-primary' && (inputTokens > 0 || outputTokens > 0)) {
    diagnostic.focuschrist_verifier_estimated_neurons = Math.ceil((inputTokens * 26668 + outputTokens * 204805) / 1000000);
  }
  return diagnostic;
}

function combinedProviderUsage(...results) {
  return results.reduce((total, result) => {
    const usage = result && result.data && result.data.usage || {};
    total.prompt_tokens += Number(usage.prompt_tokens || usage.input_tokens || 0);
    total.completion_tokens += Number(usage.completion_tokens || usage.output_tokens || 0);
    return total;
  }, { prompt_tokens: 0, completion_tokens: 0 });
}

function accumulateVerifierCalls(target, ...results) {
  target.totalCloudflareVerifierCalls = results.reduce((sum, result) => {
    const diagnostic = verifierRouteDiagnostic(result);
    return sum + Number(diagnostic.focuschrist_cloudflare_verifier_calls || 0);
  }, 0);
  target.totalGroqVerifierCalls = results.reduce((sum, result) => {
    const diagnostic = verifierRouteDiagnostic(result);
    return sum + Number(diagnostic.focuschrist_groq_verifier_calls || 0);
  }, 0);
  target.totalCloudflareEstimatedNeurons = results.reduce((sum, result) => sum + Number(
    result && (result.totalCloudflareEstimatedNeurons
      || result.cloudflareEstimatedNeurons) || 0,
  ), 0);
  target.totalCloudflareUnmeteredNeurons = results.reduce((sum, result) => sum + Number(
    result && (result.totalCloudflareUnmeteredNeurons
      || result.cloudflareUnmeteredNeurons) || 0,
  ), 0);
  return target;
}

async function callVerifier(env, body, deadline, options = {}) {
  const started = Date.now();
  const requireSourceIndexes = options.requireSourceIndexes === true;
  const allowGroqFallback = options.allowGroqFallback !== false;
  const { response_format: _providerEnforcedFormat, ...plainJsonBody } = body;
  const groqFallbackBody = { ...plainJsonBody, model: VERIFIER_MODEL };
  if (!env || !env.AI || typeof env.AI.run !== 'function') {
    if (!allowGroqFallback) {
      return {
        ...providerFailure(503, 'service_unavailable'),
        verifierRoute: 'cloudflare-required-unavailable',
        fallbackReason: 'groq-disabled-indexed-lane',
        verifierDurationMs: Date.now() - started,
      };
    }
    const fallback = validateGroqVerifierResult(
      await callGroq(env && env.GROQ_KEY_NEW, groqFallbackBody, deadline, false),
      requireSourceIndexes,
    );
    return {
      ...fallback,
      verifierRoute: 'groq-fallback',
      fallbackReason: 'binding-missing',
      primaryDiagnostic: providerDiagnostic(providerFailure(503, 'service_unavailable')),
      verifierDurationMs: Date.now() - started,
    };
  }
  if (remainingBudget(deadline) < VERIFIER_FALLBACK_RESERVE_MS + 250) {
    if (!allowGroqFallback) {
      return {
        ...providerFailure(504, 'timeout'),
        verifierRoute: 'cloudflare-required-deadline',
        fallbackReason: 'operational-fallback-disabled',
        verifierDurationMs: Date.now() - started,
      };
    }
    const fallback = validateVerifierResult(
      await callCloudflareVerifier(env.AI, plainJsonBody, deadline, {
        model: CLOUDFLARE_FALLBACK_MODEL,
        reserveMs: 0,
        limitMs: remainingBudget(deadline),
        enforceResponseFormat: false,
      }),
      requireSourceIndexes,
    );
    return {
      ...fallback,
      verifierRoute: 'cloudflare-fast-fallback',
      fallbackReason: 'deadline-direct',
      totalCloudflareVerifierCalls: Number(fallback.cloudflareCallCount || 0),
      totalCloudflareEstimatedNeurons: Number(fallback.cloudflareEstimatedNeurons || 0),
      totalCloudflareUnmeteredNeurons: Number(fallback.cloudflareUnmeteredNeurons || 0),
      verifierDurationMs: Date.now() - started,
    };
  }
  const primary = await callCloudflareVerifier(env && env.AI, body, deadline);
  const primaryVerdict = primary.response.ok ? parseVerifierJson(verifierContent(primary)) : null;
  if (primary.response.ok && isVerifierVerdictShape(primaryVerdict, requireSourceIndexes)) {
    return {
      ...primary,
      verifierRoute: 'cloudflare-primary',
      verifierDurationMs: Date.now() - started,
    };
  }
  const primaryDiagnostic = providerDiagnostic(primary);
  if (remainingBudget(deadline) < 250) {
    return {
      ...primary,
      verifierRoute: 'cloudflare-primary',
      primaryDiagnostic,
      fallbackSkippedDeadline: true,
      verifierDurationMs: Date.now() - started,
    };
  }
  if (!allowGroqFallback) {
    return {
      ...primary,
      verifierRoute: 'cloudflare-primary',
      primaryDiagnostic,
      fallbackReason: 'operational-fallback-disabled',
      verifierDurationMs: Date.now() - started,
    };
  }
  const fallbackReason = primary.formatContract || primary.response.ok
    ? 'format-contract'
    : (primary.response.status === 429
      ? 'primary-rate-limited'
      : (primary.response.status === 504 ? 'primary-timeout' : 'primary-unavailable'));
  const fallback = validateVerifierResult(
    await callCloudflareVerifier(env.AI, plainJsonBody, deadline, {
      model: CLOUDFLARE_FALLBACK_MODEL,
      reserveMs: 0,
      limitMs: remainingBudget(deadline),
      enforceResponseFormat: false,
    }),
    requireSourceIndexes,
  );
  return {
    ...fallback,
    verifierRoute: 'cloudflare-fast-fallback',
    primaryDiagnostic,
    fallbackReason,
    accumulatedUsage: combinedProviderUsage(primary, fallback),
    totalCloudflareVerifierCalls: Number(primary.cloudflareCallCount || 0)
      + Number(fallback.cloudflareCallCount || 0),
    totalCloudflareEstimatedNeurons: Number(primary.cloudflareEstimatedNeurons || 0)
      + Number(fallback.cloudflareEstimatedNeurons || 0),
    totalCloudflareUnmeteredNeurons: Number(primary.cloudflareUnmeteredNeurons || 0)
      + Number(fallback.cloudflareUnmeteredNeurons || 0),
    verifierDurationMs: Date.now() - started,
  };
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

async function produceLowRiskGeneralAnswer(env, scope, draft, deadline) {
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
  const result = await callVerifier(env, {
    messages: [{ role: 'user', content: prompt }],
    temperature: 0,
    max_tokens: 500,
    response_format: { type: 'json_object' },
  }, deadline);
  Object.assign(diagnostic, verifierRouteDiagnostic(result));
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
    const expansionResult = await callVerifier(env, {
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
      max_tokens: 650,
      response_format: { type: 'json_object' },
    }, deadline);
    expansionResult.accumulatedUsage = combinedProviderUsage(result, expansionResult);
    accumulateVerifierCalls(expansionResult, result, expansionResult);
    Object.assign(diagnostic, verifierRouteDiagnostic(expansionResult));
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

function generalAnswerPayload(answer, mode, extra, scope) {
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
    focuschrist_resolved_profile: scope && scope.faith ? 'faith-study' : (scope && scope.profile || 'general-knowledge'),
    focuschrist_classification_mode: scope && scope.classificationMode || 'request-scope',
    focuschrist_answer_word_count: String(answer || '').split(/\s+/).filter(Boolean).length,
    ...(extra || {}),
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

    const declaredLength = Number(request.headers.get('Content-Length') || 0);
    if (Number.isFinite(declaredLength) && declaredLength > REQUEST_BODY_BYTE_LIMIT) {
      return jsonResponse({ error: 'Request body is too large.' }, 413, origin);
    }
    let payload;
    try {
      const rawBody = await request.text();
      if (new TextEncoder().encode(rawBody).length > REQUEST_BODY_BYTE_LIMIT) {
        return jsonResponse({ error: 'Request body is too large.' }, 413, origin);
      }
      payload = JSON.parse(rawBody);
    } catch (_error) {
      return jsonResponse({ error: 'Invalid JSON' }, 400, origin);
    }
    if (!Array.isArray(payload && payload.messages) || payload.messages.length > REQUEST_MESSAGE_LIMIT) {
      return jsonResponse({ error: `Use no more than ${REQUEST_MESSAGE_LIMIT} conversation messages.` }, 400, origin);
    }
    const sanitized = sanitizePayload(payload || {});
    if (!sanitized.scope.question) return jsonResponse({ error: 'A user message is required' }, 400, origin);
    if (sanitized.scope.question.length > 1200) {
      return jsonResponse({ error: 'Please shorten the question to 1,200 characters or fewer.' }, 400, origin);
    }
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
    if (env && env.ASK_RATE_LIMITER && typeof env.ASK_RATE_LIMITER.limit === 'function') {
      try {
        const actor = request.headers.get('CF-Connecting-IP') || 'unknown-client';
        const limited = await env.ASK_RATE_LIMITER.limit({ key: `public-ask:${actor}` });
        if (!limited || limited.success !== true) {
          return jsonResponse({
            id: 'focuschrist-rate-limit',
            choices: [{ index: 0, message: { role: 'assistant', content: 'The question service is receiving many requests. Please wait a minute and try again.' }, finish_reason: 'rate_limit' }],
            focuschrist_sources: [],
            focuschrist_source_integrity_verified: false,
            focuschrist_source_policy: SOURCE_POLICY_VERSION,
            focuschrist_gateway_mode: 'request-rate-limit',
            focuschrist_resolved_profile: 'local-boundary',
            focuschrist_classification_mode: 'server-rate-limit',
          }, 429, origin);
        }
      } catch (_error) {
        // Availability takes precedence if the optional abuse-control binding has a transient fault.
      }
    }
    if (!sanitized.scope.faith && needsIdentityClarification(sanitized.scope.question)) {
      return jsonResponse(generalAnswerPayload(
        'Which Joseph do you mean? Please include the last name or a little more context.',
        'general-identity-clarification',
        {
          focuschrist_verifier_route: 'local-clarification',
          focuschrist_retrieval_route: 'none',
          focuschrist_groq_research_calls: 0,
        },
        sanitized.scope,
      ), 200, origin);
    }
    if (isReviewedColorRegression(sanitized.scope.question)) {
      return jsonResponse(reviewedColorPayload(), 200, origin);
    }
    const deadline = Date.now() + REQUEST_BUDGET_MS;
    const requestDiagnostic = {
      focuschrist_retrieval_route: 'none',
      focuschrist_index_candidates: 0,
      focuschrist_index_sources: 0,
      focuschrist_official_fetch_calls: 0,
      focuschrist_official_cache_hits: 0,
      focuschrist_official_cache_misses: 0,
      focuschrist_groq_research_calls: 0,
      focuschrist_source_sitemap_revision: CHURCH_SOURCE_SITEMAP_REVISION,
      focuschrist_source_robots_hash: CHURCH_SOURCE_ROBOTS_SHA256.slice(0, 12),
    };
    try {
      if (!sanitized.scope.faith && !sanitized.scope.selectedPioneer
        && !prefersResearchFirstGeneral(sanitized.scope.question)) {
        const directGeneralAnswer = await produceLowRiskGeneralAnswer(env, sanitized.scope, '', deadline);
        if (directGeneralAnswer) {
          return jsonResponse(generalAnswerPayload(
            directGeneralAnswer,
            'general-ai-low-risk',
            { ...sanitized.scope.lowRiskDiagnostic, focuschrist_retrieval_route: 'none', focuschrist_groq_research_calls: 0 },
            sanitized.scope,
          ), 200, origin);
        }
      }

      const tellMyStoryEvidence = sanitized.scope.selectedPioneer
        ? await fetchTellMyStoryEvidence(sanitized.scope.selectedPioneerName, deadline)
        : null;
      let draft = tellMyStoryEvidence
        ? `Write a concise, accurate biographical summary of ${sanitized.scope.selectedPioneerName} from the supplied Tell My Story, Too entry.`
        : '';
      let evidence = tellMyStoryEvidence ? [tellMyStoryEvidence] : [];
      let allEvidence = [];
      let researchResult = null;
      const retrievalDiagnostic = requestDiagnostic;
      if (tellMyStoryEvidence) retrievalDiagnostic.focuschrist_retrieval_route = 'reviewed-pioneer-biography';

      if (sanitized.scope.faith && !sanitized.scope.selectedPioneer) {
        const indexed = await retrieveIndexedChurchEvidence(sanitized.scope.retrievalQuestion, sanitized.scope.page, deadline);
        retrievalDiagnostic.focuschrist_index_candidates = indexed.candidates.length;
        retrievalDiagnostic.focuschrist_index_sources = indexed.evidence.length;
        retrievalDiagnostic.focuschrist_official_fetch_calls = indexed.fetchCalls;
        retrievalDiagnostic.focuschrist_official_cache_hits = indexed.cacheHits;
        retrievalDiagnostic.focuschrist_official_cache_misses = indexed.cacheMisses;
        if (indexed.evidence.length) {
          evidence = indexed.evidence;
          allEvidence = indexed.evidence;
          draft = '';
          retrievalDiagnostic.focuschrist_retrieval_route = 'church-source-index';
        }
      }

      if (!evidence.length) {
        if (!env || !env.GROQ_KEY_NEW) {
          return jsonResponse(fallbackPayload('research-unavailable', {
            ...retrievalDiagnostic,
            ...(sanitized.scope.lowRiskDiagnostic || {}),
          }, sanitized.scope), 200, origin);
        }
        researchResult = await callGroq(env.GROQ_KEY_NEW, sanitized.research, deadline);
        retrievalDiagnostic.focuschrist_groq_research_calls = Number(researchResult.callCount || 0);
        retrievalDiagnostic.focuschrist_retrieval_route = 'groq-research';
        if (!researchResult.response.ok) {
          if (!sanitized.scope.faith && !sanitized.scope.selectedPioneer
            && !requiresExternalGeneralResearch(sanitized.scope.question)) {
            const fallbackGeneralAnswer = await produceLowRiskGeneralAnswer(env, sanitized.scope, '', deadline);
            if (fallbackGeneralAnswer) {
              return jsonResponse(generalAnswerPayload(
                fallbackGeneralAnswer,
                'general-ai-low-risk',
                { ...sanitized.scope.lowRiskDiagnostic, ...retrievalDiagnostic },
                sanitized.scope,
              ), 200, origin);
            }
          }
          const limited = researchResult.response.status === 429;
          return jsonResponse(fallbackPayload(
            limited ? 'research-rate-limited' : 'research-provider-error',
            { ...providerDiagnostic(researchResult), ...retrievalDiagnostic, ...(sanitized.scope.lowRiskDiagnostic || {}) },
            sanitized.scope,
          ), 200, origin);
        }
        const researchMessage = researchResult.data && researchResult.data.choices && researchResult.data.choices[0]
          ? researchResult.data.choices[0].message
          : null;
        draft = researchMessage ? String(researchMessage.content || '').trim().slice(0, 4000) : '';
        allEvidence = collectSourceEvidence(researchMessage);
        if (!sanitized.scope.faith && isOfficialChurchIdentityEvidence(sanitized.scope.question, allEvidence)) {
          sanitized.scope.faith = true;
          sanitized.scope.profile = 'faith-study';
          sanitized.scope.classificationMode = 'official-church-identity-evidence';
        }
        evidence = (sanitized.scope.faith ? allEvidence.filter(isOfficialChurchSource) : allEvidence).slice(0, 2);
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
      if (draft && !evidence.length && !sanitized.scope.faith && !sanitized.scope.selectedPioneer) {
        const generalAnswer = await produceLowRiskGeneralAnswer(env, sanitized.scope, draft, deadline);
        if (generalAnswer) {
          return jsonResponse(generalAnswerPayload(
            generalAnswer,
            'general-ai-consensus',
            { ...sanitized.scope.lowRiskDiagnostic, ...retrievalDiagnostic },
            sanitized.scope,
          ), 200, origin);
        }
      }
      if ((!draft && retrievalDiagnostic.focuschrist_retrieval_route !== 'church-source-index') || !evidence.length) {
        return jsonResponse(fallbackPayload(
          'research-insufficient-evidence',
          { ...(sanitized.scope.lowRiskDiagnostic || {}), ...retrievalDiagnostic },
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
        'Compose the final answer from the supplied source excerpts. If the DRAFT block is empty, write the answer directly from EVIDENCE and never reject merely because no candidate draft was supplied.',
        'If a draft is present, repair it into a direct, complete answer using the evidence. Every externally checkable claim, quotation, attribution, date, statistic, scripture citation, and statement of official teaching must be directly supported by the evidence. Remove unsupported detail and correct contradictions, but preserve useful supported explanation. Do not add facts from memory.',
        'For a simple general fact, give at least 45 words and two complete sentences. For a faith or Church-history question, give 90 to 220 words and at least three complete sentences. A nuanced question normally needs two to four short paragraphs. Put the direct answer first, then explain the context supported by the evidence. Never return a one-line fact fragment, a one- or two-word answer, or padded repetition.',
        'Use independently worded paraphrase. Do not copy a long passage or reconstruct the source in ordered fragments. Apart from unavoidable names and short doctrinal phrases, avoid matching source wording for more than eight consecutive words.',
        'For a Latter-day Saint question, reject any evidence outside ChurchofJesusChrist.org.',
        'Set approved true whenever the evidence contains material that can responsibly answer the question, including when DRAFT is empty. Set approved false only when the evidence is empty, unrelated, or cannot support a responsible answer. source_indexes must list the 1-based evidence sources that directly support the final answer.',
        'Schema: {"approved":boolean,"answer":string,"source_indexes":number[]}',
        '',
        `QUESTION:\n${sanitized.scope.question}`,
        '',
        `DRAFT:\n${draft}`,
        '',
        `EVIDENCE:\n${evidenceForVerifier(evidence)}`,
      ].join('\n');
      const verifierBody = {
        messages: [{ role: 'user', content: verifierPrompt }],
        temperature: 0,
        max_tokens: sanitized.scope.selectedPioneer ? 900 : 400,
        response_format: { type: 'json_object' },
      };
      let verifierResult = await callVerifier(env, verifierBody, deadline, {
        requireSourceIndexes: true,
      });
      if (!verifierResult.response.ok) {
        return jsonResponse(fallbackPayload('verification-provider-error', {
          ...providerDiagnostic(verifierResult),
          ...verifierRouteDiagnostic(verifierResult),
          ...retrievalDiagnostic,
        }, sanitized.scope), 200, origin);
      }
      const verifierContent = verifierResult.data && verifierResult.data.choices && verifierResult.data.choices[0]
        ? verifierResult.data.choices[0].message.content
        : '';
      let verdict = parseVerifierJson(verifierContent);
      let indexes = verdict && Array.isArray(verdict.source_indexes)
        ? verdict.source_indexes.filter((index) => Number.isInteger(index) && index >= 1 && index <= evidence.length)
        : [];
      const selectedEvidenceBeforeRepair = indexes.map((index) => evidence[index - 1]);
      const needsDepthRepair = Boolean(verdict && verdict.approved === true && indexes.length
        && !answerMeetsSubstanceContract(verdict.answer, sanitized.scope));
      const needsParaphraseRepair = Boolean(verdict && verdict.approved === true && indexes.length
        && hasExcessiveSourceOverlap(verdict.answer, selectedEvidenceBeforeRepair));
      const indexedEvidenceRelevance = evidenceRelevanceReceipt(sanitized.scope.retrievalQuestion, evidence);
      const needsRelevantEvidenceReconsideration = Boolean(verdict && verdict.approved === false
        && retrievalDiagnostic.focuschrist_retrieval_route === 'church-source-index'
        && indexedEvidenceRelevance.some((entry) => entry.overlap_count >= 2));
      if ((needsDepthRepair || needsParaphraseRepair || needsRelevantEvidenceReconsideration)
        && verifierResult.verifierRoute === 'cloudflare-primary'
        && remainingBudget(deadline) >= 4500) {
        const requirements = answerSubstanceRequirements(sanitized.scope);
        const expansionPrompt = [
          verifierPrompt,
          '',
          needsRelevantEvidenceReconsideration
            ? 'Your previous rejection may be a false negative because the indexed official evidence has direct lexical relevance. Re-evaluate it once without presuming either approval or rejection.'
            : needsDepthRepair
            ? 'Your previous approved answer did not meet the required answer depth.'
            : 'Your previous approved answer failed the final publication overlap check.',
          needsRelevantEvidenceReconsideration
            ? 'If the evidence can responsibly answer the question, write the supported answer and set approved true with its source indexes. If it still cannot, keep approved false.'
            : needsDepthRepair
            ? `Rewrite it using at least ${requirements.minimumWords} words, ${requirements.minimumSentences} complete sentences, and ${requirements.minimumParagraphs} paragraph(s).`
            : 'Keep the answer complete and concise.',
          needsParaphraseRepair
            ? 'Rewrite the answer in genuinely independent language. Do not copy a long passage or reconstruct the source in ordered fragments. Preserve supported facts, but change the sentence structure and wording throughout.'
            : 'Preserve the independently worded explanation.',
          'State the direct answer first. Add only useful explanatory context supported by the supplied evidence; do not pad, repeat, speculate, or add facts from memory.',
          `PREVIOUS ANSWER:\n${String(verdict.answer || '').trim()}`,
          'Return the complete JSON object again with approved, answer, and source_indexes.',
        ].join('\n');
        const expansionResult = await callVerifier(env, {
          ...verifierBody,
          messages: [{ role: 'user', content: expansionPrompt }],
          max_tokens: sanitized.scope.selectedPioneer ? 900 : 400,
        }, deadline, {
          requireSourceIndexes: true,
          allowGroqFallback: false,
        });
        const initialVerifierResult = verifierResult;
        expansionResult.accumulatedUsage = combinedProviderUsage(initialVerifierResult, expansionResult);
        accumulateVerifierCalls(expansionResult, initialVerifierResult, expansionResult);
        verifierResult = {
          ...initialVerifierResult,
          accumulatedUsage: expansionResult.accumulatedUsage,
          totalCloudflareVerifierCalls: expansionResult.totalCloudflareVerifierCalls,
          totalGroqVerifierCalls: expansionResult.totalGroqVerifierCalls,
          totalCloudflareEstimatedNeurons: expansionResult.totalCloudflareEstimatedNeurons,
          totalCloudflareUnmeteredNeurons: expansionResult.totalCloudflareUnmeteredNeurons,
        };
        if (expansionResult.response.ok) {
          const expansionContent = expansionResult.data && expansionResult.data.choices && expansionResult.data.choices[0]
            ? expansionResult.data.choices[0].message.content
            : '';
          const expansionVerdict = parseVerifierJson(expansionContent);
          if (expansionVerdict) {
            verdict = expansionVerdict;
            verifierResult = expansionResult;
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
          ...verifierRouteDiagnostic(verifierResult),
          ...retrievalDiagnostic,
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
        focuschrist_evidence_relevance: evidenceRelevanceReceipt(sanitized.scope.retrievalQuestion, selectedEvidence),
        ...verifierRouteDiagnostic(verifierResult),
        ...retrievalDiagnostic,
      }, 200, origin);
    } catch (_error) {
      return jsonResponse(fallbackPayload('research-exception', {
        ...requestDiagnostic,
        focuschrist_retrieval_route: 'exception',
      }, sanitized.scope), 200, origin);
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
  callCloudflareVerifier,
  callVerifier,
  classifyResearchScope,
  collectSourceEvidence,
  extractSelectedPioneerName,
  extractTellMyStoryEntry,
  evaluateQuestionSafety,
  extractRelevantParagraphs,
  fetchTellMyStoryEvidence,
  fetchOfficialSource,
  guardVerifiedAnswer,
  hasKnownFalseClaim,
  hasExcessiveSourceOverlap,
  isReviewedColorRegression,
  isOfficialChurchSource,
  isOfficialChurchIdentityEvidence,
  isJsonValidationFailure,
  isVerifierVerdictShape,
  isTellMyStorySource,
  needsIdentityClarification,
  parseVerifierJson,
  providerDiagnostic,
  rankChurchSourceCandidates,
  deterministicScriptureSource,
  retrieveIndexedChurchEvidence,
  remainingBudget,
  requiresExternalGeneralResearch,
  sanitizePayload,
};
