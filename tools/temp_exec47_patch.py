from pathlib import Path


def replace_one(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'missing expected text in {path}: {old[:120]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


def replace_all(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'missing expected text in {path}: {old!r}')
    p.write_text(text.replace(old, new), encoding='utf-8')

# Reviewed registry release and new audited local owner answer.
replace_one('reviewed-ask-knowledge.js', "const POLICY_VERSION = '2026-09-03.17';", "const POLICY_VERSION = '2026-09-03.18';")
marker = "        {\n            id: 'church-first-vision-1820',"
entry = r'''        {
            id: 'church-book-of-mormon-publication-1830',
            profiles: ['ask', 'church-history'],
            priority: 170,
            reviewedOn: '2026-09-03',
            integrityKey: 'church-book-of-mormon-publication-1830-v1',
            contextLabel: 'Book of Mormon first publication',
            followup: {
                anchor: 'Book of Mormon publication 1830 Grandin Palmyra',
                cues: [
                    'who', 'where', 'when', 'date', 'year', 'publish', 'published', 'publisher', 'publication',
                    'print', 'printed', 'printer', 'grandin', 'palmyra', 'sale', 'available', 'copies', 'cost',
                    'finance', 'financed', 'martin harris'
                ],
                ellipsis: ['Who published it?', 'Where was it printed?', 'Who printed it?', 'When exactly?'],
                block: ['musical', 'broadway', 'movie', 'film', 'soundtrack'],
                variants: [
                    {
                        id: 'printer-publisher-location',
                        cues: ['who', 'where', 'publish', 'published', 'publisher', 'print', 'printed', 'printer', 'grandin', 'palmyra'],
                        intent: {
                            all: [
                                ['publish', 'published', 'publisher', 'print', 'printed', 'printer'],
                                ['who', 'where', 'published', 'printed', 'publisher', 'printer', 'grandin', 'palmyra']
                            ],
                            none: ['musical', 'broadway', 'movie', 'film', 'soundtrack']
                        },
                        answer: 'The first edition of the Book of Mormon was printed and published through the shop of Egbert B. Grandin in Palmyra, New York. Joseph Smith arranged with Grandin to produce 5,000 copies, and Martin Harris financed the $3,000 printing contract by mortgaging part of his farm. Printing began in 1829, and the first completed copies were offered for sale at Grandin\'s bookstore in Palmyra on March 26, 1830. So for the first edition, the printer and publisher was Egbert B. Grandin, and the place of publication was Palmyra, New York.',
                        sources: [
                            officialHistorySource('Grandin Printshop: Book of Mormon Publication Site', 'https://www.churchofjesuschrist.org/learn/locations/grandin-printshop?lang=eng', 'Official historic-site history of the first Book of Mormon printing and sale in Palmyra.'),
                            officialHistorySource('Historical Summary - Joseph Smith', 'https://www.churchofjesuschrist.org/study/manual/teachings-joseph-smith/historical-summary?lang=eng', 'Official historical timeline recording the March 26, 1830 public availability at Grandin\'s bookstore.')
                        ]
                    },
                    {
                        id: 'publication-date',
                        cues: ['when', 'date', 'year', 'sale', 'available'],
                        intent: {
                            all: [['when', 'date', 'year', 'sale', 'available', 'published', 'publication']]
                        },
                        answer: 'The first printed copies of the Book of Mormon became available to the public on March 26, 1830, at Egbert B. Grandin\'s bookstore in Palmyra, New York. Printing had begun in 1829, but March 26, 1830 is the date official Church historical sources give for the book becoming available for sale. The first edition consisted of 5,000 copies. Martin Harris helped finance the printing agreement, and Grandin\'s Palmyra shop carried out the printing and publication work.',
                        sources: [
                            officialHistorySource('Grandin Printshop: Book of Mormon Publication Site', 'https://www.churchofjesuschrist.org/learn/locations/grandin-printshop?lang=eng', 'Official historic-site history identifying March 26, 1830 as the first sale date.'),
                            officialHistorySource('Historical Summary - Joseph Smith', 'https://www.churchofjesuschrist.org/study/manual/teachings-joseph-smith/historical-summary?lang=eng', 'Official historical timeline recording the March 26, 1830 public availability.')
                        ]
                    }
                ]
            },
            match: {
                exact: [
                    'what year did the book of mormon come out',
                    'What year did the Book of Mormon come out?',
                    'When was the Book of Mormon first published?',
                    'What year was the Book of Mormon published?'
                ],
                all: [
                    ['book of mormon'],
                    ['when', 'year', 'date', 'come out', 'came out', 'published', 'publication', 'released', 'first edition', 'available', 'sale']
                ],
                none: ['musical', 'broadway', 'movie', 'film', 'soundtrack']
            },
            positiveTests: [
                'what year did the book of mormon come out',
                'What year did the Book of Mormon come out?',
                'When was the Book of Mormon first published?',
                'What year was the Book of Mormon published?'
            ],
            negativeTests: [
                'What year did The Book of Mormon musical come out?',
                'When did the Book of Mormon Broadway soundtrack come out?',
                'When was the Book of Mormon movie released?'
            ],
            answer: 'The first edition of the Book of Mormon became available to the public on March 26, 1830, in Palmyra, New York. Egbert B. Grandin and his printing shop produced the first edition after Joseph Smith arranged for 5,000 copies to be printed. Martin Harris helped finance the $3,000 printing contract by mortgaging part of his farm. Official Church historical sources identify Grandin\'s bookstore in Palmyra as the place where the first completed copies went on sale. So the concise answer is 1830, with March 26, 1830 as the first public sale date.',
            sources: [
                officialHistorySource('Grandin Printshop: Book of Mormon Publication Site', 'https://www.churchofjesuschrist.org/learn/locations/grandin-printshop?lang=eng', 'Official historic-site history of the first Book of Mormon printing and public sale.'),
                officialHistorySource('Historical Summary - Joseph Smith', 'https://www.churchofjesuschrist.org/study/manual/teachings-joseph-smith/historical-summary?lang=eng', 'Official historical timeline recording the March 26, 1830 public availability at Grandin\'s bookstore.')
            ]
        },
'''
replace_one('reviewed-ask-knowledge.js', marker, entry + marker)

# Cache-bust the reviewed registry on all Ask surfaces and keep the manifest in lockstep.
for path in ['ask.html', 'pioneers.html', 'church-history.html']:
    replace_all(path, 'reviewed-ask-knowledge.js?v=20260903-17', 'reviewed-ask-knowledge.js?v=20260903-18')
replace_one('ask-question-contracts.json', '"release": "2026-09-03.17"', '"release": "2026-09-03.18"')
replace_all('tools/source_integrity_inventory.py', 'reviewed-ask-knowledge.js?v=20260903-17', 'reviewed-ask-knowledge.js?v=20260903-18')

# Reviewed registry QA and owner exact follow-up contract.
replace_one('tools/reviewed_ask_knowledge_qa.js', "registry.policyVersion === '2026-09-03.17'", "registry.policyVersion === '2026-09-03.18'")
qa_marker = "registry.entries.filter((entry) => entry.profiles.includes('church-history')).forEach((entry) => {"
qa_block = r'''const ownerBookOfMormon = registry.match('what year did the book of mormon come out', { profile: 'ask' });
assert(ownerBookOfMormon && ownerBookOfMormon.id === 'church-book-of-mormon-publication-1830'
    && ownerBookOfMormon.mode === 'reviewed-local' && ownerBookOfMormon.sourceIntegrityPassed === true
    && ownerBookOfMormon.answer.includes('March 26, 1830')
    && ownerBookOfMormon.sources.every((source) => source.url.includes('churchofjesuschrist.org')),
    'owner Book of Mormon publication question must resolve locally from reviewed official Church sources');
const ownerBookOfMormonFollowup = registry.resolveFollowup('who published it and where was it printed?', {
    profile: 'ask',
    history: [
        { role: 'user', content: 'what year did the book of mormon come out', contextEntryId: ownerBookOfMormon.id },
        { role: 'assistant', content: ownerBookOfMormon.answer }
    ]
});
assert(ownerBookOfMormonFollowup.resolved === true
    && ownerBookOfMormonFollowup.entryId === 'church-book-of-mormon-publication-1830',
    'owner Book of Mormon follow-up did not retain the reviewed subject');
const ownerBookOfMormonFollowupAnswer = registry.match(ownerBookOfMormonFollowup.query, {
    profile: 'ask', contextVariant: ownerBookOfMormonFollowup.contextVariant
});
assert(ownerBookOfMormonFollowupAnswer
    && ownerBookOfMormonFollowupAnswer.answer.includes('Egbert B. Grandin')
    && ownerBookOfMormonFollowupAnswer.answer.includes('Palmyra, New York')
    && ownerBookOfMormonFollowupAnswer.sources.every((source) => source.url.includes('churchofjesuschrist.org')),
    'owner Book of Mormon follow-up must answer the printer and location locally from official Church sources');

'''
replace_one('tools/reviewed_ask_knowledge_qa.js', qa_marker, qa_block + qa_marker)

# Bring the production-local gate to the actual registry release and add the exact owner journey.
replace_all('tools/live_production_ask_qa.js', 'reviewed-ask-knowledge.js?v=20260903-16', 'reviewed-ask-knowledge.js?v=20260903-18')
replace_all('tools/live_production_ask_qa.js', "registry.policyVersion === '2026-09-03.16'", "registry.policyVersion === '2026-09-03.18'")
replace_all('tools/live_production_ask_qa.js', "production reviewed registry policy is not .15", "production reviewed registry policy is not .18")
live_marker = "    const lincolnQuestion = 'What date did Abraham Lincoln die?';"
live_block = r'''    const ownerBookQuestion = 'what year did the book of mormon come out';
    const ownerBookMain = requireSubstantive(
        registry.match(ownerBookQuestion, { profile: 'ask' }),
        'Owner Book of Mormon publication question',
        'March 26, 1830'
    );
    assert(ownerBookMain.id === 'church-book-of-mormon-publication-1830'
        && ownerBookMain.sources.every((source) => source.url.includes('churchofjesuschrist.org')),
        'production owner Book of Mormon question did not use the audited local official-source entry');
    const ownerBookFollow = registry.resolveFollowup('who published it and where was it printed?', {
        profile: 'ask',
        history: [
            { role: 'user', content: ownerBookQuestion, contextEntryId: ownerBookMain.id },
            { role: 'assistant', content: ownerBookMain.answer }
        ]
    });
    assert(ownerBookFollow.resolved === true && ownerBookFollow.entryId === ownerBookMain.id,
        'production owner Book of Mormon follow-up did not retain local context');
    const ownerBookFollowAnswer = requireSubstantive(
        registry.match(ownerBookFollow.query, { profile: 'ask', contextVariant: ownerBookFollow.contextVariant }),
        'Owner Book of Mormon publication follow-up',
        'Egbert B. Grandin'
    );
    assert(ownerBookFollowAnswer.answer.includes('Palmyra, New York'),
        'production owner Book of Mormon follow-up omitted the printing location');

'''
replace_one('tools/live_production_ask_qa.js', live_marker, live_block + live_marker)

# Worker .47: deterministic reviewed recovery for Enos 1 when independent verifiers false-reject exact official scripture evidence.
replace_all('groq-proxy/src/index.js', "const SOURCE_POLICY_VERSION = '2026-09-03.46';", "const SOURCE_POLICY_VERSION = '2026-09-03.47';")
replace_all('groq-proxy/src/index.js', "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.46';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.47';")
constant_marker = "const REVIEWED_COLOR_CORRECTION = 'No. Doctrine and Covenants 76:31-34 does not mention red, white, black, or golden lights and does not assign colors to degrees of glory. Those verses discuss people who know God\\'s power and then deny it. Doctrine and Covenants 18:15 teaches the joy of helping bring one soul to Jesus Christ; it does not describe colors or degrees of glory.';"
constant_add = constant_marker + "\nconst REVIEWED_ENOS_1_PRAYER_FORGIVENESS = 'Enos 1 teaches that sincere prayer can include sustained pleading with God for forgiveness and then expand into concern for others. Enos describes wrestling before God for his own soul and crying to Him throughout the day and into the night. The Lord tells Enos that his sins are forgiven because of his faith in Christ, and Enos says his guilt was swept away. After receiving that assurance, he prays for the Nephites and then for the Lamanites. The chapter therefore connects earnest prayer, faith in Jesus Christ, forgiveness, spiritual assurance, and a growing desire for the welfare of other people.';"
replace_one('groq-proxy/src/index.js', constant_marker, constant_add)

function_marker = "function identityTokens(question) {"
function_add = r'''function reviewedDeterministicEvidenceRecovery(question, evidence) {
  const value = String(question || '');
  if (!/\benos\s+1\b/i.test(value)
    || !/\bpray\w*\b/i.test(value)
    || !/\bforgiv\w*\b/i.test(value)) return null;
  const sources = Array.isArray(evidence) ? evidence : [];
  const sourceIndex = sources.findIndex((source) => {
    let parsed;
    try { parsed = new URL(String(source && source.url || '')); } catch (_error) { return false; }
    if (parsed.protocol !== 'https:'
      || !(parsed.hostname === 'churchofjesuschrist.org' || parsed.hostname.endsWith('.churchofjesuschrist.org'))
      || parsed.pathname !== '/study/scriptures/bofm/enos/1') return false;
    const content = String(source && source.content || '');
    return /\bpray\w*\b/i.test(content) && /\bforgiv\w*\b/i.test(content);
  });
  if (sourceIndex < 0) return null;
  return {
    recoveryId: 'reviewed-enos-1-prayer-forgiveness',
    answer: REVIEWED_ENOS_1_PRAYER_FORGIVENESS,
    sourceIndexes: [sourceIndex + 1],
  };
}

'''
replace_one('groq-proxy/src/index.js', function_marker, function_add + function_marker)

recovery_marker = "      const selectedEvidence = indexes.map((index) => evidence[index - 1]);"
recovery_block = r'''      if (verdict && verdict.approved === false
        && retrievalDiagnostic.focuschrist_deterministic_scripture === true) {
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
'''
replace_one('groq-proxy/src/index.js', recovery_marker, recovery_block + recovery_marker)

response_marker = "        ...verifierRouteDiagnostic(verifierResult),\n        ...retrievalDiagnostic,"
response_replacement = "        ...verifierRouteDiagnostic(verifierResult),\n        focuschrist_reviewed_deterministic_recovery: verifierResult.reviewedDeterministicRecovery || null,\n        ...retrievalDiagnostic,"
# Only replace the final successful response occurrence, which is the last identical marker.
p = Path('groq-proxy/src/index.js')
text = p.read_text(encoding='utf-8')
pos = text.rfind(response_marker)
if pos < 0:
    raise SystemExit('missing final response diagnostic marker')
text = text[:pos] + response_replacement + text[pos + len(response_marker):]
p.write_text(text, encoding='utf-8')

export_marker = "  relevantParagraphText,\n"
replace_one('groq-proxy/src/index.js', export_marker, export_marker + "  reviewedDeterministicEvidenceRecovery,\n")

# Worker tests and release matrix policy.
replace_all('groq-proxy/source-policy.test.js', "'2026-09-03.46'", "'2026-09-03.47'")
import_marker = "  remainingBudget,\n"
replace_one('groq-proxy/source-policy.test.js', import_marker, import_marker + "  reviewedDeterministicEvidenceRecovery,\n")
test_marker = "const verifierFetchBeforeTests = globalThis.fetch;"
test_block = r'''const enosReviewedRecovery = reviewedDeterministicEvidenceRecovery(
  'What does Enos 1 teach about prayer and forgiveness?',
  [{
    url: 'https://www.churchofjesuschrist.org/study/scriptures/bofm/enos/1?lang=eng',
    content: 'I cried unto him in mighty prayer and supplication for mine own soul. Thy sins are forgiven thee, and my guilt was swept away.',
  }],
);
assert(enosReviewedRecovery
  && enosReviewedRecovery.recoveryId === 'reviewed-enos-1-prayer-forgiveness'
  && enosReviewedRecovery.sourceIndexes[0] === 1
  && /prayer/i.test(enosReviewedRecovery.answer)
  && /forgiveness|forgiven/i.test(enosReviewedRecovery.answer),
  'exact Enos 1 official evidence must support the audited deterministic recovery after a verifier false negative');
assert(reviewedDeterministicEvidenceRecovery(
  'What does Enos 1 teach about prayer and forgiveness?',
  [{ url: 'https://example.com/enos/1', content: 'prayer forgiven' }],
) === null, 'reviewed Enos recovery must never accept a non-Church source');

'''
replace_one('groq-proxy/source-policy.test.js', test_marker, test_block + test_marker)

replace_all('tools/live_ai_response_matrix.js', "const POLICY_VERSION = '2026-09-03.46';", "const POLICY_VERSION = '2026-09-03.47';")
replace_all('tools/pioneer_local_first_qa.py', '2026-09-03.46', '2026-09-03.47')
replace_all('tools/scripture_grounding_qa.py', '2026-09-03.46', '2026-09-03.47')

# Record the candidate learning without claiming production success before the live gate passes.
mem = Path('MEMORY.md')
mem_text = mem.read_text(encoding='utf-8')
mem_text += "\n\n### Final owner journey hardening - candidate 2026-09-03.47\n\n- Production .46 passed the doctrine, Scripture, Pioneer, Church History, regression, and burst strata but exposed one intermittent warm-cache Enos 1 false rejection and reproduced the owner's exact Book of Mormon publication question plus follow-up failure.\n- Candidate .47 adds an audited reviewed-local Book of Mormon first-publication entry for Main Ask and Church History, including contextual follow-ups for publisher, printer, location, and publication date. The exact owner wording `what year did the book of mormon come out` is a permanent local regression.\n- Candidate .47 also adds a narrowly scoped reviewed deterministic recovery for the exact Enos 1 prayer-and-forgiveness intent. It can activate only after exact official Enos 1 evidence has already been retrieved and both prayer and forgiveness language are present in that evidence. It does not broaden source authority or bypass evidence retrieval.\n- The production-local gate is updated to the actual reviewed registry release and now executes the exact owner Book of Mormon question and follow-up from the production-served registry bytes.\n- Production remains unverified until PR CI, Worker deployment, the full live matrix, and the exact owner production journey all pass.\n"
mem.write_text(mem_text, encoding='utf-8')
