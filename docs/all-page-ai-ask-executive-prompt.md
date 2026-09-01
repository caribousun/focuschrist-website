# focusChrist All-Page AI Ask Executive Reliability Prompt

## Authority and use

This is the binding controller prompt for diagnosing, changing, testing, releasing, and learning from every focusChrist question-and-answer experience. It applies to the main Ask page, Pioneer Ask, Church History Ask, page-specific question tools, topic buttons, biography and card interactions, follow-up conversations, shared study-intelligence code, browser overrides, Workers, source routers, caches, and every fallback that can own the final user-visible answer.

Use this prompt in full before any future AI Ask change. Do not narrow its scope to the latest example. The reported question is a regression specimen, not the boundary of the work.

The Master Brain is the controller. Execute through this chain:

`Owner instruction -> Master Brain rules -> Focus project controls -> repository and live runtime -> evidence -> learning -> Focus state update -> reusable learning promoted to Master Brain`

Keep directive authority separate from factual evidence.

For objectives, scope, locks, approvals, and acceptable risk, use this directive hierarchy:

1. latest explicit owner instruction;
2. Master Brain governance and source-integrity rules;
3. current Focus operating controls;
4. older plans, memories, prompts, or strategy notes.

For factual claims about what is deployed, live, failing, passing, or complete, use this evidence hierarchy:

1. current verified live/runtime evidence;
2. evidence from the exact tested revision and environment;
3. current project records;
4. older plans, memories, prompts, or status claims.

Runtime evidence can disprove a stale status record, but it can never override an owner instruction or lock.

Repair stale project records in the same run. Never use an older statement of success to overrule a current reproduced failure.

## Current controlling status

The all-page AI Ask issue is **VERIFIED FAIL**.

The owner reproduced failures on the main Ask, Pioneer, and Church History pages:

> Do we know the time he died

> Handcart Companies

> Who is Jesus Christ, and why is He central to Latter-day Saint belief?

> How does the Church explain Joseph Smith and plural marriage?

The system discarded the Joseph Smith subject before local matching, failed to recognize visible topic/card prompts as reviewed inputs, and allowed source-integrity fallback language to replace useful answers. Therefore:

- the previous implementation was deployed but was not proven working across its promised scope;
- the prior completion claim was premature;
- the prior prompt and test set were insufficient;
- this failure class must be repaired systematically, not with a one-question exception;
- the reproduced defect remains `VERIFIED FAIL` until that behavior is corrected and directly retested;
- after the reproduced behavior passes, the overall release remains `INCOMPLETE` while any other required gate is unproven;
- only full completion-gate convergence may advance the overall status to `VERIFIED PASS`.

## Mission

Build one reliable Ask system that answers appropriate questions directly, uses the correct knowledge lane for each page and intent, protects source integrity, remains useful when providers fail, preserves page-specific intelligence, and grows through measured learning.

The owner outcome is simple:

> A visitor asks a reasonable question on any focusChrist page and receives the best supported answer the site can provide, without an irrelevant refusal, a fabricated claim, an unnecessary provider dependency, or loss of the page's own reviewed knowledge.

Guardrails must constrain unsupported claims. They must not disable the system's ability to answer appropriate questions.

## Truth and status language

Every claim in the execution report must use one of these states:

- `VERIFIED PASS` — directly tested at the relevant layer with retained evidence.
- `VERIFIED FAIL` — directly tested and failed.
- `UNAVAILABLE / UNPROVEN` — the required check could not be completed or evidence is missing.
- `HYPOTHESIS` — a plausible explanation that has not yet been proven.

Use `INCOMPLETE` only as the overall program or release state when the known reproduced defect has been repaired at its tested layer but one or more required completion gates remain unproven. If a required gate directly fails, overall status returns to `VERIFIED FAIL`. If all gates pass, overall status becomes `VERIFIED PASS`.

Never collapse these different states:

- code written;
- test added;
- local test passed;
- committed;
- pushed;
- deployed;
- live asset observed;
- live feature working through the real user journey.

“Fixed,” “complete,” and “working” are prohibited until all required live acceptance gates pass on the exact deployed revision. If one gate is missing, report `INCOMPLETE` with the exact missing evidence.

## Non-negotiable user experience contract

