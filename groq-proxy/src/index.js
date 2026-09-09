import { augmentRequestedCorpusEvidence } from './corpus-evidence.js';
import { checkCorpusCoverage, requestedTeachingCorpora } from './corpus-coverage.js';
import { PIONEER_SOURCE_URLS, PIONEER_TOPIC_SOURCES, PIONEER_FOCAL_PHRASES, pioneerTopic } from './pioneer-topic-sources.js';
import { CHURCH_SOURCE_INDEX, CHURCH_SOURCE_ROBOTS_SHA256, CHURCH_SOURCE_SITEMAP_REVISION } from './church-source-index.js';
import createScriptureLibrary from '../../scripture-library.js';
import scriptureCatalog from '../../scripture-data/catalog.json' with { type: 'json' };

// focusChrist server-owned, retrieval-grounded AI gateway.
// Reviewed local answers remain the first choice. This Worker retrieves
// official evidence for faith questions and independently checks every
// unreviewed answer before returning it to the browser.

const RESEARCH_MODEL = 'gpt-5.6-sol';
const VERIFIER_MODEL = 'gpt-5.6-sol';
const OPENAI_VERIFIER_MODEL = 'gpt-5.6-sol';
const OPENAI_ENDPOINT = 'https://api.openai.com/v1/chat/completions';
const ALLOWED_ORIGINS = new Set([
  'https://focuschrist.com',
  'https://www.focuschrist.com',
  'https://caribousun.github.io',
]);
const OFFICIAL_CHURCH_HOST = 'churchofjesuschrist.org';
// Existing focusChrist study resources. Church sources remain primary for doctrine;
// university publications are attributed study material, not Church declarations.
const APPROVED_LDS_STUDY_HOSTS = new Set(['rsc.byu.edu', 'scriptures.byu.edu', 'speeches.byu.edu', 'eom.byu.edu', 'www.byui.edu']);
const APPROVED_LDS_RESEARCH_POLICY = 'Search only site:churchofjesuschrist.org or site:rsc.byu.edu or site:scriptures.byu.edu or site:speeches.byu.edu or site:eom.byu.edu or site:byui.edu. Prefer scripture and official Church publications. These are the approved LDS resources already used by focusChrist; do not use forums, social posts, general internet opinion, or an AI model as evidence. Attribute university scholarship and named talks accurately; never present them as official Church declarations. A source must support the current claim, not merely discuss the same topic.';
const TELL_MY_STORY_URL = 'https://focuschrist.com/tell-my-story-too.txt';
const SOURCE_INTEGRITY_FALLBACK = "focusChrist is here to help you learn of Jesus Christ and draw closer to Him. I couldn’t find a supported answer to this question in our study library or approved LDS sources. You’re welcome to ask about Jesus Christ, scripture, faith, or Church history.";
const SOURCE_UNAVAILABLE_MESSAGE = "I’m unable to check our approved study sources right now. Please try again in a moment.";
const GENERAL_ANSWER_FALLBACK = 'Your question is valid, but the answer service is temporarily unavailable. Please try again in a moment.';
const RESPECTFUL_QUESTION_RESPONSE = 'focusChrist is an independent site centered on Jesus Christ and respectful study of Latter-day Saint beliefs. Please rephrase your question without profanity, sexual content, or disrespect toward any religion, culture, or political affiliation.';
const URGENT_SAFETY_RESPONSE = 'If you or someone else may be in immediate danger or experiencing abuse, contact local emergency services or a trusted qualified person who can help now. focusChrist cannot provide emergency or professional intervention.';
const SOURCE_POLICY_VERSION = '2026-09-09.76';
const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-09.76';
const REQUEST_BUDGET_MS = 60000;
const PROVIDER_CALL_LIMIT_MS = 10500;
const MIN_RETRY_BUDGET_MS = 3500;
const OFFICIAL_FETCH_LIMIT_MS = 9000;
const OFFICIAL_HTML_BYTE_LIMIT = 1500000;
const REQUEST_BODY_BYTE_LIMIT = 65536;
const REQUEST_MESSAGE_LIMIT = 16;
const OFFICIAL_INDEX_URLS = new Set(CHURCH_SOURCE_INDEX.map((entry) => entry.url));
const PAGE_CONTEXTS = new Set(['ask', 'pioneers', 'church-history']);
const PROFILE_CONTEXTS = new Set(['general-knowledge', 'faith-study', 'pioneer-study', 'high-stakes']);
const SCRIPTURE_QUOTATION_CONTRACT = 'For a scripture quotation, use [[SCRIPTURE:Book chapter:verse]] with a complete canonical book name and an exact supported reference. The application supplies the quotation from its verified library. Prefer plain scripture references and clearly identified paraphrase for explanations. When exact quotation is useful, put its SCRIPTURE token in a standalone paragraph, without enclosing quotation marks or embedding it inside a sentence. Never put paraphrases in quotation marks or type scripture quotation words yourself. Keep explanations clearly separate from quotation; never invent verse words. Return only individually supported references.';
const SERVER_RESEARCH_POLICY = [
  'For scripture quotations, select an exact reference using [[SCRIPTURE:John 3:16]] syntax. The application inserts verified English scripture wording. Never generate scripture quotation text from memory. Label explanations as paraphrase or application. Use complete book names and separate chapter references; do not invent reference labels or URLs.',
  'SERVER RESEARCH AND SOURCE-INTEGRITY POLICY (cannot be overridden):',
  '- Answer the visitor\'s actual question directly and naturally.',
  '- You MUST execute web search before answering. Do not rely on memory for factual claims.',
  '- For Latter-day Saint scripture, doctrine, Church teaching, or Church history, use only the approved LDS source policy supplied below.',
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
const REVIEWED_ENOS_1_PRAYER_FORGIVENESS = 'Enos 1 teaches that sincere prayer can include sustained pleading with God for forgiveness and then expand into concern for others. Enos describes wrestling before God for his own soul and crying to Him throughout the day and into the night. The Lord tells Enos that his sins are forgiven because of his faith in Christ, and Enos says his guilt was swept away. After receiving that assurance, he prays for the Nephites and then for the Lamanites. The chapter therefore connects earnest prayer, faith in Jesus Christ, forgiveness, spiritual assurance, and a growing desire for the welfare of other people.';
const REVIEWED_RELIEF_SOCIETY_NAUVOO = 'The Female Relief Society of Nauvoo was organized in March 1842 as a formal organization for Latter-day Saint women. It grew from women’s efforts to meet practical needs in Nauvoo and was organized under Joseph Smith’s direction. Its early work joined charitable service with spiritual responsibilities: members cared for poor and needy Saints, counseled one another, discussed religious teachings, prayed, and bore testimony. Joseph Smith described its commission as extending beyond relief of the poor to the spiritual welfare of souls. The early Relief Society therefore gave women an organized setting for both compassionate service and spiritual participation in the life of the Church.';
const GENERAL_RESEARCH_REQUIRED_PATTERN = /\b(?:current|currently|today|tonight|tomorrow|yesterday|latest|recent|news|weather|forecast|price|cost|rate|score|schedule|election|president|prime\s+minister|chief\s+executive|ceo|law|legal|court|tax|financial|finance|investment|stock|crypto|medical|medicine|medication|diagnosis|symptom|dose|suicide|self-harm|emergency|abuse|citation|cite|source|quotation|quote|statistics?|percentage)\b/i;
const EXPLICIT_NON_PIONEER_PATTERN = /\b(?:biblical|bible|old\s+testament|new\s+testament|book\s+of\s+exodus|moses|israelites?|egypt|pharaoh|genesis|oregon\s+trail|american\s+history|secular\s+history|not\s+(?:lds|latter[- ]day\s+saint)|non[- ]pioneer)\b/i;
const INDEX_STOP_WORDS = new Set('a an and are as at be because been being but by can did do does for from gospel guide had has have how i in into is it its latter manual me of on or our saint saints should study tell that the their them there these they this to topics us was were what when where which who why will with would you your says said teach teaches taught meaning means mean'.split(' '));
const SCRIPTURE_ROUTES = Object.freeze({
  genesis:['ot','gen'],exodus:['ot','ex'],leviticus:['ot','lev'],numbers:['ot','num'],deuteronomy:['ot','deut'],joshua:['ot','josh'],judges:['ot','judg'],ruth:['ot','ruth'],samuel:['ot','sam'],kings:['ot','kgs'],chronicles:['ot','chr'],ezra:['ot','ezra'],nehemiah:['ot','neh'],esther:['ot','esth'],job:['ot','job'],psalm:['ot','ps'],psalms:['ot','ps'],proverbs:['ot','prov'],ecclesiastes:['ot','eccl'],isaiah:['ot','isa'],jeremiah:['ot','jer'],lamentations:['ot','lam'],ezekiel:['ot','ezek'],daniel:['ot','dan'],hosea:['ot','hosea'],joel:['ot','joel'],amos:['ot','amos'],obadiah:['ot','obad'],jonah:['ot','jonah'],micah:['ot','micah'],nahum:['ot','nahum'],habakkuk:['ot','hab'],zephaniah:['ot','zeph'],haggai:['ot','hag'],zechariah:['ot','zech'],malachi:['ot','mal'],
  matthew:['nt','matt'],mark:['nt','mark'],luke:['nt','luke'],john:['nt','john'],acts:['nt','acts'],romans:['nt','rom'],corinthians:['nt','cor'],galatians:['nt','gal'],ephesians:['nt','eph'],philippians:['nt','philip'],colossians:['nt','col'],thessalonians:['nt','thes'],timothy:['nt','tim'],titus:['nt','titus'],philemon:['nt','philem'],hebrews:['nt','heb'],james:['nt','james'],peter:['nt','pet'],jude:['nt','jude'],revelation:['nt','rev'],
  'song of solomon':['ot','song'],nephi:['bofm','ne'],jacob:['bofm','jacob'],enos:['bofm','enos'],jarom:['bofm','jarom'],omni:['bofm','omni'],'words of mormon':['bofm','w-of-m'],mosiah:['bofm','mosiah'],alma:['bofm','alma'],helaman:['bofm','hel'],mormon:['bofm','morm'],ether:['bofm','ether'],moroni:['bofm','moro'],moses:['pgp','moses'],abraham:['pgp','abr'],
});
const SCRIPTURE_CHAPTER_LIMITS = Object.freeze(Object.fromEntries(scriptureCatalog.books.map(book => [book.key, book.chapters])));
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

function scriptureFetch(path, deadline) {
  const remaining = deadline - Date.now();
  if (remaining <= 0) return Promise.reject(new Error('scripture-verification-timeout'));
  return fetch('https://focuschrist.com' + path, { signal: AbortSignal.timeout(Math.min(8000, remaining)) });
}

async function jsonResponse(body, status, origin, deadline = Date.now() + 8000, checkedLibrary = null) {
  // Final, unconditional output gate: no approval flag or reviewed lane bypasses it.
  if (body.choices?.[0]?.message?.content) {
    const library = checkedLibrary || createScriptureLibrary(scriptureCatalog, path => scriptureFetch(path, deadline));
    const checked = await library.checkAnswer(body.choices[0].message.content, body.focuschrist_sources || []);
    body.choices[0].message.content = checked.answer;
    body.focuschrist_scripture_library_version = checked.version;
    body.focuschrist_scripture_validated = checked.ok;
    if (!checked.ok) {
      body.focuschrist_source_integrity_verified = false;
      body.focuschrist_sources = [];
      body.focuschrist_scripture_failure = checked.reason;
      body.choices[0].finish_reason = 'content_filter';
    }
  }
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

function scriptureSupportContext(messages) {
  const users = (Array.isArray(messages) ? messages : []).filter(message => message?.role === 'user');
  const current = String(users.at(-1)?.content || '').split('\n')[0].toLowerCase().replace(/[?.!]+$/g, '').trim();
  const requested = /^(?:(?:can|could|would) you |please )?(?:cite|site|quote|give(?: me)?|show(?: me)?|provide)(?: me)? (?:a |an |the |some )?(?:supporting )?(?:scripture|scriptures|verse|verses|scripture reference|scripture references)(?: (?:(?:for|to support|supporting) (?:that|this)|that (?:supports|explains) (?:that|this)))?$/.test(current);
  return { requested, antecedent: requested ? String(users.at(-2)?.content || '').split('\n')[0].trim().slice(0, 1200) : '' };
}

function isGodInOldTestamentQuestion(value) {
  const text = String(value || '').toLowerCase().replace(/[^a-z ]/g, ' ').replace(/\s+/g, ' ').trim();
  const vocabulary = new Set('is god in the bible old testament mentioned named does appear where can i find'.split(' '));
  return /\bgod\b/.test(text) && /\bold testament\b/.test(text)
    && text.split(' ').every(token => vocabulary.has(token));
}

function rawConversationQuestion(value) {
  // Remove only the legacy browser context wrapper, never use its claimed
  // antecedent as authority. Reconstruct context from actual user turns.
  return String(value || '').split(/\n\nThe immediately preceding user question was:/)[0].trim();
}

function isReferentialQuestion(value) {
  const text = rawConversationQuestion(value).toLowerCase().replace(/[?.!]+$/g, '').trim();
  if (scriptureSupportContext([{ role: 'user', content: text }]).requested) return true;
  // A possessive inside a question about an explicitly named subject does not
  // refer back to the conversation (for example, Lincoln and his childhood).
  const subject = text.match(/^(?:(?:what|when|where|why|how)\s+)?(?:did|does|do|was|is|were|are|can|could|will|would)\s+([a-z]+)/)?.[1];
  if (subject && !['i','you','we','us','our','your','he','him','his','she','her','they','them','their','it','its','that','this'].includes(subject)
      && !/\b(?:he|him|she|they|them|it|that|this|there|then)\b/.test(text)) return false;
  return scriptureSupportContext([{ role: 'user', content: text }]).requested
    || /\b(?:he|him|his|she|her|hers|they|them|their|it|its|that|this|there|then)\b/.test(text)
    || /^(?:tell me more|go on|continue|why|how so|what else|and why|and when|and how)$/.test(text);
}

function userConversationContext(messages) {
  const users = (Array.isArray(messages) ? messages : []).filter(message => message?.role === 'user');
  if (!isReferentialQuestion(users.at(-1)?.content)) return [];
  const context = [];
  for (let index = users.length - 2; index >= 0 && context.length < 3; index -= 1) {
    const question = rawConversationQuestion(users[index].content).slice(0, 1200);
    if (!question) continue;
    context.unshift(question);
    if (!isReferentialQuestion(question)) break;
  }
  return context;
}

function conversationInstruction(scope) {
  if (!scope.conversationContext?.length) return '';
  return [
    'CURRENT QUESTION is the request to answer. Earlier user questions identify the conversational subject only; they are not evidence. Earlier assistant statements are not evidence either.',
    'Resolve pronouns and omitted subjects from the most recent user subject. Address the new attribute or comparison, not the earlier question again. If scope remains ambiguous, explain the source-supported distinctions or ask a specific clarification; do not invent a single date or identity.',
    `CURRENT QUESTION: ${scope.question}`,
    `EARLIER USER QUESTIONS (oldest to newest): ${JSON.stringify(scope.conversationContext)}`,
  ].join('\n');
}

function classifyResearchScope(messages, requestedPage, requestedProfile) {
  const support = scriptureSupportContext(messages);
  const question = rawConversationQuestion(lastUserQuestion(messages));
  const conversationContext = userConversationContext(messages);
  if (support.antecedent && !conversationContext.length) conversationContext.push(support.antecedent);
  const normalizedQuestion = question.toLowerCase().replace(/[^a-z0-9\s'-]/g, ' ').replace(/\s+/g, ' ').trim();
  const scriptureTopicQuestion = question
    .replace(CASELESS_CANON_NAME_PERSON_QUESTION_PATTERN, '$1')
    .replace(CASELESS_CANON_NAME_PERSON_ACTION_PATTERN, '$1')
    .replace(CASELESS_CANON_NAME_PERSON_ABOUT_PATTERN, '$1');
  const page = PAGE_CONTEXTS.has(requestedPage) ? requestedPage : 'ask';
  const profile = PROFILE_CONTEXTS.has(requestedProfile) ? requestedProfile : '';
  const contextualSubject = KNOWN_CHURCH_PERSON_PHRASES.find(name => conversationContext.join(' ').toLowerCase().includes(name)) || '';
  const usesConversationContext = conversationContext.length > 0;
  const retrievalQuestion = support.antecedent ? `${support.antecedent}: cite a supporting scripture`
    : usesConversationContext ? `${question}\nEarlier user topic: ${conversationContext.join(' -> ')}` : question;
  const faith = page === 'pioneers'
    || page === 'church-history'
    || profile === 'faith-study'
    || profile === 'pioneer-study'
    || KNOWN_CHURCH_PERSON_PHRASES.some((name) => normalizedQuestion.includes(name))
    || FAITH_PATTERN.test(scriptureTopicQuestion)
    || SCRIPTURE_REFERENCE_PATTERN.test(question)
    || SCRIPTURE_BOOK_TOPIC_PATTERN.test(scriptureTopicQuestion)
    || (usesConversationContext && (Boolean(contextualSubject) || FAITH_PATTERN.test(conversationContext.join(' ')) || SCRIPTURE_BOOK_TOPIC_PATTERN.test(conversationContext.join(' '))));
  const selectedPioneerName = extractSelectedPioneerName(messages);
  return {
    faith, question, retrievalQuestion, page, profile, conversationContext, approvedSourcesOnly: true,
    classificationMode: support.antecedent || usesConversationContext ? 'conversation-context' : 'request-scope',
    scriptureSupportRequested: support.requested, scriptureSupportAntecedent: support.antecedent,
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
  const disclosureTopic = pioneerTopic(payload.focuschrist_pioneer_topic, scope.page);
  if (disclosureTopic) {
    scope.pioneerTopicKey = payload.focuschrist_pioneer_topic;
    scope.selectedPioneer = false;
    scope.selectedPioneerName = '';
    scope.question = `Explain ${disclosureTopic.subject}. Give a useful historical account using the supplied sources and distinguish established facts from recollections.`;
    scope.retrievalQuestion = disclosureTopic.subject;
  }
  const conversationMessages = clientMessages
    .filter((message) => message.role === 'user' || message.role === 'assistant')
    .slice(-8)
    .map((message) => ({ role: message.role, content: message.content.slice(0, 3000) }));
  if (disclosureTopic) conversationMessages.splice(0, conversationMessages.length, { role: 'user', content: scope.question });
  let scopeInstruction;
  if (scope.selectedPioneer) {
    scopeInstruction = `The visitor selected the pioneer ${scope.selectedPioneerName}. Search only site:churchofjesuschrist.org to corroborate that exact person's identity, company, dates, and journey. The gateway will separately supply the selected Tell My Story, Too biography.`;
  } else if (scope.page === 'pioneers' && EXPLICIT_NON_PIONEER_PATTERN.test(scope.question)) {
    scopeInstruction = 'This request comes from the Pioneers page, but the visitor explicitly requested a biblical or non-pioneer subject. Answer that explicit subject directly.';
  } else if (scope.page === 'pioneers') {
    scopeInstruction = 'This request comes from the focusChrist Pioneers page. Interpret ambiguous labels in Latter-day Saint pioneer and Church-history context. In particular, an unqualified Exodus means the 1846 exodus from Nauvoo, not the biblical Exodus. Distinguish established fact from recollection, tradition, and interpretation.';
  } else if (scope.page === 'church-history') {
    scopeInstruction = 'This request comes from the focusChrist Church History page. Interpret ambiguous questions and follow-ups within Latter-day Saint Church history. Prefer the official Church History and Saints source family.';
  } else if (scope.faith) {
    scopeInstruction = 'For this request, prefer scripture and official Church publications.';
  } else {
    scopeInstruction = 'Use web search to gather reliable evidence before answering.';
  }
  if (!scope.selectedPioneer) scopeInstruction += '\n' + APPROVED_LDS_RESEARCH_POLICY;
  const research = {
    model: RESEARCH_MODEL,
    // Browser prompts are presentation hints, not server-owned source policy.
    // Keeping them out of the research request prevents an Ask-page keyword
    // from inheriting Pioneer scope and sharply reduces provider token use.
    messages: [{ role: 'system', content: SERVER_RESEARCH_POLICY + '\n' + scopeInstruction + '\n' + conversationInstruction(scope) }, ...conversationMessages],
    max_tokens: 700,
  };
  return { research, scope };
}

function canonicalSource(rawUrl, title, content, contentLimit = 700) {
  try {
    const url = new URL(String(rawUrl || ''));
    if (url.protocol !== 'https:') return null;
    return {
      url: url.href,
      host: url.hostname.toLowerCase(),
      title: String(title || url.hostname).replace(/\s+/g, ' ').trim().slice(0, 180),
      content: String(content || '').replace(/[^\S\r\n]+/g, ' ').replace(/\r\n?/g,'\n').replace(/\n{3,}/g,'\n\n').trim().slice(0, Math.min(4200, contentLimit)),
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

function isApprovedLdsSource(source) {
  try {
    const url = new URL(source?.url);
    return url.protocol === 'https:' && !url.username && !url.password && !url.port
      && (url.hostname === OFFICIAL_CHURCH_HOST || url.hostname.endsWith('.' + OFFICIAL_CHURCH_HOST)
        || APPROVED_LDS_STUDY_HOSTS.has(url.hostname));
  } catch (_) { return false; }
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

// Cache only trusted, query-independent source metadata. Visitor questions are
// never keys in this isolate-lifetime cache.
const sourceDiscoveryTokens = new Map();
const sourceDiscoverySets = new Map();
function cachedSourceTokens(value) {
  if (!sourceDiscoveryTokens.has(value)) sourceDiscoveryTokens.set(value, normalizeDiscoveryTokens(value));
  return sourceDiscoveryTokens.get(value);
}
function cachedSourceSet(value) {
  if (!sourceDiscoverySets.has(value)) sourceDiscoverySets.set(value, new Set(cachedSourceTokens(value)));
  return sourceDiscoverySets.get(value);
}
for (const entry of CHURCH_SOURCE_INDEX) {
  cachedSourceTokens(entry.title);
  cachedSourceSet(entry.tokens);
}

function deterministicHistoryTopicSource(question, page) {
  if (!['ask', 'church-history'].includes(page)) return null;
  const queryTokens = normalizeDiscoveryTokens(question);
  if (queryTokens.length < 2) return null;
  const matches = CHURCH_SOURCE_INDEX.map((entry) => {
    if (entry.kind !== 'history-topic') return null;
    const titleTokens = cachedSourceTokens(entry.title);
    if (titleTokens.length < 2 || !titleTokens.every((token) => queryTokens.includes(token))) return null;
    return {
      ...entry,
      deterministicHistoryTopic: true,
      titleTokenCount: titleTokens.length,
      score: 900 + titleTokens.length * 25 + Number(entry.priority || 0) / 20,
      overlapCount: queryTokens.filter((token) => cachedSourceSet(entry.tokens).has(token)).length,
    };
  }).filter(Boolean);
  return matches.sort((left, right) => right.titleTokenCount - left.titleTokenCount
    || right.score - left.score
    || String(left.url).localeCompare(String(right.url)))[0] || null;
}

function namedGospelTopicSource(question, page, ranked) {
  if (!['ask','pioneers','church-history'].includes(page) || /\b(?:compare|contrast|versus|vs|difference between|relationship between)\b/i.test(String(question || ''))) return null;
  const top = ranked[0];
  if (!top || top.kind !== 'gospel-topic' || !top.titleMatch
    || normalizeDiscoveryTokens(top.title).length < 1
    || ranked.slice(1).some((entry) => entry.titleMatch)) return null;
  return { ...top, namedGospelTopic: true };
}

function isPioneerIrrigationIntent(question, page) {
  return page === 'pioneers'
    && /\b(?:irrigat\w*|shared\s+water|water\s+(?:management|distribution|systems?))\b/i.test(String(question || ''));
}

function rankChurchSourceCandidates(question, page) {
  const queryTokens = normalizeDiscoveryTokens(question);
  if (!queryTokens.length) return [];
  const scripture = deterministicScriptureSource(question);
  const pioneerIrrigation = isPioneerIrrigationIntent(question, page);
  // Discovery vocabulary from the opening definition of the official Godhead
  // topic. These terms identify a source; they never approve or write an answer.
  const topicAliases = {
    'https://www.churchofjesuschrist.org/study/manual/gospel-topics/godhead?lang=eng': ['Father Son Holy Ghost'],
  };
  const entries = new Map(CHURCH_SOURCE_INDEX.map(entry => {
    const aliases = topicAliases[entry.url] || [];
    const aliasMatch = aliases.some(alias => normalizeDiscoveryTokens(alias).every(token => queryTokens.includes(token)));
    return [entry.url, aliases.length ? { ...entry, tokens: entry.tokens + ' ' + aliases.join(' '),
      sourceAliasMatch: aliasMatch, ...(aliasMatch ? { namedGospelTopic: true } : {}) } : entry];
  }));
  if (page === 'pioneers') {
    for (const [key,topic] of Object.entries(PIONEER_TOPIC_SOURCES)) {
      const existing = entries.get(topic.url) || {url:topic.url,title:topic.subject,kind:'history-topic',priority:95,tokens:''};
      const focal = (PIONEER_FOCAL_PHRASES[key] || []).filter(phrase=>phrase.split(/\s+/).length > 1
        && new RegExp('\\b'+phrase.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\b','i').test(question));
      entries.set(topic.url,{...existing,tokens:existing.tokens+' '+topic.subject+' '+(PIONEER_FOCAL_PHRASES[key] || []).join(' '),
        namedGospelTopic:true,...(focal.length ? {pioneerDisclosure:true,focalPhrases:[...(existing.focalPhrases || []),...focal]} : {})});
    }
  }
  const ranked = [...entries.values()].map((entry) => {
    const sourceTokens = cachedSourceSet(entry.tokens);
    const overlaps = queryTokens.filter((token) => sourceTokens.has(token));
    const titleTokens = cachedSourceTokens(entry.title);
    const titleMatch = titleTokens.length > 0 && titleTokens.every((token) => queryTokens.includes(token));
    let score = overlaps.length * 18 + Number(entry.priority || 0) / 20 + (titleMatch ? 40 : 0);
    if (entry.pioneerDisclosure && entry.focalPhrases?.length) score += 400;
    // Prefer a focused, one-concept Gospel Topic when its complete title is
    // explicitly present in the question. This prevents broad framing topics
    // such as "Jesus Christ" from outranking the visitor's named subject, as
    // in "the grace of Jesus Christ", while preserving ordinary multi-topic
    // ranking and deterministic scripture routing.
    const focusedTopicMatch = entry.kind === 'gospel-topic'
      && titleTokens.length === 1
      && queryTokens.includes(titleTokens[0]);
    if (focusedTopicMatch || entry.sourceAliasMatch) score += 60;
    // A substantial ordered title match can omit an interior name, while a
    // broad place or generic "biography" title must not displace that subject.
    const partialTitleTokens = titleTokens.filter(token => queryTokens.includes(token));
    const substantialTitleMatch = entry.kind === 'history-topic' && titleTokens.length >= 4
      && partialTitleTokens.length >= 3 && partialTitleTokens.length / titleTokens.length >= .75
      && queryTokens.includes(titleTokens[0]) && queryTokens.includes(titleTokens.at(-1))
      && partialTitleTokens.every((token,index) => index === 0 || queryTokens.indexOf(token) > queryTokens.indexOf(partialTitleTokens[index-1]));
    if (substantialTitleMatch) score += 60;
    if (page === 'church-history' && /history/.test(entry.kind)) score += 8;
    if (page === 'pioneers' && /pioneer|history/.test(`${entry.tokens} ${entry.kind}`)) score += 8;
    const topicPinned = pioneerIrrigation && /\/study\/manual\/church-history-in-the-fulness-of-times\/chapter-twenty-six/.test(entry.url);
    if (topicPinned) score += 500;
    return { ...entry, namedGospelTopic:entry.namedGospelTopic || entry.kind === 'history-topic', score, overlapCount: overlaps.length, titleMatch, focusedTopicMatch, topicPinned };
  }).filter((entry) => entry.topicPinned
    || entry.overlapCount >= 2
    || (entry.overlapCount >= 1 && (queryTokens.length === 1 || entry.titleMatch)));
  if (scripture) ranked.push({ ...scripture, score: 1000, overlapCount: queryTokens.length });
  return ranked.sort((left, right) => right.score - left.score || String(left.url).localeCompare(String(right.url))).slice(0, 6);
}

function isAllowedResearchFetchUrl(rawUrl) {
  try {
    const url = new URL(rawUrl);
    if (url.protocol !== 'https:' || url.username || url.password || url.port) return false;
    if (![...url.searchParams.keys()].every(key => ['lang','id','name'].includes(key))) return false;
    if (url.searchParams.has('lang') && url.searchParams.get('lang') !== 'eng') return false;
    if (/\/(?:search|internal-use-only|login|account|api)(?:\/|$)/i.test(url.pathname)) return false;
    if (['www.churchofjesuschrist.org','churchofjesuschrist.org'].includes(url.hostname)) return /^\/study\//.test(url.pathname);
    if (url.hostname === 'history.churchofjesuschrist.org') return /^\/(?:content|exhibit|landing|chd)\//.test(url.pathname);
    if (url.hostname === 'churchhistorylibrary.churchofjesuschrist.org') return /^\/db\//.test(url.pathname);
    if (APPROVED_LDS_STUDY_HOSTS.has(url.hostname)) return url.pathname !== '/' && !/\/(?:login|search|account|user|api|wp-admin)(?:\/|$)/i.test(url.pathname);
    if (url.hostname === 'newsroom.churchofjesuschrist.org') return /^\/(?:article|topic|ldsnewsroom)\//.test(url.pathname);
    return false;
  } catch (_) { return false; }
}

function isAllowedOfficialFetchUrl(rawUrl, deterministic = false, researched = false) {
  if (researched) return isAllowedResearchFetchUrl(rawUrl);
  try {
    const url = new URL(String(rawUrl || ''));
    if (url.protocol !== 'https:') return false;
    if (PIONEER_SOURCE_URLS.has(url.href)) return true;
    if (url.hostname !== 'www.churchofjesuschrist.org') return false;
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

function extractVisibleParagraphs(htmlText, candidate = null) {
  const scopedJourney = candidate?.pioneerDisclosure
    && candidate.url === 'https://www.churchofjesuschrist.org/study/manual/church-history-in-the-fulness-of-times/chapter-twenty-six?lang=eng';
  let clean = String(htmlText || '')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<(head|script|style|nav|footer|svg|form|noscript|template|iframe)\b[\s\S]*?(?:<\/\1>|$)/gi, ' ')
    .replace(/<header\b[\s\S]*?(?:<\/header>|$)/gi, match => scopedJourney ? match : ' ')
    .replace(/<((?!(?:area|base|br|col|embed|hr|img|input|link|meta|param|source|track|wbr)\b)[a-z][a-z0-9-]*)\b[^>]*(?:\bhidden\b|\binert\b|aria-hidden\s*=\s*["']?true|style\s*=\s*(?:"[^"]*(?:display\s*:\s*none|visibility\s*:\s*hidden)[^"]*"|'[^']*(?:display\s*:\s*none|visibility\s*:\s*hidden)[^']*'|[^\s>]*(?:display\s*:\s*none|visibility\s*:\s*hidden)[^\s>]*))[^>]*>[\s\S]*?(?:<\/\1>|$)/gi, ' ');
  if (scopedJourney) {
    // Scope this chapter's fixed 1847 landmarks after visibility filtering.
    // Earlier sections describe different companies in 1846.
    const journey = /<h2\b[^>]*>\s*Journey of the Pioneer Company\s*<\/h2>([\s\S]*?)<h2\b[^>]*>\s*Establishing a Settlement in the Valley\s*<\/h2>/i.exec(clean);
    if (!journey) return [];
    clean = journey[1];
  }
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
  if (/(?:<br\b[^>]*>\s*){2,}/i.test(clean)) clean.split(/(?:<br\b[^>]*>\s*){2,}/gi).forEach(consider);
  return paragraphs;
}

function explicitHistoryYears(candidate, question) {
  return candidate && candidate.deterministicHistoryTopic === true
    ? Array.from(new Set(String(question || '').match(/\b[12]\d{3}\b/g) || [])) : [];
}

function eligibleSourceParagraphs(paragraphs, candidate) {
  return (Array.isArray(paragraphs) ? paragraphs : []).filter(text => {
    if (!candidate?.pioneerDisclosure) return true;
    if (candidate.url === 'https://www.churchofjesuschrist.org/study/manual/church-history-in-the-fulness-of-times/chapter-twenty-six?lang=eng'
      && /Chimney Rock.{0,50}landmark in Wyoming/i.test(text)) return false;
    if (candidate.url === 'https://www.churchofjesuschrist.org/study/manual/church-history-in-the-fulness-of-times/chapter-twenty-eight?lang=eng'
      && /more people died.{0,100}any other immigrant group in the United States/i.test(text)) return false;
    return true;
  });
}

function pioneerParagraphScore(paragraphs, position, candidate) {
  if (!candidate || !candidate.pioneerDisclosure || !candidate.focalPhrases?.length) return 0;
  const matches = text => candidate.focalPhrases.some(phrase => String(text || '').toLowerCase().includes(phrase));
  if (matches(paragraphs[position])) return 1200;
  if (candidate.url === 'https://www.churchofjesuschrist.org/study/manual/church-history-in-the-fulness-of-times/chapter-twenty-six?lang=eng') {
    return /the pioneer company of 1847 traversed/i.test(paragraphs[position] || '') ? 350 : 0;
  }
  return 0;
}

function relevantParagraphText(paragraphs, question, candidate = null) {
  const sourceParagraphs = eligibleSourceParagraphs(paragraphs, candidate);
  const historyYears = explicitHistoryYears(candidate, question);
  const queryTokens = normalizeDiscoveryTokens(question);
  const topicPinned = Boolean(candidate && candidate.topicPinned);
  const selected = sourceParagraphs.map((text, position) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    const overlap = queryTokens.filter((token) => tokens.has(token)).length;
    const pinnedIrrigation = topicPinned && /\birrigat\w*\b/i.test(text);
    const pinnedSettlement = topicPinned && /\b(?:settlement\w*|communit\w*|pioneer\w*|salt\s+lake\s+valley)\b/i.test(text);
    const topicScore = pioneerParagraphScore(sourceParagraphs, position, candidate) + (pinnedIrrigation ? 240 : 0) + (pinnedSettlement ? 40 : 0);
    return { text, position, overlap, topicScore, score: (historyYears.some((year) => new RegExp(`\\b${year}\\b`).test(text)) ? 400 : 0) + topicScore + overlap * 20 + Math.min(10, text.length / 180) };
  }).filter((item) => candidate?.pioneerDisclosure && candidate.focalPhrases?.length
    ? item.topicScore > 0 : item.overlap > 0 || item.topicScore > 0)
    .sort((left, right) => right.score - left.score)
    .slice(0, candidate && (candidate.namedGospelTopic === true || candidate.pioneerDisclosure === true) ? sourceParagraphs.length : 2);
  if (candidate && (candidate.namedGospelTopic === true || candidate.pioneerDisclosure === true)) {
    // A uniquely named short topic needs complete explanatory paragraphs, not
    // a 700-character fragment. Keep relevance-ranked paragraphs within the
    // existing scripture-sized budget, then restore their reading order.
    let characters = 0;
    const positions = new Set();
    for (const item of selected) {
      for (const position of [item.position,item.position-1,item.position+1]) {
        if (position < 0 || position >= sourceParagraphs.length || positions.has(position)) continue;
        // Landmark evidence has an explicit source scope. Mere adjacency must
        // not attach a separate recollection to the named place or journey.
        if (candidate.pioneerDisclosure && candidate.focalPhrases?.length
          && pioneerParagraphScore(sourceParagraphs, position, candidate) <= 0) continue;
        const text = sourceParagraphs[position];
        if (characters + text.length + 2 > 4200) continue;
        positions.add(position); characters += text.length + 2;
      }
    }
    return [...positions].sort((a,b)=>a-b).map(position=>sourceParagraphs[position]).join('\n\n');
  }
  if (isPinnedAlma32FaithStudy(candidate, question)) {
    // Keep the original question anchors; add the actual comparison rather than
    // replacing the evidence that establishes relevance to the visitor's question.
    const position = sourceParagraphs.findIndex((text) => /\bword\b/i.test(text) && /\bseed\b/i.test(text));
    if (position >= 0 && !selected.some((item) => item.position === position)) {
      selected.push({ text: sourceParagraphs[position], position });
    }
  }
  if (candidate && candidate.deterministic === true && selected.length) {
    // A named scripture chapter is already pinned to one canonical source.
    // Keep both highest-relevance anchor paragraphs before surrounding context.
    // This prevents a long early paragraph from truncating a later paragraph
    // that supplies a second concept in the visitor's question (for example
    // Enos 1 prayer plus forgiveness) on a cold, uncached fetch.
    const anchorPositions = Array.from(new Set(selected.map((item) => item.position)))
      .sort((left, right) => left - right);
    const contextPositions = new Set();
    selected.forEach((item) => {
      for (let offset = -1; offset <= 3; offset += 1) {
        const position = item.position + offset;
        if (position >= 0 && position < sourceParagraphs.length && !anchorPositions.includes(position)) {
          contextPositions.add(position);
        }
      }
    });
    return [
      ...anchorPositions,
      ...Array.from(contextPositions).sort((left, right) => left - right),
    ].map((position) => sourceParagraphs[position]).join(' ').slice(0, 4200);
  }
  if (candidate && candidate.deterministicHistoryTopic === true && selected.length) {
    const positions = new Set();
    // A deterministic history topic is an article-level match, not merely a
    // paragraph-level keyword match. Preserve its lead paragraphs so origin,
    // date, identity, and purpose are not displaced by a later heading that
    // happens to share more query tokens (for example "organization").
    for (let position = 0; position < Math.min(2, sourceParagraphs.length); position += 1) positions.add(position);
    selected.forEach((item) => {
      for (let offset = -1; offset <= 2; offset += 1) {
        const position = item.position + offset;
        if (position >= 0 && position < sourceParagraphs.length) positions.add(position);
      }
    });
    // An explicitly dated question needs its matching event before general leads.
    const anchors = historyYears.length ? selected.map((item) => item.position) : [];
    let characters = 0;
    return [...anchors, ...Array.from(positions).sort((left, right) => left - right).filter((position) => !anchors.includes(position))]
      .map((position) => sourceParagraphs[position]).filter((text) => {
        if (characters + text.length + 1 > 4200) return false;
        characters += text.length + 1;
        return true;
      }).join('\n\n');
  }
  return selected.map((item) => item.text).join(' ').slice(0, 700);
}

function uniqueEvidenceOverlapCount(content, question) {
  const questionTokenSet = new Set(normalizeDiscoveryTokens(question));
  return new Set(normalizeDiscoveryTokens(content).filter((token) => questionTokenSet.has(token))).size;
}

function isPinnedPioneerIrrigationSource(candidate, content = '') {
  return Boolean(candidate && candidate.topicPinned === true
    && /\/study\/manual\/church-history-in-the-fulness-of-times\/chapter-twenty-six/.test(String(candidate.url || ''))
    && /\birrigat\w*\b/i.test(String(content || ''))
    && /\b(?:pioneer\w*|settlement\w*|communit\w*|salt\s+lake\s+valley|planting|water)\b/i.test(String(content || '')));
}

function evidenceAdmissionSufficient(candidate, content, question) {
  const titleTokens = normalizeDiscoveryTokens(candidate?.title || '');
  const questionTokens = new Set(normalizeDiscoveryTokens(question));
  const bodyTokens = new Set(normalizeDiscoveryTokens(content));
  const explicitGospelTopic = candidate?.namedGospelTopic === true && candidate.kind === 'gospel-topic'
    && titleTokens.length > 0 && titleTokens.every(token => questionTokens.has(token) && bodyTokens.has(token))
    && String(content).split(/\s+/).length >= 25;
  return uniqueEvidenceOverlapCount(content, question) >= 2
    || explicitGospelTopic
    || isPinnedPioneerIrrigationSource(candidate, content);
}

function extractRelevantParagraphs(htmlText, question) {
  return relevantParagraphText(extractVisibleParagraphs(htmlText), question);
}

function compactParagraphPack(paragraphs, candidate, question = '') {
  paragraphs = eligibleSourceParagraphs(paragraphs, candidate);
  if (candidate?.namedGospelTopic || candidate?.pioneerDisclosure) return relevantParagraphText(paragraphs,question,candidate).split('\n\n').filter(Boolean);
  const historyYears = explicitHistoryYears(candidate, question);
  const discoveryTokens = normalizeDiscoveryTokens(`${candidate.title || ''} ${candidate.tokens || ''}`);
  const queryTokens = normalizeDiscoveryTokens(question);
  const topicPinned = Boolean(candidate && candidate.topicPinned);
  const questionFocused = topicPinned || Boolean(candidate && (candidate.deterministic === true || candidate.deterministicHistoryTopic === true || (candidate.namedGospelTopic === true || candidate.pioneerDisclosure === true)));
  const almaPinned = isPinnedAlma32FaithStudy(candidate, question);
  const originalAnchors = almaPinned ? (Array.isArray(paragraphs) ? paragraphs : []).map((text, position) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    return { position, overlap: queryTokens.filter((token) => tokens.has(token)).length,
      score: queryTokens.filter((token) => tokens.has(token)).length * 20 + Math.min(10, text.length / 180) };
  }).filter((item) => item.overlap > 0).sort((left, right) => right.score - left.score).slice(0, 2).map((item) => item.position) : [];
  const metaphorPosition = almaPinned ? paragraphs.findIndex((text) => /\bword\b/i.test(text) && /\bseed\b/i.test(text)) : -1;
  let size = 0;
  return (Array.isArray(paragraphs) ? paragraphs : []).map((text, position) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    const discoveryOverlap = discoveryTokens.filter((token) => tokens.has(token)).length;
    const queryOverlap = questionFocused ? queryTokens.filter((token) => tokens.has(token)).length : 0;
    const pinnedIrrigation = topicPinned && /\birrigat\w*\b/i.test(text);
    const pinnedSettlement = topicPinned && /\b(?:settlement\w*|communit\w*|pioneer\w*|salt\s+lake\s+valley)\b/i.test(text);
    const topicScore = pioneerParagraphScore(paragraphs, position, candidate) + (pinnedIrrigation ? 600 : 0) + (pinnedSettlement ? 100 : 0);
    const historyLeadScore = candidate && candidate.deterministicHistoryTopic === true && !historyYears.length && position < 2 ? 1200 : 0;
    const historyYearScore = historyYears.some((year) => new RegExp(`\\b${year}\\b`).test(text)) ? 2400 : 0;
    return { text, position, score: (originalAnchors.includes(position) || position === metaphorPosition ? 2400 : 0) + historyYearScore + historyLeadScore + topicScore + queryOverlap * 40 + discoveryOverlap * 20 - position / 1000 };
  }).filter(item => !candidate?.pioneerDisclosure || !candidate.focalPhrases?.length
    || pioneerParagraphScore(paragraphs, item.position, candidate) > 0)
    .sort((left, right) => right.score - left.score)
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

function officialExcerptCacheVariant(candidate) {
  return candidate && candidate.topicPinned === true
    && /\/study\/manual\/church-history-in-the-fulness-of-times\/chapter-twenty-six/.test(String(candidate.url || ''))
    ? 'pioneer-irrigation'
    : 'default';
}

async function evidenceCacheKey(candidate, question) {
  if (!globalThis.crypto || !globalThis.crypto.subtle) return null;
  const variant = officialExcerptCacheVariant(candidate);
  const deterministicQuestionKey = candidate
    && (candidate.deterministic === true || candidate.deterministicHistoryTopic === true || (candidate.namedGospelTopic === true || candidate.pioneerDisclosure === true))
    ? normalizeDiscoveryTokens(question).slice(0, 12).join('-') + (isPinnedAlma32FaithStudy(candidate, question) ? '-word-seed-v1' : '') + (explicitHistoryYears(candidate, question).length ? '-dated-history-v1' : '')
    : '';
  const normalized = `${OFFICIAL_EXCERPT_CACHE_VERSION}\n${variant}\n${deterministicQuestionKey}\n${candidate.url}`;
  const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(normalized));
  const hex = Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
  return new Request(`https://focuschrist-groq-proxy.caribousun.workers.dev/__official_excerpt_cache/${hex}`);
}

async function fetchOfficialSource(candidate, question, deadline, counters = null) {
  if (!isAllowedOfficialFetchUrl(candidate.url, candidate.deterministic === true, candidate.researched === true)) return null;
  const available = remainingBudget(deadline);
  if (available < 300) {
    if (counters) counters.transportFailures = Number(counters.transportFailures || 0) + 1;
    return null;
  }
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
          const content = relevantParagraphText(payload.paragraphs, question, candidate);
          if (content && evidenceAdmissionSufficient(candidate, content, question)) {
            if (counters) counters.cacheHits += 1;
            const source = canonicalSource(candidate.url, candidate.researched && payload.title ? payload.title : candidate.title, content,
              candidate.deterministic === true || candidate.deterministicHistoryTopic === true || candidate.namedGospelTopic === true || candidate.pioneerDisclosure === true ? 4200 : 700);
            if (source) {
              source.cacheStatus = 'hit';
              source.topicPinned = candidate.topicPinned === true;
            }
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
    if (!response.ok || response.status >= 300) {
      if (counters && (response.status === 429 || response.status >= 500)) counters.transportFailures = Number(counters.transportFailures || 0) + 1;
      return null;
    }
    const contentType = String(response.headers.get('content-type') || '').toLowerCase();
    if (!contentType.includes('text/html')) return null;
    const html = await readBoundedText(response, OFFICIAL_HTML_BYTE_LIMIT);
    const titleMatch = html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i) || html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
    const title = candidate.researched && titleMatch
      ? decodeHtmlEntities(titleMatch[1].replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim().slice(0, 180)
      : candidate.title;
    const paragraphs = extractVisibleParagraphs(html, candidate);
    const content = relevantParagraphText(paragraphs, question, candidate);
    if (!content || !evidenceAdmissionSufficient(candidate, content, question)) return null;
    if (cache && cacheKey) {
      try {
        await cache.put(cacheKey, new Response(JSON.stringify({ title, paragraphs: compactParagraphPack(paragraphs, candidate, question) }), {
          headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=3600' },
        }));
      } catch (_cacheError) {}
    }
    const source = canonicalSource(candidate.url, title, content,
      candidate.deterministic === true || candidate.deterministicHistoryTopic === true || candidate.namedGospelTopic === true || candidate.pioneerDisclosure === true ? 4200 : 700);
    if (source) {
      source.cacheStatus = 'miss';
      source.topicPinned = candidate.topicPinned === true;
    }
    return source;
  } catch (_error) {
    if (counters && String(_error?.message || '') !== 'official_html_too_large') counters.transportFailures = Number(counters.transportFailures || 0) + 1;
    return null;
  } finally {
    if (timer) clearTimeout(timer);
  }
}

async function hydrateResearchEvidence(sources, question, deadline, diagnostic = null) {
  const counters = { attempts: 0, cacheHits: 0, cacheMisses: 0 };
  const official = sources.filter(isApprovedLdsSource).slice(0, 4);
  const results = await Promise.all(official.map(async source => {
    if (!isAllowedResearchFetchUrl(source.url)) return null;
    const fetched = await fetchOfficialSource({ ...source, researched: true, namedGospelTopic: true },
      question, deadline, counters);
    if (!fetched) return null;
    const result = fetched;
    return { ...result, sourceClass: isOfficialChurchSource(result) ? 'official-church' : 'attributed-lds-study' };
  }));
  if (diagnostic) {
    diagnostic.focuschrist_source_transport_failures = Number(diagnostic.focuschrist_source_transport_failures || 0) + Number(counters.transportFailures || 0);
    diagnostic.focuschrist_official_fetch_calls = Number(diagnostic.focuschrist_official_fetch_calls || 0) + counters.attempts;
    diagnostic.focuschrist_official_cache_hits = Number(diagnostic.focuschrist_official_cache_hits || 0) + counters.cacheHits;
    diagnostic.focuschrist_official_cache_misses = Number(diagnostic.focuschrist_official_cache_misses || 0) + counters.cacheMisses;
  }
  return results.filter(Boolean);
}

function relatedConversationSources(scope) {
  if (deterministicScriptureSource(scope.question)) return [];
  const topic = [scope.question, ...(scope.conversationContext || [])].join(' ').toLowerCase();
  let paths = [];
  const identityQuestion = /\b(?:who|where|same|different|identity|jehovah|is god|was god|is he|was he)\b/i.test(scope.question);
  if (identityQuestion && /\b(?:god|jehovah|jesus|christ)\b/.test(topic) && /\b(?:old|new) testament\b/.test(topic)) {
    paths = ['gospel-topics/jesus-christ', 'gospel-topics/godhead'];
  } else if (/\b(?:when|year|date|begin|start|end|finish|last|long|departure|arrival)\b/i.test(scope.question)
      && /\b(?:pioneer|pioneers|nauvoo|latter.day saint|mormon)\b/.test(topic)
      && /\b(?:exodus|migration|trek|depart(?:ure)?|journey)\b/.test(topic)
      && !/\b(?:biblical|moses|egypt|pharaoh)\b/.test(topic)) {
    paths = ['history/topics/departure-from-nauvoo', 'history/topics/pioneer-trek'];
  }
  // This selects complementary evidence, never an answer or approval. These
  // indexed official articles supply the distinctions a title-only match misses.
  return paths.map(path => CHURCH_SOURCE_INDEX.find(entry => entry.url.includes('/' + path + '?')))
    .filter(Boolean).map(entry => ({ ...entry, namedGospelTopic: true }));
}

async function retrieveIndexedChurchEvidence(question, page, deadline, pioneerTopicKey = '') {
  const rankedCandidates = rankChurchSourceCandidates(question, page);
  const deterministicScripture = deterministicScriptureSource(question);
  const deterministicHistoryTopic = deterministicScripture ? null : deterministicHistoryTopicSource(question, page);
  const namedGospelTopic = deterministicScripture || deterministicHistoryTopic ? null : namedGospelTopicSource(question, page, rankedCandidates);
  const topic = pioneerTopic(pioneerTopicKey, page);
  const candidates = topic ? [{ url: topic.url, title: topic.subject, kind: 'pioneer-disclosure', pioneerDisclosure: true, focalPhrases: PIONEER_FOCAL_PHRASES[pioneerTopicKey] || [] }] : deterministicScripture
    ? [{ ...deterministicScripture, score: 1000, overlapCount: normalizeDiscoveryTokens(question).length }]
    : deterministicHistoryTopic
      ? [deterministicHistoryTopic]
      : namedGospelTopic ? [namedGospelTopic] : rankedCandidates;
  const counters = { attempts: 0, cacheHits: 0, cacheMisses: 0 };
  const singleSource = Boolean(topic || deterministicScripture || deterministicHistoryTopic || namedGospelTopic);
  const fetchCandidates = singleSource ? candidates.slice(0, 1) : candidates.slice(0, 2);
  const fetched = await Promise.all(fetchCandidates.map((candidate) => fetchOfficialSource(candidate, question, deadline, counters)));
  const evidence = fetched.filter(Boolean).slice(0, singleSource ? 1 : 2);
  return {
    candidates,
    evidence,
    fetchCalls: counters.attempts,
    cacheHits: counters.cacheHits,
    cacheMisses: counters.cacheMisses,
    transportFailures: Number(counters.transportFailures || 0),
    deterministicScripture: Boolean(deterministicScripture),
    deterministicHistoryTopic: Boolean(deterministicHistoryTopic),
    namedGospelTopic: Boolean(namedGospelTopic),
    pioneerDisclosure: Boolean(topic),
  };
}

// Only records returned by our hash-checked library receive this capability.
// URLs, model output and externally supplied metadata cannot grant it.
const verifiedCanonicalEvidence = new WeakSet();
function hasExcessiveSourceOverlap(answer, evidence, limit = 25) {
  const answerTokens = String(answer || '').toLowerCase().match(/[a-z0-9']+/g) || [];
  if (answerTokens.length <= limit) return false;
  return (Array.isArray(evidence) ? evidence : []).some((source) => {
    if (verifiedCanonicalEvidence.has(source)) return false;
    const sourceTokens = String(source.content || '').toLowerCase().match(/[a-z0-9']+/g) || [];
    const sourceText = ` ${sourceTokens.join(' ')} `;
    for (let index = 0; index + limit < answerTokens.length; index += 1) {
      if (sourceText.includes(` ${answerTokens.slice(index, index + limit + 1).join(' ')} `)) return true;
    }
    let reconstructedWords = 0;
    let sourceFloor = 0;
    let orderedPassWords = 0;
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
      // Repeating a substantial ordered reconstruction cannot dilute its
      // copying ratio. Restart only after a full source-derived pass, never
      // merely because ordinary short phrases or names recur.
      if (longest < 2 && orderedPassWords > limit) {
        for (let sourceIndex = 0; sourceIndex < sourceFloor; sourceIndex += 1) {
          let length = 0;
          while (answerTokens[answerIndex + length]
            && sourceTokens[sourceIndex + length] === answerTokens[answerIndex + length]) length += 1;
          if (length > longest) { longest = length; longestSourceIndex = sourceIndex; }
        }
        if (longest >= 2) orderedPassWords = 0;
      }
      if (longest >= 2) {
        reconstructedWords += longest;
        orderedPassWords += longest;
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
    let terms = queryTokens.filter((token) => sourceTokens.has(token)).slice(0, 6);
    if (terms.length < 2 && isPinnedPioneerIrrigationSource(source, source.content)) {
      const semanticTerms = terms.slice();
      if (!semanticTerms.includes('irrigation') && /\birrigat\w*\b/i.test(String(source.content || ''))) semanticTerms.push('irrigation');
      if (semanticTerms.length < 2) semanticTerms.push('pioneer-settlement-context');
      terms = semanticTerms.slice(0, 6);
    }
    return { url: source.url, overlap_count: terms.length, terms };
  });
}

const REVIEWED_ALMA_32_WORD_AND_FAITH = "In Alma 32, Alma compares the word to a seed and invites people to begin with a desire to believe. Faith is the trust involved in making room for that word and trying the invitation; the word is what is planted. In Alma 32:28-35, Alma describes noticing the effects of the growing seed, including an enlarged soul and increased understanding. He distinguishes that experience from knowing everything. Alma 32:37-43 then stresses continued care, diligence, patience, and looking forward to the fruit. Neglect can prevent growth even when the seed is good. The comparison invites sustained attention to God's word rather than demanding instant certainty. Read the full passage to distinguish Alma's imagery from additional gardening details that a modern retelling might invent.";

function isAlma32FaithStudyQuestion(value) {
  // Normalize only this equivalent chapter label; retain all scope exclusions.
  value = String(value || "").replace(/\balma\s+chapter\s+32\b/gi, "Alma 32");
  // A bounded chapter-level study of this metaphor. Verse-specific, comparative,
  // historical and personal instructions remain on the normal evidence route.
  const almaStudyVocabulary = new Set('how does do can what is are alma 32 describe describes developing develop faith teach teaches about the seed comparison metaphor lesson lessons teachings of in explain growth grow growing nourish nourishing word and patience diligence a tell me with emphasis on meaning using official scripture text should reader understand give identity cause'.split(' '));
  return String(value || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').split(/\s+/).filter(Boolean).every((token) => almaStudyVocabulary.has(token))
    && /\balma\s+32\b(?!\s*[:0-9])/i.test(value)
    && /\b(?:faith|seed)\b/i.test(value)
    && !/\b(?:compare|contradict|versus|history|historical|archaeology|baptism|poverty|poor|money|medical|medicine|medication|diagnosis|prove|proof|guarantee)\b/i.test(value)
    && !/\balma\s+32\s*:\s*\d|\b(?:verse|verses|chapter|chapters)\s+\d|\b(?:john|james|nephi|moroni|mosiah)\s+\d/i.test(value);
}

function isPinnedAlma32FaithStudy(candidate, question) {
  return Boolean(candidate && candidate.deterministic === true
    && /^https:\/\/www\.churchofjesuschrist\.org\/study\/scriptures\/bofm\/alma\/32(?:\?|$)/.test(String(candidate.url || ''))
    && isAlma32FaithStudyQuestion(question));
}

function reviewedDeterministicEvidenceRecovery(question, evidence) {
  const value = String(question || '');
  const sources = Array.isArray(evidence) ? evidence : [];
  if (isAlma32FaithStudyQuestion(value)) {
    const sourceIndex = sources.findIndex((source) => {
      let parsed;
      try { parsed = new URL(String(source && source.url || '')); } catch (_error) { return false; }
      const content = String(source && source.content || '');
      return parsed.protocol === 'https:'
        && parsed.hostname === 'www.churchofjesuschrist.org'
        && parsed.pathname === '/study/scriptures/bofm/alma/32'
        && /\bword\b/i.test(content) && /\bseed\b/i.test(content)
        && /\bfaith\b/i.test(content) && content.trim().length >= 180;
    });
    if (sourceIndex >= 0) return {
      recoveryId: 'reviewed-alma-32-word-and-faith',
      answer: REVIEWED_ALMA_32_WORD_AND_FAITH,
      sourceIndexes: [sourceIndex + 1],
    };
  }
  if (/\benos\s+1\b/i.test(value)
    && /\bpray\w*\b/i.test(value)
    && /\bforgiv\w*\b/i.test(value)) {
    const sourceIndex = sources.findIndex((source) => {
      let parsed;
      try { parsed = new URL(String(source && source.url || '')); } catch (_error) { return false; }
      if (parsed.protocol !== 'https:'
        || !(parsed.hostname === 'churchofjesuschrist.org' || parsed.hostname.endsWith('.churchofjesuschrist.org'))
        || parsed.pathname !== '/study/scriptures/bofm/enos/1') return false;
      const content = String(source && source.content || '');
      return content.trim().length >= 80;
    });
    if (sourceIndex >= 0) {
      return {
        recoveryId: 'reviewed-enos-1-prayer-forgiveness',
        answer: REVIEWED_ENOS_1_PRAYER_FORGIVENESS,
        sourceIndexes: [sourceIndex + 1],
      };
    }
  }
  if (/\brelief\s+society\b/i.test(value)) {
    const sourceIndex = sources.findIndex((source) => {
      let parsed;
      try { parsed = new URL(String(source && source.url || '')); } catch (_error) { return false; }
      if (parsed.protocol !== 'https:'
        || !(parsed.hostname === 'churchofjesuschrist.org' || parsed.hostname.endsWith('.churchofjesuschrist.org'))
        || !['/study/history/topics/female-relief-society-of-nauvoo', '/study/history/topics/relief-society'].includes(parsed.pathname)) return false;
      const content = String(source && source.content || '');
      return /\brelief\s+society\b/i.test(content)
        && /\b(?:nauvoo|1842)\b/i.test(content)
        && /\b(?:organiz\w*|poor|women|souls?)\b/i.test(content);
    });
    if (sourceIndex >= 0) {
      return {
        recoveryId: 'reviewed-relief-society-nauvoo',
        answer: REVIEWED_RELIEF_SOCIETY_NAUVOO,
        sourceIndexes: [sourceIndex + 1],
      };
    }
  }
  return null;
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
  const text = evidence.map((source, index) => [
    `SOURCE ${index + 1}`,
    `SOURCE CLASS: ${source.sourceClass || (isOfficialChurchSource(source) ? 'official-church' : 'web')}`,
    `TITLE: ${source.title}`,
    `URL: ${source.url}`,
    `CONTENT: ${source.content || '(No retrievable source excerpt was returned.)'}`,
  ].join('\n')).join('\n\n');
  // Keep all six admitted article passages (up to 4,200 characters each),
  // or the bounded canonical pack. Never truncate a final passage or source.
  if (evidence.length > 6 || text.length > 40000) throw new Error('evidence-pack-limit');
  return text;
}

function parseVerifierJson(text) {
  const raw = String(text || '').trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '');
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (_error) {}
  const firstBrace = raw.indexOf('{');
  const lastBrace = raw.lastIndexOf('}');
  if (firstBrace >= 0 && lastBrace > firstBrace) {
    try { return JSON.parse(raw.slice(firstBrace, lastBrace + 1)); } catch (_error) {}
  }
  return null;
}

function isJsonValidationFailure(result) {
  const error = result && result.data && result.data.error ? result.data.error : {};
  return Boolean(result && result.response && result.response.status === 400
    && /json[_ -]?validate|failed_generation/i.test(`${error.code || ''} ${error.type || ''} ${error.message || ''}`));
}

function verifiedAnswerFailureReason(answer, evidence, scope, approved) {
  const text = String(answer || '').trim();
  if (!approved) return 'not-approved';
  if (!text) return 'empty-answer';
  if (!Array.isArray(evidence) || !evidence.length) return 'missing-evidence';
  if (scope.selectedPioneer && !evidence.some(isTellMyStorySource)) return 'missing-biography';
  if ((scope.faith || scope.approvedSourcesOnly) && !scope.selectedPioneer && (!evidence.length || !evidence.every(isApprovedLdsSource))) return 'missing-official-source';
  if (hasKnownFalseClaim(text)) return 'known-false-claim';
  if (hasExcessiveSourceOverlap(text, evidence)) return 'excessive-source-overlap';
  if (!answerMeetsSubstanceContract(text, scope)) return 'insufficient-substance';
  return null;
}

function guardVerifiedAnswer(answer, evidence, scope, approved) {
  return verifiedAnswerFailureReason(answer, evidence, scope, approved)
    ? SOURCE_INTEGRITY_FALLBACK : String(answer || '').trim();
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

function answerMeetsRepairMargin(answer, scope) {
  const text = String(answer || '').replace(/\s+/g, ' ').trim();
  const original = String(answer || '').trim();
  const words = text ? text.split(' ').filter(Boolean).length : 0;
  const sentences = countCompleteSentences(text);
  const paragraphs = original ? original.split(/\n\s*\n/).filter((value) => value.trim()).length : 0;
  if (scope && scope.selectedPioneer) return words >= 120 && sentences >= 4 && paragraphs >= 2;
  if (scope && scope.faith) return words >= 95 && sentences >= 4 && paragraphs >= 1;
  return words >= 55 && sentences >= 3 && paragraphs >= 1;
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

async function callApprovedResearch(env, body, deadline, diagnostic = {}) {
  const reserve = 12000; // Article hydration plus the existing semantic verifier.
  if (!env?.OPENAI_API_KEY || diagnostic.focuschrist_openai_research_calls
      || remainingBudget(deadline) < reserve + 1000) {
    diagnostic.focuschrist_openai_research_error_stage = !env?.OPENAI_API_KEY ? 'missing-key' : diagnostic.focuschrist_openai_research_calls ? 'call-limit' : 'deadline-reserve';
    return providerFailure(503, 'service_unavailable');
  }
  diagnostic.focuschrist_openai_research_calls = 1;
  diagnostic.focuschrist_research_provider = 'openai';
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), Math.min(35000, remainingBudget(deadline) - reserve));
  let result;
  let stage = "transport";
  try {
    const response = await fetch('https://api.openai.com/v1/responses', {
      method: 'POST', redirect: 'manual', signal: controller.signal,
      headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: OPENAI_VERIFIER_MODEL, store: false, reasoning: { effort: 'low' },
        max_output_tokens: 900, max_tool_calls: 1,
        tools: [{ type: 'web_search', search_context_size: 'low', filters: {
          allowed_domains: [OFFICIAL_CHURCH_HOST, ...APPROVED_LDS_STUDY_HOSTS],
        } }], tool_choice: { type: 'web_search' }, include: ['web_search_call.action.sources'],
        instructions: 'Search only the allowed LDS sources. Find original articles that address the current question and its core relationships. If the question asks what a particular scripture corpus teaches, find direct passages in that requested corpus that address the question, in addition to relevant study articles. A modern article about the topic alone does not establish what the requested corpus teaches. Search output is discovery metadata, not verified evidence. Return source URLs; do not compose an answer or invent quotations.',
        input: (body.messages || []).filter(message => message.role === 'user')
          .map(message => ({ role: 'user', content: String(message.content || '').slice(0, 12000) })).slice(-4),
      }),
    });
    diagnostic.focuschrist_openai_research_http_status = response.status;
    if (response.status >= 300 && response.status < 400) {
      diagnostic.focuschrist_openai_research_error_stage = 'provider-redirect';
      return providerFailure(502, 'service_unavailable');
    }
    stage = "response-body";
    const raw = await response.text();
    if (raw.length > 128000) throw new Error('response-limit');
    stage = "response-json";
    const data = JSON.parse(raw);
    stage = "response-shape";
    result = { response, data, callCount: 0 };
    if (!response.ok) diagnostic.focuschrist_openai_research_error_stage = 'http-error';
    if (response.ok) {
      const safeStatus = value => ['completed','incomplete','failed','in_progress','queued','cancelled','searching'].includes(value) ? value : 'unknown';
      diagnostic.focuschrist_openai_research_response_status = safeStatus(data.status);
      const reason = data.incomplete_details?.reason;
      diagnostic.focuschrist_openai_research_incomplete_reason = ['max_output_tokens','content_filter','steered'].includes(reason) ? reason : reason ? 'other' : 'none';
      const searchCalls = Array.isArray(data.output) ? data.output.filter(item => item?.type === 'web_search_call') : [];
      diagnostic.focuschrist_openai_research_search_call_count = Math.min(searchCalls.length, 100);
      diagnostic.focuschrist_openai_research_search_status = searchCalls.length === 1 ? safeStatus(searchCalls[0].status) : 'unknown';
      // A finished search can supply URL leads even if unused prose exhausted
      // its token budget. Never consume incomplete tool output or filtered prose.
      const usableResponse = data.status === 'completed' || (data.status === 'incomplete' && reason === 'max_output_tokens');
      const valid = usableResponse && !data.error && searchCalls.length === 1 && searchCalls[0].status === 'completed';
      if (!valid) {
        diagnostic.focuschrist_openai_research_error_stage = 'incomplete-search';
        result = { ...providerFailure(503, 'service_unavailable'), callCount: 0 };
      }
      else {
        stage = "source-leads";
        const urls = new Set();
        const leads = (Array.isArray(searchCalls[0].action?.sources) ? searchCalls[0].action.sources : []).filter(source => {
          if (!source || source.type !== 'url' || !isAllowedResearchFetchUrl(source.url) || urls.has(source.url)) return false;
          urls.add(source.url); return true;
        }).slice(0, 4).map(source => ({ url: source.url, title: String(source.title || 'Approved study article').slice(0, 200) }));
        diagnostic.focuschrist_openai_research_lead_count = leads.length;
        diagnostic.focuschrist_openai_research_error_stage = 'none';
        result.data = { choices: [{ message: { content: '', executed_tools: [{ search_results: leads }] } }] };
      }
    }
  } catch (error) {
    diagnostic.focuschrist_openai_research_error_stage = controller.signal.aborted ? 'timeout' : error?.message === 'response-limit' ? 'response-limit' : stage;
    result = { ...providerFailure(controller.signal.aborted ? 504 : 503, controller.signal.aborted ? 'timeout' : 'service_unavailable'), callCount: 0 };
  } finally { clearTimeout(timer); }
  const safe = providerDiagnostic(result);
  diagnostic.focuschrist_openai_research_status = safe.focuschrist_provider_status;
  diagnostic.focuschrist_openai_research_code = safe.focuschrist_provider_code;
  return result;
}

async function callOpenAIVerifier(apiKey, body, deadline) {
  if (!apiKey) return { ...providerFailure(503, 'service_unavailable'), openaiCallCount: 0 };
  const available = remainingBudget(deadline);
  if (available < 250) return { ...providerFailure(504, 'timeout'), openaiCallCount: 0 };
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timeoutMs = Math.max(200, Math.min(PROVIDER_CALL_LIMIT_MS, available - 50));
  const timer = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;
  let response;
  try {
    response = await fetch(OPENAI_ENDPOINT, {
      method: 'POST', redirect: 'manual',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: OPENAI_VERIFIER_MODEL,
        messages: body.messages,
        reasoning_effort: 'low',
        max_completion_tokens: Math.max(300, Number(body.max_tokens || 0)),
        response_format: body.response_format || { type: 'json_object' },
        store: false,
      }),
      signal: controller ? controller.signal : undefined,
    });
    if (response.status >= 300 && response.status < 400) return { ...providerFailure(502, 'service_unavailable'), openaiCallCount: 1 };
    const raw = await response.text();
    if (raw.length > 128000) throw new Error('response-limit');
    return { response, data: JSON.parse(raw), openaiCallCount: 1 };
  } catch (error) {
    return {
      ...providerFailure(error && error.name === 'AbortError' ? 504 : 503,
        error && error.name === 'AbortError' ? 'timeout' : 'service_unavailable'),
      openaiCallCount: 1,
    };
  } finally {
    if (timer) clearTimeout(timer);
  }
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

function verifierRouteDiagnostic(result) {
  const usage = result?.accumulatedUsage || result?.data?.usage || {};
  return {
    focuschrist_verifier_route: result?.verifierRoute || 'openai-primary',
    focuschrist_openai_verifier_calls: Number(result?.totalOpenAIVerifierCalls || result?.openaiCallCount || 0),
    focuschrist_verifier_duration_ms: Number(result?.verifierDurationMs || 0),
    focuschrist_verifier_input_tokens: Number(usage.prompt_tokens || usage.input_tokens || 0),
    focuschrist_verifier_output_tokens: Number(usage.completion_tokens || usage.output_tokens || 0),
  };
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
  target.totalOpenAIVerifierCalls = results.reduce((sum, result) => sum + Number(
    result?.totalOpenAIVerifierCalls || result?.openaiCallCount || 0), 0);
  return target;
}

async function callVerifier(env, body, deadline, options = {}) {
  const started = Date.now();
  const raw = await callOpenAIVerifier(env?.OPENAI_API_KEY, body, deadline);
  return {
    ...validateVerifierResult(raw, options.requireSourceIndexes === true),
    verifierRoute: options.forceOpenAI ? 'openai-repair' : 'openai-primary',
    totalOpenAIVerifierCalls: Number(raw.openaiCallCount || 0),
    verifierDurationMs: Date.now() - started,
  };
}

function fallbackPayload(mode, extra, scope) {
  const general = scope && !scope.faith && !scope.selectedPioneer;
  const unavailable = /(?:unavailable|provider-error|rate-limited|exception)/.test(mode);
  const message = unavailable ? SOURCE_UNAVAILABLE_MESSAGE : SOURCE_INTEGRITY_FALLBACK;
  return {
    id: 'focuschrist-source-policy',
    choices: [{
      index: 0,
      message: { role: 'assistant', content: message },
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

function providerRetryAfterSeconds(result) {
  const header = result?.response?.headers?.get('retry-after');
  if (header) {
    const seconds = /^\d+(?:\.\d+)?$/.test(header.trim()) ? Number(header)
      : (Date.parse(header) - Date.now()) / 1000;
    if (Number.isFinite(seconds) && seconds >= 0) return Math.ceil(seconds);
  }
  const message = String(result?.data?.error?.message || '');
  const delay = message.match(/try again in\s+((?:[\d.]+\s*(?:milliseconds?|minutes?|seconds?|hours?|ms|h|m|s)\s*)+)/i);
  if (!delay) return null;
  let seconds = 0;
  for (const match of delay[1].matchAll(/([\d.]+)\s*(milliseconds?|minutes?|seconds?|hours?|ms|h|m|s)/gi)) {
    const unit = match[2].toLowerCase();
    seconds += Number(match[1]) * (unit === 'ms' || unit.startsWith('milli') ? .001 : unit.startsWith('m') ? 60 : unit.startsWith('h') ? 3600 : 1);
  }
  return Number.isFinite(seconds) && seconds >= 0 ? Math.ceil(seconds) : null;
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
    ...(result?.response?.status === 429 ? {
      focuschrist_provider_retry_after_seconds: providerRetryAfterSeconds(result),
      focuschrist_provider_rate_limit_category: /\b(?:per day|daily|TPD|RPD)\b/i.test(String(error.message || '')) ? 'daily-quota'
        : /\b(?:per minute|TPM|RPM|per second)\b/i.test(String(error.message || '')) ? 'pacing' : 'unspecified',
    } : {}),
  };
}

export default {
  async fetch(request, env) {
    const deadline = Date.now() + REQUEST_BUDGET_MS;
    const localScriptures = createScriptureLibrary(scriptureCatalog, path => scriptureFetch(path, deadline));
    const origin = request.headers.get('Origin') || '';
    if (!ALLOWED_ORIGINS.has(origin)) return new Response('Origin not allowed', { status: 403 });
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: corsHeaders(origin) });
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405 });
    if (!(request.headers.get('Content-Type') || '').toLowerCase().includes('application/json')) {
      return jsonResponse({ error: 'Content-Type must be application/json' }, 415, origin, deadline, localScriptures);
    }

    const declaredLength = Number(request.headers.get('Content-Length') || 0);
    if (Number.isFinite(declaredLength) && declaredLength > REQUEST_BODY_BYTE_LIMIT) {
      return jsonResponse({ error: 'Request body is too large.' }, 413, origin, deadline, localScriptures);
    }
    let payload;
    try {
      const rawBody = await request.text();
      if (new TextEncoder().encode(rawBody).length > REQUEST_BODY_BYTE_LIMIT) {
        return jsonResponse({ error: 'Request body is too large.' }, 413, origin, deadline, localScriptures);
      }
      payload = JSON.parse(rawBody);
    } catch (_error) {
      return jsonResponse({ error: 'Invalid JSON' }, 400, origin, deadline, localScriptures);
    }
    if (!Array.isArray(payload && payload.messages) || payload.messages.length > REQUEST_MESSAGE_LIMIT) {
      return jsonResponse({ error: `Use no more than ${REQUEST_MESSAGE_LIMIT} conversation messages.` }, 400, origin, deadline, localScriptures);
    }
    const sanitized = sanitizePayload(payload || {});
    if (!sanitized.scope.question) return jsonResponse({ error: 'A user message is required' }, 400, origin, deadline, localScriptures);
    if (sanitized.scope.question.length > 1200) {
      return jsonResponse({ error: 'Please shorten the question to 1,200 characters or fewer.' }, 400, origin, deadline, localScriptures);
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
      }, 200, origin, deadline, localScriptures);
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
          }, 429, origin, deadline, localScriptures);
        }
      } catch (_error) {
        // Availability takes precedence if the optional abuse-control binding has a transient fault.
      }
    }
    if (sanitized.scope.scriptureSupportRequested && !sanitized.scope.scriptureSupportAntecedent) {
      return jsonResponse(generalAnswerPayload('Which question or teaching would you like a scripture for? Please name the subject so I can find a passage that actually supports it.', 'scripture-context-clarification', {}, sanitized.scope), 200, origin, deadline, localScriptures);
    }
    // Reject only canonical catalog errors here; library/network errors are not invalid references.
    try { localScriptures.references(sanitized.scope.question); }
    catch (error) {
      if (['invalid-scripture-reference', 'invalid-verse-selection', 'invalid-numbered-scripture-book'].includes(error.message)) {
        return jsonResponse(fallbackPayload('invalid-scripture-reference', { focuschrist_verifier_route: 'local-canonical-validation', focuschrist_openai_verifier_calls: 0 }, sanitized.scope), 200, origin, deadline, localScriptures);
      }
    }
    const supportOldTestament = sanitized.scope.scriptureSupportRequested
      && isGodInOldTestamentQuestion(sanitized.scope.scriptureSupportAntecedent);
    const directScripture = await localScriptures.lookupRequest(supportOldTestament ? 'Genesis 1:1' : sanitized.scope.question);
    if (directScripture && supportOldTestament) directScripture.answer = 'Genesis 1:1 explicitly names God as the creator of heaven and earth.\n\n' + directScripture.answer;
    if (directScripture) return jsonResponse({
      id: 'focuschrist-local-scripture',
      choices: [{index:0,message:{role:'assistant',content:directScripture.answer},finish_reason:'stop'}],
      focuschrist_sources: directScripture.sources,
      focuschrist_source_integrity_verified: true,
      focuschrist_source_policy: SOURCE_POLICY_VERSION,
      focuschrist_gateway_mode: 'local-scripture-library',
      focuschrist_openai_verifier_calls: 0,
    },200,origin,deadline,localScriptures);
    if (!sanitized.scope.faith && needsIdentityClarification(sanitized.scope.question)) {
      return jsonResponse(generalAnswerPayload(
        'Which Joseph do you mean? Please include the last name or a little more context.',
        'general-identity-clarification',
        {
          focuschrist_verifier_route: 'local-clarification',
          focuschrist_retrieval_route: 'none',
        },
        sanitized.scope,
      ), 200, origin, deadline, localScriptures);
    }
    if (isReviewedColorRegression(sanitized.scope.question)) {
      return jsonResponse(reviewedColorPayload(), 200, origin, deadline, localScriptures);
    }
    const requestDiagnostic = {
      focuschrist_retrieval_route: 'none',
      focuschrist_index_candidates: 0,
      focuschrist_index_sources: 0,
      focuschrist_official_fetch_calls: 0,
      focuschrist_official_cache_hits: 0,
      focuschrist_official_cache_misses: 0,
      focuschrist_source_sitemap_revision: CHURCH_SOURCE_SITEMAP_REVISION,
      focuschrist_source_robots_hash: CHURCH_SOURCE_ROBOTS_SHA256.slice(0, 12),
    };
    try {
      if (!sanitized.scope.approvedSourcesOnly && !sanitized.scope.faith && !sanitized.scope.selectedPioneer
        && !prefersResearchFirstGeneral(sanitized.scope.question)) {
        const directGeneralAnswer = await produceLowRiskGeneralAnswer(env, sanitized.scope, '', deadline);
        if (directGeneralAnswer) {
          return jsonResponse(generalAnswerPayload(
            directGeneralAnswer,
            'general-ai-low-risk',
            sanitized.scope,
          ), 200, origin, deadline, localScriptures);
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

      if (!sanitized.scope.selectedPioneer) {
        try {
          // Current explicit references take precedence. Only preceding USER
          // questions can supply a missing reference through retrievalQuestion.
          const currentRefs = localScriptures.references(sanitized.scope.question);
          const scriptureEvidence = await localScriptures.evidenceRequest(currentRefs.length
            ? sanitized.scope.question : sanitized.scope.retrievalQuestion);
          if (scriptureEvidence.length) {
            for (const source of scriptureEvidence) verifiedCanonicalEvidence.add(source);
            evidence = scriptureEvidence;
            allEvidence = scriptureEvidence;
            retrievalDiagnostic.focuschrist_retrieval_route = 'church-source-index';
            retrievalDiagnostic.focuschrist_deterministic_scripture = true;
            retrievalDiagnostic.focuschrist_local_canonical_evidence = true;
            retrievalDiagnostic.focuschrist_index_candidates = scriptureEvidence.length;
            retrievalDiagnostic.focuschrist_index_sources = scriptureEvidence.length;
          }
        } catch (_error) {
          // Invalid or unavailable passages never become admitted evidence.
          // Existing bounded research and the final reference gate still apply.
        }
      }

      const relatedSources = !evidence.length && (sanitized.scope.faith || sanitized.scope.approvedSourcesOnly) && !sanitized.scope.selectedPioneer
        ? relatedConversationSources(sanitized.scope) : [];
      if (relatedSources.length) {
        const counters = { attempts: 0, cacheHits: 0, cacheMisses: 0 };
        evidence = (await Promise.all(relatedSources.map(source => fetchOfficialSource(source,
          `${sanitized.scope.retrievalQuestion} ${source.title}`, deadline, counters)))).filter(Boolean);
        if (evidence.length !== relatedSources.length) evidence = [];
        allEvidence = evidence;
        retrievalDiagnostic.focuschrist_retrieval_route = 'church-source-index';
        retrievalDiagnostic.focuschrist_related_source_pack = true;
        retrievalDiagnostic.focuschrist_index_candidates = relatedSources.length;
        retrievalDiagnostic.focuschrist_index_sources = evidence.length;
        retrievalDiagnostic.focuschrist_official_fetch_calls = counters.attempts;
        retrievalDiagnostic.focuschrist_official_cache_hits = counters.cacheHits;
        retrievalDiagnostic.focuschrist_official_cache_misses = counters.cacheMisses;
        retrievalDiagnostic.focuschrist_source_transport_failures = Number(retrievalDiagnostic.focuschrist_source_transport_failures || 0) + Number(counters.transportFailures || 0);
      }

      if (!evidence.length && (sanitized.scope.faith || sanitized.scope.approvedSourcesOnly) && !sanitized.scope.selectedPioneer) {
        const indexed = await retrieveIndexedChurchEvidence(sanitized.scope.retrievalQuestion, sanitized.scope.page, deadline, sanitized.scope.pioneerTopicKey);
        retrievalDiagnostic.focuschrist_index_candidates = indexed.candidates.length;
        retrievalDiagnostic.focuschrist_index_sources = indexed.evidence.length;
        retrievalDiagnostic.focuschrist_deterministic_scripture = indexed.deterministicScripture === true;
        retrievalDiagnostic.focuschrist_deterministic_history_topic = indexed.deterministicHistoryTopic === true;
        retrievalDiagnostic.focuschrist_named_gospel_topic = indexed.namedGospelTopic === true;
        retrievalDiagnostic.focuschrist_pioneer_disclosure = indexed.pioneerDisclosure === true;
        retrievalDiagnostic.focuschrist_official_fetch_calls = indexed.fetchCalls;
        retrievalDiagnostic.focuschrist_official_cache_hits = indexed.cacheHits;
        retrievalDiagnostic.focuschrist_official_cache_misses = indexed.cacheMisses;
        retrievalDiagnostic.focuschrist_source_transport_failures = Number(retrievalDiagnostic.focuschrist_source_transport_failures || 0) + Number(indexed.transportFailures || 0);
        if (indexed.evidence.length) {
          evidence = indexed.evidence;
          allEvidence = indexed.evidence;
          draft = '';
          retrievalDiagnostic.focuschrist_retrieval_route = 'church-source-index';
        }
      }

      if (!evidence.length) {
        if (!env || !env.OPENAI_API_KEY) {
          return jsonResponse(fallbackPayload('research-unavailable', {
            ...retrievalDiagnostic,
            ...(sanitized.scope.lowRiskDiagnostic || {}),
          }, sanitized.scope), 200, origin, deadline, localScriptures);
        }
        researchResult = await callApprovedResearch(env, sanitized.research, deadline, retrievalDiagnostic);
        retrievalDiagnostic.focuschrist_retrieval_route = 'openai-research';
        if (!researchResult.response.ok) {
          if (!sanitized.scope.approvedSourcesOnly && !sanitized.scope.faith && !sanitized.scope.selectedPioneer
            && !requiresExternalGeneralResearch(sanitized.scope.question)) {
            const fallbackGeneralAnswer = await produceLowRiskGeneralAnswer(env, sanitized.scope, '', deadline);
            if (fallbackGeneralAnswer) {
              return jsonResponse(generalAnswerPayload(
                fallbackGeneralAnswer,
                'general-ai-low-risk',
                { ...sanitized.scope.lowRiskDiagnostic, ...retrievalDiagnostic },
                sanitized.scope,
              ), 200, origin, deadline, localScriptures);
            }
          }
          const limited = researchResult.response.status === 429;
          return jsonResponse(fallbackPayload(
            limited ? 'research-rate-limited' : 'research-provider-error',
            { ...providerDiagnostic(researchResult), ...retrievalDiagnostic, ...(sanitized.scope.lowRiskDiagnostic || {}) },
            sanitized.scope,
          ), 200, origin, deadline, localScriptures);
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
        evidence = sanitized.scope.approvedSourcesOnly
          ? await hydrateResearchEvidence(allEvidence, sanitized.scope.retrievalQuestion, deadline - 3500, retrievalDiagnostic)
          : allEvidence.slice(0, 2);
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
      if (draft && !evidence.length && !sanitized.scope.approvedSourcesOnly && !sanitized.scope.faith && !sanitized.scope.selectedPioneer) {
        const generalAnswer = await produceLowRiskGeneralAnswer(env, sanitized.scope, draft, deadline);
        if (generalAnswer) {
          return jsonResponse(generalAnswerPayload(
            generalAnswer,
            'general-ai-consensus',
            { ...sanitized.scope.lowRiskDiagnostic, ...retrievalDiagnostic },
            sanitized.scope,
          ), 200, origin, deadline, localScriptures);
        }
      }
      if (!evidence.length) {
        return jsonResponse(fallbackPayload(
          retrievalDiagnostic.focuschrist_source_transport_failures > 0 ? 'research-unavailable' : 'research-insufficient-evidence',
          { ...(sanitized.scope.lowRiskDiagnostic || {}), ...retrievalDiagnostic },
          sanitized.scope,
        ), 200, origin, deadline, localScriptures);
      }

      // Exact reviewed recoveries do not need a stochastic model verdict once the
      // Worker has already retrieved and validated their pinned official source.
      // This keeps these narrow owner journeys available during provider faults or
      // rate pressure without weakening the fail-closed contract for any other ask.
      const reviewedDeterministic = retrievalDiagnostic.focuschrist_retrieval_route === 'church-source-index'
        ? reviewedDeterministicEvidenceRecovery(sanitized.scope.retrievalQuestion, evidence)
        : null;
      if (reviewedDeterministic) {
        const recoveryIndexes = reviewedDeterministic.sourceIndexes
          .filter((sourceIndex) => Number.isInteger(sourceIndex) && sourceIndex >= 1 && sourceIndex <= evidence.length);
        const recoveryEvidence = recoveryIndexes.map((sourceIndex) => evidence[sourceIndex - 1]);
        const recoveryAnswer = guardVerifiedAnswer(
          reviewedDeterministic.answer,
          recoveryEvidence,
          sanitized.scope,
          recoveryEvidence.length > 0,
        );
        if (recoveryAnswer !== SOURCE_INTEGRITY_FALLBACK && recoveryEvidence.length > 0) {
          return jsonResponse({
            id: 'focuschrist-reviewed-deterministic-evidence',
            choices: [{
              index: 0,
              message: { role: 'assistant', content: recoveryAnswer },
              finish_reason: 'stop',
            }],
            focuschrist_sources: recoveryEvidence.map((source) => ({
              text: source.title || 'Source',
              url: source.url,
            })),
            focuschrist_source_integrity_verified: true,
            focuschrist_source_policy: SOURCE_POLICY_VERSION,
            focuschrist_gateway_mode: 'retrieval-researched-and-verified',
            focuschrist_resolved_profile: sanitized.scope.faith ? 'faith-study' : (sanitized.scope.profile || 'general-knowledge'),
            focuschrist_classification_mode: sanitized.scope.classificationMode || 'request-scope',
            focuschrist_answer_word_count: recoveryAnswer.split(/\s+/).filter(Boolean).length,
            focuschrist_evidence_relevance: evidenceRelevanceReceipt(sanitized.scope.retrievalQuestion, recoveryEvidence),
            focuschrist_verifier_route: 'reviewed-deterministic',
            focuschrist_openai_verifier_calls: 0,
            focuschrist_verifier_conservative_unmetered_neurons: 0,
            focuschrist_reviewed_deterministic_recovery: reviewedDeterministic.recoveryId,
            ...retrievalDiagnostic,
          }, 200, origin, deadline, localScriptures);
        }
      }

      const expandCanonicalEvidence = async () => {
        const added = await augmentRequestedCorpusEvidence(sanitized.scope, evidence, localScriptures,
          isAllowedResearchFetchUrl, () => remainingBudget(deadline) > 12000);
        for (const source of added) verifiedCanonicalEvidence.add(source);
        evidence = [...evidence, ...added];
        allEvidence = [...allEvidence, ...added];
      };
      await expandCanonicalEvidence();

      const makeVerifierPrompt = () => (sanitized.scope.selectedPioneer ? [
        'You are writing a source-grounded biographical summary. Return one JSON object only.',
        `The visitor selected ${sanitized.scope.selectedPioneerName}. The evidence below is that person's permitted Tell My Story, Too entry.`,
        'Write a concise two-to-four paragraph answer using only facts in that entry. Do not use the optional research draft or add facts from memory.',
        'Attribute diary material, descendant recollections, family histories, traditions, and miraculous accounts to the people or source traditions named in the entry. Do not present them as official Church declarations.',
        'Do not reproduce long passages. Paraphrase the biography and preserve meaningful uncertainty words such as apparently, probably, recalled, reported, or according to the entry.',
        'If the entry contains usable biographical information for the selected person, set approved true and source_indexes to [1]. Set approved false only if the evidence is empty or belongs to a different person.',
        requestedTeachingCorpora(sanitized.scope).length
          ? 'The visitor requests teaching from a named scriptural corpus. Cite at least one concrete canonical chapter or verse from each requested corpus in your answer, supported by the selected EVIDENCE. A generic modern doctrinal explanation without such support does not meet this request. Do not invent a citation to satisfy this requirement; reject when evidence lacks it.' : '',
        'Schema: {"approved":boolean,"answer":string,"source_indexes":number[]}',
        '',
        `EVIDENCE:\n${evidenceForVerifier(evidence)}`,
      ].join('\n') : [
        'You are a strict evidence verifier. Return one JSON object only.',
        'Compose the final answer from the supplied source excerpts. If the DRAFT block is empty, write the answer directly from EVIDENCE and never reject merely because no candidate draft was supplied.',
        'When EVIDENCE is canonical scripture, explain the current question from that passage. A request to teach, explain, compare, or apply is not satisfied by returning only the passage text. Previous user questions supply conversational context only, not evidence or a replacement question.',
        'If a draft is present, repair it into a direct, complete answer using the evidence. Every externally checkable claim, quotation, attribution, date, statistic, scripture citation, and statement of official teaching must be directly supported by the evidence. Remove unsupported detail and correct contradictions, but preserve useful supported explanation. Do not add facts from memory.',
        'Keep each person, organization, place, date, and action attached to the relationship actually stated in its source context. A shift of time or setting can change the subject even within one paragraph. Never combine an earlier location with a later organization merely because both occur in the same excerpt. Do not increase geographic specificity, infer an unnamed city, or resolve an ambiguous referent unless the evidence explicitly supports it. Preserve these limits when combining neighboring paragraphs or separate sources.',
        'For a simple general fact, give at least 45 words and two complete sentences. For a faith or Church-history question, give 90 to 220 words and at least three complete sentences. A nuanced question normally needs two to four short paragraphs. Put the direct answer first, then explain the context supported by the evidence. Never return a one-line fact fragment, a one- or two-word answer, or padded repetition.',
        'Preserve the exact subjects and relationships in scriptural comparisons. Do not extend a metaphor with invented physical details or present a personal application as something the passage says. If the text compares the word to a seed, do not replace the word with faith or invent watering, warmth, or other gardening instructions.',
        'Use independently worded paraphrase. Do not copy a long passage or reconstruct the source in ordered fragments. Apart from unavoidable names and short doctrinal phrases, avoid matching source wording for more than eight consecutive words.',
        'Explain the supported facts in a fresh structure organized around the visitor question. Do not follow the source sentence by sentence or substitute synonyms into its clauses. Shared short fragments in the same order can also reproduce too much of the source. Rebuild the explanation while preserving exact names, dates, offices, relationships, and chronology. Do not add facts or filler to dilute overlap.',
        APPROVED_LDS_RESEARCH_POLICY,
        'Answer coverage is required in addition to source accuracy. Identify the core of the current question: its requested entities, event, comparison, or relationship. Set approved true only when the evidence supports a substantive answer to that core request, including when DRAFT is empty. An accurate paragraph about only one requested entity does not answer a multi-entity relationship question. Evidence about a different time period does not answer the requested period; stating that the supplied source only covers another date is not sufficient coverage. Do not approve a partial answer whose main response is that the evidence lacks the other central entities or relationship; set approved false so additional sources can be researched. A clearly supported answer that an asserted premise is false may be approved. source_indexes must list the 1-based evidence sources that directly support the final answer.',
        'Interpret ordinary awkward grammar by its clear intended meaning. Do not reject a scripture, doctrine, or history question merely because its wording is imperfect. If the named official source directly addresses the named topic or concept, answer from that evidence.',
        retrievalDiagnostic.focuschrist_deterministic_scripture === true
          ? 'The visitor explicitly named a canonical scripture chapter. EVIDENCE contains that exact official scripture source and no competing research source. If its excerpt directly addresses the requested concept, compose the supported answer from it and approve it. Do not reject merely because the visitor asks for an explanation rather than a quotation.'
          : retrievalDiagnostic.focuschrist_deterministic_history_topic === true
            ? 'The visitor explicitly named, or the bounded conversation context resolved to, an indexed Church History topic. EVIDENCE contains that exact official Church History topic and no competing research source. If its excerpt directly describes the requested identity, role, event, date, purpose, or historical setting, compose the supported answer from it and approve it. For a faith or Church-history answer, aim for 100 to 170 words and at least four complete sentences so the response clears the publication-depth floor with margin. Do not infer relative ages within a family or add biographical relationships that the evidence does not explicitly state.'
            : 'Evaluate the supplied official evidence normally under the source-integrity contract.',
        sanitized.scope.pioneerTopicKey
          ? 'This is a fixed historical timeline entry. Describe only causal links explicitly stated in the evidence: chronology or paragraph proximity does not establish cause. Do not infer motives, feelings, sounds, or present-day conditions. Do not invent journals, quotations, later accounts, or source descriptions. Keep dates and companies distinct, and do not move an event to the requested year simply because that year appears in the question. Omit unbounded comparisons. Attribute remembered experiences to the named narrator. Write a connected historical explanation without Context or Source fact labels and without repeating the same facts in a second summary.'
          : '',
        requestedTeachingCorpora(sanitized.scope).length
          ? 'The visitor requests teaching from a named scriptural corpus. Cite at least one concrete canonical chapter or verse from each requested corpus in your answer, supported by the selected EVIDENCE. A generic modern doctrinal explanation without such support does not meet this request. Do not invent a citation to satisfy this requirement; reject when evidence lacks it.' : '',
        'Schema: {"approved":boolean,"answer":string,"source_indexes":number[]}',
        '',
        `QUESTION:\n${sanitized.scope.question}`,
        conversationInstruction(sanitized.scope),
        '',
        `DRAFT:\n${draft}`,
        '',
        `EVIDENCE:\n${evidenceForVerifier(evidence)}`,
      ].join('\n')) + '\n' + SCRIPTURE_QUOTATION_CONTRACT;
      let verifierPrompt = makeVerifierPrompt();
      const verifierBody = {
        messages: [{ role: 'user', content: verifierPrompt }],
        temperature: 0,
        max_tokens: sanitized.scope.selectedPioneer ? 900 : (sanitized.scope.faith ? 1000 : 500),
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
        }, sanitized.scope), 200, origin, deadline, localScriptures);
      }
      const verifierContent = verifierResult.data && verifierResult.data.choices && verifierResult.data.choices[0]
        ? verifierResult.data.choices[0].message.content
        : '';
      let verdict = parseVerifierJson(verifierContent);
      let indexes = verdict && Array.isArray(verdict.source_indexes)
        ? verdict.source_indexes.filter((index) => Number.isInteger(index) && index >= 1 && index <= evidence.length)
        : [];
      const initialCorpusCoverage = checkCorpusCoverage(sanitized.scope, verdict?.answer,
        indexes.map(index => evidence[index - 1]), localScriptures, isAllowedResearchFetchUrl);
      if (verdict?.approved === true && !initialCorpusCoverage.ok) {
        verdict = { ...verdict, approved: false };
        indexes = [];
        retrievalDiagnostic.focuschrist_corpus_coverage_failure = initialCorpusCoverage.reason;
      }
      let freshResearchEvidence = false;
      // A local index hit is a discovery lead, not proof that the question can
      // be answered from that excerpt. Search once before declining an unknown.
      if (verdict?.approved === false && (sanitized.scope.faith || sanitized.scope.approvedSourcesOnly) && !sanitized.scope.selectedPioneer
          && retrievalDiagnostic.focuschrist_retrieval_route === 'church-source-index'
          && !retrievalDiagnostic.focuschrist_openai_research_calls && env?.OPENAI_API_KEY
          && remainingBudget(deadline) >= 9000) {
        const researched = await callApprovedResearch(env, sanitized.research, deadline, retrievalDiagnostic);
        retrievalDiagnostic.focuschrist_research_escalated = true;
        if (!researched.response.ok && (researched.response.status === 429 || researched.response.status >= 500)) retrievalDiagnostic.focuschrist_source_transport_failures = Number(retrievalDiagnostic.focuschrist_source_transport_failures || 0) + 1;
        if (researched.response.ok) {
          const message = researched.data?.choices?.[0]?.message;
          const discovered = await hydrateResearchEvidence(collectSourceEvidence(message),
            sanitized.scope.retrievalQuestion, deadline - 3500, retrievalDiagnostic);
          const usable = discovered.filter(source => source.content && source.content.length >= 80);
          if (usable.length) {
            evidence = usable;
            allEvidence = usable;
            await expandCanonicalEvidence();
            draft = String(message?.content || '').slice(0, 4000);
            retrievalDiagnostic.focuschrist_retrieval_route = 'index-then-approved-research';
            retrievalDiagnostic.focuschrist_deterministic_scripture = false;
            retrievalDiagnostic.focuschrist_deterministic_history_topic = false;
            retrievalDiagnostic.focuschrist_named_gospel_topic = false;
            retrievalDiagnostic.focuschrist_related_source_pack = false;
            verifierPrompt = makeVerifierPrompt();
            indexes = [];
            freshResearchEvidence = true;
          }
        }
      }
      const selectedEvidenceBeforeRepair = indexes.map((index) => evidence[index - 1]);
      const scriptureBeforeRepair = verdict && verdict.approved === true
        ? await localScriptures.checkAnswer(verdict.answer, selectedEvidenceBeforeRepair)
        : {ok:true};
      const needsScriptureRepair = !scriptureBeforeRepair.ok
        && !/unavailable|fetch|timeout|integrity-mismatch/i.test(scriptureBeforeRepair.reason || '');
      const needsDepthRepair = Boolean(verdict && verdict.approved === true && indexes.length
        && (!answerMeetsSubstanceContract(verdict.answer, sanitized.scope)
          || ((retrievalDiagnostic.focuschrist_deterministic_history_topic === true
            || sanitized.scope.classificationMode === 'conversation-context')
            && !answerMeetsRepairMargin(verdict.answer, sanitized.scope))));
      const needsParaphraseRepair = Boolean(verdict && verdict.approved === true && indexes.length
        && hasExcessiveSourceOverlap(verdict.answer, selectedEvidenceBeforeRepair));
      const indexedEvidenceRelevance = evidenceRelevanceReceipt(sanitized.scope.retrievalQuestion, evidence);
      const hasPinnedPioneerIrrigationEvidence = isPioneerIrrigationIntent(
        sanitized.scope.retrievalQuestion,
        sanitized.scope.page,
      ) && evidence.some((entry) => /\/study\/manual\/church-history-in-the-fulness-of-times\/chapter-twenty-six/.test(entry.url));
      const needsRelevantEvidenceReconsideration = Boolean(verdict && verdict.approved === false
        && !retrievalDiagnostic.focuschrist_source_transport_failures
        && retrievalDiagnostic.focuschrist_retrieval_route === 'church-source-index'
        && (indexedEvidenceRelevance.some((entry) => entry.overlap_count >= 2)
          || hasPinnedPioneerIrrigationEvidence));
      if ((freshResearchEvidence || needsDepthRepair || needsParaphraseRepair || needsRelevantEvidenceReconsideration || needsScriptureRepair)
        && ['openai-primary'].includes(verifierResult.verifierRoute)
        && remainingBudget(deadline) >= 4500) {
        const requirements = answerSubstanceRequirements(sanitized.scope);
        const repairMinimumWords = requirements.minimumWords
          + (sanitized.scope.selectedPioneer ? 30 : (sanitized.scope.faith ? 25 : 10));
        const repairMinimumSentences = requirements.minimumSentences + (sanitized.scope.faith ? 1 : 0);
        const expansionPrompt = [
          verifierPrompt,
          needsScriptureRepair
            ? 'The deterministic scripture check rejected the previous answer: ' + scriptureBeforeRepair.reason + '. Repair it once using only the provided evidence. Remove unsupported references or quotation claims. For exact scripture words use [[SCRIPTURE:Book chapter:verse]] with a complete supported reference. Do not guess a substitute passage. If evidence cannot support the claim, omit it or reject the answer.'
            : '',
          '',
          freshResearchEvidence
            ? 'Additional approved-source research was required because the first local excerpts did not answer the question. Verify the new EVIDENCE independently and answer the current question if supported; the earlier rejection applies to the earlier evidence only.'
            : needsRelevantEvidenceReconsideration
            ? 'Your previous rejection may be a false negative because the indexed official evidence has direct lexical relevance. Re-evaluate it once without presuming either approval or rejection. Interpret awkward but understandable grammar naturally. A named scripture chapter or Church-history topic that directly addresses the requested concept is usable evidence and should not be rejected merely because the visitor phrased the question imperfectly.'
            : needsDepthRepair
            ? 'Your previous approved answer did not meet the required answer depth.'
            : needsParaphraseRepair
            ? 'Your previous approved answer failed the final publication overlap check.'
            : 'Your previous approved answer failed the deterministic scripture check.',
          needsRelevantEvidenceReconsideration
            ? (retrievalDiagnostic.focuschrist_deterministic_scripture === true
              ? 'This is the exact canonical scripture source named by the visitor. Re-read its excerpt for the requested concept. If the excerpt supports a responsible explanation, write that explanation and set approved true with source_indexes [1]. Keep approved false only if the excerpt truly lacks the requested concept.'
              : retrievalDiagnostic.focuschrist_deterministic_history_topic === true
                ? 'This is the exact official Church History topic named by the visitor or resolved from bounded conversation context. Re-read its excerpt for the requested identity, leadership role, event, or setting. If the excerpt supports a responsible answer, write a complete answer of roughly 100 to 170 words with at least four sentences and set approved true with source_indexes [1]. Keep approved false only if that exact topic excerpt truly lacks the requested material.'
                : 'If the evidence can responsibly answer the question, write the supported answer and set approved true with its source indexes. If it still cannot, keep approved false.')
            : needsDepthRepair
            ? `Rewrite it using at least ${repairMinimumWords} words, ${repairMinimumSentences} complete sentences, and ${requirements.minimumParagraphs} paragraph(s). The publication gate is lower, but this repair target deliberately includes safety margin. Do not stop at the minimum. For a conversation-context or deterministic Church History answer, treat this margin as mandatory for the repaired draft.`
            : 'Keep the answer complete and concise.',
          needsParaphraseRepair
            ? 'Rewrite the answer in genuinely independent language. The previous answer also fails the overlap check, even if it needs depth repair. Do not retain its sentence skeleton or assemble the source from short ordered fragments. Start a fresh explanation organized around the question, preserving exact facts, names, dates, and chronology. Do not add unsupported detail or filler. Keep both the required depth and independent wording.'
            : 'Preserve the independently worded explanation.',
          'State the direct answer first. Add only useful explanatory context supported by the supplied evidence; do not pad, repeat, speculate, or add facts from memory.',
          `PREVIOUS ANSWER:\n${String(verdict.answer || '').trim()}`,
          'Return the complete JSON object again with approved, answer, and source_indexes.',
        ].join('\n');
        const expansionResult = await callVerifier(env, {
          ...verifierBody,
          messages: [{ role: 'user', content: expansionPrompt }],
          max_tokens: sanitized.scope.selectedPioneer ? 900 : (sanitized.scope.faith ? 1000 : 500),
        }, deadline, {
          requireSourceIndexes: true,
          forceOpenAI: verifierResult.verifierRoute === 'openai-primary',
        });
        const initialVerifierResult = verifierResult;
        expansionResult.accumulatedUsage = combinedProviderUsage(initialVerifierResult, expansionResult);
        accumulateVerifierCalls(expansionResult, initialVerifierResult, expansionResult);
        verifierResult = {
          ...initialVerifierResult,
          accumulatedUsage: expansionResult.accumulatedUsage,
          totalOpenAIVerifierCalls: expansionResult.totalOpenAIVerifierCalls,
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
      if (verdict && verdict.approved === false
        && (retrievalDiagnostic.focuschrist_deterministic_scripture === true
          || retrievalDiagnostic.focuschrist_deterministic_history_topic === true)) {
        const reviewedRecovery = reviewedDeterministicEvidenceRecovery(
          sanitized.scope.retrievalQuestion,
          evidence,
        );
        if (reviewedRecovery) {
          verdict = {
            approved: true,
            answer: reviewedRecovery.answer,
            source_indexes: reviewedRecovery.sourceIndexes,
          };
          indexes = reviewedRecovery.sourceIndexes.slice();
          verifierResult = {
            ...verifierResult,
            reviewedDeterministicRecovery: reviewedRecovery.recoveryId,
          };
        }
      }
      const finalCorpusCoverage = checkCorpusCoverage(sanitized.scope, verdict?.answer,
        indexes.map(index => evidence[index - 1]), localScriptures, isAllowedResearchFetchUrl);
      if (verdict?.approved === true && !finalCorpusCoverage.ok) {
        verdict = { ...verdict, approved: false };
        indexes = [];
        retrievalDiagnostic.focuschrist_corpus_coverage_failure = finalCorpusCoverage.reason;
      } else if (finalCorpusCoverage.ok) {
        delete retrievalDiagnostic.focuschrist_corpus_coverage_failure;
      }
      const selectedEvidence = indexes.map((index) => evidence[index - 1]);
      const pinnedPioneerSupport = isPioneerIrrigationIntent(
        sanitized.scope.retrievalQuestion,
        sanitized.scope.page,
      ) ? evidence.filter((source) => isPinnedPioneerIrrigationSource(source, source.content)).slice(0, 1) : [];
      const publishedEvidence = [];
      const publishedEvidenceUrls = new Set();
      [
        ...selectedEvidence,
        ...pinnedPioneerSupport,
        ...(sanitized.scope.selectedPioneer ? officialEvidence : []),
      ].forEach((source) => {
        if (!source || !source.url || publishedEvidenceUrls.has(source.url)) return;
        publishedEvidenceUrls.add(source.url);
        publishedEvidence.push(source);
      });
      const answer = guardVerifiedAnswer(
        verdict && verdict.answer,
        selectedEvidence,
        sanitized.scope,
        Boolean(verdict && verdict.approved === true && indexes.length),
      );
      if (answer === SOURCE_INTEGRITY_FALLBACK) {
        return jsonResponse(fallbackPayload(!freshResearchEvidence && retrievalDiagnostic.focuschrist_source_transport_failures > 0 ? 'research-unavailable' : 'verification-rejected', {
          focuschrist_verifier_approved: Boolean(verdict && verdict.approved === true),
          focuschrist_verifier_publication_failure: verifiedAnswerFailureReason(verdict && verdict.answer, selectedEvidence, sanitized.scope, Boolean(verdict && verdict.approved === true && indexes.length)),
          focuschrist_verifier_source_indexes: verdict && Array.isArray(verdict.source_indexes)
            ? verdict.source_indexes.slice(0, 6)
            : [],
          focuschrist_verifier_answer_length: verdict ? String(verdict.answer || '').length : 0,
          ...verifierRouteDiagnostic(verifierResult),
          ...retrievalDiagnostic,
        }, sanitized.scope), 200, origin, deadline, localScriptures);
      }

      return jsonResponse({
        id: 'focuschrist-retrieval-verified',
        choices: [{
          index: 0,
          message: { role: 'assistant', content: answer },
          finish_reason: 'stop',
        }],
        focuschrist_sources: publishedEvidence.map((source) => ({
          text: source.title || 'Source',
          url: source.url,
        })),
        focuschrist_source_integrity_verified: true,
        focuschrist_source_policy: SOURCE_POLICY_VERSION,
        focuschrist_gateway_mode: 'retrieval-researched-and-verified',
        focuschrist_resolved_profile: sanitized.scope.faith ? 'faith-study' : (sanitized.scope.profile || 'general-knowledge'),
        focuschrist_classification_mode: sanitized.scope.classificationMode || 'request-scope',
        focuschrist_answer_word_count: answer.split(/\s+/).filter(Boolean).length,
        focuschrist_evidence_relevance: evidenceRelevanceReceipt(sanitized.scope.retrievalQuestion, sanitized.scope.selectedPioneer ? selectedEvidence : publishedEvidence),
        ...verifierRouteDiagnostic(verifierResult),
        focuschrist_reviewed_deterministic_recovery: verifierResult.reviewedDeterministicRecovery || null,
        ...retrievalDiagnostic,
      }, 200, origin, deadline, localScriptures);
    } catch (_error) {
      return jsonResponse(fallbackPayload('research-exception', {
        ...requestDiagnostic,
        focuschrist_retrieval_route: 'exception',
      }, sanitized.scope), 200, origin, deadline, localScriptures);
    }
  },
};

export {
  isGodInOldTestamentQuestion,
  jsonResponse,
  GENERAL_ANSWER_FALLBACK,
  OFFICIAL_EXCERPT_CACHE_VERSION,
  PROVIDER_CALL_LIMIT_MS,
  REQUEST_BUDGET_MS,
  SOURCE_INTEGRITY_FALLBACK,
  SOURCE_UNAVAILABLE_MESSAGE,
  answerMeetsSubstanceContract,
  answerMeetsRepairMargin,
  answerSubstanceRequirements,
  callApprovedResearch,
  callOpenAIVerifier,
  callVerifier,
  classifyResearchScope,
  relatedConversationSources,
  isAllowedResearchFetchUrl,
  isApprovedLdsSource,
  hydrateResearchEvidence,
  collectSourceEvidence,
  compactParagraphPack,
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
  isPioneerIrrigationIntent,
  isPinnedPioneerIrrigationSource,
  isVerifierVerdictShape,
  isTellMyStorySource,
  needsIdentityClarification,
  parseVerifierJson,
  providerDiagnostic,
  evidenceForVerifier,
  rankChurchSourceCandidates,
  relevantParagraphText,
  reviewedDeterministicEvidenceRecovery,
  deterministicScriptureSource,
  deterministicHistoryTopicSource,
  namedGospelTopicSource,
  verifiedAnswerFailureReason,
  evidenceCacheKey,
  officialExcerptCacheVariant,
  retrieveIndexedChurchEvidence,
  remainingBudget,
  requiresExternalGeneralResearch,
  sanitizePayload,
};
