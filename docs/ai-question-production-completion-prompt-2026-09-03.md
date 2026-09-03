# focusChrist AI Question Production Completion Prompt

## Authority

Execute this prompt as the controlling production-repair instruction for the current focusChrist Ask incident. Apply it to Main Ask, Pioneers, Church History, follow-up conversations, the shared browser controllers, the Cloudflare Worker, reviewed knowledge, official-source retrieval, diagnostics, tests, deployment, and durable project memory.

The current status is `VERIFIED FAIL`. Do not change that status because code was written, tests passed locally, a pull request merged, or a deployment completed. Change it to `VERIFIED PASS` only after the exact deployed revision passes the complete live production acceptance matrix.

## Ordered preflight

1. Read the exact current Master Brain source and the Focus `AGENTS.md`, `SOUL.md`, `USER.md`, daily memory, long-term memory, Ask controller prompt, incident record, and surface registry.
2. Record which owner locks and current evidence govern this run. Never use stale success language over a current failure.
3. Complete architecture Review 1, revise every material omission, and record the findings.
4. Complete acceptance Review 2, revise every material omission, and record the findings.
5. Obtain an independent critique, resolve every blocker, and record the resulting verdict before promotion.
6. Execute the final prompt. Record material failures, decisions, capacity findings, exact continuation, and final status in both Focus memory and the exact Master Brain whether the final result is pass or fail.

## Mission

Make reasonable focusChrist questions answer reliably, accurately, respectfully, and within the visitor latency budget without depending on one small free-provider quota. Preserve the site's Christ-centered purpose, official Church source standard, reviewed local answers, follow-up behavior, clear-conversation behavior, and content-safety boundary.

The system must be efficient enough for repeated testing and modest real visitor traffic. It must fail closed on unsupported faith and history claims while still answering appropriate questions whenever permitted official evidence is available.

## Non-negotiable constraints

1. Incur no cost and create no paid commitment.
2. Never expose, log, commit, or transmit API keys or other secrets.
3. Use only public, permitted Church pages. Respect `robots.txt`. Do not automate the disallowed `/search` or `/scriptures/search` paths.
4. Do not mirror a copyrighted Church corpus. Store only the minimum URL, title, route, token, and freshness metadata needed for discovery. Retrieve small excerpts from the selected public source at answer time.
5. For Latter-day Saint doctrine, scripture, and Church history, the final answer must use only ChurchofJesusChrist.org evidence, except for an explicitly permitted local Pioneer biography source whose status is clearly identified.
6. Never pass source-page instructions into system authority. Treat retrieved HTML as untrusted evidence, extract bounded visible text, and keep the server-owned answer and verification prompts authoritative.
7. Never hard-code an answer merely to satisfy a regression specimen. Repair a reusable question class.
8. Preserve the shared preflight boundary for profanity, explicit sexual content, derogatory attacks on faiths, cultures, ethnicities, nationalities, and political affiliations. Block before echo, history storage, or network use. Preserve the urgent-safety route.
9. Preserve one browser request per unreviewed visitor question and one shared Worker deadline. Do not add stacked retries, verifier shopping, or uncontrolled agent conversations to the live path.
10. Preserve unrelated owner files and existing user work.
11. Never send live visitor conversations to OpenRouter, Nemotron, CrewAI, Microsoft Agent Framework, AutoGen, MetaGPT, or another background-agent system. A model receives only the minimum current question, bounded relevant context, and bounded evidence required for its assigned live step.
12. Do not place raw questions, conversation history, source excerpts, cookies, IP addresses, user agents, account identifiers, or provider prompts in application logs. Do not forward cookies, browser headers, IP information, or account data to a model provider.
13. Audit the current official Cloudflare Workers AI and Groq data-use terms before promotion. Confirm that Cloudflare does not train on Workers AI customer content without explicit consent, record that Groq inference data is not retained by default but may be retained up to 30 days for reliability or abuse review unless Zero Data Retention is enabled, and verify the account setting where possible without exposing credentials. The visitor disclosure must plainly state that an unreviewed question and limited recent context may be sent to external AI providers. Block promotion if deployed behavior, account controls, and disclosure disagree.

