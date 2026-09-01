# focusChrist Local-First Interaction Reliability Prompt

Use this prompt whenever Pioneer-page search, biography selection, Journey cards, Trail cards, handcart cards, source verification, or AI fallback behavior is changed.

## Role and objective

Act as the senior reliability, source-integrity, accessibility, and interaction engineer for focusChrist. Preserve truthful sourcing without turning source verification into a user-visible refusal when reviewed local material already answers the interaction. Make every interaction feel immediate, understandable, and recoverable.

The governing principle is: **local reviewed knowledge is the first answer; AI is a conditional enhancement or a true no-match fallback.** AI availability must never gate content that the website already owns, indexes, and has reviewed.

This policy is site-wide. Every question surface must select the correct source lane: ordinary questions use reliable general sources or low-risk AI consensus; Latter-day Saint questions use official Church sources; reviewed local page/PDF content answers immediately. A faith-centered site must not force an ordinary question such as “What color is the sky?” into the Gospel Library lane.

## Non-negotiable rules

1. Treat “color” as the original regression example, not the scope. The guardrail applies to every factual, scriptural, historical, biographical, quoted, attributed, chronological, and source-dependent claim.
2. Never invent a scripture, quotation, person, date, event, attribution, source, journal entry, or doctrinal interpretation.
3. A selected indexed person from *Tell My Story, Too* must be answered from that exact local entry before any remote AI request.
4. Biography boundaries must end at the next indexed person, never at a PDF page marker. Continuation pages belong to the selected biography. The next person must never leak into the answer.
5. Prefetch the local book text during idle time and cache it. A click on a displayed name must not create an AI spinner.
6. If the local book has no exact person entry, or a follow-up asks beyond the entry, queue the AI research path. Show a clear research state promptly and keep the interface usable.
7. Journey, Trail, and Willie/Martin cards already contain reviewed local facts. Opening a card must immediately display reviewed local content. Optional background AI research may replace that content only after source verification succeeds.
8. An AI timeout, rate limit, provider error, empty answer, verifier rejection, or insufficient evidence must never replace reviewed local content with a refusal, endless spinner, blank panel, or unrelated Gospel Library direction.
9. AI-generated faith claims must be verified against the official Gospel Library or other explicitly allowed authoritative sources. The server owns source policy and returns a verification receipt; the browser must not relabel unverified output as verified.
10. Preserve accessible buttons, exact-name choices, keyboard activation, `aria-expanded`, visible collapse controls, and safe text rendering. Never use unsafe HTML rendering for generated or book-derived text.
11. Keep policy and cache versions synchronized across the page, shared runtime, source router, Worker, and regression tests.
12. Do not declare completion from a direct API probe alone. Test the actual production page with real typing and clicking.
13. General, non-faith questions must not be redirected to the Gospel Library. Stable low-risk general knowledge may use a separately checked AI-consensus answer when retrieval returns no excerpts. Current, medical, legal, financial, safety, statistical, quotation, and source-specific questions still require external evidence.

## Required execution sequence

### 1. Inventory interaction surfaces

Identify and test every distinct route:

- free-form Pioneer question;
- partial-name search returning multiple clickable people;
- exact indexed name returning one biography;
- selected biography button;
- random “Tell My Story” selection;
- Journey timeline card;
- Trail location card;
- Willie/Martin timeline card;
- follow-up question after a local biography;
- deliberately absent person or topic that must enter the AI queue;
- provider/verifier failure while reviewed local content is visible.
- an ordinary general question on the main Ask page, including `What color is the sky?`;
- a current or high-stakes general question that must not use the low-risk consensus lane.

### 2. Enforce the decision order

For each interaction, use this order:

1. validated reviewed page content;
2. exact local *Tell My Story, Too* entry;
3. verified AI research using the source class appropriate to the question;
4. separately checked low-risk AI consensus only for stable ordinary general knowledge when retrieval returns no excerpts;
5. transparent limitation that preserves valid local content and offers a relevant retry or source path.

Never reverse steps 1–3. Never call AI merely to restate an exact local biography or gate a reviewed card.

### 3. Protect speed and state

- Render local selected biographies synchronously after the choice click.
- Render reviewed card content synchronously after the expand click.
- Do not show a provider-dependent spinner for those two local routes.
- Queue AI only after local matching reports no exact entry or an explicit enhancement/follow-up needs research.
- Prevent repeated clicks from spawning duplicate requests.
- Preserve valid local content if a background request finishes late or fails.
- A collapsed or different card must not be reopened, cleared, or replaced by a late response.

### 4. Protect source boundaries

- Strip PDF page markers, continuation headers, isolated page numbers, and reuse notices from displayed biography text without deleting substantive content.
- Keep family recollections, diary material, and traditions attributed as the entry attributes them.
- Label the local source as *Tell My Story, Too — [exact selected name]*.
- Do not present a local family-history account as an official Church declaration.
- For AI-only facts, retain only claims supported by the returned verified evidence.

### 5. Add regression coverage

Automated checks must prove:

- local biography rendering appears before `requestPioneerAI` in the selected-person flow;
- Journey/Trail local rendering appears before optional AI research;
- card disclosure code contains no provider spinner and never installs a refusal on failure;
- AI output can replace a card only when `sourceIntegrityPassed` is true;
- exact-name choices remain buttons;
- the book is prefetched;
- Elizabeth Smith retains her Page 2 and Page 3 continuation material;
- a true no-match still reaches the AI request;
- all expandable Pioneer cards have a reviewed description and response container;
- policy and cache versions agree;
- the false D&C color claim remains blocked.
- an ordinary sky-color question remains general, answers directly, and never mentions the Gospel Library;
- current and high-stakes questions cannot enter the low-risk consensus lane.

### 6. Production acceptance test

On the live site:

1. Type `Elizabeth` and submit.
2. Click `ELIZABETH SMITH`.
3. Confirm the response mode is the reviewed local book entry, the local source label is correct, continuation material is present, no loading indicator appears, and no Worker request is needed for the selection.
4. Start a new question with a deliberately absent name and confirm the AI research queue appears.
5. Open `Entering the Valley` and one Trail card. Confirm each opens immediately with reviewed local content, no spinner, and no refusal.
6. Recheck after a background research failure window; local card content must remain.
7. Probe the live Worker’s known-false color regression and confirm it reports the current policy and blocks the false claim.
8. On the live Ask page, ask `What color is the sky?` and confirm a direct general answer appears with no Gospel Library fallback.

### 7. Shared learning

Record the final policy, architectural decision, failure mode, regression tests, production evidence, and future invariant in the Master Brain, Focus operating system, current state, run log, integrity rules, and recovery prompt. The durable learning is broader than the triggering person or color question: **never make verified local knowledge wait for or depend on generative AI.**

## Completion report

Report only after code checks, source-integrity checks, actual browser interactions, Worker policy verification, deployment, and shared-learning readback all pass. Include the production policy version, commit, tested interactions, and any remaining limitation.
