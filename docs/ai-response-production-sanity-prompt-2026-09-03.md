# focusChrist AI Response Production Sanity, Accuracy, and Performance Prompt

Date: 2026-09-03

Status at invocation: `VERIFIED FAIL` because the owner reproduced a reasonable Main Ask question, `who is hyrum smith`, receiving the generic general-answer failure after a long wait.

## Authority and objective

Execute a production-critical, evidence-based audit and repair of every focusChrist question-and-answer surface and every page that can submit, expand, continue, or route a question. The site is built around sincere questions. A reasonable visitor question must receive the best supported, direct, complete answer the system can safely provide, with accurate sources, bounded response time, correct page context, useful failure behavior, and no fabricated claims.

This prompt extends `docs/all-page-ai-ask-executive-prompt.md`. Where this prompt adds stricter accuracy, coverage, latency, observability, or production-sampling requirements, use the stricter requirement. Do not weaken existing source-integrity, accessibility, conversation, identity, cache, or deployment controls.

Execute through this authority chain:

`Owner instruction -> current Master Brain -> current Focus project brain -> current production evidence -> isolated repair -> independent verification -> production verification -> Focus learning -> transferable Master Brain learning`

Do not resume artwork or make unrelated presentation changes during this incident.

## Non-negotiable outcomes

1. Inventory every page and every route that can produce, request, expand, or route an answer. Confirm whether Home, Ask, Answers, individual Answer pages, Art, Art study pages, Church History, Pioneers, Watch, About, and utility pages own an AI answer surface or only route to one.
2. Identify the final runtime owner after inline, deferred, and dynamically loaded scripts finish. No source-file string inspection may substitute for invoking the final owner.
3. Classify the visitor's intent from the complete question and page context before choosing sources, models, or fallbacks.
4. Answer reviewed local knowledge immediately without a network dependency.
5. Use official Church sources as the external authority for Latter-day Saint doctrine, scripture, policy, institutional history, and Church figures. Use the exact selected project source for selected biographies or records.
6. Use reliable general sources for ordinary general questions. Never direct unrelated general questions to the Gospel Library.
7. Preserve accuracy through final browser rendering. No later formatter, citation guard, context resolver, or stale request may corrupt or replace a correct answer.
8. Bound total wait time. Remove stacked full retries and unnecessary sequential model calls. A failure must terminate predictably and preserve any useful verified result already available.
9. Provide a specific, useful failure state. Do not tell the visitor merely to rephrase when the same question is valid and the provider failed.
10. Verify the exact deployed revision through the real visitor journey before calling the incident resolved.
11. Incur no new cost, paid service, subscription, or provider commitment. Preserve the existing secret boundary and never expose keys, prompts, internal diagnostics, or private visitor content.
12. Enforce the owner's respect boundary before local matching or any AI request. Do not accept profanity, explicit sexual questions, or derogatory and demeaning questions about any faith, culture, ethnicity, nationality, or political affiliation.

## Required evidence states

Every material conclusion must be labeled:

- `VERIFIED PASS`: directly tested at the relevant layer.
- `VERIFIED FAIL`: directly tested and failed.
- `UNAVAILABLE / UNPROVEN`: required evidence could not be obtained.
- `HYPOTHESIS`: plausible but not proven.

Code written, tests passing locally, a merged pull request, a deployed asset, and a successful live visitor journey are different states. Never call the system fixed until they converge.

## Phase 1: Recover current truth

1. Read current Master Brain START HERE and Intelligence State.
2. Read current Focus START HERE, Current State, Unified Website Experience prompt, Hardened Study Intelligence directive, Ask reliability prompt, Surface Registry, root-cause records, decision records, and QA controls.
3. Fetch the current GitHub `main` revision and compare it with the local checkout.
4. Inspect current deployment workflows, Worker configuration, page asset versions, policy versions, and live endpoint behavior.
5. Preserve unrelated owner work and untracked files.
6. Mark stale success claims as historical evidence, not current truth.

## Phase 2: Complete surface and ownership inventory

Derive the inventory from production files. Do not rely only on an existing hand-written list.

Search all HTML and JavaScript for:

- composers, forms, inputs, buttons, Enter handlers, topic buttons, starter prompts, suggestion cards, biography choices, random-person actions, journey/trail expanders, follow-up controls, reset controls, and contextual deep links;
- `sendMessage`, `askAI`, `focusChristStudyAskV3`, `focusChristHistoryAsk`, `askTopic`, `requestPioneerAI`, reviewed-knowledge matchers, renderers, source routers, deferred loaders, and global replacements;
- every API/Worker URL, model name, timeout, retry, cache key, policy version, fallback string, and provider diagnostic;
- every public page that routes a question to another page even when it does not answer inline.

Update a machine-readable surface manifest containing:

- public page and URL;
- exact trigger and submitted text transformation;
- page profile and intended domain;
- final browser owner;
- local reviewed provider;
- selected-source provider;
- external source class;
- Worker/API path;
- timeout and retry path;
- success renderer and final integrity guard;
- failure behavior;
- automated test owner;
- live acceptance specimen.

An unregistered route, duplicate final owner, version mismatch, or question control without an executable contract blocks release.

## Phase 3: Question taxonomy and classification audit

Test the final classification and routing decision for each category below. Each category requires positive specimens, near-neighbor negatives, and at least one follow-up or subject-switch case where relevant.

### A. Stable general knowledge

Examples: sky color, historical general figures, basic science, geography, definitions, everyday how-to questions. These use general sources or a controlled stable-general lane. They must not inherit religious context solely because the site is religious.

### B. Current or time-sensitive information

Examples: current office holders, weather, schedules, prices, recent news, current Church announcements, current policy, and changing statistics. These require fresh retrieval and must not use memorized or stable-general fallback answers.

### C. Latter-day Saint doctrine and belief

Examples: Jesus Christ, Restoration, temples, priesthood, ordinances, plan of salvation, revelation, families, and commandments. These require official Church sources and careful separation of doctrine, interpretation, practice, and personal application.

### D. Scripture

Test exact references, paraphrases, chapter summaries, meaning questions, cross-scripture comparison, quotations, requests for exact wording, and fabricated or miscited claims. Never invent wording or citations. Preserve the distinction between the text and an interpretation.

### E. Church history and Church figures

Test famous and less-famous names, including full names, lowercase names, misspellings, initials, surnames, name collisions, and people absent from reviewed local knowledge. Include Hyrum Smith as a permanent specimen. A Church figure must not be classified as ordinary general knowledge merely because the name is missing from a fixed keyword list.

### F. Pioneer and selected-biography questions

Test exact indexed people, partial matches, multiple matches, absent people, similarly named people, selected biographies, source-bounded follow-ups, journey/trail cards, Handcart Companies, and non-Pioneer negative controls.

### G. Ambiguous identity or intent

Test first names, shared surnames, pronouns without context, short ellipses, multiple people in one question, competing named subjects, places that resemble names, and questions that genuinely require clarification. Clarify only when ambiguity changes the answer materially.

### H. Conversation context

Test first question, direct follow-up, pronoun follow-up, chained ellipsis, new named subject, competing subject, reset, refresh continuity, stale response, simultaneous submission, and page navigation. Context may use only the permitted recent turns and must never skip past an intervening subject.

### I. High-stakes and sensitive questions

Test medical, mental-health, self-harm, abuse, legal, financial, criminal, and emergency questions. Give appropriately bounded information and qualified-help routes without pretending the site provides professional care. Immediate-danger cases require concise urgent guidance.

### J. Adversarial, malformed, and unsupported requests

Test prompt injection, requests to ignore source rules, fabricated premises, requests for private information, hateful or unsafe content, nonsense, blank input, excessive length, Unicode punctuation, HTML/script content, malformed JSON, and unsupported languages. The system must render safely and fail clearly without exposing secrets or internal prompts.

### J1. Respect, profanity, and sexual-content boundary

Reject before local matching, conversation storage, or remote AI submission:

- profanity and cuss words, including common punctuation masking, spacing, repeated characters, and predictable spelling substitutions;
- explicit sexual words, descriptions, solicitations, or questions;
- derogatory, insulting, demeaning, or dehumanizing questions or statements about a religion, denomination, culture, ethnicity, nationality, or political affiliation;
- attempts to make the system rank protected groups as inferior, evil, stupid, subhuman, or deserving of harm.

