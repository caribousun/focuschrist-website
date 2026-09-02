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

## Approved artwork

### Home

- `assets/page-art/home-seek-study-remember.webp`
- Approved as the supporting image following Our Purpose.

### Ask

- `assets/page-art/ask-seek-study-800.webp`
- `assets/page-art/ask-seek-study-1400.webp`
- Approved daytime image of Jesus Christ studying scripture with a present-day seeker.
- Placement: right of the Your Study Conversation introduction, with the conversation area remaining full width below.

- `assets/page-art/ask-nicodemus-640.webp`
- `assets/page-art/ask-nicodemus-1122.webp`
- Approved realistic predawn image of Jesus Christ speaking with Nicodemus.
- Placement: left of the Continue Your Study links.

## Not selected

- The walking image generated for the Ask page was rejected and must not be used.
- The earlier stylized Nicodemus image was rejected because it looked cartoon-like and must not be used.

## Release protection

- `tools/unified_experience_qa.py` verifies that approved supporting artwork remains wired, responsive, lazy-loaded, and within its delivery-size budget.
- `tools/production_hardening_qa.py` verifies the production WebP dimensions.
- Any new approved supporting artwork must extend these checks.