For every Ask surface, select the answer lane before deciding whether to answer, retrieve, research, clarify, or limit.

Use this order:

1. **Reviewed local answer** — answer immediately from page-owned or project-owned reviewed knowledge. Do not call the Worker to rediscover a fact already owned by the page.
2. **Selected project source** — when the visitor selected a biography, document, card, or record, answer from that exact source and preserve its identity and boundaries.
3. **Authoritative retrieval plus AI synthesis** — retrieve the correct source class, then summarize only supported claims.
4. **Stable low-risk general knowledge** — on the broad Ask page, a separately controlled general-knowledge lane may answer ordinary stable questions when retrieval has no useful excerpts.
5. **Clarification** — when identity, subject, era, or requested meaning is materially ambiguous, ask a concise relevant question.
6. **Transparent limitation** — fail closed only for the unsupported portion. Preserve valid local content and offer a relevant next action or source route.

Additional rules:

1. General questions use reliable general sources or the controlled low-risk general lane. Do not force them into the Gospel Library.
2. Scripture, doctrine, Church teaching, and Latter-day Saint history use official Church sources as the primary external authority.
3. Current, medical, legal, financial, safety, statistical, quotation, and other high-stakes or time-sensitive questions require fresh external evidence and may not use the low-risk consensus lane.
4. Reviewed page facts remain available when remote AI, retrieval, verification, or the network fails.
5. No model output may invent or silently alter a scripture, quotation, person, date, event, attribution, source, journal entry, or doctrinal interpretation.
6. No browser code may relabel unverified model output as verified. Source policy and receipts are server-owned.
7. A valid answer must not be replaced later by a slower failure, stale request, or unrelated response.
8. Use safe text rendering. Preserve keyboard access, focus, visible loading and error states, screen-reader labels, source visibility, reset behavior, and mobile usability.
9. Unless a visitor explicitly asks for brevity, give a complete and useful answer. A simple fact must include the direct answer and enough context to understand it; a nuanced question normally requires two to five short paragraphs. Never reduce a sincere question to one or two words. Enforce this at the final gateway: general researched answers require at least 45 words and two complete sentences; faith or Church-history research requires at least 70 words and three complete sentences; selected Pioneer biographies require at least 90 words, three sentences, and two paragraphs. If an otherwise verified draft is shorter, expand it once from the same evidence and reject it if it still fails. Do not add padding or unsupported facts.
10. When retrieval is unavailable or rate-limited, stable low-risk general knowledge must still use the same 45-word/two-sentence final contract. If the low-risk checker returns a short correct fact, expand it once through that same checker before falling back. Current, high-stakes, specialized, quotation, citation, or source-specific requests must never be downgraded into this no-retrieval lane.
10. Every visible starter, topic button, suggestion, and question card is an executable product promise. Its exact submitted text must be inventoried and tested through the final runtime owner.

## Required architecture audit

Before changing code, inventory the real final runtime. Do not assume the newest-looking file owns the answer.

Create and maintain an Ask Surface Registry with one row for every user-visible question path. Each row must identify:

- page and public URL;
- input, topic, card, selection, or follow-up trigger;
- page profile and intended domain;
- local reviewed knowledge provider;
- selected-source provider, if any;
- external source class;
- client entry point;
- every script that can install or replace the handler;
- final runtime owner after all deferred scripts and inline code execute;
- Worker/API route;
- cache and version owner;
- provider-failure behavior;
- automated test owner;
- live acceptance specimen.

The inventory must include at least:

- main Ask composer, topic controls, follow-ups, reset, sources, and suggestions;
- Pioneer free-form composer and topic controls;
- Pioneer exact-person, partial-person, choice-button, random-person, biography follow-up, Journey, Trail, and handcart-card routes;
- Church History composer, topic controls, context, follow-ups, and reset;
- any question interface added to other pages;
- shared study-intelligence versions, inline legacy handlers, page-specific experience scripts, Worker routes, and service/cache layers that can change the final answer.

Search for duplicate handlers, late global overrides, inline legacy databases, multiple versions of the same runtime, page-global function replacement, mismatched cache versions, and code paths that bypass source policy.

### Mandatory executable question discovery

Do not rely on a hand-written sample list. Before implementation and again before release, derive the question contract from the current repository and fail on any unaccounted route.

