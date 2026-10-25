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

Amendment (2026-10-25): the ask.html span now also renders the
served record's follow-up chips. The only chips renderer lived
inside study-intelligence-v3.js, which replaces the inline
controller only once it loads; a bank serve completed by the inline
controller therefore rendered the full reviewed answer and sources
with no chips, permanently for that serve (diagnosis:
fcfix2/chips-diagnosis, 78 instrumented probes; chips presence
separated perfectly on which controller owned the submit). Inside
the existing span, the inline serve captures the node `addMessage`
returns (the display gate's pending node, whose synchronously
appended children survive its verified-content swap, the mechanics
the v3 renderer relies on) and appends the identical adjunct the v3
renderer builds: the "Additional questions" heading as the group's
sibling, then the `ask-followup-chips` group carrying
`data-followup-for`, one button per chip from the lane's
`followUpChips()` with its `data-followup-target`, wired to set the
input and call `window.sendMessage()`. The block runs only on the
inline lane serve, which returns before the v3 controller can serve
the same submit, so no serve can render two groups. The span's
previous bytes, this layer's BEFORE states, and the site-common.js
registration are unchanged; the span's current bytes grow in place
and the entry-scroll successor above it is re-pinned mechanically
with its span bytes unchanged. Proof: tools/ask_bank_serve_chips_runtime_qa.js
exercises both controllers against the shipped bank.

Amendment (2026-10-25, lane readiness): the ask.html span's inline
controller now waits for the bank lane before producing any
outcome when the lane has not arrived yet. The bank scripts are
deferred and answer-bank-data.js alone is about 800 KB; on a slow
connection a visitor who types and submits in the first seconds
reached the controller while window.FocusChristAnswerBankLane
was still unset, fell through to the legacy askAI stub, and was
shown its "couldn't find a supported answer" verdict for
questions the bank answers (diagnosis:
fcfix2/endure-pill-diagnosis, defect 2; the failing attempt
instrumented lanePresent=false and bankDataPresent=false at
submit, and the failure reproduced under Slow 4G throttling in
two independent probes). Inside the existing span: when the lane
is absent at submit, the controller polls every 100 ms for up to
10 seconds (the window the throttled probes measured the lane
arriving in) and then consults the lane exactly as before. The
visitor's question is already rendered and the existing loading
indicator already runs; both stay through the wait, and no new
visitor-facing wording is introduced. If a newer submit or a
chat clear replaced the exchange during the wait (this submit's
loading node is no longer in the chat box), the superseded
submit renders nothing further, so repeated interaction can
never produce two answers. If the lane never arrives inside the
bound, the controller renders the temporary state the site
already uses when its approved study sources cannot be checked
(the v3 controller's SOURCE_UNAVAILABLE message, word for word)
and returns: the legacy lookup never runs on that path, so a
bank that was never asked is not treated as a proven miss, and
there is no fallthrough to any research leg as a substitute for
waiting. Readiness is the lane's presence with an answer
function: the lane script publishes the lane only after its
fail-closed loadBank has verified every record's whole-entry
pin, so presence is the validation-completed signal. Once the
lane is present, behavior is unchanged, including the fallthrough
of a genuine non-serve to the legacy lookup. The span's previous
bytes, this layer's BEFORE states, and the site-common.js
registration are unchanged; the entry-scroll successor above is
re-pinned mechanically with its span bytes unchanged. Proof:
tools/ask_bank_lane_readiness_runtime_qa.js exercises
delayed-lane, ready-lane, genuine-miss, readiness-failure, and
repeated-submit paths against the shipped bank.
