# Generic study-to-Ask repair

Confirmed trigger: Come, Follow Me passes topic and return parameters but no artwork, Watch, or named-study parameter. The previous helper exited before showing the context or filling the question.

The helper now recognizes generic topic context only when no existing artwork/Watch/named-study mode applies. It displays the topic, supplies an editable scripture-study question, and offers a return link to a known same-origin study page. Existing typed text wins; explicit q or search-question wins over the generated question when the field is empty. No form submission, assistant request, or network call is triggered. Topic-only links without a return show Browse study topics, leading to Answers rather than claiming a return to an unknown page.

Return policy: explicit allowlist of current topic-link source pages, same origin, query discarded, plain fragment only. Unknown/external/protocol-relative external/JavaScript destinations fall back to Answers; invalid fragment is removed from an otherwise known page. Existing art, Watch, Evidences and Covenant sanitizers and behavior are unchanged.

Inventory source pages: Atonement; Church history; Come, Follow Me; Joseph Smith likeness; Missionary; Pioneers; Bible and Book of Mormon together; God our Heavenly Father; Grief and faith; Look Unto Me; Restored Church; Settle This in Your Hearts; Stand Forever; Eternal Marriage. CFM's weekly topic is updated dynamically, so its generated current-week wording is handled without hardcoding a date or scripture book.

Changed scope: art-ask-context.js; its exact Ask consumer cache version in ask.html; tools/art_ask_context.test.cjs. No global stylesheet or other copy changes.

Five DOM runtime tests pass using existing jsdom at C:/Users/wyatt/Documents/Codex/2026-09-22/jesus-journey/work/qa-jsdom/node_modules as NODE_PATH. Tests cover editable CFM topic, visible context and return, zero submit/fetch/send calls, q/search-question and typed draft precedence, known and rejected return destinations, no-return/empty-topic behavior, and all four existing context modes. Fermi's browser remains unavailable; Albert owns final rendered CFM link verification. Newton independent review requested before commit.
