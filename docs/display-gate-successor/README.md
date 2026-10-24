# Display-gate bank exemption successor registration

This directory registers one exact change set: the scripture display
gate exemption for pinned reviewed-bank serves in `site-common.js`,
built as PR #509 on branch `feature/display-gate-bank-exemption`
(the display-gate fix for the answer bank: the gate in site-common.js
re-verified rendered answers with the scripture library's
checkAnswer and replaced 54 of the 222 reviewed bank answers at
render; the exemption renders a serve as served when the answer bank
lane's complete provenance marker is present).

- site-common.js: predecessor SHA-256
  `4a7e22262e1a62e9b9e119cc83b70f02f6fc2902a935d03ffec77f67333911a9`,
  candidate SHA-256
  `9090c0bf19a4093f881bf0d1f9f95236ec1db8d61a7072251d807f5c9ce3a041`.
  Three spans in candidate-byte coordinates, together exactly the
  PR #509 edit (+18/-2 lines):
  - [60694, 60870): the `focusChristVerifyScriptureAnswer` signature
    line replaced (79 bytes) with the three-parameter signature and
    the pinned-bank early-return line (176 bytes).
  - [61427, 62287): the `isPinnedReviewedBankServe` predicate
    inserted (860 bytes, empty previous bytes).
  - [63071, 63162): the display-gate wrapper call line replaced
    (84 bytes) with the call passing its fourth argument through
    (91 bytes).

The predecessor hash is exactly the after hash the continue-motion
predecessor map (docs/continue-motion/predecessors.json) pins for
site-common.js; the layer strips back to it, and the motion chain
then reconstructs the historical predecessor
`fc0ae667fd977c6cd66ef2e649ef9da2cbcf5eee4201094dd90ed48b551e6488`.
`manifest.json` is pinned in `tools/display_gate_successor.py` as
`SOURCE_SHA`. That pin records the exact candidate spans only. It is
not review approval. No predecessor map, MAP_SHA, or motion review
record is changed by this layer.

## Review model

The code change in PR #509 was independently reviewed by Jeff in
J-2026-10-24-068 (CONCUR WITH CONDITIONS). Conditions C1-C3 of that
review require this registration delta on the same branch, Jeff's
independent review of the resulting head (registration-source scope
plus a delta spot-check that the code diff is unchanged), and green
CI at that head before any merge. That review is delivered on the
channel and gates the merge; no finished in-tree review record is
claimed in this directory, and the module's check verifies the
registration's exact bytes, spans, and round trip only.
