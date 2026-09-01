# focusChrist Ask Surface Registry

Release candidate: `2026-09-01.9` / cache `20260901-9`

This registry records the final user-visible owner after all inline, deferred, and dynamically loaded scripts execute. A link to the Ask page is not classified as a separate Ask surface.

| Surface | Trigger | Final runtime owner | First local provider | External path | Provider-failure behavior | Runtime test |
|---|---|---|---|---|---|---|
| Main Ask | Primary composer button or Enter | `study-intelligence-v3.js` installs `window.sendMessage` after `site-common.js` loads it | `reviewed-ask-knowledge.js`, then individually verified `ask.html` entries | Worker, profile selected as general, faith, or high-stakes | Reviewed answers remain available; unreviewed source-dependent output fails closed | `tools/study_intelligence_v3_runtime_qa.js` |
| Main Ask topics | Topic button through `ask-experience.js` | `ask-experience.js` submits through the v3-owned primary composer; the legacy inline topic path is bypassed | Same shared registry and verified local entries | Same Worker route | Same as Main Ask, including request ownership and reset cancellation | `tools/study_intelligence_v3_runtime_qa.js`; page QA suites |
| Main Ask follow-up | Follow-up composer | `ask-experience.js` copies the question into the primary composer, then calls v3 `window.sendMessage` | Same shared registry with bounded conversation history | Same Worker route | Same as Main Ask; stale responses can be cancelled by reset | `tools/study_intelligence_v3_runtime_qa.js` |
| Main Ask reset | New Question | `ask-experience.js` wraps inline `clearChat` | Clears DOM and session conversation | No external call | Cancels the active request and restores controls | Page QA suites |
| Pioneer free-form | Primary composer button or Enter | `pioneer-experience.js` owns `window.sendMessage` | Shared reviewed registry, then exact *Tell My Story, Too* selection | Pioneer Worker profile | Reviewed facts and exact biographies remain available; remote-only question gets a bounded limitation | `tools/pioneer_ask_runtime_qa.js` |
| Pioneer topics | Topic button | `pioneer-experience.js` owns `window.askTopic` | Shared reviewed registry | Pioneer Worker profile | Reviewed topic remains available without Worker | `tools/pioneer_ask_runtime_qa.js`; Pioneer QA suites |
| Pioneer exact person | Exact indexed person in free-form search | `pioneer-experience.js` `answerSelectedPioneer` | Exact local *Tell My Story, Too* biography | Worker only if no complete local biography exists | A complete local biography is returned without a Worker dependency | `tools/pioneer_ask_runtime_qa.js`; `tools/hardened_experience_qa.py`; `tools/pioneer_local_first_qa.py` |
| Pioneer partial person | Multiple indexed matches | `pioneer-experience.js` `renderPioneerChoices` | Local person index | Worker only after an exact choice or true no-match | Accessible choice buttons remain available | `tools/hardened_experience_qa.py` |
| Pioneer random person | Tell My Story action | `pioneer-experience.js` `askTellMyStory` | Local text index and exact biography | Optional corroborating Worker research | Local index error is explicit; selected biography remains local-first | Pioneer QA suites |
| Pioneer Journey/Trail/handcart card | Click, Enter, or Space | Capture-phase controller in `pioneer-experience.js` | Reviewed date/title/description already displayed by the card | Optional verified enhancement | Local card remains visible through timeout, verifier rejection, or provider failure | `tools/hardened_experience_qa.py`; `tools/pioneer_local_first_qa.py` |
| Pioneer reset | New Question | `pioneer-experience.js` `window.clearChat` | Clears DOM and session conversation | No external call | Cancels the active request and restores the local welcome state | Pioneer QA suites |
| Church History composer | Form submit, button, or Enter | `church-history-experience.js` `answerQuestion` | Shared reviewed registry | v3 plus official Church History Worker profile | Reviewed facts remain available; remote-only question retains official study routes | `tools/church_history_ask_runtime_qa.js` |
| Church History suggestions | Suggested question button | `church-history-experience.js` delegates to `answerQuestion` | Shared reviewed registry | Same Church History route | Same as composer | `tools/church_history_ask_runtime_qa.js`; `tools/church_history_qa.py` |
| Church History follow-up | Same composer after answer | `church-history-experience.js` with bounded page conversation | Shared registry for a directly matched follow-up | Same Church History route with bounded context | Reset cancels stale ownership; official routes remain | Church History runtime and page QA |
| Church History reset | New Question | `church-history-experience.js` `resetConversation` | Clears page conversation | No external call | Invalidates pending response ownership and restores controls | Church History QA |

## Shared boundaries

- `reviewed-ask-knowledge.js` is the only cross-page reviewed fact registry. It contains positive tests, negative tests, page profiles, exact source metadata, reviewer metadata, and integrity keys.
- `answer-audit.json` pins every reviewed registry entry by SHA-256 and exact authoritative source list.
- The 494-entry legacy Ask database remains quarantined except for its three previously reviewed entries. The Pioneer legacy database remains fully quarantined.
- `site-common.js` owns the browser source-integrity guard and dynamically loads shared study assets on Ask and Pioneers.
- `study-intelligence-v3.js` owns broad Ask final submission and supplies the research function used by Church History.
- `pioneer-experience.js` deliberately owns Pioneer submission so person-selection and card behavior cannot be replaced by a global handler.
- The Worker owns external retrieval and server verification. Browser links alone never create a verification receipt.
- No service worker is registered. Cache control is the versioned asset query string plus the GitHub Pages/edge response cache.
- Art and Watch pages route context into the main Ask page but do not render a separate inline AI answer surface.

## Permanent discovery control

Before each Ask release, repository search must reconcile this registry against:

- every `userInput`, `historyAskForm`, `sendMessage`, `askTopic`, `focusChristStudyAsk`, and `focusChrist*AskAI` definition;
- every script capable of installing or replacing those functions;
- every question button, biography choice, expandable card, follow-up composer, and reset control;
- every versioned loader, Worker route, source-policy version, and cache identifier.

An unregistered user-visible question path is a release blocker.