## Required architecture

### 1. Reviewed local knowledge first

Keep `reviewed-ask-knowledge.js` as the first lane on every Ask surface. Reviewed answers must make zero Worker calls and remain available during every external outage. Do not promote unreviewed legacy content.

### 2. Maintainable Church-source index

Create a reproducible build tool that reads the official English Church sitemap index and its declared sitemap children. Filter only high-authority, broadly reusable source families such as scripture chapters, Gospel Topics or study guides, Church History topics, core Church History collections, and carefully selected official explanatory pages.

On every network refresh, fetch and parse the current `User-agent: *` rules from the official Church `robots.txt`. Fail closed if robots rules are unavailable, malformed, or inconsistent with the configured allowlist. Accept the sitemap index only from `sitemaps.churchofjesuschrist.org`, follow no more than ten child sitemap URLs from that same host, accept XML only, and reject redirects or child locations outside the exact sitemap host.

The generated Worker index must:

- contain discovery metadata, not copied article bodies;
- contain only HTTPS Church-owned URLs from allowed public paths;
- remove language duplicates, fragments, tracking parameters, search URLs, internal-only pages, and duplicates;
- retain normalized title or slug tokens and source-family priority;
- be deterministic and small enough for the Worker bundle;
- include the exact source sitemap revision plus SHA-256 hashes of the fetched robots file and combined sitemap inputs; never include a wall-clock generation timestamp;
- be committed so production does not need to download multi-megabyte sitemaps per question;
- be testable for minimum coverage, permitted paths, uniqueness, size, and representative doctrine, scripture, Church History, and Pioneer topics.

The normal CI gate must validate the committed generated artifact without requiring the external sitemap to be reachable. Network refresh belongs in an explicit refresh job or controlled maintenance run. Use only deterministic source revision and content-hash metadata so identical inputs produce byte-identical output. Reject `DOCTYPE` and `ENTITY` declarations, XML deeper than eight elements, and inputs with more than 1,000,000 elements. Limit robots and sitemap-index responses to 150,000 bytes, each child sitemap to 60,000,000 bytes, each network request to 45 seconds, and the exact index to ten child sitemaps. Fetch children sequentially with at least 250 ms between requests. Fail closed rather than silently truncating an over-limit child list.

Refresh the committed source index at least weekly. Run a no-cost daily robots and sitemap revision audit that compares current SHA-256 hashes with the approved embedded hashes and opens no visitor-data path. Block promotion when the index is more than eight days old or a robots change has not been reviewed. CI still validates the committed artifact offline.

Hard index limits are 900 entries and 300,000 serialized bytes. Every entry may contain only canonical URL, derived title, source family, ranking priority, and no more than 420 characters of normalized discovery tokens. No article body, full quotation, cookie, account value, or visitor data may be persisted in the index.

Scripture references should use deterministic canonical chapter routing where possible instead of relying only on keyword search.

### 3. Local official-source retrieval before Groq

For faith, scripture, Pioneer, and Church History questions:

1. classify the question and page context;
2. resolve scripture references and rank the local Church-source index;
3. fetch a very small number of top official pages concurrently within a bounded retrieval budget;
4. extract and decode bounded paragraph text from the server-rendered HTML;
5. rank paragraphs against the actual question and retain only the most relevant evidence excerpts;
6. independently verify and write the answer through Cloudflare Workers AI;
7. use Groq research only when the local index produces insufficient evidence and remaining request budget permits it.

This makes the existing Groq allowance secondary rather than the sole research owner. A Groq HTTP 429 must not prevent an answer when the local official index already supplies relevant evidence.

