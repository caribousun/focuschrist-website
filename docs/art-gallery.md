# Complete artwork gallery

The owner approved a searchable gallery integrated with Art, preserving the existing artwork, study panels, pill styling, fonts and colors. The owner also requested a page-by-page check of centered opening text and navigation.

`art-gallery.html` is linked above Featured Art & Study and in the shared footer. Its index contains each unique artwork once and retains every original study occurrence. Search matches titles, descriptions and page names; section filters include every section in which a shared image occurs.

The gallery opens the original page in a same-origin frame and activates its existing artwork controller. Original descriptions, scripture pills, onward studies and styles remain in their original documents. The bridge adds View in Original Study and Copy Picture Link using the original control styling. Close restores the gallery position and focus. Full-size viewing and scripture reading remain nested in the original controller. The one image with only a full-image viewer retains that behavior; no scripture or study pills are invented.

`?picture=art-ID` links to a gallery picture. `?gallery-art=source-ID` opens an exact original picture. `?gallery-position=source-ID` returns to the original picture within its lesson without reopening the panel. Unknown source IDs do not activate a different picture. Cross-origin messages and navigation are rejected.

The gallery stays visible while the original panel prepares, then opens that panel directly. Recovery pills appear only on an error or after a 15-second delay. Escape cancels a pending opening and restores the gallery focus. Verify delayed loads, cancellation, error recovery and normal opening whenever changing this transition.

## Updating artwork

After changing an original artwork trigger or image, run `python tools/build_art_gallery.py`. The generator derives the index from public sitemap pages and validates image paths. CI and Pages deployment run `--check`; an outdated index fails the release. Do not copy original panel prose or pills into the gallery index. Navigation previews, video thumbnails and the error page are not study artwork entries.

Run the existing artwork and Art study gates. For rendered comparison use `GALLERY_QA_BASE` with `node tools/art_gallery_browser_qa.js` (Playwright and Chromium required). The test follows every card and alternate original location at desktop and phone widths, comparing actual visible images, text, original pills and computed styles. Reader, full-size, sharing, original navigation and focus-return journeys also require interaction checks. Exact external destination preservation is not a fresh availability audit of every third-party website.

## Centering

The desktop header previously distributed the navigation between an unequal-width wordmark and menu button, placing the navigation about 67 pixels right of the page center. Equal outer grid tracks now center the links; typography, colors, gaps, header heights, wordmark and menu dimensions remain unchanged. Mobile keeps its approved layout. Standard opening text was already centered; intentional split-layout introductions remain intact.

Run `node tools/header_centering_browser_qa.js` against the preview or production base documented in that script. It checks every sitemap page at desktop and phone widths, top and scrolled states, plus narrow desktop boundaries, while comparing hero geometry and font/color signatures against the prior header layout.

The original deployment can be restored by reverting this scoped gallery/header release. No artwork files, original panel scripts/styles, AI provider settings, credentials, schedules, or unrelated work are changed.

## Previously shared picture links

Reviewed image replacements can change generated picture and source IDs. The gallery keeps a finite compatibility map for the retired Joseph-and-Emma marriage picture and Emma portrait IDs; the original-page bridge also resolves the retired marriage source ID. Each alias must resolve to an existing catalog entry on the correct owning page. Unknown IDs, missing targets and source IDs used on another page remain rejected.

Gallery links normalize to the current picture ID. Embedded View in Original Study and Continue Lesson links use the current source ID while retaining unrelated query parameters and the destination fragment. The unchanged Emma portrait source continues to support both opening its study panel and returning to its position without reopening.

Run `node tools/gallery_compatibility_runtime_qa.js` with the existing JSDOM dependency. Both CI workflows run this offline production-script regression after their JSDOM setup. It covers legacy/current links, unchanged portrait routing, missing targets, wrong pages, unknown/prototype-like IDs, canonical links and focus return. Native desktop/phone study, nested full-size, sharing and return checks remain separate release requirements.
