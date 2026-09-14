# Body gutters and theme flow, 14 September 2026

The owner requested uniform horizontal and vertical breathing room and softer
theme transitions, using Home and Watch as examples. This follows the published
section-spacing correction without changing its protected opening behavior.

Opaque full-width fills, wrapper borders and inset shadows caused Home's hard
bands. Body wrappers now fade to transparent at both vertical edges, with subtle
green or darker blue accents. Nested card fills and boundaries remain. One
16–24px outer gutter aligns comparable body containers; reading and gallery
maximum widths remain intentional. Watch's topic card and featured section share
the full section gap. Heroes, introductions, images, text and controls are intact.

Independent review caught a double gutter inside already constrained Ask and
article main containers. A scoped full-width, zero-inline-margin exception
corrects those children while preserving their internal padding. Twelve fresh
phone/desktop cases verify matching parent edges. This is why container ancestry
must be checked instead of applying viewport insets indiscriminately.

Local verification: 37 public routes at 390×844 and 1280×900, 74 settled layout
cases and 584 section observations, no overflow and unchanged compared opening
rectangles. Home wide-desktop/phone and Watch desktop screenshots show the softer
flow with readable cards. All 102 workflow commands passed; four relevant checks
passed after the nested-container correction. The connected-study rerun required
Python UTF-8 on Windows; its initial default-codepage failure is an environment
failure, not a content-integrity exception. Final independent review ACCEPT.

The final computed-style pass covers all 70 applicable outer wrappers at both
widths (140 observations). It caught higher-priority About closing and History
Ask rules; these now fade as well, with no opaque wrapper edges or visible
boundary borders remaining in that inventory. The About override is corrected
at its existing source instead of adding another important-selector override.
Unified presentation, Church History and production-hardening checks passed
after these two final background-only adjustments.

Public deployment, exact bytes and rendered acceptance are recorded separately
in the canonical release receipt. Future reviews should compare outer edges,
combined section gaps, nested card ancestry, actual theme boundaries and settled
screenshots while retaining the opening and source-integrity checks.