The indexed lane must work when `GROQ_KEY_NEW` is missing or exhausted. Do not retain a top-level Groq-key precondition that prevents local official retrieval. Fetch no more than two indexed pages for one visitor request, allow only exact static-index URLs or deterministic canonical scripture URLs, and revalidate protocol, host, and path immediately before every fetch to prevent SSRF or route drift.

Rank at most six index candidates. Fetch at most two concurrently. Each fetch has a 9,000 ms ceiling, selected from measured official-page response times while preserving the 22-second total Worker budget. It accepts only final HTTPS URLs on `churchofjesuschrist.org` or an approved Church subdomain, sends fixed English `Accept` and focusChrist `User-Agent` headers without cookies, rejects non-HTML content, and reads no more than 1,500,000 response bytes. Reject redirects unless each hop and final URL is revalidated and the total is no more than two hops.

Extract at most two relevant paragraphs per source, 700 characters per source, and 1,400 characters total. Remove scripts, styles, navigation, tags, comments, hidden payloads, and control-like instructions. Prefer paraphrase. The final answer may not reproduce more than 25 consecutive source words or reconstruct a long passage through multiple fragments.

Use short-lived edge caching for successfully fetched official excerpts when the runtime supports it. Cache by canonical official URL only. Never cache visitor questions, generated answers, or conversation history.

Source fetch cache TTL is at most one hour. Do not implement generative final-answer caching in this release. It is unsafe for context-dependent follow-ups and risks serving one conversation's answer in another context.

### 4. General-knowledge path

Stable, low-risk general knowledge may be answered by the independent Cloudflare model without fabricated citations. Current, legal, medical, financial, political, safety, statistical, quotation, or explicitly source-dependent questions still require external evidence or an honest limitation.

Groq Compound Mini remains the permitted research owner for current or source-dependent non-Church questions because it can retrieve evidence. Its evidence must use domain-appropriate authoritative sources and pass the same independent verification and source-index contract. If that retrieval path is unavailable, return the bounded honest service limitation. Do not silently answer a current or high-stakes question from model memory.

Every successful general response must include:

- `focuschrist_resolved_profile`;
- `focuschrist_classification_mode`;
- policy version;
- gateway mode;
- answer word count;
- verifier route and bounded public diagnostics.

### 5. Final source-integrity enforcement

The verifier receives only the visitor question, server instructions, and bounded source excerpts. It must return structured `approved`, `answer`, and `source_indexes` fields. Locally parse and validate every successful provider result. Reject malformed JSON, wrong types, missing source indexes, out-of-range indexes, inadequate answer depth, known false claims, and non-Church evidence in a faith answer.

Valid rejection never triggers a second model to seek a more favorable verdict. Operational failure may use one bounded fallback only when time remains.

### 6. Performance and capacity

- Browser hard ceiling: 25 seconds.
- Worker total budget: 22 seconds.
- Production p95 target for the acceptance matrix: at most 20 seconds.
- Prefer local reviewed answers, deterministic routing, concurrent bounded retrieval, and edge caching.
- Do not spend Groq quota when local official evidence is sufficient.
- Expose a bounded public retrieval-route receipt so tests can prove that indexed evidence, Groq research, or a controlled fallback actually owned the request.

An index-covered question may use zero Groq research calls, no more than two official-page fetches, one primary verifier call, and at most one operational verifier fallback or one depth-repair call, never both after a valid rejection. An index miss may use one Groq research call plus one rate-limit retry only when `Retry-After` fits the shared deadline. Cap all verifier output allowances for one visitor request at 1,800 tokens total.

Target cold-cache p95 is at most 20 seconds and warm-cache p95 is at most 12 seconds for the indexed faith/history lane. Preserve at least 20 percent of each known free daily provider allocation as an operational reserve. Record measured calls per successful question and the resulting conservative daily question capacity. If exact neuron accounting is unavailable, state that capacity as unverified rather than inventing a number.