1. Parse every production HTML page for question-bearing attributes and controls, including `data-question`, `data-ask-starter`, `data-ask-topic`, `data-history-question`, `data-topic`, `data-focus-expand`, form submit values, button text transformed into a question, links that open Ask, and inline click handlers.
2. Search JavaScript for all submission and rendering owners, including `sendMessage`, `askAI`, `focusChristStudyAskV3`, `focusChristHistoryAsk`, `askTopic`, `requestPioneerAI`, reviewed-knowledge matchers, `addMessage`, deferred script loaders, and assignments that replace page-global functions.
3. Produce a machine-readable manifest containing the exact submitted text, source file and control, page profile, final runtime owner, expected answer lane, test owner, and minimum acceptance assertion.
4. Compare the manifest with the reviewed registry and declared external-source routes. A visible prompt with no tested answer contract is an orphan and fails the release.
5. Assert count equality between discovered controls and tested controls. Adding, renaming, or removing a visible card must cause QA to fail until its contract and test are deliberately updated.
6. Invoke the final controller for every discovered exact string, then exercise the real DOM control after all production scripts load. A source-file string match, a direct helper call, or a visibly correct label is not sufficient proof.
7. Run the discovered controls under normal, Worker-disabled, verifier-rejected, timeout, empty-response, and stale-response conditions as appropriate to their declared lane.
8. Reject blank answers and known generic non-answer patterns, including “I cannot verify the specific source claim,” “Please confirm the subject,” “I could not complete that general answer,” and equivalent language when the question has a supported reviewed or authoritative route.
9. Enforce answer substance: direct answer first; ordinary fact plus useful context; nuanced questions normally at least 70 words unless the reviewed contract explicitly justifies a shorter response; visible supporting sources for Church/history claims.
10. Retain the manifest and per-control results as release evidence. Never ask the owner to act as the discovery system.

## Root-cause requirement

Do not begin with a patch. First produce an evidence-backed root-cause record that answers:

1. What failed for the exact handcart question?
2. Which final runtime handler owned that submission?
3. Why did it ignore a reviewed fact already present on the page?
4. Why did provider or verifier unavailability become a user-visible non-answer?
5. Why did the earlier implementation and prompt not cover this route?
6. Why did earlier QA permit a “fixed” claim?
7. Which other Ask surfaces share the same failure class?
8. What permanent control will detect this class before release?

For each causal statement, cite a `VERIFIED PASS` evidence check that proves it or label the statement `HYPOTHESIS`. Turn every evidence-backed systemic cause into a test, invariant, or release gate.

## Implementation requirements

### 1. One explicit page-profile contract

Define server-controlled profiles for broad Ask, Pioneer Ask, Church History Ask, and future domain pages. A profile specifies permitted local providers, external source class, conversation rules, and safe fallback behavior. Do not accept arbitrary client instructions as source-policy authority.

### 2. One reviewed local knowledge contract

Create a data-driven, auditable registry for reviewed page facts and intent matchers. Each entry must contain:

- stable ID;
- page/profile scope;
- supported question intents and paraphrase tests;
- explicit negative-intent tests;
- concise reviewed answer;
- exact source title and URL;
- claim-to-source evidence note;
- reviewer/status metadata;
- content hash or other integrity pin;
- review or freshness policy where applicable.

Do not revive the legacy unreviewed Q&A bank wholesale. It stays quarantined by default. Promote an entry only after claim-by-claim review and ledger pinning.

Do not implement a growing pile of one-off string checks. Use normalized, data-driven intent matching with required positive and negative controls. A new owner-reported example must strengthen a reusable intent class and its test family.

### 3. Local-first routing

Every submission must follow one inspectable decision function:

`surface/profile -> selected context -> reviewed local match -> ambiguity -> external source lane -> verified answer or bounded limitation`

For a reviewed local match:

- render immediately;
- attach its reviewed source;
- record the local answer mode;
- make zero Worker requests;
- remain correct when the Worker is disabled;
- allow optional background enhancement only when it cannot delay, erase, or contradict the reviewed answer.

### 4. Selected-source identity safety

For selected people, biographies, cards, documents, or records:

- bind the answer to the exact selected identity;
- keep biography boundaries intact across continuation pages;
- prevent adjacent-person leakage;
- require clarification for identity collisions;
- never silently substitute a similarly named person;
- retain source attribution as the source attributes it.

