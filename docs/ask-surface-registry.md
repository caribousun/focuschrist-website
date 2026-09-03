# focusChrist Ask Surface Registry

Browser release/cache: `2026-09-03.16` / `20260903-16`; Worker policy: `2026-09-03.34`

This registry records the final user-visible owner after all inline, deferred, and dynamically loaded scripts execute. A link to the Ask page is not classified as a separate Ask surface.

| Surface | Trigger | Final runtime owner | First local provider | External path | Provider-failure behavior | Runtime test |
|---|---|---|---|---|---|---|
| Main Ask | Primary composer button or Enter | `study-intelligence-v3.js` installs `window.sendMessage` after `site-common.js` loads it | `reviewed-ask-knowledge.js`, then individually verified `ask.html` entries | Worker, profile selected as general, faith, or high-stakes | Reviewed answers remain available; unreviewed source-dependent output fails closed | `tools/study_intelligence_v3_runtime_qa.js` |
| Main Ask starters/topics | Exact `data-ask-starter` or topic button through `ask-experience.js` | `ask-experience.js` submits through the v3-owned primary composer; the legacy inline topic path is bypassed | Shared registry; every visible starter is an executable reviewed contract | Same Worker route for unreviewed questions | Reviewed starters remain complete during provider failure; request ownership and reset cancellation remain active | `tools/reviewed_ask_knowledge_qa.js`; `tools/study_intelligence_v3_runtime_qa.js`; page QA suites |
| Main Ask follow-up | Follow-up composer | `ask-experience.js` copies the question into the primary composer, then calls v3 `window.sendMessage` | Shared registry resolves declared reviewed subject context before classification and matching | Same Worker route only when no reviewed contextual match exists | Context receipt is inspectable; reset prevents stale subject inheritance and cancels stale responses | `tools/reviewed_ask_knowledge_qa.js`; `tools/study_intelligence_v3_runtime_qa.js` |
| Main Ask reset | New Question | `ask-experience.js` wraps inline `clearChat` | Clears DOM and session conversation | No external call | Cancels the active request and restores controls | Page QA suites |
| Pioneer free-form | Primary composer button or Enter | `pioneer-experience.js` owns `window.sendMessage` | Shared reviewed registry, then exact *Tell My Story, Too* selection | Pioneer Worker profile | Reviewed facts and exact biographies remain available; remote-only question gets a bounded limitation | `tools/pioneer_ask_runtime_qa.js` |
| Pioneer topics | Topic button | `pioneer-experience.js` owns `window.askTopic` | Shared reviewed registry with exact visible-label matching | Pioneer Worker profile | Reviewed topic remains available without Worker; `Handcart Companies` is a permanent zero-Worker specimen | `tools/pioneer_ask_runtime_qa.js`; Pioneer QA suites |
| Pioneer exact person | Exact indexed person in free-form search | `pioneer-experience.js` `answerSelectedPioneer` | Exact local *Tell My Story, Too* biography | Worker only if no complete local biography exists | A complete local biography is returned without a Worker dependency | `tools/pioneer_ask_runtime_qa.js`; `tools/hardened_experience_qa.py`; `tools/pioneer_local_first_qa.py` |
| Pioneer partial person | Multiple indexed matches | `pioneer-experience.js` `renderPioneerChoices` | Local person index | Worker only after an exact choice or true no-match | Accessible choice buttons remain available | `tools/hardened_experience_qa.py` |
| Pioneer random person | Tell My Story action | `pioneer-experience.js` `askTellMyStory` | Local text index and exact biography | Optional corroborating Worker research | Local index error is explicit; selected biography remains local-first | Pioneer QA suites |
| Pioneer Journey/Trail/handcart card | Click, Enter, or Space | Capture-phase controller in `pioneer-experience.js` | Reviewed date/title/description already displayed by the card | Optional verified enhancement | Local card remains visible through timeout, verifier rejection, or provider failure | `tools/hardened_experience_qa.py`; `tools/pioneer_local_first_qa.py` |
| Pioneer reset | New Question | `pioneer-experience.js` `window.clearChat` | Clears DOM and session conversation | No external call | Cancels the active request and restores the local welcome state | Pioneer QA suites |
| Church History composer | Form submit, button, or Enter | `church-history-experience.js` `answerQuestion` | Shared reviewed registry | v3 plus official Church History Worker profile | Reviewed facts remain available; remote-only question retains official study routes | `tools/church_history_ask_runtime_qa.js` |
| Church History suggestions | Ten exact `data-history-question` buttons | `church-history-experience.js` delegates to `answerQuestion` | Shared reviewed registry; all ten exact questions are reviewed contracts | No external call for the visible cards | Every card remains substantive and sourced with the Worker unavailable | `tools/reviewed_ask_knowledge_qa.js`; `tools/church_history_ask_runtime_qa.js`; `tools/church_history_qa.py` |
| Church History follow-up | Same composer after answer | `church-history-experience.js` with bounded page conversation | Shared registry resolves declared reviewed subject context before matching | Same Church History route only when no reviewed contextual match exists | Reset prevents subject leakage and cancels stale ownership; official routes remain | `tools/church_history_ask_runtime_qa.js` |
| Church History reset | New Question | `church-history-experience.js` `resetConversation` | Clears page conversation | No external call | Invalidates pending response ownership and restores controls | Church History QA |

