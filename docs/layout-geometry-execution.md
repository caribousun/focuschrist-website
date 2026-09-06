# Layout geometry correction

## Owner-directed execution prompt

Audit every canonical focusChrist page for balanced text and media proportions and unobstructed hero subjects. Inspect the approved artwork itself, shared CSS and actual rendered geometry. Reserve space for navigation so it cannot cover the opening artwork. Frame the close portrait independently from wide panoramas, preserving the approved image bytes and likeness. Keep contextual videos subordinate to the neighboring explanation, with an uncropped preview, clear title and source. Do not add filler, clip copy, distort thumbnails or change the verified unique media selections. Preserve scripture readers, artwork dialogs, navigation and Ask behavior. Check desktop, narrow and ultrawide layouts, correct exceptions, independently review, publish, verify delivered files, and update canonical memory. Do not claim device or viewport checks that were not performed.

## Diagnosis and implementation

The opaque fixed desktop header occupied 72px while the artwork began at zero. The opening layout now reserves 72px and subtracts that space in its viewport-height calculation. The reserved space remains stable when the header shrinks to 64px on scroll. Mobile keeps its existing in-flow header with no second spacer.

The close portrait was enlarged with cover to fill a shallow wide banner, cutting off hair independently of the header. Its new portrait class scales the original to the banner height, centers the full vertical composition and blends the edges into a warm background using CSS. No approved image file is changed. Panoramic page heroes retain their own compositions.

All 24 contextual Answer companions retain their original thumbnails, titles and source links. Duplicate explanatory card paragraphs are removed because the substantive explanation already appears beside each card. All narrative outside resource cards remains byte-equivalent in parsed text. Cards are bounded to 340px, vertically balanced with the copy, and centered below it on small screens. Standalone video/resource grids remain separate.

## Verification procedure

`tools/layout-review.html` is a noindex internal review page with same-origin iframes sized at 390x844, 820x1180, 1363x936, 1920x1200 and 3440x1440. It loads all canonical pages from the sitemap, records real iframe viewport dimensions, document overflow, opening header clearance and every contextual prose/card height. CSS scale only fits the review frame on the reviewer screen; media queries run at the selected iframe width. This is responsive browser verification, not a physical-device test. Visually inspect representative hero compositions and both media rows of every Answer; automated dimensions do not replace visual judgment.

Release and production verification receipts are recorded in the canonical project memory after deployment. Prior PR179 desktop acceptance did not catch the owner's geometry defects and is superseded for presentation quality.

## Owner refinement after PR180

The owner rejected the small free-standing card beside a long narrow text column. Although all 130 viewport geometry checks passed, those measurements did not establish a good composition. The final layout uses a unified study panel: the existing heading and brief introduction share a compact row with the video, then the complete scripture discussion flows below a divider. This preserves all text and source selections and removes the disconnected tall-column arrangement. Visual acceptance must assess grouping, whitespace and reading flow in addition to numerical bounds.

The owner accepted the menu itself and reported opening buttons below the fold in shorter desktop windows. Menu styling remains unchanged. The hero now accounts for viewport height as well as width, and short-desktop introductory spacing is more compact. Review includes1366x768,1536x792 and1920x990 in addition to prior widths and explicitly measures the bottom of opening action buttons.

## Full composition correction after PR181

The owner still rejected the opening artwork: reducing banner height while retaining cover cropped the foreground even though viewport bounds passed. Desktop panoramas now scale proportionally to their full native composition inside the available hero height, with narrow edge blending into the site background. The Sacred Grove uses its own 1916:821 ratio. Bottom fading is confined to the final tenth of the artwork, protecting hands, books, paths and other foreground details. Approved menu geometry and artwork files remain unchanged. Numerical fit is only a regression guard; rendered composition must also be reviewed.

## Owner rejection of PR182 and wide-opening correction

The full-composition contain approach was rejected: the narrow centered artwork and empty side bands looked wrong. Restore wide panoramas, keep navigation untouched, and measure the actual introductory content after fonts and responsive wrapping. The image receives the remaining viewport height instead of a fixed 410px text allowance. Introduction spacing and title size are restrained. On unusually short windows, content may flow normally; it is never clipped or hidden. The review harness now varies its page URL per load and reports the stylesheet version to avoid confusing cached HTML with the current release.
