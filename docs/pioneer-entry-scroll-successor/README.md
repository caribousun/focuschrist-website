# Pioneer entry scroll-follow successor registration

This directory registers one exact change set: the Pioneer
conversation scroll-follow fix in `pioneers.html` and
`pioneer-experience.js`, built on branch
`feature/pioneer-entry-scroll-follow-2026-10-25`. It is the
Pioneers counterpart of the Ask entry scroll fix in PR #520
(docs/entry-scroll-successor/).

The defect: the Pioneers page carries the same defect class
through its own code. In pioneers.html, the page's own
`addMessage` ended by forcing the internally scrolling chat
panel to its absolute top (`c.scrollTop=0`) on every append; it
never anchored the entry just added. The transcript is not
single-use (story, choice, and journey flows append without
clearing), so the forced top shows the oldest content in the
box, not the new entry. In pioneer-experience.js, whose
`window.addMessage` override is the live append path on the
page, the append itself performed no anchoring at all: anchoring
depended on each caller remembering `positionAnswer()`. The
composer answer paths call it, but the choice-list append in
`renderPioneerChoices`, the `askTellMyStory` error appends, and
the `askTopic` error append never anchor the entry they add, so
those entries can land outside the visitor's view.

The fix:

- pioneers.html: a new `bringEntryIntoView(entry)` helper (the
  same helper PR #520 added to ask.html) sits directly above
  `addMessage`, and `addMessage` calls it on the appended entry
  in place of the top-force assignment. `scrollIntoView` with
  `block: 'start'` scrolls every scrollable ancestor, so the new
  entry's top lands at the top of the internally scrolling chat
  panel and the panel is brought into the window's view. It runs
  on every append through the page's own implementation and
  never on page load.
- pioneer-experience.js: a new `bringPioneerEntryIntoView(entry)`
  helper sits directly above `window.addMessage`, and
  `window.addMessage` calls it on the message immediately after
  appending it. Every append through the live path now anchors
  its own entry, including the choice-list, story, and error
  appends that never call `positionAnswer`. The composer paths
  keep their existing exchange-level refinement: `positionAnswer`
  still promotes the newest exchange and positions it after the
  append, unchanged. `window.addMessage` still returns the
  appended message element, so every existing caller is
  unchanged.

Registered spans (candidate-byte coordinates):

- pioneers.html: predecessor SHA-256
  `0674855075616de71f8b89b8b6e3b0145a48e80cc7e7f1b8b7a64874b77fa05d`,
  candidate SHA-256
  `b9275099d3a124a940e3c402d905c7994be2fbaf6fe69caebf28481e84078e4f`
  (317,309 bytes). Two spans:
  - [176973, 177236): the `bringEntryIntoView` helper inserted
    (263 bytes, empty previous bytes) directly above
    `addMessage`.
  - [178489, 178510): the top-force assignment `c.scrollTop=0`
    (13 bytes) replaced with the `bringEntryIntoView(d)` call
    (21 bytes).
- pioneer-experience.js: predecessor SHA-256
  `b1f6f02625377c9f28850e88d707c4e9837c0d6c183510463b65448294cfb9cb`,
  candidate SHA-256
  `2baf4d3cef128337fb687f99299d21ebdcf4831cd781d5fa8b72fee6955f00cd`
  (87156 bytes). Two spans:
  - [39308, 39753): the `bringPioneerEntryIntoView` helper
    inserted (445 bytes, empty previous bytes) directly above
    `window.addMessage`. The helper text is the amended text
    described under "Composer-path amendment" below.
  - [43058, 43136): the append line
    `box.appendChild(message);` (34 bytes, with its indent and
    newline) replaced with the append plus the
    `bringPioneerEntryIntoView(message);` call (78 bytes).

The pioneers.html predecessor hash is exactly the after hash
the legacy-answer-repairs successor layer
(docs/legacy-answer-repairs-successor/manifest.json) pins for
pioneers.html; this layer strips back to it, the legacy layer
then strips back to the answer-bank layer's after state
(`b2b988d240a7d54b60b2d2701fde26f54fa6ca1b63261b3d7f7f9e89377a3bf5`),
the answer-bank layer strips back to the state the
continue-motion predecessor map pins as current for
pioneers.html
(`57fe21dc3a92dde1b5c51cddcf872cabe62d1e88a7ec259fc135afaa80cb8b81`),
and the motion chain then reconstructs the historical
predecessor
`b2ed6c9a12d25600262997235fa9971972dddd93f0ef26cad852f7ab66ffc0e0`.
The pioneer-experience.js predecessor hash is exactly the
after hash the answer-bank layer pins for pioneer-experience.js;
this layer strips back to it, the answer-bank layer strips back
to the state the continue-motion predecessor map pins as
current for pioneer-experience.js
(`229d4698dd9316af84047e295134636f77ed9965291c5444c03183fa54487593`),
and the motion chain then reconstructs its historical
predecessor
`427b27638ea9bcc1509b046e38e52e0daad6979b5aca2a3ddf4033b5bda72449`.

`manifest.json` is pinned in
`tools/pioneer_entry_scroll_successor.py` as `SOURCE_SHA`.
That pin records the exact candidate spans only. It is not
review approval. No legacy, answer-bank, or other manifest,
module, or review record, no other successor layer, no
predecessor map, MAP_SHA, or motion review record is changed
by this layer. Because the answer-bank layer's check and the
legacy layer's check read the pioneer files raw, the
continue-motion binding validates those layers against restored
projections of the pioneer files (temporary views) rather than
the raw final bytes, without altering those layers themselves.

Sequencing note: this layer was built on main
`3584d138980097886ef4a32a8a3204e3e4c39ec5`, which already
includes PR #516 (the legacy answer repairs layer), PR #518
(the bank-serve decoupling layer), and PR #520 (the Ask entry
scroll layer this fix parallels). Neither pioneer file was
touched by those PRs' content changes beyond the layers already
registered above them.

