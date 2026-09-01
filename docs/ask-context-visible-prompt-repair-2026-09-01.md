# Ask Context and Visible-Prompt Repair - 2026-09-01

## Current state

Overall release state: `INCOMPLETE`.

The exact owner-reproduced failures now pass local final-owner runtime tests, but the repair is not complete until independent verification, merge, deployment, exact-revision confirmation, and fully loaded production journeys pass.

## Reproduced failures

1. Main Ask lost the Joseph Smith subject in the follow-up `Do we know the time he died` and returned a general-answer failure.
2. Pioneer topic `Handcart Companies` was not an exact reviewed match and returned a source-verification refusal.
3. Main Ask starter `Who is Jesus Christ, and why is He central to Latter-day Saint belief?` entered the remote source lane and returned the same refusal.
4. The owner observed answers that were only one or two words or otherwise too brief to be useful.

## Root causes

- Context was supplied to generative prompts but was not resolved before classification, reviewed-local matching, and source-lane selection.
- The reviewed matcher required date/start language for handcart history, so the page's own exact visible label missed the reviewed answer.
- Main Ask starter questions were visible product promises but were not represented as reviewed executable contracts.
- Prompt language repeatedly optimized for concision without a minimum usefulness standard.
- Prior completion evidence tested isolated facts, not the exact live conversational and clickable paths later used by the owner.

## Repair

- Added data-driven exact matching for visible prompts without weakening negative domain guards.
- Added safe reviewed follow-up resolution before classification and matching, with declared entry anchors/cues, referential-pronoun requirements unless ellipsis is explicitly permitted, competing-identity controls, persisted context receipts for chained follow-ups, newest-user-turn-only inheritance, and reset boundaries.
- Expanded the Joseph Smith answer with the responsible historical time: about or shortly after 5:00 p.m. on June 27, 1844, without claiming an unsupported exact minute.
- Added substantive reviewed answers and official sources for all six visible main Ask starters.
- Added an exact, substantive reviewed answer for the visible `Handcart Companies` topic.
- Added a cross-client and Worker answer-depth contract: direct answer plus useful context for simple facts; normally two to five short paragraphs for nuanced questions; never one- or two-word answers unless explicitly requested.
- Added final-owner regression tests for real follow-up history, reset isolation, visible starter inventory, visible Handcart topic, zero-Worker local routing, answer substance, negative controls, and integrity hashes.

## Completion gates

- full repository suite;
- independent current-tree verifier;
- exact local/remote tree identity;
- pull-request and post-merge release gates;
- live main Ask Joseph Smith date and time follow-up;
- live reset isolation;
- live Jesus Christ starter answer;
- live Pioneer Handcart Companies topic;
- live Church History Joseph Smith follow-up;
- exact Worker policy and browser cache version;
- project-state, recovery, control, and reusable-learning close receipt.
