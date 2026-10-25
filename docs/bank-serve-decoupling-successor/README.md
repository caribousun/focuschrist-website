# Bank-serve decoupling successor

Registration layer for the reviewed-bank decoupling fix, spanning two
files:

- `ask.html`: the inline legacy `sendMessage` controller consults the
  reviewed answer bank lane before its legacy lookup, so a bank-bound
  question is answered by the bank whichever controller owns the ask.
- `site-common.js`: the display gate's reviewed-bank exemption is
  bound through the bank-owning code. The lane's `verifyPinnedServe`
  must confirm the claimed record ID, whole-entry pin, exact served
  answer, and sources against the loaded, pin-checked bank; a forged
  marker, a wrong pin, an edited answer, or a stale, unreviewed, or
  missing record earns no exemption.

Why: in `study-intelligence-v3.js` the composed path awaited the live
scripture lookup before consulting the bank, so a failed or hung live
leg could withhold reviewed bank answers, and the gate replaced
unmarked renders wholesale with its fail-closed fallback when the
library promise rejected (41 of 106 trials in the 2026-10-24 demo
census). The v3 reorder itself is in `study-intelligence-v3.js`,
which is not a pinned file; this layer registers the two pinned files
the fix touches.

The layer sits outermost over both files: its ask.html BEFORE state
is the legacy answer repairs successor's AFTER state (which composes
over the citation rendering successor's AFTER state), and its
site-common.js BEFORE state is the evaluator corrections successor's
AFTER state. The continue-motion binding composes it innermost on
restore and outermost on advance. `manifest.json` pins the exact
spans; `tools/bank_serve_decoupling_successor.py` verifies bytes,
spans, and the round trips. The pin is not review approval: the
independent exact-head review of the PR carrying this registration
(Jeff, with Newton's parallel review) gates merge.
