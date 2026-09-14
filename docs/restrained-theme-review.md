# Restrained body theme and editorial alignment

Owner-authorized refinement of the Home and History screenshots, 2026-09-14.

The previous transparent-edge gradients removed hard seams but repeated broad green washes still read as bands. Replace warm/CFM, History question and About closing wrapper washes with a faint .035-opacity elliptical accent. Reduce the dark wrapper accent to .06. The ellipse reaches transparency before the vertical section boundaries, leaving the continuous blue body field dominant. Existing green card fills provide the stronger color emphasis.

Remove the center modifiers only from the Home and History evidence-entry card headings and actions. Their text and controls now share a left edge with the eyebrow and description. Standalone Home invitations remain centered. No spacing, typography, card fill, artwork, header or opening geometry is changed.

Validation: 102 workflow checks exercised; 101 passed initially. The unified cache-version assertion caught its stale expected value; synchronized it with all 37 page references and reran successfully. Preserve this failed-attempt evidence in the release receipt. Independent diff review: ACCEPT. Settled browser review at 390x844 and 1280x900 covered all 37 public routes (74 cases, 584 sections), with no overflow or changes to compared opening rectangles. Home desktop/phone and History phone were visually inspected. Emulated layouts do not certify physical browser toolbar behavior.

For future visual reviews, inspect the whole composition: transparent gradient endpoints alone do not establish a continuous appearance. Keep background accents subordinate to artwork and cards. Preserve the shared spacing scale and deliberate alignment differences between editorial cards and standalone invitations.

Rollback baseline: 1bda30decf961a0cd7afc85eeaf4854fa5de9cd9 (PR280).
