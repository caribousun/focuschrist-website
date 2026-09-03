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

## First post-deploy acceptance, Worker policy 2026-09-03.16

`VERIFIED FAIL`

- Browser deployment and post-merge site QA passed at merge `179b8be3d0a4788ab88fc3fe48289a116d47f37c`.
- Cloudflare Worker deployment succeeded with version ID `5d846d4a-6714-46fe-aaf3-c6d6506ca5e8`.
- The new live matrix failed as designed. Hyrum Smith completed in 8.9 seconds but used `general-ai-low-risk`, returned no sources or verification receipt, and was only 60 words. The research-first identity upgrade could not operate when research was unavailable.
- Scripture and Pioneer specimens terminated in 4.8 and 5.6 seconds with explicit `research-rate-limited` fallbacks. The new deadline fixed the excessive wait, but reliability still failed.

Follow-up root cause: known Church-person classification must exist server-side before the research call, not only in the browser or as a post-research evidence upgrade. The one permitted 429 retry also needs to honor the provider's bounded delay within the shared deadline. The five-specimen matrix should pace calls to avoid creating an artificial burst while still gating each response's own latency.

## Second post-deploy acceptance, Worker policy 2026-09-03.17

`VERIFIED FAIL`

- Hyrum Smith passed in 3.6 seconds with 211 words, faith-study classification, and official Church History sources only.
- General science passed in 4.8 seconds.
- The next three faith/history specimens reached the verifier but returned `verification-provider-error`; later inspection identified HTTP 429 `rate_limit_exceeded` on the verifier.
- A separate Alma 32 request after the burst passed in 11.7 seconds with 83 words and five official Church sources, proving the verifier was healthy outside the token window.
- A later 15-second-paced matrix still produced verifier 429 responses for two middle specimens, while the first, fourth, and fifth passed.

Official Groq documentation lists a free-plan limit of 8,000 tokens per minute for `openai/gpt-oss-20b`, compared with 70,000 tokens per minute for `groq/compound-mini`. The pre-repair verifier could receive six evidence excerpts of up to 1,800 characters each, plus the draft and policy. The remaining bottleneck was verifier input volume, not request count alone.

Worker policy 2026-09-03.18 therefore caps collected evidence at four compact excerpts and sends only the two highest-ranked eligible sources to verification, with each excerpt capped at 700 characters and the complete evidence block capped at 5,000 characters. This retains a distinct verifier step while fitting the existing no-new-cost provider limits.

## Third post-deploy acceptance, Worker policy 2026-09-03.18

`VERIFIED FAIL`

- Four of five production specimens passed with verified answers in 3.3 to 10.6 seconds.
- The final Church History specimen reached the verifier but returned HTTP 429 `rate_limit_exceeded` after 7.0 seconds.
- The evidence reduction materially improved throughput but did not remove the single-model 8,000-TPM bottleneck. A core public question service cannot depend on that verifier lane alone.

Worker policy 2026-09-03.19 separates the two AI stages across providers. Groq Compound Mini continues official-source research. Cloudflare Workers AI `@cf/openai/gpt-oss-20b` becomes the primary evidence verifier through the Worker's native `AI` binding; Groq `openai/gpt-oss-20b` remains a one-shot operational fallback. Both receive the same server-owned prompt, evidence, output contract, and deterministic final guards. A valid verifier rejection never triggers another model, preventing verdict shopping. The research draft and completion ceilings are also bounded.

Official Cloudflare documentation states a 10,000-neuron daily free allocation, 300 text-generation requests per minute, JSON-compatible response formatting, and no use of Workers AI customer content for training or service improvement without explicit consent. Production remains `VERIFIED FAIL` until the exact `.19` deployment and five-question matrix pass.

The exact `.19` deployment proved the native AI binding but failed acceptance. Three of five specimens used Cloudflare successfully. The Hyrum Smith and Pioneer evidence prompts produced an empty/unusable primary response and used the one-shot Groq fallback; Pioneer recovered, but Hyrum's fallback returned `json_validate_failed`. Cloudflare's official JSON Mode supported-model list does not include GPT-OSS 20B, so the intermittent strict-output behavior was outside the documented contract.

