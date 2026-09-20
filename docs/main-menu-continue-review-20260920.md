# Main menu mobile opening review — 2026-09-20

Wyatt expanded the main-page scope to all site links in the hamburger above Official Church Resources. The 13 pages are Home, Ask, Answers, General Conference, Come Follow Me, Art, Missionary, Church History, Pioneers, Watch, About, Atonement, and Book of Mormon Evidences. Church resources and sections below that divider are excluded. Individual Answer topics and other study pages retain the PR342 presentation restored by PR344.

Every scoped main page now inherits the original Book of Mormon Evidences bordered Continue below pill, arrow, and existing anchor-scroll behavior. Only its surrounding margin is adjusted in the main-page mobile rules. General Conference and Come Follow Me use compact opening copy; longer explanation and Conference collection statistics remain immediately below. Desktop restores the original copy, controls, and positions. Artwork assets and original full-width rendering are preserved, with no added sides or surrounds.

## Rendered verification

- All 13 pages at 320×568, 375×667, 390×740, 412×775, 430×844, and 700×900: 78 checks passed. Opening controls and Continue fit inside the visual viewport, touch targets are at least 44px, destinations exist, and no horizontal overflow occurs.
- All 78 computed pill styles match the original live Book of Mormon Evidences reference: border, radius, background, type, padding, letter spacing, minimum height, and arrow gap.
- Hero height is uniform across all 13 at each viewport: approximately 238.6, 280.2, 310.8, 325.6, 354.5, and 360px respectively.
- At 200% text, all 13 openings grow naturally and retain readable, unclipped controls.
- Added General Conference, Come Follow Me, and Book of Mormon Evidences desktop opening geometry, text, and styles match the PR342 baseline. The first two have an extra hidden notes container with no desktop layout effect.
- Keyboard activation of Continue on the three added main pages updates the correct anchor and brings the destination into view. Existing shared scrolling code is unchanged.
- Browser screenshots reviewed for General Conference and Come Follow Me. Automated checks are not owner visual approval.

Independent review approved the 13-page scope, original pill inheritance, mobile-only rules, retained supporting copy, and exclusion of individual Answer topic pages. The original CSS prefix and original shared script outside the main-only copy block remain protected by regression checks.