Use one calm response consistent with the owner's direction:

> focusChrist is an independent site centered on Jesus Christ and respectful study of Latter-day Saint beliefs. Please rephrase your question without profanity, sexual content, or disrespect toward any religion, culture, or political affiliation.

Do not claim that focusChrist is an official Church property. Do not echo the prohibited wording back to the visitor. Do not send the prohibited question to the Worker or model. Do not store it in conversation history. Restore the input controls and allow a respectful rephrasing.

Test legitimate near-neighbor questions so the control does not become a viewpoint censor. Respectful factual questions about a faith, culture, political belief, disagreement, or historical conflict may proceed when they contain no prohibited language or derogatory premise. Questions reporting abuse, exploitation, coercion, or immediate danger must enter the appropriate safety-help lane rather than being reduced to the general respect redirect.

### K. Personal spiritual and pastoral questions

Test sincere questions about prayer, doubt, grief, repentance, perceived silence from God, family strain, faith during trials, and what the visitor should study next. The answer should be compassionate and Christ-centered when relevant, distinguish doctrine from individualized revelation or professional advice, avoid claiming to know God's private will for the visitor, and provide appropriate official study pathways without becoming repetitive or formulaic.

### L. Visitor language and presentation

Test common misspellings, casual lowercase wording, mobile input, paragraph formatting, lists, citations, source labels, Unicode normalization, and plain-text rendering. A valid informal question must not fail merely because capitalization or punctuation differs.

### M. Public API security and privacy

Test permitted and rejected origins, OPTIONS/CORS behavior, accepted methods and content types, malformed and oversized payloads, message-count and message-length bounds, client attempts to override server policy, prompt-injection attempts, response diagnostics, and secret handling. Confirm that production-safe diagnostics identify the failed stage without returning provider credentials, hidden prompts, chain-of-thought, private conversation history, or internal stack traces. Do not add invasive analytics, session replay, persistent visitor profiling, or unnecessary storage.

## Phase 4: Accuracy and answer-quality contract

For every sampled answer, score and retain evidence for:

1. **Intent fidelity**: answers the actual question first.
2. **Identity fidelity**: discusses the correct person, place, event, scripture, era, or selected record.
3. **Claim support**: each externally checkable claim is supported by the displayed source class.
4. **Source authority**: the source class matches the question category.
5. **Completeness**: enough context to understand the answer without filler.
6. **Uncertainty honesty**: unsupported details are omitted or labeled uncertain.
7. **Faith framing**: accurate, respectful, independent, and never falsely official.
8. **Safety**: high-stakes boundaries are appropriate.
9. **Rendering integrity**: no fabricated citation, broken source, unsafe HTML, corrupted punctuation, or hidden truncation.
10. **Conversation integrity**: the answer belongs to the right request and preserves or resets context correctly.

Any materially unsupported date, quotation, scripture wording, identity, doctrine, official-policy claim, or selected-biography claim is a release blocker.

## Phase 5: Performance and resilience contract

Measure end-to-end visitor-perceived latency, not only provider latency. Record at least minimum, median, p95 where sample size permits, maximum, lane, outcome, provider receipt, and failure mode.

Initial budgets to validate and refine from evidence:

- reviewed local answer: target under 250 ms after submission, hard local ceiling 1 second;
- selected local biography or card: target under 500 ms, hard local ceiling 1.5 seconds;
- externally researched answer: target median at or below 10 seconds and p95 at or below 20 seconds;
- absolute visitor wait ceiling for one remote question: 25 seconds unless a visible partial verified result is already available;
- no second full browser retry after an already bounded server attempt;
- at most one deliberate retry for a transient provider condition, and only within the total deadline;
- retry delays must honor the remaining deadline and must not stack across research, verification, expansion, and browser layers;
- a client abort must prevent stale rendering and should cancel downstream work where the platform permits;
- repeated clicks or Enter presses must not create duplicate provider calls.

If the provider cannot meet these budgets reliably, simplify the pipeline, increase reviewed-local coverage for common stable questions, use one-pass structured synthesis where safe, or return a precise source-grounded limitation. Do not trade correctness for speed, but do not treat avoidable sequential calls as necessary rigor.

