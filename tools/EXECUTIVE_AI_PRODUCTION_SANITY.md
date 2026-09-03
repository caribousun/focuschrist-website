# focusChrist AI Executive Production Sanity Script

## Mission

Close the focusChrist Ask AI system to a verified production state. Do not optimize for passing a test. Optimize for a visitor receiving a direct, accurate, source-grounded answer whose evidence remains independently retrievable from the source shown to the visitor.

## Non-negotiable production contract

1. Do not weaken, remove, skip, or special-case a release gate merely to make CI green.
2. Faith, scripture, Church doctrine, and Church-history answers must remain grounded in ChurchofJesusChrist.org evidence.
3. Never invent scripture wording, quotations, dates, people, statistics, historical claims, official teachings, sources, or success status.
4. Reviewed local answers remain first choice when applicable.
5. Unreviewed faith answers remain fail-closed if authoritative evidence is unavailable or insufficient.
6. Preserve bounded retrieval, provider-call limits, the existing request budget, visitor latency ceiling, rate limiting, source-domain restrictions, source indexes, paraphrase checks, known-false-claim checks, and answer-depth requirements.
7. Do not add spend, paid services, subscriptions, or new owner commitments.
8. A production answer is not accepted unless the displayed source can be independently fetched and contains evidence that substantively supports the answer.
9. Cache hits and fresh fetches must obey the same evidence-admission contract.
10. A test expectation may be changed only when the production contract has intentionally become stricter and the old test is proving obsolete behavior. Record why.

## Failure diagnosis sequence

For every failed production run:

1. Read the exact live matrix failure and the full specimen result.
2. Classify the failure before editing code:
   - classification or routing
   - retrieval candidate ranking
   - fresh-source extraction
   - cached-source extraction
   - evidence relevance
   - verifier provider or JSON contract
   - verifier false rejection
   - source-index selection
   - final answer guard
   - displayed-source integrity
   - independent source re-fetch or extraction
   - latency, rate, or capacity
3. Reproduce the exact failing question and preserve it as a regression.
4. Inspect the actual authoritative source currently returned by production.
5. Compare what the Worker extracted with what an independent verifier can retrieve from that same public source.
6. Repair the earliest incorrect layer. Do not compensate downstream for an upstream defect.
7. Prefer stable, directly relevant, independently retrievable official sources over broad or dynamically rendered sources when both support the claim.
8. For a known topic-specific source, preserve it as supporting evidence when it is substantively relevant even if the answer verifier also selects a second official source.

## Required verification before merge

Run the complete release suite, including source policy, Church source index, source-index build check, site QA, unified experience, resources, Study Intelligence, hardened experience, Pioneer local-first, production hardening, Church History, scripture grounding, source-integrity inventory, static-content audit, runtime source guard, reviewed Ask knowledge, Pioneer Ask, Church History Ask, Study Intelligence runtime, question safety, Worker JavaScript validation, and live-matrix definition validation.

Add a regression for every exact production failure discovered during this closeout.

## Production deployment acceptance

After branch QA passes:

1. Open a PR and require normal repository CI to pass.
2. Merge only after the PR is mergeable and CI is green.
3. Deploy the Worker from main.
4. Require all pre-deployment tests and deployment steps to pass.
5. Run the full paced live AI response matrix against the deployed Worker.
6. Inspect every failure rather than accepting the first successful subset.
7. If any live specimen fails, return to diagnosis and repeat the repair cycle.
8. Production is VERIFIED PASS only when the full live matrix completes successfully without known fallbacks, unverifiable displayed sources, source-integrity defects, or gate exceptions.

## Current closeout focus

The current known defect is a Pioneer irrigation answer that can be correct and internally verified while displaying only a broad official history page whose raw public HTML does not yield independently extractable supporting paragraphs to the production matrix. The repair must preserve or return a stable, topic-specific official Pioneer source, especially the existing Chapter Twenty-Six source, when it substantively supports irrigation and settlement context. The broad source may remain supplemental, but it must not be the only independently verifiable support.
