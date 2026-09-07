# Below-hero uniformity execution prompt

Standardize only the text-and-pill area immediately beneath every hero. Use a
shared page-width container with safe matching gutters; align gold statements
and titles, preserve all wording, and give existing action pills uniform size,
spacing and bottom clearance. Preserve every hero asset, framing, dimension,
effect and navigation rule. Preserve the opening section's existing minimum
height. Where the unchanged artwork leaves insufficient room for readable
content, allow natural scrolling rather than hiding, clipping or shrinking text.
Check all 27 public pages including dynamic Ask/Pioneer pills, all 13 Answer
pages, four art studies and 404 at the same viewport sizes. Compare actual text
bounds, action bounds and hero styles. Review screenshots as well as metrics.
Use independent subagents for visual and code verification. Publish only the
reviewed change, verify delivered files and record exact evidence and limits.

Three prompt reviews completed before implementation:

1. Scope: owner's correction explicitly limits work to below the hero. Hero
   artwork, crop, geometry, effects and menu are locked; text is preserved.
2. Coverage: full width with gutters, shared anchors, uniform existing pills,
   wrapped text, font loading, dynamic controls, small and wide windows covered.
3. Acceptance: all routes enumerated, real content bounds and visual review
   required, hero comparison and deployed-byte verification required. A passed
   outer-section height measurement alone is not proof of presentation quality.

## Verified implementation

All original stylesheet bytes, navigation, hero selectors and assets are
preserved. The appended rules apply only to introduction panels and their
descendants. All 27 HTML modifications are solely the shared stylesheet cache
revision. Panels now share page-width gutters, aligned gold statements and
titles, and existing 44px action pills with consistent bottom clearance.
Narrow screens wrap pills; dense desktop panels size typography and gaps from
their available space. No content or new action pills were introduced.

## Release validation for PR 202

- Independent screenshot review passed all nine primary pages at 1536 x 792.
- Independent rendered-DOM review passed all 17 study/detail pages and 404 at
  1536 x 792. One detail page was also screenshot-reviewed; remaining detail
  screenshot capture timed out, so no all-detail visual claim is made.
- All nine primary pages passed fresh-load review at both 390 x 844 and
  3440 x 1440: 18 completed cases, zero failures. See
  `below-hero-responsive-results.json` for actual bounds and pill alignment.
- The 404 recovery card retains its separate, contained button layout.
- Unified 27-page QA, site QA, Church History QA, static content audit and
  JavaScript syntax checks pass. GitHub's complete required Site QA also passes.
- This is browser viewport testing, not physical-device certification. No
  unrelated AI or content behavior was changed or represented as newly tested.

The review tool now uses fresh page loads at each audited viewport. Reusing a
mobile-initialized document at desktop widths retained an existing mobile
navigation state and produced misleading header failures. It also checks real
text/child bounds, includes incomplete-run failures, normalizes equivalent CSS
serialization and supports explicit page/viewport groups. Automatic browser
recovery interrupted earlier broad runs; they are not counted as passes.
