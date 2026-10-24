# A047 citation rendering successor registration

This directory registers one exact change set: the A047 citation
rendering correction in `ask.html`, built as PR #515 on branch
`feature/a047-citation-rendering` (the Ask page's `addMessage`
appended every source to one group titled "Official Church sources",
so a reviewed record's own focusChrist study page rendered as a pill
under the official Church heading, and the study-source router then
linked the same page a second time in its "Related focusChrist study"
group; `addMessage` now classifies each source by its actual URL host
at render time, keeping the groups' provenance apart).

- ask.html: predecessor SHA-256
  `735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612`,
  candidate SHA-256
  `4881b5a20ed045b1d45dd1c393d3204c56cf46692d7fa4837e5257346aa4e7a9`.
  Five spans in candidate-byte coordinates, together exactly the
  PR #515 edit (+53/-11 lines), all inside `addMessage`'s sources
  block:
  - [411516, 413775): the single official-group construction (525
    bytes) replaced with the host classification setup: the Church
    and site host sets, the per-group constructors for the official,
    related, and referenced groups (2259 bytes).
  - [413776, 413822): the cross-group dedupe set
    (`renderedSourceUrls`) inserted (46 bytes, empty previous bytes).
  - [414095, 414213): the dedupe guard inside the per-source loop
    inserted (118 bytes, empty previous bytes): a destination already
    rendered is skipped, and each rendered destination is recorded.
  - [414707, 415388): the unconditional official-list append (48
    bytes) replaced with the host classification branch that routes
    each link to the official, related (with the
    `data-focuschrist-answer-source` dedupe marker), or referenced
    group (681 bytes).
  - [415505, 415855): the single conditional group append (94 bytes)
    replaced with the per-group conditional appends, so each group
    renders only when it holds a link (350 bytes).

The predecessor hash is exactly the after hash the answer-bank
successor layer (docs/answer-bank-successor/manifest.json) pins for
ask.html; this layer strips back to it, the answer-bank layer then
strips back to the state the continue-motion predecessor map
(docs/continue-motion/predecessors.json) pins as current for ask.html
(`4a5f73ee35fb5cd8d1a9d30109f7daf9f85f7e3913fb5e3cc012a996d6058db3`),
and the motion chain then reconstructs the historical predecessor
`bbeeb8c6e40d4b55a7949ba7544200796457df1ad975fbd2bdb9b75f9d8c8a04`.
`manifest.json` is pinned in `tools/citation_rendering_successor.py`
as `SOURCE_SHA`. That pin records the exact candidate spans only. It
is not review approval. No answer-bank manifest, module, or review
record, no display-gate layer, no predecessor map, MAP_SHA, or motion
review record is changed by this layer. Because the answer-bank
layer's check reads ask.html raw, the continue-motion binding
validates that layer against the citation-restored projection of
ask.html (a temporary view) rather than the raw final bytes, without
altering the answer-bank layer itself.

## Review model

The code change in PR #515 was independently reviewed by Jeff in
J-2026-10-24-075 (CONCUR WITH CONDITIONS: the Church host set and the
related-group design ruled correct as built; C1 requires this
registration delta on the same branch, C2 requires Jeff's independent
re-review of the resulting head and green CI at that head before any
merge). That re-review is delivered on the channel and gates the
merge; no finished in-tree review record is claimed in this
directory, and the module's check verifies the registration's exact
bytes, spans, and round trip only.
