# All-Page Ask Repair Root Cause — 2026-09-01

## Status

Overall release state: `VERIFIED PASS`.

The owner-reproduced handcart behavior is `VERIFIED PASS` in the local final-owner runtime and on the fully loaded production Pioneer page: it returns 1856 from reviewed local knowledge with the official Handcart Companies source. Automated runtime proof confirms this reviewed route makes zero Worker calls.

## Supplemental final closure — policy 2026-09-01.15

The earlier policy `2026-09-01.9` receipt remains historical evidence, but it was superseded after the owner found additional main Ask and card/follow-up failures.

Additional verified root causes:

1. A final browser attribution guard interpreted the person name “Abraham Lincoln” as a Book of Abraham source claim and replaced a correct server answer with a Gospel Library limitation.
2. The stable low-risk lane answered a chained `What time?` follow-up with a fluent but false 10:00 p.m. death time. The initial question and first follow-up passing did not prove the conversation chain.
3. Competing-person detection depended on Title Case and then on two-word names. Lowercase names, surnames, and acronyms could inherit Joseph Smith context.
4. Repository-local and provider-response tests did not prove the final postprocessed answer or canonical production cache state.
5. A cache-busted production probe could see fresh origin bytes while canonical visitor cache keys or transitive scripts remained stale.

Final systemic repair:

- Added the reviewed, integrity-pinned `general-abraham-lincoln-death-1865` entry with Library of Congress and National Park Service sources.
- Kept Lincoln’s main question, pronoun follow-up, and chained ellipsis on the reviewed zero-Worker lane with the exact 7:22 a.m. time.
- Made explicit competing-subject detection case-insensitive and grammar-anchored for full names, lowercase names, surnames, and acronyms while preserving valid contextual modifiers.
- Added adversarial registry and full-controller tests for source-title/person collisions, conjunctions, identity switches, reset isolation, and final rendered output.
- Added a latest-only post-deploy gate that recursively discovers the Ask dependency graph, requires exact bytes through canonical visitor cache keys and separate origin probes, repeats after a stability interval, and executes the stable canonical registry.

Final evidence:

- PR `#56` CI run `33474211249`: success.
- Feature merge `f58b232ed9386361285fafd44e5fea8390fe1868`.
- Post-feature Site QA `33474356949`, Worker `33474356964`, and Pages `33474356962`: success.
- PR `#57` CI run `33475167356`: success.
- Verified Ask runtime / production-gate merge commit `baaa15a24e5b35101bde8a5046b86295310b50bb`.
- Post-gate Pages run `33475248240`: success.
- Post-gate Site QA/live production run `33475248219`: success; output recorded `LIVE PRODUCTION ASK QA PASS`.
- Independent adversarial verdicts for both releases: `VERIFIED PASS`.

## Production completion receipt

- Merged pull request: `#47`
- Production merge commit: `31c7ac9baf9ee9794b802d30c6cd66cff3bf31c8`
- Source-integrity policy: `2026-09-01.9`
- Browser cache version: `20260901-9`
- GitHub release gates: pull-request `focusChrist Site QA` run 212 and post-merge run 213 — success
- Live Main Ask: versioned registry/controller assets loaded; reviewed sky answer and source passed; a general family-business question returned a substantive answer through the general-knowledge lane; New Question restored controls and cleared the visible conversation.
- Live Pioneers: exact owner question and handcart paraphrase returned 1856 with the official Handcart Companies source; a different Pioneer-history question returned a substantive researched answer; New Question restored controls and welcome state.
- Live Church History: First Vision and Church organization questions returned reviewed answers with official sources and appropriate historical qualification; New Question restored controls and cleared the visible conversation.
- Live Worker probe: policy `2026-09-01.9` returned a complete general-knowledge answer through mode `general-ai-low-risk`.
- Application console: no application errors observed; the expected source-integrity warning occurred only for an adversarial handcart-racing negative control, which correctly did not receive the 1856 Pioneer fact.
- Rollback target: `8309d240f01d5fe8f628f1e9ab53451cad21f527`.

## Owner-reproduced failure

Question: `What year did the handcarts begin?`

Expected: a direct 1856 answer from reviewed Pioneer/official Church History knowledge.

Observed before repair: a limitation stating that the answer could not be verified well enough.

## Evidence-backed causes