### 5. External research lanes

When no reviewed local answer exists:

- broad ordinary questions use reliable general retrieval or the controlled stable-general lane;
- Church, scripture, doctrine, and Pioneer questions use official Church evidence first;
- selected local records remain primary for claims about their contents;
- unsupported claims are removed rather than softened into apparent fact;
- the returned receipt identifies source class, policy version, evidence, and verification state;
- a limitation is specific to the missing evidence and never directs an unrelated general question to the Gospel Library.

### 6. Conversation and request safety

- Preserve bounded context for real follow-up questions.
- Resolve pronouns and bounded short elliptical follow-ups before profile classification, local matching, retrieval, or source-lane selection. Reviewed subjects use declared anchors and cues; unreviewed subjects must make the immediately preceding user question explicit to research. A short question that introduces a named subject must never inherit a different prior identity.
- A resolved follow-up must retain the visitor's original wording in history and expose an inspectable context-resolution receipt.
- Persist that receipt with the user turn so chained follow-ups remain bound. Inheritance may consider only the most recent prior user turn; it must never skip backward past an intervening subject.
- A generic context receipt must retain the root subject question through multiple follow-ups; repeating only the latest pronoun-based wording is not sufficient.
- Resolve a generic follow-up into an explicit research query, but do not rematch the augmented query against the prior reviewed answer. The original wording already had its local-match opportunity; the contextual query is for classification and research, not for accidentally replaying the antecedent answer.
- A named competing person in the current question overrides inherited context. Do not infer a competing person merely from a multiword place or title such as `Carthage Jail`.
- Reset must clear both visible and hidden conversation state.
- Abort or ignore stale requests after reset, navigation, selection change, or a newer submission.
- Prevent duplicate requests from repeated clicks or Enter presses.
- A late response may update only the interaction that created it.
- Never leak Pioneer context into broad Ask or one person's identity into another person's answer.

### 7. Version and cache control

- Use one release identifier across page assets, shared runtime, source router, Worker policy, integrity ledger, and tests.
- Prove the browser loaded the exact tested assets.
- Prove the live Worker reports the exact tested policy.
- Treat mixed-version behavior as a release failure.

## Mandatory regression matrix

Build a test matrix across every registered Ask surface and these answer modes:

- reviewed local answer;
- selected local source;
- authoritative retrieved answer;
- stable low-risk general answer;
- ambiguity/clarification;
- unsupported claim rejection;
- provider unavailable;
- verifier rejects evidence;
- timeout/empty response;
- stale request or reset;
- cached prior release versus current release.

At minimum, retain these named specimens.

### Main Ask specimens

- `Why is the sky blue?` — direct ordinary general answer; no Gospel Library fallback.
- every exact `data-ask-starter` question in `ask.html` — substantive reviewed answer, authoritative sources, and zero Worker requests.
- `Who is Jesus Christ, and why is He central to Latter-day Saint belief?` — complete reviewed answer, not a verification refusal.
- `What makes a family business successful?` — useful general answer using the general lane.
- `What year was Joseph Smith killed?` — supported answer identifying June 27, 1844, with official Church history evidence.
- after the Joseph Smith date question, `Do we know the time he died` — resolve Joseph Smith before routing and answer about or shortly after 5:00 p.m.; after reset, the same wording must not inherit Joseph Smith.
- after changing the subject to `What date did Abraham Lincoln die?`, both `Do we know the time he died?` and chained `What time?` — resolve Lincoln for general research, never Joseph Smith and never a generic completion failure.
- after the Joseph Smith date question, `How old was he?`, `Why was he in Carthage Jail?`, `Who was with him?`, and `Where did he live?` — use Joseph Smith as immediate context and answer the specific intent from a reviewed contextual variant when one exists; otherwise research it. Never replay a death-only answer or depend on the Worker for a fact the reviewed registry already owns.
- after Joseph Smith context, `When did he die—Abraham Lincoln?` and `Do we know what time he died, Abraham Lincoln?` — treat Abraham Lincoln as the explicit current subject and never return Joseph Smith's answer.
- `What year was Joseph Stalin killed?` — must not be captured by the Joseph Smith intent.
- a supported scripture/doctrine question — official Church evidence.
- a fabricated or miscited scripture claim — blocked or corrected with evidence.
- a current/high-stakes question — cannot enter stable low-risk consensus.

