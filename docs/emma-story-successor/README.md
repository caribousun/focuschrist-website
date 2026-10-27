# Emma story successor

Registration layer for the Emma Hale Smith story enrichment
doorways and hub reading-flow remedies, in one file:

- `history/emma-hale-smith.html`: a "More of Emma's stories"
  doorway section with five story cards, "Continue with ..."
  doorway links at the ends of hub sections 2, 3 (two, in story
  order), 4, and 6, a small doorway style block, and the three
  transition remedies judged by Hannah in the assembled candidate
  (the reworded night-prayer reflection in section 1; the pause
  paragraph and reworded reflection around the well picture in
  section 2; the boat picture and its reflection moved, wording
  unchanged, to after the David paragraph in section 6).

Why: under action A-2026-10-26-EMMA-STORY-ENRICHMENT-01, five new
Emma story pages (history/emma-elect-lady.html,
history/emma-hymns.html, history/emma-winter-crossing.html,
history/emma-relief-society.html, history/emma-last-testimony.html)
carry the concurred stage-1 story texts, and the hub is their
doorway. Under A-2026-10-26-EMMA-VISUAL-REFERENCE-COORDINATION-01,
Albert's desktop audit and Newton's pixel review of the existing
hub found that the body pictures' captions stay hidden until their
dialogs, so the flow remedies above work in the visible reading
sequence: Emma's grief is given room before the well picture and
she is named in its reflection; the night-prayer reflection begins
from Emma's own documented prayer life (the family tradition
labeled as such) before turning to the reader; and the boat
reflection's gentleness now follows David's illness instead of
preceding it.

The hub was already pinned in the continue-motion predecessors
map; this layer composes as the new outermost layer in
`tools/continue_motion_binding.py` (restore, advance, and check),
which the CI gate step runs. Restoration reproduces the mapped
AFTER bytes exactly, and the map spans then apply as before. The
figure at `#picture-emma-h4`, its artwork, caption, and id are
byte-identical, and no existing picture, caption, or source link
outside the registered spans changes.

This historical registration layer adds no image files; it pins only
the hub doorway and reading-flow spans. The current assembled candidate
separately includes the five reviewed Emma scene pictures and their WebP
derivatives. Their image, identity, source and finished-layout review
gates remain separate from this exact-span registration. Image creation
and review are not authorized or proven by this module.

`manifest.json` pins the exact spans;
`tools/emma_story_successor.py` verifies bytes, spans, and the
round trip. The pin is not review approval: the finished
candidate carries Jeff's independent exact-bytes review on the
channel, and publication requires Albert's concurrence on the
finished package.
