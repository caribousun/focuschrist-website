# Study layout uniformity review — 2026-09-14

Joseph Smith likeness used a wider main container, several nested text widths and left-aligned mobile chapter navigation. Align the study to the shared 1040px content width and outer gutter tokens, shared chapter spacing and centered action groups. Keep its approved artwork, hero geometry, content and study interactions.

Atonement, Book of Mormon evidences, weekly study and Search now share the same outer content borders. Preserve deliberately narrower long-form reading columns and wider galleries. The later weekly-study width override also required correction; checking only its earlier rule missed the rendered difference.

Browser validation covered 38 destinations at phone and desktop widths without horizontal overflow. Five affected layouts were measured at 390, 820 and 1280px. Their desktop content borders align at 1040px; phone gutters remain consistent. Ten formerly left-aligned shared action groups were revisited after the shared centering change, with no remaining alignment failures. Joseph's phone and desktop composition and an artwork study dialog were visually reviewed. This is a layout review, not a new owner artwork approval.

The executable study_layout_uniformity_qa.py check runs in CI and checks later CSS overrides, shared widths, Joseph chapter navigation and default action centering. AGENTS.md and the Master Brain carry the corresponding future-page rules.