Within the current 10,000-neuron Cloudflare Workers AI free daily allocation, the initial operational target is 50 unreviewed indexed questions per day while retaining the 20 percent reserve. Measure actual input and output tokens for the deployed model against Cloudflare's published per-model neuron conversion. If the measured 95th-percentile indexed request would make 50 daily questions exceed 8,000 neurons, reduce prompt/output budgets or lower the documented capacity before promotion. Never advertise a higher limit from a theoretical average.

Enforce maximum question length and bounded conversation turns before any provider call. Use only official-source excerpt caching and the existing one-request browser owner to reduce repeated consumption. If the currently available no-cost Cloudflare controls cannot enforce per-visitor rate limiting safely, record that as a scale blocker and do not claim unlimited or abuse-resistant capacity.
- Return useful, specific failure copy when no responsible answer can be produced. Never blame a valid visitor question for a provider failure.

## Required implementation work

1. Correct missing general-answer receipts in every successful general and identity-clarification branch.
2. Add the reproducible Church-source index builder and generated index.
3. Add deterministic scripture-reference routing.
4. Add source ranking, safe official-page fetching, bounded HTML text extraction, relevant-paragraph selection, and optional edge excerpt caching.
5. Route indexed official evidence before Groq for faith and history questions.
6. Preserve Groq as bounded secondary retrieval for index misses.
7. Increment the Worker policy version and update every exact policy assertion, registry, incident record, and production gate.
8. Add diagnostics identifying indexed retrieval, index miss, fetch failure, Groq fallback, and verifier route without leaking prompts, secrets, or raw provider errors.
9. Add a no-cost scheduled regression workflow that runs the bounded production matrix at a responsible cadence and preserves failure evidence. It must not create an uncontrolled quota drain or silently weaken the gate after failures.
10. Define a candidate-answer review path that can use regression findings to propose reviewed local answers, but never automatically promotes AI-generated doctrine or history into the reviewed registry. Human or explicitly authorized source review and integrity pinning remain required.

## Required adversarial verification

### Static and unit controls

Test at minimum:

- index contains only allowed Church HTTPS URLs;
- no `/search`, `/scriptures/search`, tracking URLs, or internal-only paths;
- deterministic build and bounded generated size;
- representative source discovery for Jesus Christ, temples, prayer, Alma 32, Hyrum Smith, Relief Society, Nauvoo exodus, handcarts, and pioneer settlement;
- unrelated and ambiguous questions do not receive a false strong match;
- weak one-token index matches do not become verified answers unless the fetched paragraphs establish relevance to the complete question;
- scripture citations resolve to the correct canonical work and chapter;
- HTML extraction removes scripts, styles, navigation, tags, entities, and page instructions;
- evidence excerpts remain bounded;
- indexed evidence bypasses a simulated Groq 429;
- indexed evidence still succeeds when no Groq key exists;
- an index miss uses at most one Groq research sequence;
- malformed or irrelevant official HTML fails closed;
- verifier malformed JSON, wrong types, invalid indexes, rejection, timeout, and rate limit remain controlled;
- general answer and identity clarification include all receipt fields;
- prohibited content is not echoed, stored, or sent externally on any Ask surface;
- respectful doctrinal, historical, interfaith, and political-neutrality questions remain answerable;
- follow-up, subject switching, reset isolation, stale-response cancellation, and final-controller ownership remain intact.
- source extraction and final answers pass a 25-consecutive-word overlap guard and do not reconstruct long source passages;
- oversized questions, excessive conversation turns, oversized HTML, non-HTML content, redirects to another host, malformed XML, unavailable robots rules, and external sitemap locations fail closed;
- provider and retrieval receipts report bounded call counts without logging visitor content.

### Local release gate

Run every existing Python, browser-runtime, Worker policy, source-integrity, scripture, safety, and syntax test. Add the index builder validation and generated-file freshness check to GitHub QA and Worker deployment.