## Composer-path amendment (2026-10-25)

The original registration above shipped in PR #522. Its finisher's
live watch then caught a regression on the typed composer path:
after a first exchange, a second typed question left the panel
scrolled to the middle of the previous answer, with the promoted
newest exchange entirely above the visible region. Swapping only
pioneer-experience.js back to the pre-#522 bytes anchored
correctly, isolating the cause to this layer's append-time
scrollIntoView. An instrumented live probe (wrapped
scrollIntoView/scrollTo with stacks) pinned the mechanism:
site-common's scripture display gate wraps window.addMessage, so
a bot answer is first rendered as a [data-scripture-pending]
placeholder; the caller positions that placeholder
(positionAnswer promotes the exchange and sets the panel scroll);
only then does the gate call the real addMessage, whose
append-time scrollIntoView fired after positioning and dragged
the panel to the appended element's position at the end of the
transcript (observed scrollTop 13 -> 2502 -> 3285). The
answer-ready listener's re-positioning is suppressed when an
earlier exchange follows the promoted one in DOM order, so the
wrong scroll stood. In the topic path the same late scroll is
repaired by that listener, which is why topic appends looked
correct, and the pre-#522 bytes never scroll on the late append
at all.

The amendment changes one span: the helper text in span 1. The
helper is called immediately after the append, so the entry's
parent is the chat box; when that box still holds a
[data-scripture-pending] placeholder, this append is the gate's
real-answer append (or a concurrent append inside the same gate
window) whose content is transplanted into the already
positioned placeholder, and the helper returns without
scrolling. Every append with no gate placeholder pending keeps
the original scrollIntoView anchor unchanged, so the
choice-list, story, and error appends that never call
positionAnswer are still anchored: directly at append time when
no gate placeholder is pending, and through the placeholder's
own positioning (caller positionAnswer and the answer-ready
listener) when one is. positionAnswer,
promoteLatestExchangeToTop, the append-returns-element
contract, and the helper's null and scroll-less guards are
unchanged. pioneers.html is not changed by the amendment: its
own addMessage has no positionAnswer composition, and its
appends keep the immediate anchor.

The layer's BEFORE pins are unchanged (pioneers.html
06748550..., pioneer-experience.js b1f6f026...); only the
pioneer-experience.js AFTER pin and span 1 moved, with a new
SOURCE_SHA. tools/pioneer_entry_scroll_runtime_qa.js is extended
with a composed scenario that runs the real helper, addMessage,
promoteLatestExchangeToTop, positionAnswer, and the answer-ready
listener together through a simulated display-gate wrapper, so
the composer path is exercised as a composition, not in
isolation; the pre-amendment bytes fail that scenario's composer
case and the amended bytes pass it.

## Review model

The independent review of this registration is Jeff's exact-head
review of the PR carrying it, delivered on the channel; it gates
merge, and no finished in-tree review record is claimed in this
directory. The module's check verifies the registration's exact
bytes, spans, and round trip only. Rendered behavior is covered
by `tools/pioneer_entry_scroll_runtime_qa.js` (wired into the
Site QA Pioneer step beside
`tools/pioneer_composer_scroll_runtime_qa.js`, which stays green
unchanged) and by the post-merge live census in the release
finisher, not by this registration.