Candidate policy `2026-09-03.20` changes only the Cloudflare verifier model to the non-deprecated `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, which Cloudflare explicitly lists as JSON Mode compatible. Groq Compound Mini research, one-shot Groq 20B fallback, deadlines, evidence limits, source-index requirement, diagnostics, and deterministic final guards are unchanged. Production remains `VERIFIED FAIL` pending the exact `.20` live matrix.

## Policy .22 deployed failure

Policy `.22` deployed at commit `c9288cb18352e74e95fea3678a95fe5a85d621a4`, Worker version `5051c511-0873-4cf3-a1ef-b84c240342f1`. The new 900-URL official Church index successfully answered covered retrieval needs without Groq research. The exact 15-core matrix nevertheless passed only nine specimens because the 70B Cloudflare verifier intermittently timed out or rejected usable indexed evidence, and the depleted Groq operational fallback could not recover. This isolates the remaining failure to verifier reliability rather than retrieval.

Candidate `.23` retains the index and every source-integrity control, but selects `@cf/meta/llama-3.2-11b-vision-instruct` for primary verification. Cloudflare documents this exact active ID for JSON Mode and prices it at 4,410 input and 61,493 output neurons per million tokens. Promotion still requires the complete unchanged live matrix and rendered browser journeys.

## Policy .23 deployed failure and policy .24 root fix

Policy `.23` deployed at commit `de684822daed4339cf6881690529c220c4ba2078`, Worker version `81128a24-9588-4079-a344-fd072183d7a5`. The 11B endpoint returned Cloudflare `service_unavailable` during the exact matrix, so most indexed questions depended on Groq fallback and failed closed.

The deployed receipts exposed a separate prompt defect: after successful indexed retrieval, the gateway placed a task instruction in a field labeled `DRAFT`. A strict verifier could reject that instruction as unsupported even though the official evidence was relevant. Candidate `.24` leaves `DRAFT` empty for indexed retrieval and explicitly composes the answer from evidence. It restores the documented 70B JSON-mode primary, allows that primary at most 12 seconds inside the unchanged 22-second Worker budget, and caps normal verifier output at 500 tokens. Production remains `VERIFIED FAIL` pending the unchanged matrix.

The clean `.20` rerun removed the propagation variable and still failed. The 70B verifier completed some strict verdicts in 5.4 to 6.1 seconds but timed out on other complex prompts at the 6.5-second ceiling. Groq's fallback then sometimes returned `json_validate_failed` before the Worker could parse or validate the model output. Candidate `.21` raises only the primary ceiling to 9 seconds while preserving a 5-second fallback reserve, removes provider-side `response_format` enforcement from the single Groq fallback while retaining the prompt JSON contract and Worker parser, and adds a 15-second post-deploy settle before the matrix. No second fallback or verifier retry is added. Production remains `VERIFIED FAIL` pending exact `.21` acceptance.

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

## Policy .24 overlap failure and policy .25 repair

Exact `.24` deployed successfully and returned complete Cloudflare-primary answers for 13 of 15 paced core specimens. The two failures had relevant indexed Church evidence, `approved: true`, and valid source indexes, but the deterministic final guard rejected the generated wording for excessive ordered overlap with source excerpts. The system therefore failed closed as designed.

Candidate `.25` does not raise or remove the overlap limit. It tells the first verifier pass to use independent phrasing and adds one bounded combined repair when an approved answer fails either depth or overlap. That repair uses Cloudflare only, is capped at 400 normal-output tokens, shares the 22-second request deadline, and cannot run after a Groq fallback. Production remains `VERIFIED FAIL` until the exact `.25` matrix, capacity calculation, and rendered journeys pass.

## Policy .25 cumulative-overlap false positive and policy .26 correction

Exact `.25` kept Cloudflare and indexed retrieval stable, but the baptism specimen still failed closed. The approved long answer contained enough sparse two-word source matches to cross the cumulative 25-word counter, even though those matches were a small portion of the independently worded response. The first verifier also consumed enough of the shared deadline that the optional repair could not start. Separately, the matrix rejected the official daily-life Pioneer history URL before independent evidence validation because that valid indexed path was absent from its expected URL pattern.

Candidate `.26` continues to reject any run longer than 25 consecutive source words. Cumulative ordered fragments still require more than 25 matched words, and now must also account for at least 40 percent of the answer before being treated as reconstructed source text. Dense two-word mosaic copying remains blocked by regression; sparse common phrases in a much longer answer do not create a false rejection. The daily-life Pioneer URL is admitted only to the test's path pattern; the independent official-page fetch and expected-concept checks remain unchanged. Production remains `VERIFIED FAIL` pending exact `.26` acceptance.

## Policy .26 fast false rejection and policy .27 reconsideration

Exact `.26` fixed the baptism overlap false positive and produced complete answers for 14 of 15 core specimens. One terse Pioneer irrigation question received an initial false verdict in 2,226 ms despite indexed official evidence. An immediate live replay of the same question succeeded with an official-only answer, showing a stochastic verifier false negative rather than an evidence or provider outage.

Candidate `.27` pins Pioneer-page irrigation intent to the official Pioneer Settlements topic. When an indexed official evidence set overlaps at least two direct query terms but the first verifier verdict is false, the same Cloudflare verifier may re-evaluate exactly once. The re-evaluation prompt does not force approval; a second false verdict remains a fail-closed response. It shares the request deadline, disables Groq fallback, and preserves the two-call ceiling, final source-index requirement, answer-depth guard, source-overlap guard, and capacity accounting. Production remains `VERIFIED FAIL` pending exact `.27` acceptance.

## Policy .27 primary timeout and policy .28 budget allocation

Exact `.27` proved the Pioneer routing and indexed-verdict changes but failed one of 15 core specimens when the final doctrine request reached the 12-second Cloudflare primary ceiling. The receipt showed one Cloudflare attempt and zero Groq fallback calls. The system failed closed, while the other 14 core answers remained complete.

Candidate `.28` keeps the 22-second Worker deadline and all live p95 and 25-second visitor ceilings unchanged. It allocates at most 15 seconds to Cloudflare instead of 12, retains a 3-second reserve for one Groq operational fallback instead of 5, and lowers normal verifier output from 500 to 400 tokens. This favors the provider that is actually completing the indexed workload and reduces generation size without changing retrieval, verification, source, safety, copyright, or capacity requirements. Production remains `VERIFIED FAIL` pending exact `.28` acceptance.