Exercise the rendered Main Ask, Pioneer, and Church History interfaces after deployment. Submit through the visible form controls, confirm that answers and source links render, ask a follow-up, switch subjects, clear the conversation, and confirm that the next question begins without leaked context. Worker-only HTTP tests do not substitute for these visitor journeys.

### Independent critique

Before commit, assign the complete diff and test evidence to an independent verifier. Require it to search for fail-open behavior, test gaming, stale version references, false source matches, unsafe HTML handling, quota multiplication, missing receipt branches, and divergence among Main Ask, Pioneers, and Church History. Resolve every blocker and obtain an explicit verified pass.

## Production acceptance matrix

Deploy one coherent revision, wait for propagation, verify exact deployed assets and policy version, and run a paced live matrix that includes:

1. known Church person from an initially general profile;
2. stable low-risk general knowledge;
3. scripture meaning with a canonical chapter source;
4. Pioneer practice or settlement question;
5. Church History organization or event question;
6. a second question in each major faith/history class that was not used to construct the index tests;
7. follow-up continuity and competing-subject switching;
8. reset isolation;
9. prohibited-content boundary with zero prohibited-text echo;
10. respectful interfaith and political-neutrality controls;
11. simulated provider failure locally and real live repeated requests paced within published limits.
12. a small concurrent burst proving that separate requests do not share mutable question state and that the Worker remains within its deadline.

For each successful source-dependent specimen require HTTP 200, a substantive answer, official-only source hosts, `focuschrist_source_integrity_verified: true`, the exact policy version, correct resolved profile and classification mode, a recognized verifier route, no known fallback copy, and completion within 25 seconds. Require matrix p95 at or below 20 seconds.

For the canonical indexed specimens, also require the indexed retrieval receipt and expected subject concepts in both the selected official source and final answer. An official-domain URL alone is not sufficient evidence of relevance.

Require zero Groq research calls for representative index-covered questions on Main Ask, Pioneers, and Church History. Use at least twelve faith/history holdout specimens, with at least three from each of scripture, doctrine, Pioneer history, and Church History. Require at least 80 percent of them to succeed through indexed retrieval without Groq. Select holdout questions only after implementation, include unique paraphrases and near-neighbor negatives, and run time-separated cold-cache and warm-cache rounds. Self-reported verification fields are receipts, not proof; compare final claims against expected facts and the actual selected excerpts.

Run the five core question classes in three time-separated rounds with at least 60 seconds between rounds. Use a different natural paraphrase in every round so an answer cache or exact-string special case cannot manufacture reliability. Require zero core failures across all fifteen requests. Run a concurrent burst of exactly three unique, index-covered requests and require isolated state, correct receipts, and completion within the shared deadline. Do not call production passed if only an isolated question succeeds.

## Completion and learning

If any required gate fails, keep `VERIFIED FAIL`, record the exact evidence and continue repairing within the authorized scope. Do not conceal failure by weakening assertions, removing questions, raising latency limits, or preloading exact test answers.

After verified production success:

- record the exact commit, Worker version, workflow runs, policy version, matrix receipts, latency, source routes, and remaining capacity risks;
- update the Focus daily and long-term memory;
- update the exact Master Brain source with the reusable architecture lesson;
- leave a reproducible continuation for index refresh, nightly regression audits, candidate-answer review, content planning, artwork workflows, and Shorts production;
- report clearly what is proven, what remains bounded, and what would require a paid service at larger scale.

`VERIFIED PASS` means the system passed the defined tests within the currently configured free-service envelope. It does not mean unlimited capacity. Record remaining daily quotas, expected cache benefits, rate-limit behavior, and the threshold at which a paid retrieval or inference service must be evaluated.

## Prompt verification record

This prompt must be reviewed twice before execution:

1. Architecture critique: verify that the design removes the demonstrated sole-provider quota dependency, preserves source integrity, and does not create an unbounded latency or crawling path.
2. Acceptance critique: verify that the tests can detect false success, intermittent failures, test-specific hard-coding, missing receipt branches, unsafe content handling, and cross-page divergence.

Revise the prompt for every material omission found, then execute the final text without pausing for discretionary approval.

### Completed review evidence

- Review 1, architecture: removed the Groq-key precondition from the intended indexed lane, required local official retrieval before Groq, separated sitemap refresh from offline CI, added deterministic sitemap revision metadata, and bounded index size, candidate count, fetch count, response bytes, excerpt size, redirects, cache life, and provider calls.
- Review 2, acceptance: added indexed-route and provider-call receipts, zero-Groq requirements, forced-429 and missing-key cases, weak-match negatives, relevance checks, rendered all-surface journeys, repeated cold/warm rounds, holdout prompts, concurrent isolation, and an explicit no-test-gaming rule.
- Independent critique: the first reviewed draft failed because it did not load and record both brains, could still pass through Groq, underspecified robots, copyright, redirect, privacy, capacity, and anti-gaming controls, and left non-Church external research undefined. The second review found unsafe final-answer caching, incomplete XML and freshness bounds, insufficient provider disclosure controls, and nonnumeric capacity sampling. The final prompt removes answer caching, adds deterministic hashes and XML limits, makes provider-term/disclosure agreement a promotion gate, and requires twelve holdouts, fifteen time-separated core requests, and a three-request burst. A final independent verdict is required before promotion.
- Final independent verdict: `VERIFIED PASS`. No material prompt blocker remained after the four second-review defects were corrected.
- Pre-deployment implementation verdict: `VERIFIED PASS`. The independent verifier first rejected the implementation for a matrix initialization error, incomplete doctrine holdouts, optimistic fallback-capacity math, unsafe external evidence checking, short-fragment reconstruction bypasses, and generic source-instruction bypasses. After correction, it reproduced the 15-core matrix definition, exact three-per-stratum holdouts, bounded independent source checks, all 2-to-7-word ordered reconstruction regressions plus legitimate-paraphrase negatives, all instruction-injection probes, and the targeted Worker/index/safety suites without a remaining blocker. This verdict authorizes deployment testing only; final production status remains `VERIFIED FAIL` until the exact deployed revision completes the full live matrix and rendered-browser journeys.


### Execution continuation through policy .30

- Exact policy `.28` merged at `a159970c8bc788e805aface76db48b8207afbda9` and deployed as Worker version `aae79062-4621-40b2-a584-0f42c093cccf` in run `33719411666`. All 15 core requests returned complete HTTP 200 answers with required receipts and zero Groq research for indexed questions. The gate failed because grace selected broad Jesus Christ sources instead of a grace-specific official URL.
- Exact policy `.29` merged at `9926fad955d2a317c853a9f4d7e01f2b14a91251` and deployed as Worker version `a02b3e67-b894-4a95-9abe-490a1e45cdb4` in run `33720321990`. Grace routing passed and 14 other core requests succeeded. The first cold Atonement request failed closed after the 70B primary produced no usable result and the Groq fallback did not recover.
- Candidate `.30` addresses the repeatedly ineffective fallback without changing an acceptance threshold. It uses the same Cloudflare binding with the active, explicitly priced 8B FP8 fast model for one operational fallback, omits undocumented provider-side JSON enforcement, applies the strict local verdict schema and all final guards, forbids a third verifier call, and preserves the 22-second Worker, 25-second visitor, and 20-second p95 ceilings.
- Every Cloudflare attempt without returned usage, including a logically timed-out call that may continue provider-side, adds a conservative 1,000-neuron allowance. The capacity gate adds that allowance to measured usage. The same accounting is retained when a required depth, paraphrase, or reconsideration call fails closed.
- Final production status remains `VERIFIED FAIL` until the exact `.30` revision passes every matrix stage and rendered browser journey.
