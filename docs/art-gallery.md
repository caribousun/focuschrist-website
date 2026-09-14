# Complete artwork gallery

The owner approved a searchable gallery integrated with Art, preserving the existing artwork, study panels, pill styling, fonts and colors. The owner also requested a page-by-page check of centered opening text and navigation.

`art-gallery.html` is linked above Featured Art & Study and in the shared footer. Its index contains each unique artwork once and retains every original study occurrence. Search matches titles, descriptions and page names; section filters include every section in which a shared image occurs.

The gallery opens the original page in a same-origin frame and activates its existing artwork controller. Original descriptions, scripture pills, onward studies and styles remain in their original documents. The bridge adds View in Original Study and Copy Picture Link using the original control styling. Close restores the gallery position and focus. Full-size viewing and scripture reading remain nested in the original controller. The one image with only a full-image viewer retains that behavior; no scripture or study pills are invented.

`?picture=art-ID` links to a gallery picture. `?gallery-art=source-ID` opens an exact original picture. `?gallery-position=source-ID` returns to the original picture within its lesson without reopening the panel. Unknown source IDs do not activate a different picture. Cross-origin messages and navigation are rejected.

## Updating artwork

After changing an original artwork trigger or image, run `python tools/build_art_gallery.py`. The generator derives the index from public sitemap pages and validates image paths. CI and Pages deployment run `--check`; an outdated index fails the release. Do not copy original panel prose or pills into the gallery index. Navigation previews, video thumbnails and the error page are not study artwork entries.

Run the existing artwork and Art study gates. For rendered comparison use `GALLERY_QA_BASE` with `node tools/art_gallery_browser_qa.js` (Playwright and Chromium required). The test follows every card and alternate original location at desktop and phone widths, comparing actual visible images, text, original pills and computed styles. Reader, full-size, sharing, original navigation and focus-return journeys also require interaction checks. Exact external destination preservation is not a fresh availability audit of every third-party website.

## Centering

The desktop header previously distributed the navigation between an unequal-width wordmark and menu button, placing the navigation about 67 pixels right of the page center. Equal outer grid tracks now center the links; typography, colors, gaps, header heights, wordmark and menu dimensions remain unchanged. Mobile keeps its approved layout. Standard opening text was already centered; intentional split-layout introductions remain intact.

Run `node tools/header_centering_browser_qa.js` against the preview or production base documented in that script. It checks every sitemap page at desktop and phone widths, top and scrolled states, plus narrow desktop boundaries, while comparing hero geometry and font/color signatures against the prior header layout.

The original deployment can be restored by reverting this scoped gallery/header release. No artwork files, original panel scripts/styles, AI provider settings, credentials, schedules, or unrelated work are changed.