Run controlled failure injection for:

- offline/network error;
- DNS/connect failure;
- Worker 4xx and 5xx;
- provider 429 with and without Retry-After;
- provider timeout;
- research success with no evidence;
- verifier rejection;
- verifier malformed JSON;
- empty response;
- expansion failure;
- browser abort;
- reset during request;
- later request completing before an earlier request;
- mixed cached asset and Worker versions.

For every respect-boundary specimen, assert zero Worker requests, zero conversation-history writes, no echo of the prohibited wording, controls restored, and the exact focusChrist rephrasing guidance shown.

Every path must terminate, restore controls, remove the spinner, avoid duplicate answers, and display either a correct answer or a specific useful limitation.

## Phase 6: Mandatory incident specimens

Retain all named specimens in `docs/all-page-ai-ask-executive-prompt.md` and add:

- Main Ask: `who is hyrum smith`
- Main Ask capitalization variant: `Who is Hyrum Smith?`
- Main Ask misspelling variant: `who was hyrum smth`
- Main Ask Church-person negative control: `Who is Will Smith?`
- Main Ask context: `Who is Hyrum Smith?` then `How old was he when he died?`
- Main Ask subject switch: Hyrum Smith context, then `Who is Abraham Lincoln?`, then `How old was he when he died?`
- Main Ask doctrine: one common reviewed question and one unreviewed but answerable doctrine question
- Main Ask scripture: one exact verse request, one interpretation question, and one fabricated citation premise
- Main Ask current: one question that must require fresh evidence
- Main Ask high-stakes: one medical or legal question that must use the safe boundary
- Main Ask respect boundary: profanity, masked profanity, explicit sexual content, derogatory religious language, derogatory cultural language, derogatory political language, and respectful near-neighbor questions
- Pioneers: reviewed topic, exact biography, partial biography, absent person, contextual follow-up, negative general-history control, provider disabled
- Church History: every visible suggestion, one unreviewed Church figure, one unreviewed event, follow-up, subject switch, reset, provider disabled
- Every non-inline page route into Ask: exact context arrives, composer owns the submission, and the return route remains correct

For Hyrum Smith specifically, prove:

1. It is classified as Latter-day Saint Church history on Main Ask.
2. Only the permitted Church-source class is shown.
3. The response does not depend on capitalization.
4. A provider failure does not wait through stacked retries.
5. The visible failure message distinguishes provider unavailability from an invalid question.
6. Follow-ups retain Hyrum Smith until a new subject or reset occurs.

Do not solve this with only a single `hyrum smith` keyword. Repair the reusable person/domain classification failure and add tests for positive, negative, misspelled, and unknown Church figures.

## Phase 7: Baseline execution before repair

Before editing runtime code:

1. Run every existing static and runtime QA command used by the site and Worker workflows.
2. Run the current live production Ask gate against the exact `main` revision.
3. Run a bounded repeated live sample across Main Ask, Pioneers, and Church History, including Hyrum Smith.
4. Capture status, response time, gateway mode, source class, policy version, answer length, and generic-fallback incidence.
5. Produce an evidence-backed root-cause record explaining the symptom, final owner, classification, provider chain, retry multiplication, failure message, missing tests, and why prior gates passed.

Do not begin a code patch until the baseline and root cause are recorded.

## Phase 8: Repair principles

1. Prefer one explicit routing contract shared between browser and Worker over duplicate keyword lists.
2. Keep server-owned authority decisions on the server. Client classification may provide a hint but must not weaken source policy.
3. Use data-driven intent and entity rules with positive and negative tests. Avoid accumulating isolated regex exceptions.
4. Preserve local-first reviewed answers and selected-source answers.
5. Reduce unnecessary sequential calls. Research, verify, expand, retry, and browser retry must share one total deadline.
6. Preserve the best verified result. A later enhancement failure may not erase it.
7. Return machine-readable diagnostics that are safe for production and useful for QA without exposing secrets or prompts.
8. Give the visitor a calm, specific, actionable limitation and an authoritative source route when a sourced answer cannot be produced.
9. Change only what the incident requires. Preserve approved page layout, artwork, navigation, conversation controls, and unrelated content.

