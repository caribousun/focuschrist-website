# Ask entry scroll-follow successor registration

This directory registers one exact change set: the Ask conversation
scroll-follow fix in `ask.html` and `ask-experience.js`, built on
branch `feature/ask-entry-scroll-follow-2026-10-25`.

The defect: every conversation entry is appended by `addMessage` in
ask.html, which ended by forcing the transcript to its bottom
(`chatBox.scrollTop = chatBox.scrollHeight`). The post-append follow
in ask-experience.js then anchored the view to the first exchange in
the box, on the assumption that its latest-first promotion had moved
the newest exchange to the top. A follow-up chip click never clears
the `data-focuschrist-latest-first` marker (the typed, starter,
topic, and dock paths clear it through `focusConversation()`), so no
promotion runs for a chip-sent follow-up: the new answer stays
appended at the bottom while the follow scrolls the panel back to
the first answer, and the visitor has to scroll down inside the
panel to find the answer they just asked for.

The fix:

- ask.html: a new `bringEntryIntoView(entry)` helper sits directly
  above `addMessage`, and `addMessage` calls it on the appended
  entry in place of the bottom-force line. `scrollIntoView` with
  `block: 'start'` scrolls every scrollable ancestor, so the new
  entry's top lands at the top of the internally scrolling chat
  panel and the panel is brought into the window's view. It runs on
  every append (typed question, starter click, topic, dock, or chip
  click; bank serve, live answer, suggestion, or the honest
  fallback), never on page load, and never when nothing was
  appended. `addMessage` still returns nothing, so
  study-intelligence-v3's chip hosting is unchanged.
- ask-experience.js: the MutationObserver captures the actual added
  bot-message node instead of re-querying the first one, and passes
  it to `focusLatestAnswer` and `addRelatedStudyToLatestAnswer`;
  the `focuschrist:answer-ready` handler passes its event target.
  `focusLatestAnswer` and `focusLatestAnswerSettled` now anchor the
  exchange that owns the answer (its own preceding user message)
  instead of the first user message in the box, and
  `addRelatedStudyToLatestAnswer` accepts the same optional
  candidate and reads the question from the paired user message.
  Where promotion has run, the paired sibling is exactly the node
  the old selection picked, so the previously working paths behave
  as before.

Registered spans (candidate-byte coordinates):

- ask.html: predecessor SHA-256
  `0d9a5f1ba3a6bf815084ef3df330b25b771332dfa837dd2f21e74b133a9cfc90`,
  candidate SHA-256
  `1c6b962d3b0066a8503b3f9075509594cc2e260a8c60c1d0720a7276852a3f8c`
  (438,913 bytes). Two spans:
  - [430971, 431234): the `bringEntryIntoView` helper inserted
    (263 bytes, empty previous bytes) directly above `addMessage`.
  - [436670, 436703): the bottom-force line
    `chatBox.scrollTop = chatBox.scrollHeight;` (46 bytes) replaced
    with the `bringEntryIntoView(message);` call (33 bytes).
- ask-experience.js: predecessor SHA-256
  `62f17066d8d50d8e8ec417190f026111b628f11e8221f2babd7b40d257ea2fab`,
  candidate SHA-256
  `9aba64e444ddc89f1b0c3a5dfc5fdae3b77e6933a28cc83901059b8041e34b8d`
  (32,304 bytes). Ten spans, all inside the follow machinery:
  the `focusLatestAnswer` and `focusLatestAnswerSettled` exchange
  anchors, the `addRelatedStudyToLatestAnswer` candidate parameter,
  answer selection, paired-question lookup and read, the
  answer-ready handler's pass of `event.target`, and the
  MutationObserver's capture and use of the added answer node.

The ask.html predecessor hash is exactly the after hash the
legacy-answer-repairs successor layer
(docs/legacy-answer-repairs-successor/manifest.json) pins for
ask.html; this layer strips back to it, the legacy layer then
strips back to the citation-rendering layer's after state
(`4881b5a20ed045b1d45dd1c393d3204c56cf46692d7fa4837e5257346aa4e7a9`),
the citation layer strips back to the answer-bank layer's after
state
(`735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612`),
the answer-bank layer strips back to the state the continue-motion
predecessor map pins as current for ask.html
(`4a5f73ee35fb5cd8d1a9d30109f7daf9f85f7e3913fb5e3cc012a996d6058db3`),
and the motion chain then reconstructs the historical predecessor
`bbeeb8c6e40d4b55a7949ba7544200796457df1ad975fbd2bdb9b75f9d8c8a04`.
The ask-experience.js predecessor hash is exactly the after hash
the continue-motion predecessor map pins as current for
ask-experience.js; this layer strips back to it and the motion
chain reconstructs its historical predecessor
`7ec29c6d51c3ec0939c52e883f7dd6ac70f8d492e356970c5d7380c1d6157c62`.

`manifest.json` is pinned in `tools/entry_scroll_successor.py` as
`SOURCE_SHA`. That pin records the exact candidate spans only. It
is not review approval. No legacy, answer-bank, or citation
manifest, module, or review record, no other successor layer, no
predecessor map, MAP_SHA, or motion review record is changed by
this layer. Because the answer-bank layer's check and the citation
layer's check read ask.html raw, the continue-motion binding
validates those layers against restored projections of ask.html
(temporary views) rather than the raw final bytes, without
altering those layers themselves.

Sequencing note: this layer is built on main
`b0c8f8ba585280e919c82de71fd484b2d0ea541d`, which already includes
PR #516 (the legacy answer repairs layer). PR #518 also changes
ask.html and merges before this PR; this layer's ask.html spans
will be re-pinned onto the post-#518 head, with a bounded
re-review of the re-pin, before this PR merges.
ask-experience.js is untouched by either PR.

## Review model

The independent review of this registration is Jeff's exact-head
review of the PR carrying it, delivered on the channel; it gates
merge, and no finished in-tree review record is claimed in this
directory. The module's check verifies the registration's exact
bytes, spans, and round trip only. Rendered behavior is covered by
`tools/ask_entry_scroll_runtime_qa.js` (wired into the Site QA DOM
step beside `tools/ask_composer_scroll_runtime_qa.js`, which stays
green unchanged) and by the post-merge live census in the release
finisher, not by this registration.
