# Restore study pages; limit mobile redesign to main navigation pages

Wyatt rejected the added image sides and explicitly limited this work to the main pages linked in the top navigation. PR343's sitewide image containment, surrounds, short hero heights, and compact introductions were not approved. Its prior technical completion record is superseded by this owner correction.

## Scope

Only Home, Ask, Answers, Art, Missionary, Church History, Pioneers, About, Watch, and the central Atonement link receive the new `fc-main-opening` class. Only these ten pages use the shared `42svh` mobile image frame and compact introduction layout.

Individual Answer topic pages, art studies, Come Follow Me, General Conference, Book of Mormon Evidences, Joseph Smith's portrait, Birth of Christ, the gallery, and Search are excluded. The full stylesheet preceding the main-only additions is exactly the normalized pre-PR343 `7e22dd7` stylesheet. The new mobile copy logic is guarded by the main-page class; all excluded-page JavaScript opening behavior matches that same baseline.

## Changes

- Removed all introduced image-surround elements, blur backgrounds, containment overrides, and the added Home image override. The previous full-width artwork presentation is restored. Original artwork assets and full-size paths are unchanged.
- Main-page mobile controls retain 44px touch heights, with shorter labels and tighter spacing. Mobile Answers, Watch, and Missionary headings are concise; original desktop wording returns exactly.
- Missionary's supporting scripture and Art's longer usage hint remain immediately below their opening on mobile and return to their original positions on desktop. Individual Answer topics have no shortened copy, moved text, or changed pills.
- Prior completed Answers directory card rows remain intact; no further Answer topic content or layouts are redesigned.

## Verification

- Direct rendered comparison of all 31 excluded canonical routes against a server using the original `7e22dd7` CSS and JavaScript: 320x568, 390x740, and 1440x900; 93 comparisons, zero differences in opening content, geometry, typography, hero sizing, or image fitting.
- Ten main pages at six mobile viewport sizes: 320x568, 375x667, 390x740, 412x775, 430x844, and 700x900; 60 checks. Every action and Continue cue fits inside the initial visual viewport; 44px minimum controls, no horizontal overflow, no side elements. Minimum clearance beneath the cue is 12px.
- Main-page hero heights match at each viewport: approximately 238.55, 280.21, 310.8, 325.58, 354.48, and 360 CSS pixels. Excluded pages retain their original sizing, as explicitly directed by Wyatt.
- Independent review approved scope isolation and exact restoration. Regression gates lock the original stylesheet prefix, exact ten-page allowlist, absence of surrounds, unchanged excluded-page mobile text, retained destinations, reversible desktop copy, and accessible names for redesigned controls.
- All ten main-page desktop openings matched the original baseline at 1440x900. At 200 percent text size on a 320x568 viewport, all ten main openings expanded with their controls; no opening action had clipped text, a touch height below 44px, or a bottom outside its expanded introduction.

These are technical checks, not owner visual approval. Enlarged text may need scrolling and must not be clipped to force first-screen fit. Future work must not reapply the main-page design to individual studies without explicit owner direction.
