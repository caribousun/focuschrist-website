# focusChrist AI Response Incident Root Cause

Date: 2026-09-03

Baseline production revision: `2e103d04d543d029c5a5237d7a6259610af05b64`

Production policy/cache observed in source and live receipts: `2026-09-01.15` / `20260901-15`

Overall baseline state: `VERIFIED FAIL`

## Cross-surface live baseline

The new live matrix submitted five unreviewed questions directly through the deployed pre-repair Worker on 2026-09-03:

| Specimen | Result | Time | Source result |
|---|---:|---:|---|
| Main Ask, `Who is Hyrum Smith?` | Abort/failure | 26.0 s | No completed answer |
| Main Ask, stable general science | Pass | 10.2 s | NOAA and NASA evidence |
| Main Ask, Alma 32 scripture | Pass | 13.5 s | Official Church sources only |
| Pioneers, irrigation free-form | Abort/failure | 26.0 s | No completed answer |
| Church History, Relief Society | Pass | 9.9 s | Official Church sources only |

Measured sample: two failures out of five, 40 percent fallback/abort incidence, p95 26.0 seconds, maximum 26.0 seconds. The sample proves that the defect is path-dependent and affects more than the original Hyrum Smith question.

## Owner-reproduced incident

The Main Ask page accepted `who is hyrum smith` but eventually displayed:

> I could not complete that general answer just now. Please try again or rephrase the question.

The screenshot proves the page submitted and rendered a Worker-generated general fallback. It does not prove which provider stage failed because the browser currently discards the Worker's gateway-mode and provider-stage diagnostics.

## Evidence and causal findings

### 1. Hyrum Smith is classified in the wrong domain

`VERIFIED PASS` evidence:

- `study-intelligence-v3.js` uses fixed `FAITH_TERMS` and `FAITH_PHRASES` lists.
- Those lists contain Joseph Smith and several other Church figures but not Hyrum Smith.
- `classifyQuestion('who is hyrum smith')` therefore selects `general-knowledge` on the Main Ask page.
- The Worker `FAITH_PATTERN` also does not independently recognize Hyrum Smith, although it honors the client's recognized `faith-study` profile.
- A live request using `general-knowledge` returned non-Church sources including Wikipedia and BYU RSC. A live request using `faith-study` returned only ChurchofJesusChrist.org sources.

Root cause: a Latter-day Saint Church-history identity can enter the general lane when the person's name is absent from a manually maintained keyword list. This violates the source-authority contract and is broader than one name.

### 2. The visitor wait can multiply across layers

`VERIFIED PASS` evidence:

- Browser v3 currently performs two full attempts with 25-second and 18-second client timeouts.
- One Worker request can perform research, verification, and a depth-expansion call sequentially.
- Every provider call can independently retry a 429 after waiting up to 30 seconds.
- JSON validation failure can add a fixed 12-second wait and another verifier call.
- Browser and Worker layers do not share one total deadline.

Root cause: retry and deadline ownership is distributed across browser, research, verifier, expansion, and provider helpers. A reasonable question can spend tens of seconds in work that eventually produces no answer.

### 3. The visible fallback blames the question instead of identifying service failure

`VERIFIED PASS` evidence:

- The exact screenshot message is `GENERAL_ANSWER_FALLBACK` from the Worker.
- It tells the visitor to try again or rephrase even though `who is hyrum smith` is a valid question.
- Worker responses include `focuschrist_gateway_mode` and some safe provider diagnostics, but `study-intelligence-v3.js` does not retain or expose them in the returned answer receipt.

Root cause: the browser collapses multiple operational failure states into generic copy and loses the evidence needed to diagnose the actual stage after the incident.

### 4. Existing QA passed without exercising the failing production dependency

`VERIFIED PASS` evidence:

- All 17 existing local Python, JavaScript, and Worker policy suites passed against production revision `2e103d0` in 4.01 seconds.
- The current live production Ask gate passed in 23.08 seconds and verified 15 exact deployed assets plus reviewed registry behavior.
- That live gate does not submit an unreviewed question to the live Worker. It executes reviewed local knowledge in a VM after checking deployed bytes.
- Existing runtime tests stub `fetch` and do not sample live provider latency or intermittent fallback incidence.
- No current release gate asserts end-to-end latency budgets or retries per visitor request.

Root cause: the gates strongly verify reviewed-local behavior, source policy, cache identity, and mocked failure behavior, but they do not verify the live remote lane that failed for the owner.

### 5. The failure is intermittent, not a permanent endpoint outage

`VERIFIED PASS` evidence:

- Live `general-knowledge` request for the exact question later succeeded with HTTP 200 in 12.68 seconds.
- Live `faith-study` request for the exact question later succeeded with HTTP 200 in 9.99 seconds.
- Both durations exceed local-answer expectations but are within the new initial remote median budget.

`HYPOTHESIS`:

The screenshot fallback was caused by a transient research, evidence, verifier, or provider failure. The exact stage is unproven because the browser discarded the response diagnostics and the screenshot contains only final copy.

### 6. Respect filtering exists but is incomplete and inconsistent

`VERIFIED PASS` evidence:

- `ask.html` contains a small exact-substring list and `containsInappropriate` function.
- The list does not establish the owner's full boundary for profanity variants, explicit sexual questions, or derogatory attacks on faiths, cultures, and political affiliations.
- Main Ask v3 appends the visitor question to the visible conversation before checking `containsInappropriate`.
- Pioneer has separate redirect copy and Church History has no proven shared preflight contract.
- Existing QA stubs `containsInappropriate` to always return false and therefore does not test the production filter.

Root cause: content-boundary ownership is page-local, word-list based, late in the submission lifecycle, and not governed by shared behavior tests.

## Why earlier completion claims were allowed

The prior reliability work centered on owner-reproduced reviewed-local failures, identity follow-ups, cache consistency, and provider-disabled behavior for facts already owned by the site. Those controls work and still pass. The completion criteria did not include representative live unreviewed Church figures, general-versus-Church entity classification, total remote deadline ownership, repeated provider sampling, or the complete respect boundary. The tests therefore proved a narrower contract than the site's broad Ask promise.

## Shared failure classes

1. Any unlisted Church figure can be routed as general knowledge.
2. Any remote-only question can experience stacked latency and retries.
3. Any provider-stage failure can be rendered as an unhelpful generic fallback.
4. Any page relying on page-local inappropriate-content handling can diverge in coverage, timing, copy, storage, or provider-call behavior.
5. The existing live gate can pass while the live remote answer lane is failing.

## Required permanent controls

- Reusable Church-history entity classification with positive, negative, unknown-name, misspelling, and subject-switch tests.
- One end-to-end deadline budget shared across the browser and Worker, with bounded retry ownership.
- Safe gateway diagnostics retained by the browser and exercised by QA.
- A repeated live remote-lane matrix with latency and fallback-rate evidence.
- One shared preflight respect boundary used by Main Ask, Pioneers, and Church History before rendering, storing, or submitting prohibited questions.
- Exact respectful redirect copy, zero Worker calls, zero history writes, no prohibited-text echo, and restored controls tested at final runtime.

## Baseline evidence summary

- Existing local suites: `VERIFIED PASS`, 17 of 17.
- Existing live asset/reviewed-contract gate: `VERIFIED PASS`.
- Owner's exact live journey: `VERIFIED FAIL`.
- Live endpoint availability after incident: `VERIFIED PASS`, intermittent success observed.
- Exact original provider-stage failure: `UNAVAILABLE / UNPROVEN` because diagnostics were not retained.
- All-page broad remote-lane reliability and latency: `UNAVAILABLE / UNPROVEN` until the new matrix is implemented and run.
