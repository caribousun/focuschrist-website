# Birth of Christ release verification

Date: 2026-09-19. Checkout: `focus-birth-of-christ`. This record describes local verification only; no production deployment or public-site evidence exists for this release yet.

## Integrated scope

Birth of Christ contains twenty-three unique reviewed artworks: one Nativity hero and twenty-two body pictures, with twelve reading stops, eight guided reflections, eight official resource cards and four onward study paths. Final captions, exact scripture actions, social metadata, discovery entries and shared asset/resource ledgers are integrated. The twenty-three Birth selections have explicit owner approval recorded independently from technical review.

The same release preserves all Life After Death imagery while improving reading order and connections, adds the Emily Belle Freeman resource to Grief, and adds four reviewed pictures at the identified gaps in Death of a Child, Divorce, Heavenly Father and Grief. Existing heroes remain unchanged.

## Local automated checks

The first complete local suite ran 113 checks: 110 passed and three reported stale integration expectations. Those three checks were corrected narrowly and rerun successfully:

- `artwork_details_qa.py`: exactly 36 hero pages, including Birth, and Birth’s precise hero script version.
- `topic_artwork_details_qa.py`: the original 99 adapter pictures and three preserved detail pictures remain required; the 18 Life After Death additions and four study-gap additions must separately match their exact reviewed manifests. New additions must open study details before the full-image viewer.
- `production_hardening_qa.py`: Ask must load the current contextual script version containing Birth’s return-route allowance.

Independent diff review found a hypothetical Birth hero path in the runtime test fixture. The fixture now uses the actual integrated Nativity asset; `hero_details_runtime_qa.js` passes. `git diff --check` also passes. The focused Birth, study-gap and shared art enrichment gates passed during integration. The complete 113-check suite was not repeated after these scoped QA-only corrections; the previously failing checks and the corrected runtime fixture were rerun directly.

## Local browser and visual evidence

The parent implementation agent reports the following completed local browser checks; this document records that evidence without representing it as a separate second browser run:

- All twenty-two body artwork details were inspected on desktop earlier in the release and on phone in the final pass. Each loaded the 1536-pixel image with contained presentation; its four action links stayed within the 376-pixel phone viewport.
- The phone opening hero screenshot passed visual review without enlarging the established opening to accommodate the artwork.
- Nested scripture reading, full-image viewing, closing/reopening, and the contextual Ask return journey were tested. Ask retained an editable question and did not submit automatically.
- All four new study-gap pictures received desktop and phone review.

These checks establish local rendering and interaction behavior. They do not establish deployed bytes, cache refresh, public behavior or completion of a production release.

## Review boundary

No content or integration blocker remained in the independent final diff review. Only scoped QA expectations and the runtime fixture changed during that final correction pass. No commit or publication was performed by the reviewing agent. Generated Python cache files are not release artifacts and should remain outside the staged changes.
