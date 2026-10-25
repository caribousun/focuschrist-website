# Bank context bypass successor

Registration layer for the Ask generic-context bank bypass fix, in one
file:

- `study-intelligence-v3.js`: inside `askV3`, when
  `resolveQuestionContext` classifies the visitor's question as a
  generic-context follow-up (`genericContext=true`), the reviewed
  answer bank is first matched against the visitor's ORIGINAL
  wording, and an actual bank serve (never a suggestion set) returns
  before the generic-context guard can suppress the bank. The
  death-as-background and support-request guards still suppress the
  new match exactly as they suppress the existing local lanes.

Why: `resolveFollowup` treats any question containing a referential
token (it, that, this, he, they, ...) as a follow-up candidate. A
complete, self-contained bank canonical such as "What does it mean
to endure to the end?" was reclassified whenever any earlier question
existed in the session; `genericContext` became true, `askV3` set
`allowContextualLocalMatch=false`, and the bank was never consulted.
The question fell to the live research leg, which rendered either a
generated answer or the fail-closed "I'm unable to check our
approved study sources right now" message. That chip under the
faith-during-trials answer is the only pill carrying the question,
so the natural visitor path never served its reviewed record. The
verdict sweep in the diagnosis (`fcfix2/endure-pill-diagnosis`) shows
all 13 bank canonicals containing a referential token flip to
`genericContext=true` with any one-question history, and none
without; fresh single-question sessions were unaffected, which is
why every census missed the defect.

The guard's purpose is preserved: a genuinely elliptical follow-up
("How old was he?") whose own wording the bank does not serve keeps
the existing flow unchanged, because only an actual serve on the
original wording short-circuits, and the augmented generic-context
query still never reaches a local lane.

`study-intelligence-v3.js` was not a pinned file before this layer
(the bank-serve decoupling successor's README records that status);
this layer pins it for the first time. Its BEFORE state is the exact
file at the base of this change, and no other registration composes
over it, so restoration reproduces those bytes directly. The layer
is registered in the composed binding chain in
`tools/continue_motion_binding.py` (restore, advance, and check),
which the CI gate step runs. `manifest.json` pins the exact span;
`tools/bank_context_bypass_successor.py` verifies bytes, spans, and
the round trip. The pin is not review approval: Jeff's independent
exact-head review of the PR carrying this registration gates merge.

Proof: `tools/ask_bank_context_bypass_runtime_qa.js` exercises the
composed v3 path in two-question sessions: all 13 referential-token
bank canonicals serve their records with a real first question in
history (the endure canonical after the faith-during-trials starter,
the chip path), genuinely elliptical follow-ups still resolve
contextually with no bank force-match, fresh single-question serves
are unchanged, and a non-bank question with history still reaches
the research leg. The same cases run against the layer's BEFORE
bytes to pin the pre-fix outcome classes.
