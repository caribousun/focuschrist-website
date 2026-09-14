# Continuous page background

Owner acceptance, 2026-09-14: no horizontal body-section banding on any page. This supersedes the earlier faded-gradient approach in PR280/281.

Cause: each ordinary, warm or dark wrapper restarted a color layer. Low opacity and transparent endpoints softened transitions but could not guarantee one continuous field. CFM and Conference also supplied independent parent/section gradients. The previous edge-opacity review did not test the stronger requirement.

Use one solid deep-blue page canvas (#17323f), with transparent body layout wrappers, including CFM and Conference. Preserve green card fills, artwork overlays, text, gold controls and spacing. Make chapter and footer divider colors transparent without removing their occupied border widths. Remove only the introduction's bottom separator line. Conference now shares the page canvas; its opening image, text, controls and geometry are unchanged.

All 37 routes were checked at 390x844 and 1280x900: 74 cases, 584 section observations, no horizontal overflow and unchanged compared opening rectangles. In addition, inspect computed backgrounds on every nested main section/nav, excluding approved opening artwork and bounded cards: all unboxed body sections must have background-image:none and a transparent background color. Full-width main/section/div wrapper inspection also covers page-specific parent fills. Inset notices are content panels, not page bands.

Repeat these rendered checks on the published site after verifying deployed bytes. Inspect Home, History and special Conference/CFM layouts visually; geometry alone cannot establish the visual result. Keep this computed-style audit and whole-composition review in future background changes instead of accepting merely faint gradients.

102 workflow checks exercised: 101 passed initially; the hardened-experience marker still required the retired body gradient. Update it to the new continuous canvas and rerun successfully. Original failure retained in local release evidence. No source, media or interaction integrity checks removed.

Rollback: 9e149b879b72a8fe9bffdf15cb458b62b69edd40 (PR281). Physical mobile toolbar behavior is outside emulated-layout coverage.
