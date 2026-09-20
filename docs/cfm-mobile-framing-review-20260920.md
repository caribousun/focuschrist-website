# Come Follow Me mobile head framing — 2026-09-20

Wyatt reported that the mobile crop clipped the top of Christ's head. The original portrait contains the full head, but centering that tall image in the compact main-page frame selected too low a portion of the artwork.

The only visual change is a page-specific mobile background position of center 25% in come-follow-me.css. Full-width cover rendering, the shared hero height, original artwork bytes, text, controls and desktop styling remain unchanged. Only the page's own stylesheet cache reference is refreshed.

Rendered checks at 320×568, 375×667, 390×740, 412×775, 430×844 and 700×900 confirm the new focal position, preserved height, visible actions/Continue and no horizontal overflow. Screenshots at narrow, standard and wide mobile sizes show Christ's entire head with space above it. Desktop geometry, content and background properties match live production after normalizing the local preview origin. Independent review approved the narrow change.

Wyatt also asked about the Pioneers heading “Leaving home, preparing a way,” then noted that it might be centered correctly. Live inspection at 390×740 confirmed a centered heading, zero text-indent, and matching horizontal bounds with its left-aligned paragraph. The isolated final word on the second line explains the uneven appearance. Pioneers was left unchanged, and that finding was reported to Wyatt.