## Shared boundaries

- `reviewed-ask-knowledge.js` is the only cross-page reviewed fact registry. It contains positive tests, negative tests, page profiles, exact source metadata, reviewer metadata, integrity keys, and cue-selected contextual variants for stable follow-ups the project can answer without remote research.
- `answer-audit.json` pins every reviewed registry entry by SHA-256 and exact authoritative source list.
- `ask-question-contracts.json` is the machine-readable inventory of exact Ask starters, Ask topics, Pioneer topics, and Church History cards. QA reparses the production HTML and fails on any count, value, owner, or lane drift.
- The 494-entry legacy Ask database remains quarantined except for its three previously reviewed entries. The Pioneer legacy database remains fully quarantined.
- `site-common.js` owns the browser source-integrity guard and dynamically loads shared study assets on Ask and Pioneers.
- `site-common.js` also owns the shared question-safety evaluator. Main Ask, Pioneers, and Church History evaluate the question before rendering the user turn, writing history, disabling controls, or starting a Worker request. The Worker enforces the same boundary for direct API traffic.
- Profanity, explicit sexual content, and derogatory attacks on a religion, culture, ethnicity, nationality, or political affiliation receive the approved focusChrist mission redirect. The blocked text is not echoed or stored. Immediate abuse or danger disclosures receive urgent safety guidance. Respectful doctrinal, historical, interfaith, cultural, and political-neutrality questions remain answerable.
- `study-intelligence-v3.js` owns broad Ask final submission and supplies the research function used by Church History.
- `pioneer-experience.js` deliberately owns Pioneer submission so person-selection and card behavior cannot be replaced by a global handler.
- The Worker owns external retrieval and server verification. A deterministic 900-URL official Church index and canonical scripture router run before Groq research. Cloudflare Workers AI performs primary verification; the existing Groq verifier is a one-shot operational fallback. A valid rejection never triggers provider fallback. One same-provider reconsideration is permitted only when a false verdict conflicts with direct lexical relevance in indexed official evidence; a second false verdict remains closed. Provider fallback never stacks with the single combined depth/paraphrase repair or reconsideration. Browser links alone never create a verification receipt.
- No service worker is registered. Cache control is the versioned asset query string plus the GitHub Pages/edge response cache.
- Art and Watch pages route context into the main Ask page but do not render a separate inline AI answer surface.
- The browser makes one bounded Worker attempt per unreviewed question. The Worker owns a shared 22-second request budget across research, verification, and any eligible retry or expansion; Cloudflare may use at most 15 seconds and one Groq operational fallback retains a 3-second reserve. The browser ceiling is 25 seconds.
- Official excerpt packs are sanitized, bounded, cached by canonical Church URL for at most one hour, and selected against each live question without caching the question or answer. Public receipts report actual fetch attempts and cache outcomes.
- The Cloudflare rate-limit binding caps the AI path at 20 requests per client address per minute at each location. The address is not logged or sent to an AI provider.

## Permanent discovery control

Before each Ask release, repository search must reconcile this registry against:

- every `userInput`, `historyAskForm`, `sendMessage`, `askTopic`, `focusChristStudyAsk`, and `focusChrist*AskAI` definition;
- every script capable of installing or replacing those functions;
- every question button, biography choice, expandable card, follow-up composer, and reset control;
- every versioned loader, Worker route, source-policy version, and cache identifier.

An unregistered user-visible question path is a release blocker.

Current executable control counts are six main Ask starters, 56 main Ask topic controls, 17 Pioneer topic controls, and ten Church History question cards. Final-owner QA executes every exact value; reviewed visible cards additionally require a substantive answer, official sources, and zero Worker calls.
