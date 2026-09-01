# Ask Context and Visible-Prompt Repair - 2026-09-01

## Current state

Overall release state: `INCOMPLETE`.

The exact owner-reproduced failures now pass local final-owner runtime tests, but the repair is not complete until independent verification, merge, deployment, exact-revision confirmation, and fully loaded production journeys pass.

## Reproduced failures

1. Main Ask lost the Joseph Smith subject in the follow-up `Do we know the time he died` and returned a general-answer failure.
2. Pioneer topic `Handcart Companies` was not an exact reviewed match and returned a source-verification refusal.
3. Main Ask starter `Who is Jesus Christ, and why is He central to Latter-day Saint belief?` entered the remote source lane and returned the same refusal.
4. The owner observed answers that were only one or two words or otherwise too brief to be useful.
5. Live post-deploy adversarial testing showed that a reviewed Joseph Smith chain worked, but a general follow-up after changing the subject to Abraham Lincoln still returned the generic completion failure.
6. The Church History `Plural marriage` card submitted `How does the Church explain Joseph Smith and plural marriage?` and returned the generic source-verification refusal even though the page displayed official study routes.
7. Independent adversarial review found that `How old was he?` after Joseph Smith could embed the antecedent for research and then accidentally rematch that augmented query to the death entry, replaying the wrong answer.
8. The first competing-subject heuristic treated any capitalized two-word phrase as a person, so a place such as `Carthage Jail` could incorrectly break valid Joseph Smith context.
9. Live `.11` acceptance proved the new routing was active but exposed a Worker `429 rate_limit_exceeded` failure: `How old was he?` correctly retained Joseph Smith context, yet the exhausted research provider caused the browser guard to show the generic source-verification refusal.

## Root causes

- Context was supplied to generative prompts but was not resolved before classification, reviewed-local matching, and source-lane selection.
- The reviewed matcher required date/start language for handcart history, so the page's own exact visible label missed the reviewed answer.
- Main Ask starter questions were visible product promises but were not represented as reviewed executable contracts.
- Prompt language repeatedly optimized for concision without a minimum usefulness standard.
- Prior completion evidence tested isolated facts, not the exact live conversational and clickable paths later used by the owner.
- The first contextual repair resolved only subjects represented in reviewed local knowledge. The general research lane still received an ambiguous follow-up even though conversation history existed, so retrieval and verification could fail before the model produced an answer.
- The Church History cards had source-router links but no answer contract. Source discovery and answer generation were incorrectly treated as equivalent, so verifier rejection could erase the answer while leaving links visible.
- Prior QA used a hand-written sample instead of extracting every exact visible question from the current HTML. Nine of ten Church History card submissions were therefore orphaned from reviewed knowledge and final-owner tests.
- A generic follow-up query was built by appending the antecedent, then was allowed to re-enter local reviewed and legacy matchers. That conflated contextual research input with a new local-answer candidate.
- Proper-name detection was capitalization-based rather than syntax- and domain-aware, creating false subject changes for historical places and titles.
- Reviewed context supported only the prior death/date intent. Other stable, source-supported Joseph Smith follow-ups were sent to remote research even though the site could own them safely; provider exhaustion therefore became an avoidable user-visible failure.

## Repair

- Added data-driven exact matching for visible prompts without weakening negative domain guards.
- Added safe reviewed follow-up resolution before classification and matching, with declared entry anchors/cues, referential-pronoun requirements unless ellipsis is explicitly permitted, competing-identity controls, persisted context receipts for chained follow-ups, newest-user-turn-only inheritance, and reset boundaries.
- Extended the same resolver to unreviewed general and historical subjects. It now makes the immediately preceding user question explicit to research, persists that root subject through chained ellipses, never skips backward across a newer subject, and keeps the visitor's original wording in the visible transcript.
- Expanded the Joseph Smith answer with the responsible historical time: about or shortly after 5:00 p.m. on June 27, 1844, without claiming an unsupported exact minute.
- Added substantive reviewed answers and official sources for all six visible main Ask starters.
- Added an exact, substantive reviewed answer for the visible `Handcart Companies` topic.
- Added a cross-client and Worker answer-depth contract: direct answer plus useful context for simple facts; normally two to five short paragraphs for nuanced questions; never one- or two-word answers unless explicitly requested.
- Added final-owner regression tests for real follow-up history, reset isolation, visible starter inventory, visible Handcart topic, zero-Worker local routing, answer substance, negative controls, and integrity hashes.
- Added substantive, officially sourced reviewed answers for all ten exact Church History card questions, including plural marriage, seer stones, priesthood restoration, the Kirtland Safety Society, Mountain Meadows, Willie and Martin, Word of Wisdom development, global growth, and women\'s history.
- Added `ask-question-contracts.json`, generated from the actual production controls, and count/exact-value reconciliation for all Ask starters, Ask topics, Pioneer topics, and Church History cards.
- Added final-owner execution of every discovered Ask topic, Pioneer topic, and Church History card; all exact Church History cards require at least 70 words, official sources, and zero Worker calls.
- Generic contextual research now bypasses both reviewed and legacy local matching after the original wording has had its direct-match opportunity. Explicit current people override inherited context, while multiword historical places such as `Carthage Jail` do not.
- Added regression specimens for `How old was he?`, `Why was he in Carthage Jail?`, `Who was with him?`, `Where did he live?`, and explicit Abraham Lincoln appositives.
- Added integrity-pinned contextual answer variants for Joseph Smith's age at death, Carthage imprisonment, the historical context of the attack, companions during the attack, and his Nauvoo residence at the end of his life. Intent-specific phrase rules prevent overlapping words such as “who,” “why,” “where,” “Carthage,” and “jail” from selecting the wrong answer. Main Ask, Pioneer, and Church History return these variants with official sources and zero Worker calls even under rate limits.
- Live `.12` acceptance showed that general research and subject continuity were correct, but the verifier could still compress an exact factual follow-up into one sentence. Gateway policy `.13` now enforces numeric answer-depth thresholds after verification, performs one evidence-only expansion pass for a short approved answer, and rejects any result that remains too brief.

## Completion gates

- full repository suite;
- independent current-tree verifier;
- exact local/remote tree identity;
- pull-request and post-merge release gates;
- live main Ask Joseph Smith date and time follow-up;
- live main Ask general-subject change and follow-up (`Abraham Lincoln` -> `Do we know the time he died?` -> `What time?`);
- live reset isolation;
- live Jesus Christ starter answer;
- live Pioneer Handcart Companies topic;
- live Church History Joseph Smith follow-up;
- every live Church History card, especially `Plural marriage`, through the actual button;
- live generic Joseph Smith research follow-ups without replaying the death answer;
- live explicit Abraham Lincoln override and `Carthage Jail` place-context preservation;
- exact Worker policy and browser cache version;
- project-state, recovery, control, and reusable-learning close receipt.
