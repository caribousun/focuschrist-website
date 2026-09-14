# Mobile continuation cue

Owner follow-up to published PR274: add Continue or Continue below and a down arrow, reuse existing invitations, and leave breathing room. Owner subsequently requested Push and verify to GitHub.

The shared script adds one mobile-only Continue below link to each of the 35 study openings. Existing mobile cues are replaced using their original destinations; desktop originals and primary study actions remain. The 404 page has no next study section and is excluded. A 44px touch target, 20px top margin plus the existing container gap, and keyboard focus outline preserve clear separation. New targets account for the sticky header; Pioneer uses the canonical ask-pioneers ID assigned by its experience script. General Conference uses a readable 2rem mobile heading and 20px outer padding to fit the cue.

All 35 cues fit at 390x844 with at least 16px bottom clearance, and all destinations exist after initialization. At 432x810 the initial audit found General Conference needed extra room; the heading/padding adjustment resolves that case. Eight representative page-family tap journeys were checked. Sixteen production/local comparisons at 702x900 and 1440x900 matched opening geometry and confirmed new cues are hidden on desktop/tablet.

Independent review and all 100 local workflow commands passed on the initial cue implementation. Subsequent Pioneer ID, action ordering, target scroll margin and General Conference changes received targeted syntax, unified-experience, visual and interaction checks. GitHub runs verify the final committed state.

Limits: approved hero heights are preserved. On very short screens such as 360x640, some longer openings require scrolling to reach the cue; text and buttons are not compressed to force them onto one screen. Physical Android/iOS browser-toolbar behavior is not certified. No artwork files or source/doctrinal content changed.

Earlier failures retained: first Pioneer fallback ID was overwritten by its experience script; canonical ID fixes it. Primary action ordering initially put the cue above the button; order20 fixes it. Initial gallery desktop DOM reads briefly observed an empty navigation context; one bounded reload recovered the comparison. Initial fallback scrolling placed some targets beneath the sticky header; the mobile scroll margin fixes it.
