# Uniform gold mobile continuation cues

Owner follow-up to PR275: present the words and down arrow in the same location on each page and use the site's gold.

Each study opening now owns its mobile cue directly. The cue is centered 20px above the opening bottom, with a 44px touch target and 88px reserved space. This leaves at least 24px between the content and cue. Topic openings reserve that space in their nested introduction; Come, Follow Me's cue sits above its background overlay. Every cue uses the same site gold, #e8b54d, instead of page-specific gold variable overrides. General Conference's top padding is reduced by 4px to retain first-screen clearance.

Verification: all 140 browser cases (35 study pages at 360x640, 390x844, 432x810, 700x500) passed centered alignment, consistent gold, bottom clearance, at least 23px measured content separation, and no horizontal overflow. All 70 cases at the two taller portrait sizes fit the first screen. Sixteen production/local tablet and desktop comparisons matched. Home and Come, Follow Me mobile screenshots were reviewed. Independent final implementation review and all 100 local workflow commands passed.

The existing target links, labels, hero files/heights and desktop presentation remain. Very short screens may scroll naturally to the cue at the opening bottom; the cue is not fixed over scrolling content. The 404 page still has no study continuation cue. Physical device toolbar and text-only magnification behavior are not certified by this normal viewport review.
