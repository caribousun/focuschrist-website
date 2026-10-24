# Answer bank (step 1) successor registration

This directory registers one exact change set: the wiring that lets the
reviewed 168-record answer bank serve on the Ask and Pioneer pages
(step (1) of the answer-engine release).

- ask.html: predecessor SHA-256
  `4a5f73ee35fb5cd8d1a9d30109f7daf9f85f7e3913fb5e3cc012a996d6058db3`,
  candidate SHA-256
  `735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612`.
  One insertion span of 321 bytes at candidate bytes [9707, 10028): the
  four deferred answer-bank script tags (answer-bank-data.js,
  answer-bank-matcher.js, answer-bank-guards.js, answer-bank-lane.js,
  each with `?v=20261023-answer-bank-1`) placed immediately after the
  reviewed-ask-knowledge.js tag, with empty previous bytes.
- pioneers.html: predecessor SHA-256
  `57fe21dc3a92dde1b5c51cddcf872cabe62d1e88a7ec259fc135afaa80cb8b81`,
  candidate SHA-256
  `b2b988d240a7d54b60b2d2701fde26f54fa6ca1b63261b3d7f7f9e89377a3bf5`.
  The same 321-byte insertion at candidate bytes [16265, 16586).
- pioneer-experience.js: predecessor SHA-256
  `229d4698dd9316af84047e295134636f77ed9965291c5444c03183fa54487593`,
  candidate SHA-256
  `b1f6f02625377c9f28850e88d707c4e9837c0d6c183510463b65448294cfb9cb`.
  One insertion span of 399 bytes at candidate bytes [71012, 71411):
  the guarded bank branch at the top of researchDisclosure, with empty
  previous bytes.

The predecessor hashes are exactly the after hashes the continue-motion
predecessor map (docs/continue-motion/predecessors.json) pins for these
files; the layer strips back to them, and the motion chain then
reconstructs the historical predecessors. `manifest.json` is pinned in
`tools/answer_bank_successor.py` as `SOURCE_SHA`. That pin records the
exact candidate spans only. It is not review approval. No predecessor
map, MAP_SHA, or motion review record is changed by this layer.

## Review evidence model (A002 split scopes)

Three separate, explicitly scoped, hash-bound records are required in
`reviews.json`. No scope may stand in for another, and no blanket true
flags may be set on a record beyond what its author actually verified.

1. **Jeff registration/source review.** Jeff is the independent
   registration and source-behavior reviewer for Merlin-carried work.
   His review must cover this registration itself (module, manifest,
   spans, binding composition, tests) at the exact PR head, with
   `finished_pixels: false`. Jeff's J-2026-10-23-047 concurrence covers
   the candidate change (the ten answer-bank files and their wiring,
   including the rendered evidence collected for the candidate); it is
   not this registration review and is not recorded as one.
2. **Merlin rendered evidence collection.** Before the pin, Merlin
   renders the exact candidate bytes on desktop and phone viewports,
   opens the Ask bank serve, the sensitive-record serve, the suggestion
   path, both fall-throughs, and a Pioneer item disclosure opened in
   frame, and records captures (stored as base64 text, `.png.b64`, so
   QA screenshots never enter the site artwork raster inventory) and
   observations under `rendered/`, hash-bound as `rendered_evidence`.
   Collection is evidence gathering, not approval.
3. **Independent rendered review.** Jeff inspects the captured pixels
   and results and authors a rendered review bound to the exact capture
   hashes, with `finished_pixels` and `finished_behavior` true.

## Gate and pin status

Status: PENDING. No scope is recorded yet. `reviews.json` carries
`status: PENDING`, and `tools/answer_bank_successor.py` carries
`APPROVED_REVIEWS = None`, so the gate blocks with
"Answer bank successor finished review PENDING" and the continue-motion
binding reports exactly that block. Only after every scope is complete
with actual reviews may the finished `reviews.json` be recorded and
pinned as `APPROVED_REVIEWS`, followed by CI green at the same final
reviewed head, an expected-head merge, deployment, and ordinary public
byte and live desktop/phone verification.
