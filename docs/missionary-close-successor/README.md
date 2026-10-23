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

## Review evidence model (A-2026-10-23-002 amended split)

Albert's A-2026-10-23-002 decision amended the evidence route for this layer.
The gate now requires three separate, explicitly scoped, hash-bound records
in `reviews.json`. No scope may stand in for another, and no blanket true
flags may be set on a record beyond what its author actually verified.

1. **Jeff registration/source review (RECORDED).** Jeff is the independent
   registration and source-behavior reviewer. His receiver-authored review
   J-2026-10-23-007 (decision CONCUR) is recorded with
   `finished_pixels: false`, exactly as he reported it: he verified the
   diff, hashes, composition, tests, and the source-level wiring (13
   triggers, one shared dialog, the pill wired to `dialog.close()`), and he
   did NOT inspect rendered pixels. His exact review bytes are the evidence
   file `jeff-registration-review-j007.json` in this directory, hash-bound
   in `reviews.json`. Source wiring is not rendered behavior and is never
   relabeled as such.

2. **Merlin rendered evidence collection (COLLECTED).** Before merge, Merlin
   renders the exact candidate bytes (served from the candidate Git head,
   not current production) on a desktop viewport and a narrow phone
   viewport (phone emulation is acceptable if honestly labeled), opens the
   commission panel plus representative other shared-dialog triggers, and
   verifies: Close visible and in bounds; ordinary pointer/touch activation
   actually closes the dialog; keyboard operation and returned focus;
   Continue Lesson and the X control retained; 13 trigger/content parity.
   Actual screenshots and observed results, with viewport, browser, and
   served Git head / page / script hashes, are recorded here and hash-bound
   as `rendered_evidence`. Collection is evidence gathering, not approval:
   Merlin is the executor and cannot approve his own rendered result.

3. **Independent rendered review (FINISHED).** Jeff may independently
   inspect the captured pixels and results and author a new review bound to
   the exact capture/evidence hashes; browser ownership is not required for
   image review, but actual visual inspection is. If Jeff cannot view the
   images, Albert performs this finished-image/result review instead. The
   record must name the actual reviewer (Jeff or Albert), scope `rendered`,
   decision CONCUR, and `finished_pixels` / `finished_behavior` true, bound
   to the capture hashes. Wyatt is not the required premerge tester.

## Gate and pin status

Status: COMPLETE. All three scopes are recorded in `reviews.json`:
scope 1 by Jeff's J-2026-10-23-007, scope 2 collected by Merlin
(Chrome for Testing 156 headless, desktop 1440x1000 and phone-emulated
390x844, captures under `rendered/`, stored as base64 text (`.png.b64`) so QA screenshots never enter the site artwork raster inventory; the gate decodes them and binds the exact PNG bytes by hash), and scope 3 by Jeff's
J-2026-10-23-009 rendered CONCUR bound to the capture hashes. The
completed `reviews.json` is pinned as `APPROVED_REVIEWS` by its
canonical hash in `tools/missionary_close_successor.py`. The gate still
rejects absent, wrong-scope, wrong-actor, unfinished, or tampered
records in any scope, even if resealed.

This gate/schema change itself requires a fresh independent Jeff source and
test review before any pin. Only after every scope is complete with actual
reviews may the finished `reviews.json` be recorded and pinned as
`APPROVED_REVIEWS` in `tools/missionary_close_successor.py`, followed by CI
green at the same final reviewed head, an expected-head merge, deployment,
and ordinary public byte and live desktop/phone verification.