## Phase 9: Automated release gates

The candidate must pass:

- all existing Python QA suites;
- all existing JavaScript runtime QA suites;
- Worker source-policy tests;
- new taxonomy/classification tests;
- new deadline/retry/failure-injection tests;
- machine-readable surface-manifest reconciliation;
- syntax checks;
- source-audit and reviewed-knowledge integrity checks;
- final-runtime DOM tests after production script load order;
- accessibility and interaction checks for submit, loading, answer, follow-up, reset, and sources;
- independent diff and test-evidence review.

Tests must assert behavior, network-call count, source class, latency/deadline behavior, and final rendered answer. A string existing in a file is not sufficient.

## Phase 10: Production release and live acceptance

1. Work from current `origin/main` on an isolated branch.
2. Keep unrelated work out of the incident release.
3. Commit only after local gates and independent verification pass.
4. Open one pull request and wait for required checks.
5. Merge only when checks pass.
6. Confirm the Worker and site deployment workflows succeed for the exact merged revision.
7. Confirm live page asset versions and Worker policy match the tested release.
8. Execute the real visitor journey on Main Ask, Pioneers, and Church History.
9. Run repeated remote samples within a responsible request budget and record fallback rate and latency.
10. If a material live defect remains, report `VERIFIED FAIL`, repair or roll back, and do not resume artwork.

## Phase 11: Durable learning and brain updates

Record project-specific findings in:

- Focus Current State;
- Focus Decision/Change Log;
- Focus Autonomous Run Log;
- Focus recovery prompt when boot-relevant;
- repository root-cause record, Surface Registry, test manifest, and QA documentation;
- local `MEMORY.md` and dated memory note when available.

Promote only transferable lessons to:

- Master Brain Intelligence State and Self-Improvement Log;
- Cross-Project Learning Library;
- shared website/AI QA standards when justified.

The minimum reusable lesson is:

> A source-grounded AI feature is not production-ready when it can be accurate only under ideal provider conditions. Classification coverage, total deadline ownership, bounded retries, useful degraded behavior, and repeated live latency/failure sampling are part of correctness.

Reread every updated record and reconcile it with the exact deployed truth. Never store secrets, tokens, or private provider details.

## Completion receipt

Report:

- overall evidence state;
- exact tested and deployed revisions;
- policy/cache release ID;
- complete surface count and page coverage;
- question taxonomy and specimen coverage;
- root causes and why previous QA missed them;
- architecture and behavior changed;
- source-integrity results;
- local, selected-source, and remote latency results;
- repeated live fallback/error rate;
- failure-injection results;
- accessibility and conversation results;
- independent-verifier findings and resolutions;
- production workflow and real visitor-journey results;
- Focus records updated;
- Master Brain learning promoted;
- remaining limitations and exact continuation point.

The result may be called `VERIFIED PASS` only when code, tests, source integrity, performance budgets, failure behavior, exact deployment identity, live user journeys, and brain readback agree. Otherwise report `VERIFIED FAIL`, `INCOMPLETE`, or `UNAVAILABLE / UNPROVEN` with the exact missing evidence.

## Prompt-quality review record

- Review 1 checked surface coverage, question taxonomy, source authority, latency, failure injection, release evidence, and learning. It found missing pastoral-question, public API/privacy, and no-new-cost requirements; those were added before execution.
- Review 2 reread the revised prompt against the owner incident and Master Brain rules. It confirmed explicit final-owner testing, Hyrum positive/negative/misspelling coverage, total-deadline ownership, real live sampling, exact deployment proof, and Focus-first learning.
- Review 3 followed the owner's respect-boundary addition. It found that browser-only blocking could be bypassed by direct Worker traffic, and added server enforcement, zero-network/zero-history/no-echo assertions, urgent-safety routing, and respectful near-neighbor tests.
- Review 4 reread the complete amended prompt for conflicts and omissions. It confirmed that respectful questions remain answerable, prohibited content receives the exact independent-site redirect, immediate abuse or danger receives safety guidance, and neither browser nor Worker may rely on prompt text alone as the enforcement boundary.
