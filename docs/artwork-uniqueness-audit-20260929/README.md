# Artwork uniqueness audit — September 29, 2026

The 23 baseline candidate families are adjudicated, with no unresolved candidate remaining in the reviewed scope. Eleven distinct new originals replace repeated navigation/card illustrations: three Stand Forever cards, four Come, Follow Me resource cards, and four Art study cards. Existing owning pictures remain in place. Four desktop hero derivatives are not counted as new originals.

## Evidence and scope

- The baseline occurrence audit examined 123 public HTML documents and 1,245 static image elements. Its 23 candidates combined occurrence/source lineage with independent pixel matches; candidates were never automatic violations.
- Newton's independent raster corpus examined 2,019 files and 1,099 representative families. Responsive sizes, encodings, and visually shared background sequences were separated from whole-picture duplication through full-image review.
- The final scanner records 1,269 image/inline-style occurrences and 872 apparent owning families before manual reference classification. It nominates 16 families, all adjudicated in `final-occurrences.json`. This raw count is not a count of original artworks.
- The final scanner also records 29 image literals in directly loaded local CSS/JavaScript and the generated gallery index (857 artwork records at this checkpoint). CSS/JS literals identify potential usage, not browser visibility. Dynamic gallery entries are an index of existing owning artwork, not additional originals.
- The eleven new pictures have exact output/source hashes and independent visual acceptance in `new-art-review.json`. The gallery was rebuilt to include all eleven, and retains per-occurrence owner page/selector metadata.

## Decisions

The repeated Stand Forever, Come, Follow Me toolkit, and Art lower-card pictures were replaced. The Conference card's Home image and its Look unto Me pathway's wrong Answers thumbnail were corrected to the actual destination originals. Reused navigation pictures now name their owning page. Answers' personal-study reference opens the exact Come, Follow Me original; the Art portrait reference opens the exact Answers original. Three Art study heroes explicitly link the original gallery pictures.

The Art portrait link was moved outside the gallery click control. Its title remains `Jesus Christ`; a real event regression checks that the source link does not open the artwork modal or contaminate the artwork query. The link's full wrapped box is clickable.

Four sets of shared-background narrative pictures remain: John's witness and questioning visitors; the midnight request and bread received; the wounded traveler and Samaritan's care; and the servant's plea, pardon, and witnesses. Newton and Albert independently inspected the full pictures and confirmed distinct meaningful story actions with consistent returning characters. These are not crop/rename copies. The Atonement's sensitive preview/open states and the Joseph Smith likeness comparison also remain purposeful references to one original each.

## Reproduce and prevent recurrence

Run `python tools/audit_artwork_occurrences.py --output work/artwork-audit-current` for fresh static, inline-style, CSS/JS literal, gallery, and source/pixel-family evidence. `tools/audit_artwork_pixel_families.py` contains the independent raster scan. The dated pixel snapshot remains baseline evidence; new originals additionally carry exact hashes and direct visual review.

`tools/artwork_reference_repairs_qa.py` verifies eleven reviewed unique-source pictures, sole card placements, preserved original-family occurrences, owner labels/anchors, and separate official-resource controls. Negative fixtures restore an old card, add a differently sized old original, and misdirect a reference; each must fail. `tools/artwork_reference_runtime_qa.js` exercises the portrait link/title and all four Come, Follow Me picture panels, including distinct headings, scene descriptions, clean official-source labels, and separate resource navigation. Both gates are wired into both CI workflows.

This audit does not claim every lazy-loaded or remote browser state was exhaustively traversed. Static evidence, exact/visual asset review, generated-index checks, interaction tests, and selected actual browser reviews are separate evidence classes. The reported zero unresolved count refers to the candidates identified and adjudicated within that coverage.
