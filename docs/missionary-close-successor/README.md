# Missionary Close successor registration

This directory registers one exact change: the standard Close pill added to
the Mission detail dialog in `missionary.html` (PR 500).

- Predecessor SHA-256: `028f7bc23aa9c7a21e8cc2def40c429ba5ea628880347653292974e8fe7caa31`
- Candidate SHA-256: `e5696e60b60faef5f456647ff2a153b939871acb895a6671d3d95a718d2ad55a`
- The manifest records the single minimal insertion span: 104 bytes
  (20 spaces, the Close button markup, and the original newline), with empty
  previous bytes, measured in candidate (after) bytes.
- `manifest.json` is pinned in `tools/missionary_close_successor.py` as
  `SOURCE_SHA`. That pin records the exact candidate spans only. It is not
  review approval.

## Review evidence status: PENDING

The required independent reviewer for this layer is Jeff, as designated by
Wyatt for Merlin-carried work. `reviews.json` stays PENDING with no finished
flags set and no review entry until Jeff's own finished review exists.

Jeff's finished review is a separate, receiver-authored step after this
registration candidate. It must cover two scopes:

1. The page change itself: source, placement, and wiring review bound to the
   unchanged candidate page SHA above (the scope of Jeff's earlier
   J-2026-10-22-006 review on the channel).
2. A new finished registration review bound to the final code-file hashes,
   the manifest canonical hash, the complete test results, and the page SHA,
   including Jeff's own check of the actual Close behavior and pixels.

Only after that review says CONCUR may its evidence file be added here by its
author, recorded in `reviews.json`, and pinned as `APPROVED_REVIEWS` in
`tools/missionary_close_successor.py`. No evidence file for Jeff is authored
as part of this registration candidate.
