# Approved Mission hero and shared opening layout

Wyatt approved exec-dafafa9f-89f8-420f-8df0-9be8297692a4.png on 2026-09-06 for the Mission hero. Native dimensions: 2172 x 724. Source SHA256: a1aa627b9a800cae2ad4cc245d6262734f3198b03fec585838a6039aa23363bf. The published candidate assets/heroes/missionary.webp decodes to exactly the same RGB pixels; no upscaling or lossy recompression was used.

The owner specifically asked for parity with other pages. The Mission-only desktop hero-height, intro-padding, heading-size, paragraph-spacing and button-spacing overrides are removed. Mission inherits the shared opening system, including a desktop hero height of clamp(350px, 27vw, 440px) and the existing 300px mobile rule. Natural content flow allows the introduction to grow when required; buttons are not clipped to force a single-screen fit. Desktop image positioning uses center top to protect Christ's hair below the fixed navigation. Existing mobile center 34% positioning and ultrawide edge blending are retained.

Only this approved hero, its social-preview cache version, Mission CSS cache version and corresponding existing QA version marker change. Supporting artworks, viewer behavior, content and other page styles remain intact. The prior mission-artwork-opening-handoff.md is historical and its Mission-only desktop sizing is superseded here.

Validation: exact decoded image comparison passed. Existing production-hardening, artwork-detail and unified-experience QA passed. Independent reviewer and release/live receipts are required before production completion; final evidence is recorded in Focus Current State and Run Log.

Continuation: owner-directed Mission content enrichment, then Watch separately. No broad production-health or indexing claim is implied by this hero release. Direct display was authorized for this particular image review, not as a permanent replacement of the private-review rule.

## Owner correction: opening content must fit without resizing the hero

After publication, the owner supplied a shorter desktop viewport where the two-line heading pushed the pills below the fold. The correction preserves the hero, all shared font sizes/families/weights/line heights and pill styling. Mission's desktop introduction uses the existing shared gallery-width token (1440px), retaining the standard36px side allowance, removes the title's 940px maximum, and adapts only vertical outer padding to viewport height. This lets the long title use a single line where space allows and reduces blank space before sacrificing content. Existing smaller-screen natural flow is preserved. The first desktop screenshot alone did not establish shorter-viewport acceptance.
