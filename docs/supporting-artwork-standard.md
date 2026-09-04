# focusChrist Supporting Artwork Standard

Updated: 2026-09-02

## Purpose

Supporting artwork beautifies the content of each page without replacing or changing its approved hero. The number of images is determined by the page's length, themes, and visual flow. Do not limit every page to one image, and do not add images where they would crowd controls or interrupt study.

## Visual direction

- Use high-fidelity cinematic photographic realism.
- Jesus Christ must retain the approved likeness established by the page hero and approved reference artwork.
- Skin, hands, eyes, hair, fabric, light, and environments must look naturally photographed, not painted, cartooned, airbrushed, or game-rendered.
- Expressions should be compassionate and restrained. Avoid exaggerated smiles, halos, fantasy lighting, and theatrical poses.
- Artwork must clearly reflect the theme and content near its placement.
- Existing approved focusChrist artwork is the literal visual reference for character likeness, realism, light, color, and emotional restraint. Photorealism by itself is not a match.
- Favor varied compositions and placements. Images may sit left, right, or span a section when that creates better flow. Do not mechanically center every image.

## Page layout

- Heroes remain unchanged unless Wyatt separately approves a hero change.
- Place artwork beside or between meaningful content sections.
- Alternate visual weight and image position when the page supports it.
- Keep interactive controls and reading areas clear and usable.
- On narrow screens, side-by-side arrangements stack into a natural reading order without horizontal overflow.

## Image delivery

- Store production artwork locally as WebP.
- Provide responsive `srcset` variants sized for the image's actual placement.
- Keep visible image quality high while targeting no more than 120 KB per delivered variant when practical.
- Use explicit `width` and `height` attributes to prevent layout movement.
- Use `loading="lazy"` and `decoding="async"` for supporting artwork.
- Keep source artwork outside the runtime page unless an original is specifically required.
- Every non-hero artwork displayed in page content must open its highest-resolution local source when clicked or keyboard-activated. Use a semantic link with a visible focus state and `target="_blank"` plus `rel="noopener noreferrer"`.
- The Art gallery may use its existing accessible full-screen viewer instead of opening a raw image tab. Art study pages may continue linking directly to their full source.
- The Mission page may open an accessible detail window first when the original artwork link remains the no-JavaScript fallback and the window provides a clear full-size image action. The detail window must also explain the scene, distinguish portrayals from documentary images, and provide an official source when relevant.
- Page heroes remain non-interactive unless Wyatt separately approves a change to their behavior.

## Approved artwork

### Home

- `assets/page-art/home-seek-study-remember.webp`
- Approved for the Our Purpose section.
- Placement: a large image on the right of the purpose copy in a Missionary-style editorial split. On narrow screens, the purpose copy remains first and the image follows before the study-path cards.

### Ask

- `assets/page-art/ask-seek-study-800.webp`
- `assets/page-art/ask-seek-study-1400.webp`
- Approved daytime image of Jesus Christ studying scripture with a present-day seeker.
- Placement: a large image on the left of the Your Study Conversation introduction, following the established Missionary page split layout. The conversation area remains full width below.

- `assets/page-art/ask-nicodemus-640.webp`
- `assets/page-art/ask-nicodemus-1122.webp`
- Approved realistic predawn image of Jesus Christ speaking with Nicodemus.
- Placement: right of a clean vertical continuation list inside a unified presentation panel. At tablet and mobile widths, the image stacks above the links.

### Church History

- `assets/history/first-vision-800.webp`
- `assets/history/first-vision-1400.webp`
- `assets/history/joseph-emma-harmony-800.webp`
- `assets/history/joseph-emma-harmony-1400.webp`
- `assets/history/three-witnesses-800.webp`
- `assets/history/three-witnesses-1400.webp`
- `assets/history/restoration-print-shop-800.webp`
- `assets/history/restoration-print-shop-1400.webp`
- `assets/history/preserving-the-record-800.webp`
- `assets/history/preserving-the-record-1400.webp`
- `assets/history/christ-museum-record-800.webp`
- `assets/history/christ-museum-record-1400.webp`
- `assets/history/christ-through-eras-800.webp`
- `assets/history/christ-through-eras-1400.webp`
- Approved as seven sequential visual chapters distributed through the History page. The sequence begins after the unchanged hero and source standard, leaves the Ask controls unobstructed, alternates visual offsets, and concludes before the continuation links.
- The First Vision portrayal keeps Jesus Christ and Joseph Smith as the primary characters while God the Father is forward-facing but lightly seen.
- The Three Witnesses portrait uses their June 1829 ages: Oliver Cowdery 22, David Whitmer 24, and Martin Harris 46.

### Missionary Work

- `assets/missionary/christ-commissions-twelve-900.webp`
- `assets/missionary/christ-commissions-twelve-1100.webp`
- `assets/missionary/christ-commissions-twelve-1672.webp`
- Approved depiction of Jesus Christ walking with exactly twelve distinct Apostles as He gives them their commission to teach all nations.
- Placement: a wide supporting artwork immediately beneath the Christ's commission text and Matthew 28:19 quotation. The 900 and 1100 pixel variants serve the page responsively, and selecting the image opens the full 1672 pixel source.
- Christ retains the approved `art/The-Living-Christ.png` likeness and wears a muted deep blue-gray outer robe over a warm ochre-brown tunic. Record these colors as used so later Christ artwork intentionally rotates to a different historically plausible palette unless Wyatt requests otherwise.
- Preserve the exact count of Christ plus twelve Apostles, the warm Judean field, restrained expression, distinct Apostle faces, natural movement, and near-photorealistic finish.
- All seven Mission supporting artworks open a shared detail window containing the selected image, reviewed context, an official source, and a separate full-size image action. Read the Savior's commission, Study Early Missionaries, and Explore the Growth of the Work use the same pattern before visitors choose the official source.

## Not selected

- The walking image generated for the Ask page was rejected and must not be used.
- The earlier stylized Nicodemus image was rejected because it looked cartoon-like and must not be used.
- The 2026-09-03 Answers-page courtyard teaching candidate was rejected because it did not match the approved focusChrist character or established artwork. It must not be used or treated as a style reference.
- The Church History `A Worldwide Living History` candidate was rejected and must not be used.
- All Moroni and Joseph bedroom candidates reviewed on 2026-09-04 were rejected and must not be used.

## Release protection

- `tools/unified_experience_qa.py` verifies that approved supporting artwork remains wired, responsive, lazy-loaded, and within its delivery-size budget.
- `tools/unified_experience_qa.py` also verifies that every supporting artwork collection retains a full-resolution opening path.
- `tools/production_hardening_qa.py` verifies the production WebP dimensions.
- Any new approved supporting artwork must extend these checks.
