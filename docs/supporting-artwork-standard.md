# focusChrist Supporting Artwork Standard

Updated: 2026-09-05

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
- Every appropriate non-hero artwork displayed in page content must provide a clear path to its highest-resolution local source when clicked or keyboard-activated. Use a semantic link with a visible focus state and preserve the original destination as the no-JavaScript fallback.
- Normal full-size image activation opens the exact local source inside a same-page viewer. The viewer must close with its centered control, Escape, or the backdrop and must return focus to the invoking control. Modified clicks retain the original new-tab behavior.
- The Art gallery may use its existing accessible full-screen viewer instead of opening a raw image tab. Art study pages may continue linking directly to their full source.
- Home, Ask, Answers, Church History, Mission, and the Featured Art and Study cards open an accessible detail window first. The window must explain the scene, distinguish portrayals from documentary images, provide an official source, and offer a clear full-size image action.
- Featured Art and Study cards also provide a direct action to the complete study page. Their original study-page destination remains the fallback.
- The Read the Art Study action is optional. It remains hidden by default and appears only when the selected artwork record has a reviewed complete study page.
- Artwork descriptions must be sacred, respectful, specific to the selected image, and genuinely informative. Do not fill artwork windows or captions with repeated documentary, provenance, or portrayal disclaimers.
- Preserve normal modified-click behavior so visitors can still open an original destination in a new tab.
- The dialog must support mouse, touch, keyboard activation, Escape, backdrop close, focus return, body scroll locking, and responsive stacking.
- The circular close control uses CSS-drawn crossing lines centered at exactly 50 percent on both axes. Do not replace it with a font multiplication glyph, which appears optically off-center.
- Page heroes remain non-interactive unless Wyatt separately approves a change to their behavior.

## Site-wide interaction inventory

- 28 supporting artworks use the detail-first experience: 3 Home, 3 Ask, 4 Answers, 7 Church History, 7 Mission, and 4 Featured Art and Study cards.
- All heroes remain unchanged. The Pioneer hero retains its preexisting full-image link and is not enrolled in the detail window.
- The 39 main Art gallery works retain the dedicated full-screen gallery viewer and its contextual study actions.
- The four main images on dedicated Art and Study pages continue opening their full sources because the surrounding page already provides the detailed study experience.
- Watch thumbnails retain their video-link behavior. Logos, icons, arrows, play controls, and dialog display images are not artwork-detail triggers.

## Approved artwork

### Home

- `assets/page-art/home-seek-study-remember.webp`
- Approved for the Our Purpose section.
- Placement: a large image on the right of the purpose copy in a Missionary-style editorial split. On narrow screens, the purpose copy remains first and the image follows before the study-path cards.

- `assets/page-art/home-come-and-see-900.webp`
- `assets/page-art/home-come-and-see-1672.webp`
- Approved for the opening transition between the welcome introduction and Our Purpose.
- The image shows Christ in a muted olive-green outer cloak inviting four attentive seekers to walk with Him. Preserve the approved likeness, restrained expression, people, composition, and warm Galilee setting.

- `assets/page-art/home-light-through-study-900.webp`
- `assets/page-art/home-light-through-study-1672.webp`
- Approved within More Ways to Study, between the first and second rows of study paths.
- The image shows Christ in a slate-blue cloak studying with a young man and an older woman. Preserve the approved likeness, three-person composition, books, light, and near-photographic finish.

### Ask

- `assets/page-art/ask-seek-study-800.webp`
- `assets/page-art/ask-seek-study-1400.webp`
- Approved daytime image of Jesus Christ studying scripture with a present-day seeker.
- Placement: a large image on the left of the Your Study Conversation introduction, following the established Missionary page split layout. The conversation area remains full width below.

- `assets/page-art/ask-nicodemus-640.webp`
- `assets/page-art/ask-nicodemus-1122.webp`
- Approved realistic predawn image of Jesus Christ speaking with Nicodemus.
- Placement: right of a clean vertical continuation list inside a unified presentation panel. At tablet and mobile widths, the image stacks above the links.

- `assets/page-art/ask-road-to-emmaus-eye-corrected-900.webp`
- `assets/page-art/ask-road-to-emmaus-eye-corrected-1672.webp`
- Approved after the Nicodemus continuation artwork.
- The scene contains Jesus Christ and exactly two distinct disciples walking toward Emmaus. Preserve the approved ochre cloak, Christ likeness, two-disciple count, walking movement, and warm near-photographic atmosphere.

### Answers

- `assets/page-art/answers-savior-welcomes-child-900.webp`
- `assets/page-art/answers-savior-welcomes-child-1672.webp`
- Approved between the family-related answer path and the next row of Answer Library topics.
- The image shows Christ in a burgundy mantle welcoming a mother and young child. Preserve the approved Christ likeness, clear healthy complexion, gentle expression, family, composition, and near-photographic finish.

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

### Pioneers

- Ten approved photorealistic scenes are integrated as four visual chapters without changing the approved Pioneer hero.
- The story order is: leaving Nauvoo, Winter Quarters, daily life on the trail, traveling beside the Platte River, a river crossing, the handcart journey, rescue wagons arriving, the first view of the Salt Lake Valley, building a new community, and construction of the Salt Lake Temple.
- The artwork is distributed around the existing Journey, Trail, and Willie and Martin history sections. It is not presented as one detached gallery and is not placed inside the expandable history controls.
- Desktop presentation uses compact two-card and three-card editorial grids. Tablet presentation reduces three-card groups to two columns. Mobile presentation uses one column with the original 16:9 composition preserved.
- Each scene has 800 and 1400 pixel responsive WebP variants. Each opens its local 1672 pixel source through the shared same-page image viewer, with the semantic link retained as a new-tab fallback.
- Preserve the distinct people, clothing, family relationships, broken-up wagon groupings, and photorealistic finish Wyatt approved. The rejected original winter rescue image must never be used.
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
- `tools/artwork_details_qa.py` verifies the 21 non-Mission records, the 7 Mission artwork triggers, exact trigger-to-record matching, required official sources, local full-size assets, intentional exclusions, interaction safeguards, and the centered close controls.
- `tools/production_hardening_qa.py` verifies the production WebP dimensions.
- Any new approved supporting artwork must extend these checks.