1. `VERIFIED PASS` — `pioneer-experience.js` was the final owner of Pioneer free-form submission. Its prior order was exact-person search followed directly by `requestPioneerAI`; it had no reviewed page-fact lookup.
2. `VERIFIED PASS` — `pioneers.html` already displayed handcart chronology, including the 1856–1860 period, but that display content was reachable only through card/disclosure behavior, not free-form Ask.
3. `VERIFIED PASS` — the Pioneer legacy Q&A database contained a handcart answer but was correctly quarantined because it had not been individually reviewed and included mixed-quality sources. The free-form controller therefore could not safely use it.
4. `VERIFIED PASS` — when remote retrieval or verification was unavailable, the browser source-integrity guard correctly rejected an unverified source-dependent answer. Because no reviewed local lane ran first, a valid known fact became a non-answer.
5. `VERIFIED PASS` — Church History had the same failure class: its composer showed a loading state and invoked remote study intelligence before checking reviewed page facts.
6. `VERIFIED PASS` — the main Ask, Pioneer, and Church History pages had different final controllers and separate local knowledge locations. A global source-integrity change could therefore alter all pages while page-specific knowledge remained inaccessible.
7. `VERIFIED PASS` — earlier QA covered main Ask source lanes, exact Pioneer biographies, and reviewed Pioneer cards, but did not run a final-owner free-form Pioneer specimen for an obvious page fact. Static checks verified code markers and order inside selected flows, not the missing route.
8. `VERIFIED PASS` — the earlier production acceptance list tested one general Ask question, selected biographies, no-match research, and cards. It did not include representative reviewed page-fact questions or negative intent controls on every Ask surface. That allowed “deployed” to be reported as “fixed.”

## Systemic repair

- Added one shared, data-driven reviewed knowledge registry used before Worker calls by the free-form, topic, and Church History question controllers. Selected-person and Journey/Trail card lanes keep their more specific reviewed page source first, with Worker research only as an optional enhancement.
- Added individually reviewed general, Joseph Smith, Pioneer, and Church History facts with page profiles, positive paraphrases, negative controls, exact authoritative sources, review date, and integrity key.
- Pinned every registry entry and source list in `answer-audit.json` with SHA-256.
- Preserved the quarantine of 491 unreviewed main Ask entries and every Pioneer legacy entry.
- Added final-owner runtime tests proving the handcart and Church History local routes make zero Worker calls.
- Added negative tests for handcart racing, shopping carts, modern handcarts, biblical Exodus, Joseph Stalin/Joseph of Egypt, unrelated First Vision media, general design/color, and non-Latter-day Saint church organization.
- Added request-ownership invalidation so reset or a newer interaction cannot be overwritten by a stale response.
- Moved conversation-history commits behind current-request ownership checks, so delayed free-form or selected-person results cannot silently repopulate state after reset.
- Replaced the main Ask label `SCRIPTURAL SOURCES` with the domain-neutral `Sources`, allowing authoritative general sources to be presented accurately.
- Synchronized policy, Worker, asset, ledger, and cache versions at `2026-09-01.9` / `20260901-9`.

## Permanent prevention controls

1. `tools/reviewed_ask_knowledge_qa.js` executes every positive, negative, profile-boundary, source, and integrity-hash test.
2. `tools/pioneer_ask_runtime_qa.js` invokes the actual Pioneer final owners and proves the owner's question and a reviewed topic return locally, exact-person selection stays local-first, Journey/Trail cards survive provider failure, and reset restores controls while cancelling stale output.
3. `tools/church_history_ask_runtime_qa.js` invokes the actual Church History final owner and proves reviewed facts bypass the Worker while a negative control enters research.
4. `tools/study_intelligence_v3_runtime_qa.js` invokes the actual main Ask final owner and proves reviewed general and faith facts bypass the Worker while unrelated questions retain their correct external lane.
5. Both CI and production deployment workflows run these controls before release.
6. `docs/ask-surface-registry.md` makes missing or duplicate final runtime ownership a release blocker.
7. Production acceptance must exercise all three fully loaded pages on the exact deployed revision before overall status becomes `VERIFIED PASS`.

## Learning record

Observation: stronger source-integrity controls exposed reviewed-knowledge routing gaps as user-visible refusals.

Interpretation: source verification and answer usefulness are separate concerns; both must be explicitly routed.

Hypothesis tested: a shared reviewed-local first lane can preserve source integrity while restoring direct answers.

Action: introduced the shared registry, final-owner integration, integrity ledger, negative controls, and zero-Worker runtime tests.

Local outcome: all repository suites and new final-owner tests pass, including an independent current-tree verification after adversarial false-positive, stale-state, selected-person, route-coverage, cache, and ledger review.

Promoted rule: reviewed knowledge already owned by focusChrist must answer before generative AI and must remain available when the provider, retrieval, verifier, or network is unavailable. Release proof must cover representative positive, negative, failure-state, and fully loaded live journeys on every registered Ask surface.
