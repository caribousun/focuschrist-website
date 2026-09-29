# Temple history expansion — September 29, 2026

Owner scope: substantially enrich the Temples section with at least fifteen additional original pictures, telling its story from the beginning to the present. Preserve the existing content and original artwork.

Wyatt explicitly approved a **temple-page-only exception to the half-Christ artwork ratio** during this work so the chronological history can include accurate, varied ancient and modern temple scenes. This exception applies only to `answers/why-latter-day-saints-build-temples.html`. It does not relax the ratio for any other page, permit artwork reuse, change approved character identities, or turn a technical review into owner aesthetic approval.

## Integration gates

- `chapters.json` supplies the chronological narrative, exact official source links, scene constraints, captions, and alternative text.
- `art-ready.json` records the actual asset paths, intrinsic dimensions, and the independent visual review state. Only records explicitly marked `reviewed: true` may enter the public page. That field means technical/content visual review, not owner approval.
- `tools/build_temples_history.py` refuses to change the public HTML when any planned chapter is missing a reviewed image. Asset names in the research plan are plans until their generated files and visual reviews exist.
- Every new original owns one position on this page. Chapter navigation has no repeated thumbnail copies. Responsive variants and full-size views count as one original.
- Each picture opens the shared study panel first, with its own caption, official sources, full-size image, onward study, Continue Lesson, and Close actions.
- The chronology retains the site's shared content boundary, existing temple hero, existing illustrations, and all earlier reflection/resource sections. Page CSS does not change hero frames or shared CSS.

## Verification

`tools/temples_history_qa.py` verifies integration completeness, retained earlier images and exact hero markup, decoded-image uniqueness among new originals, intrinsic full-image dimensions, sources, chapter anchors, reflections, and onward study.

`tools/temples_history_runtime_qa.js` exercises every new study panel, including official Newsroom source pills, nested full-size viewing, repeated opening, restored focus, and return to the associated lesson.

These checks do not establish historical accuracy of each rendering, identity consistency, meaningful visual scene diversity, layout at desktop/phone/200% text, or owner aesthetic approval. Those reviews remain separate release evidence.