### Pioneer specimens

- `What year did the handcarts begin?` — **1856**, reviewed local/official answer, source visible, zero Worker requests.
- visible topic `Handcart Companies` — substantive reviewed 1856-1860 explanation, source visible, zero Worker requests.
- paraphrases such as `When did handcart travel start?` and `What year did the handcart companies begin?` — same reviewed intent.
- negative controls such as `When did handcart racing begin?`, `When did shopping carts begin?`, and a clearly modern handcart question — must not match the Pioneer reviewed fact.
- `Tell me about the pioneer exodus` — answer from reviewed Pioneer/Church-history context when present; zero Worker requests for the reviewed portion.
- `Tell me about the Exodus in the Bible` — must not be captured by the Pioneer exodus intent.
- exact indexed Pioneer name — immediate exact local biography.
- partial name with multiple matches — accessible choice buttons.
- absent person — enters the authoritative research lane.
- similarly named or ambiguous people — clarification, never identity substitution.
- Journey, Trail, and handcart card — immediate reviewed content.
- follow-up grounded in a selected biography — retains exact identity and source boundaries.
- Worker disabled — all reviewed page facts, biographies, and cards still answer.

### Church History specimens

- extract and test every exact `data-history-question` value from `church-history.html`; the discovered count and tested count must be equal.
- `What do the different First Vision accounts say, and how does the Church explain them?` — substantive reviewed answer with official sources and zero Worker requests.
- `How does the Church describe the translation of the Book of Mormon and the use of seer stones?` — substantive reviewed answer with official sources and zero Worker requests.
- `What is known about the restoration of the Aaronic and Melchizedek Priesthood?` — substantive reviewed answer with official sources and zero Worker requests.
- `What happened with the Kirtland Safety Society, and why did it fail?` — substantive reviewed answer with official sources and zero Worker requests.
- `How does the Church explain Joseph Smith and plural marriage?` — substantive reviewed answer with official sources and zero Worker requests; never the generic verification refusal.
- `What does the Church teach about the Mountain Meadows Massacre?` — substantive reviewed answer with official sources and zero Worker requests.
- `What happened to the Willie and Martin handcart companies?` — substantive reviewed answer with official sources and zero Worker requests.
- `How did observance of the Word of Wisdom develop historically?` — substantive reviewed answer with official sources and zero Worker requests.
- `How did the Church become a global church during the twentieth century?` — substantive reviewed answer with official sources and zero Worker requests.
- `Where can I study women in Latter-day Saint Church history?` — substantive reviewed answer and official study routes with zero Worker requests.
- a question requiring external Church history research — official Church sources.
- a biblical or general term sharing a historical keyword — correct intent separation.
- a follow-up, reset, ambiguity case, and provider-unavailable case.

No test may pass merely by finding a string in a file. Tests must invoke the final runtime decision owner or exercise the actual DOM flow after all production scripts load.

## Verification program

### Static and integrity verification

- Ask Surface Registry is complete against repository search results.
- Reviewed knowledge registry and audit ledger agree.
- Every reviewed claim maps to exact supporting evidence.
- All unreviewed legacy entries remain quarantined.
- Positive and negative intent tests exist for every promoted local answer.
- Policy, cache, and asset versions agree.
- No later script or inline handler can bypass the tested controller.

### Runtime and failure injection

- Run final-owner browser tests with all scripts loaded in production order.
- Count Worker requests and prove local answers make zero requests.
- Stub timeout, rate limit, empty output, verifier rejection, malformed payload, and offline conditions.
- Disable the Worker entirely and confirm reviewed local routes remain useful.
- Test delayed responses after reset, new question, selection change, and navigation.
- Test source rendering, safe text rendering, loading transitions, and response replacement rules.

### User-flow QA

Test real typing, Enter submission, button submission, topic selection, follow-up, reset, source opening, and choice selection. Verify:

- desktop and mobile layouts;
- keyboard-only operation;
- visible focus;
- screen-reader names and state;
- no trapped focus or inaccessible custom control;
- no console error, unhandled promise rejection, endless spinner, blank answer, duplicate answer, or stale overwrite;
- useful, page-appropriate language in success and limitation states.

