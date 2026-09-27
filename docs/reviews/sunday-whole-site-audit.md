# Sunday whole-site review

This is a repeatable review procedure, not a promise that every defect will be found. Passing code checks, coherent teaching, usable browser journeys, historical grounding, owner aesthetic acceptance, and publication are separate conclusions.

## Start from current authority

Read the exact connected-Drive Master and protected foundation, latest 00B, Focus Brain Map and Current State, and repository AGENTS.md. Stop if required authority is unavailable. Record the source revision, branch/head, live deployment, authorized changes and paused work. Ask no one to relay routine team messages. A scheduled review may inspect and repair only within its current authority; this document creates no schedule or publication permission.

## Divide the review without leaving gaps

Generate the current route inventory from sitemap.xml, then compare it with root/topic HTML, generated canonical sources and the build inventory. Explain every excluded nonpublic page. Give each route one named reviewer and an independent verifier. Begin at Home as a newcomer, choose different topics, and record the actual route followed; opening each URL directly is useful coverage but is not the same as following the learner journey.

For every route, record in the review receipt:

- Entry link actually followed; starting question or interest; whether the opening explains what the visitor will learn.
- Complete narrative read, including every chapter, panel, caption, question, disclosure and initially hidden text. Record chapter/panel IDs in reading order and compare them with the source inventory.
- Human-voice verdict with exact awkward sentences and replacements, or an explicit reviewed/no-change finding. Preserve quotations, doctrine, uncertainty, historical evidence and testimony boundaries. Explain unfamiliar terms before relying on them. Invite reflection without promising what the reader will feel.
- Actual chapter/next/back and onward destination followed. Check that labels describe the destination and that context survives. Record source/detail/full-size/return, media and disclosure interactions exercised for each distinct template; do not represent source inspection as clicking.
- Desktop, phone and enlarged-text findings, including the final section and footer. Include actual viewport width, font scale and screenshots for defects; document-level overflow alone does not establish unclipped controls.
- Open issue, owner-only decision, reviewer, independent verifier, evidence paths and a precise limit for anything not exercised.

All routes and all chapter sequences must be accounted for before claiming a whole-site review. Mark blocked or incomplete coverage explicitly; a sampled browser review cannot be relabeled complete.

## Reuse the established checks

The authoritative automated gate list is `.github/workflows/site-qa.yml`; run its current read-only source, source-integrity, content-ledger, generated-artifact and interaction checks rather than maintaining a second shortened list. Record each exact command, exit status and artifact. Separate provider/network checks from local checks, and never submit live Ask questions merely to satisfy this review unless that use is authorized.

`tools/canonical_presentation_browser_qa.js` inventories sitemap routes at desktop (1366), phone (390), and narrow/enlarged text (320 at 200%). Its control measurement checks text fragments and parent clipping; filled Ask composers also compare their internal scroll dimensions with visible dimensions. `tools/canonical_presentation_measurement.test.js` includes deliberately clipped native-input and textarea fixtures, so a page that fits horizontally can still fail correctly.

`tools/interaction_presentation_browser_qa.js` exercises established template interactions and calls `tools/ask_growing_composer_browser_qa.js`. That regression fills both composers with long questions, checks their complete visible text, checks Enter versus Shift+Enter, and deliberately constrains the field height to prove the measurement detects clipped rows. Its send function is mocked, so it does not contact an AI provider. `tools/ask_growing_composer.test.cjs` additionally covers programmatic drafts, shrinking, native textarea behavior and IME Enter protection. Retain existing Ask context/return and composer-scroll regressions.

Hosted browser gates may use their established Playwright runtime. Local interactive browser verification uses the supported CUA browser tools; do not launch a substitute local Playwright session. Human reviewers still read the complete teaching and follow every chapter sequence. Automated geometry and link checks cannot establish a coherent spiritual learning experience.

## Review presentation inside the controls

At minimum inspect desktop 1366 and 1920, phone 390, and narrow 320 with 200% text. Check parent rows, button labels, navigation, tabs, select menus, modal close/return controls, long source titles, images and final rows. Inspect blank gaps and clipped content, not just the presence of elements. For Ask, test incoming topic/artwork prefills, a long edited draft, a follow-up draft, shortening, newlines, Enter, Shift+Enter, IME composition, and return-to-study. Verify keyboard focus, labels and help text. A long question must remain readable without sideways scrolling or hidden rows.

## Repair and close the loop

Reproduce each defect before editing. Keep repairs narrow and independently review the final diff. Verify factual changes against primary sources before wording or artwork generation; technical image checks do not approve likeness, atmosphere, eye contact or aesthetics.

When reviewed copy changes generated metadata, synchronize its actual dependency chain: canonical source/HTML, active artwork manifests, Gallery, Search, then the content ledger. Preserve identity, destinations and approval records; do not rewrite historical audit snapshots. A stale guard is a finding to diagnose, not permission to weaken it. Re-run the affected gates and the full required hosted workflow after the final source change.

Save the route/chapter matrix, human review, browser artifacts, negative-test results, source checks and unresolved items with the reviewed head. A passing draft PR is not a live release. Obtain the required final acceptance, then separately verify deployment, public bytes, real interactions and durable continuity readback before reporting publication.

## Hosted cadence and receipts

Owner-requested cadence is Sunday04:00 in the fixed IANA timezone `America/Denver`, following Mountain daylight-saving changes rather than the owner device location. Reuse Merlin's existing `focus-weekly-watch` hosted job; do not create an additional local or cloud worker. Apply the change only after this framework and candidate checks are complete. Obtain receiving-worker acknowledgement, scheduler identity, enabled state, exact timezone/cadence, next run and last run, then a real scheduled receipt. Configuration, manual checks and scheduled execution are separate evidence.

Preserve Wyatt's quiet notification setting until he explicitly unmutes it. Keep ordinary unchanged results in durable receipts. A run must say exactly which checks were executed, which human reviews occurred and what remained blocked; never call a sampled or partially failed run a whole-site pass. Preserve maintenance authority and existing publication, cost and project boundaries.
