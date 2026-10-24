# A047 evaluator corrections successor registration

This directory registers one exact change set: the A047 Step S
evaluator corrections in `site-common.js`, built as PR #512 on branch
`feature/a047-evaluator-token-boundary`. The corrections are (1)
token-boundary profanity matching: the whitespace-stripped compact
string is never tested as a whole again, because joining across
ordinary words creates false hits (the compact form of "publish its"
contains "shit", and the live bank phrasing "Does the Church publish
its finances?" was blocked as respect-boundary on main); and (2)
defect D4: bare past-tense "hurt me" leaves the urgent-safety
alternation only inside a forgiveness question stating the harm as a
completed act in a subordinate construction, with no stated future,
threatened, or intended harm, so the forgiveness record's canonical
can serve. The release's blocker alternation carries the four
stated-intent forms Jeff's adversarial probing of the first candidate
required (threatens to, plans to, intends to, promised to, each with
"hurt me"). The same evaluator change is mirrored in
`groq-proxy/src/index.js`, which carries no hash pin and is not
registered here.

- site-common.js: predecessor SHA-256
  `9090c0bf19a4093f881bf0d1f9f95236ec1db8d61a7072251d807f5c9ce3a041`,
  candidate SHA-256
  `54cfb9fc5de9c5ab76133cb32843053ee6c5700ff0fe11d8bedd470de3412a77`.
  Four spans in candidate-byte coordinates, together exactly the
  PR #512 evaluator edit as amended by Jeff's condition C1:
  - [10731, 13120): the two helpers inserted (2,389 bytes, empty
    previous bytes): the token-boundary comment and
    `compactProfanityHit`, then the release comment and
    `pastHurtForgivenessRelease`.
  - [13228, 13228): the whole-string compact construction line
    `const compact = normalized.replace(/\s+/g, '');` removed
    (56 bytes, empty current bytes).
  - [13494, 13688): the urgent alternation line replaced (123 bytes)
    with the alternation without bare "hurt me", closed by the
    release-gated clause
    `|| (/\bhurt me\b/.test(normalized) && !pastHurtForgivenessRelease(normalized));`
    (194 bytes).
  - [14477, 14524): the compact whole-string `matchesAny` block
    (121 bytes) replaced with `]) || compactProfanityHit(normalized);`
    (47 bytes).

The predecessor hash is exactly the after hash the display-gate
successor layer (docs/display-gate-successor/manifest.json) pins for
site-common.js; this layer strips back to it, the display-gate layer
then strips to the continue-motion predecessor map's after hash
`4a7e22262e1a62e9b9e119cc83b70f02f6fc2902a935d03ffec77f67333911a9`,
and the motion chain reconstructs the historical predecessor
`fc0ae667fd977c6cd66ef2e649ef9da2cbcf5eee4201094dd90ed48b551e6488`.
`manifest.json` is pinned in `tools/evaluator_corrections_successor.py`
as `SOURCE_SHA`. That pin records the exact candidate spans only. It
is not review approval. No predecessor map, MAP_SHA, or motion review
record is changed by this layer.

## Review model

The code change in PR #512 was independently reviewed by Jeff in
J-2026-10-24-074 (CONCUR WITH CONDITIONS). Conditions C1-C3 of that
review require the blocker fix (delivered in the commit beneath this
registration on the same branch), this registration delta, Jeff's
independent re-review of the resulting head, and green CI at that
head before any merge. That review is delivered on the channel and
gates the merge; no finished in-tree review record is claimed in this
directory, and the module's check verifies the registration's exact
bytes, spans, and round trip only.