### Production acceptance

On `https://focuschrist.com`, against the exact deployed revision:

1. Confirm live page assets and Worker policy match the tested release ID.
2. Perform every named main Ask specimen.
3. Perform every named Pioneer specimen, beginning with the owner's exact handcart question.
4. Perform the required Church History specimens.
5. Repeat reviewed-local specimens with the Worker unavailable or safely simulated as unavailable.
6. Simulate a Worker `429 rate_limit_exceeded` condition and prove that every reviewed starter, visible card, and reviewed contextual variant still answers completely without the generic source-verification refusal.
7. Confirm sources support the displayed claims.
8. Confirm browser behavior after all scripts, caches, and service layers are fully active.
9. Retain the commit, deployment identity, policy version, timestamps, test output, network-call evidence, and screenshots or equivalent browser evidence.

A direct API response, source-file inspection, or local unit test is not production acceptance.

## Independent verification

Before commit or release, an independent verifier must inspect the diff, root-cause record, source ledger, runtime ownership, regression matrix, test output, and live acceptance evidence. Resolve every material finding. If independent verification is unavailable, status is `UNAVAILABLE / UNPROVEN`, not complete.

## Release rules

- Work from the current production baseline in an isolated branch.
- Preserve the verified production version until the candidate passes local and preview QA.
- Do not mix unrelated changes into the Ask release.
- Do not deploy if source integrity, runtime ownership, cache consistency, or named regression coverage fails.
- After deployment, test the real production journey again. Roll back or repair immediately on a material regression.
- Never ask the owner to rediscover a defect that automated or production acceptance should catch.

## Learning and intelligence growth

Close every discovered failure through this learning kernel:

`observation -> interpretation -> hypothesis -> action -> outcome -> promoted or retired rule`

For each owner-caught defect:

1. repair the immediate user flow;
2. identify the reusable failure class;
3. add a durable detection control;
4. verify that control on the next release;
5. update Focus Current State, recovery instructions, run log, source-integrity rules, and test inventory;
6. promote the reusable lesson to the Master Brain;
7. reread the updated controls and confirm they agree with live truth.

The durable invariant from this incident is:

> Reviewed knowledge already owned by a page must answer immediately and must never wait for, depend on, or be erased by generative AI. A release is not working until representative positive, negative, failure-state, and live user-journey tests pass across every registered Ask surface.

## Required execution order

1. Load Master Brain and current Focus controls.
2. Reconcile project records with current production evidence.
3. Mark the current issue `VERIFIED FAIL`.
4. Build the Ask Surface Registry and find the final runtime owner for every route.
5. Produce the root-cause record, including why prior QA failed.
6. Define the shared routing and reviewed-knowledge contracts.
7. Write the complete positive, negative, failure-injection, and final-owner tests before or alongside the repair.
8. Implement the smallest maintainable systemic change that satisfies the architecture; reject fragile one-question patches and duplicate policy logic.
9. Run static, integrity, runtime, accessibility, and failure-injection checks.
10. Obtain independent verification and resolve findings.
11. Deploy the exact tested revision through the authorized release process.
12. Run full production acceptance on every registered surface.
13. Measure remaining failure patterns and limitations.
14. Update Focus and Master Brain learning records.
15. Issue the completion receipt only if every gate converges.

## Completion receipt

The final report must contain:

- overall status: `VERIFIED PASS`, `VERIFIED FAIL`, `UNAVAILABLE / UNPROVEN`, or `INCOMPLETE`;
- exact root causes and evidence;
- Ask Surface Registry coverage summary;
- architecture changed and why it prevents recurrence;
- reviewed knowledge entries added or changed, with source evidence;
- automated tests and named specimens passed/failed;
- failure-injection results;
- independent verifier findings and resolutions;
- tested commit, deployed commit, release/policy/cache ID, and proof they match;
- live production browser results for main Ask, Pioneer, and Church History;
- known limitations and exact next actions;
- Focus state/recovery/run-log updates;
- reusable learning promoted to Master Brain;
- exact continuation point if any item remains open.

Do not issue this receipt as `VERIFIED PASS` unless code, tests, source integrity, final runtime ownership, deployment identity, fully loaded live user journeys, failure-state behavior, documentation, and learning readback all agree.
