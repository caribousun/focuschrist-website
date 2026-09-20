# Mobile opening spacing and introductions

Wyatt approved PR348's common mobile hero sizes and directed that they be locked. This refinement preserves the entire reviewed CSS baseline, including image heights and focal points, and adds only text spacing and conditional explanatory copy. No artwork, sides, surrounds, desktop presentation, source links or full-size paths change.

## Spacing correction

Rendered inspection found 6px gaps on main pages, a later 12px topic rule, 8px Conference gaps, extra action margins, and a zero effective eyebrow-to-heading gap on Come Follow Me. A shared 8px text gap now applies to all opening text wrappers. Local action and Come Follow Me margins are reset; the first text starts 10px below the image on those two special templates, matching standard openings. Continue retains its approved appearance and bottom position.

## Optional section descriptions

Twenty-six topic and art-study openings have a brief authored guide to the section. Main pages already have descriptive introductions, so they do not receive duplicate paragraphs. The previous unused reflection-question code is replaced.

The paragraph appears at its normal .9rem font size only if it fits the spare area. A fit check first measures the opening, hero, heading, action groups and Continue without the paragraph. It then rejects the paragraph if any of those bounds move, the opening exceeds the viewport, the text overflows horizontally, or less than 16px remains before Continue. It never reduces the font size, squeezes controls or changes image height. Resize, breakpoint, font readiness and element-size changes repeat the check. The original full study remains available regardless of whether the optional guide fits.

## Verification

- 240 rendered opening checks: 40 openings at 320×568, 375×667, 390×740, 412×775, 430×844 and 700×900. All images retained PR348's exact heights at each size; all checked text wrappers used 8px gaps; controls and openings fit without horizontal overflow.
- 134 of the 156 eligible page/size combinations displayed a description. All 26 appeared at 430×844. Conditional visibility is intentional: a description is omitted whenever the measured space is insufficient.
- Forty desktop opening comparisons against PR348 matched visible text, dimensions, typography, backgrounds and image positions. The hidden paragraph is absent from the desktop accessibility tree.
- Forty doubled-text checks at 320px passed opening containment. Optional descriptions were omitted, leaving the existing readable text and controls to expand naturally.
- Birth of Christ remained stable across 430→320→430 resizing and return navigation after Continue. Runtime regression checks cover insufficient clearance, moved headings/actions/cue, changed opening height, horizontal overflow, desktop, resize and page-specific copy.
- Visual review covered the special templates and representative new descriptions, including Birth of Christ, Eternal Marriage, Look Unto Me, Good Shepherd, Stand Forever and Melchizedek Priesthood. Independent review approved the implementation and authored descriptions.

The mobile-scene guard now locks the exact PR348 stylesheet baseline and rejects new hero-height or focal-point overrides in the copy layer. The existing exact stylesheet review gate protects the new additions. Hosted CI, deployment, live checks and owner feedback remain separate evidence.
