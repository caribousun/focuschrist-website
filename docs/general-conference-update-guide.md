# General Conference update and review guide

Use this guide for the April 2027 update and later conferences. It records Wyatt's October 2026 directions and the defects that escaped the first review. It is a recovery guide, not authority to invent future sources or bypass current owner instructions. Start with the live Master protected foundation, latest 00B, Focus Current State and current repository mandates. Their newer scoped instructions take precedence.

## Preserve the established experience

Wyatt requested the exact existing format, look and feel, changing only needed wording, official video/read destinations and native thumbnails. Preserve original artwork, typography, colors, footer, hero width/height/framing and the exact Continue position and outer dimensions. Archive the prior collection on the same page in its original session order. Do not silently resume deferred opening flash/reflow, download formats or the held unrelated audit. Focus remains noncommercial; no new cost, schedules or replacement cloud workers.

The October update contains 38 official messages in four sessions (9/10/9/10) and retains 37 April messages (9/10/9/9). Those are historical counts, not future defaults. Derive the next conference's actual index, sessions, message identities and counts from the current official collection. Keep source titles, speaker bylines, roles, order, destinations and native poster provenance exact. Attribute unfamiliar speakers through official source bindings, not face recognition.

## Update the complete dependency set

1. Preserve a clean release baseline and use an isolated branch/worktree. Reconcile pending work and one action owner before editing.
2. Build a source manifest from the official collection and individual messages. Record native poster URL, local path, SHA-256 and dimensions. Retrieve the original preview; do not replace it with generated artwork or force a different crop. The October sustaining poster is 3:2 and must remain contained within the established card frame.
3. Update current message cards, current session counts, introductory statistics, collection links, six topic pathways and optional reflections. Ground pathway prose in actual transcripts, write warmly, and avoid visitor-facing verification jargon. Preserve exact quotations and official titles. Keep the AI/artwork disclosure in the existing footer only.
4. Move the preceding collection into the labeled archive without losing messages, sources or order. Use distinct archive attributes so current search/session filters cannot hide, open or count archived cards. Nested disclosure styling must target each details element's own direct summary.
5. Update the source ledger, homepage wording and generated search index. Refresh only genuinely affected content-audit records. Update actual panel inventory counts (October: 75 cards and nine disclosures). Derive counts from current markup rather than copying old values.
6. If CSS changes, discover every consumer, update exactly one cache reference on each, and update the narrow byte-preserving inverse in `tools/anchor_alignment_qa.py`. Current consumers are `general-conference.html` and `answers.html`; verify discovery anew. Reject missing, duplicate, mixed, old, unknown and unrelated versions. Do not weaken unrelated artwork/layout bindings.
7. Preserve unchanged source/contact-sheet evidence. Any changed page/CSS context requires fresh, truthful reviewer consent and root rendered evidence in `docs/conference-2026-10-native-review.json` or the new period's explicitly reviewed equivalent. Do not merely rewrite hashes to pass a gate. New source sets require new substantive review, exact finite bindings and negative cases in the native source gate. Never give the entire resources directory a blanket exception.

Do not blindly rerun the historical workspace update script: it preceded later corrections and can overwrite them. Review any generator's output against the current published state before use.

## Required people and independent concurrence

Wyatt explicitly requested two UI reviewers after he found issues the first inspection missed. These are distinct agent assignments, not claims of human credentials.

- **UI reviewer 1:** inspect the actual rendered page, diagnose and implement the smallest justified layout correction; retain before/after evidence.
- **UI reviewer 2:** independently operate and inspect the rendered result, including the owner's screenshot cases. Review the full composition and controls, not only the first reviewer's report. Own or independently verify recurrence tests.
- **Fermi and Newton:** read the current applicable mandates, independently verify source/prose/preservation and the exact final candidate. Newton may also serve as UI reviewer 2, but each responsibility requires its own evidence.
- **Albert/root:** reconcile both UI reviews, personally inspect the assembled desktop/phone result, verify exact-head manifests and own publication/closure. Agreement or a numerical test pass alone is not sufficient.

Both UI reviewers must concur, then Albert must concur, before presenting a corrected candidate as ready. Material changes invalidate affected approvals. Serialize browser viewport changes if reviewers share a browser; use separate task tabs and explicit ownership handoff. Reuse unchanged evidence, but never substitute an old narrower review for a new owner-reported case.

## Visual checks that must not be missed

Inspect wide desktop at the owner's actual screenshot dimensions as well as ordinary desktop and narrow/wide phone. October's missed cases appeared around 1722–1905 pixels: a 1280-pixel pass did not prove wide-canvas centering. Record actual viewport dimensions, zoom/scaling, scrollbar and screenshot clipping limitations. Obtain complete-width settled screenshots and wait for lazy images through normal page traversal.

- Inspect the complete page, every section transition and footer, both default/collapsed state and all current and archived sessions expanded. Inspect every card and final row, not only one session or the top screen.
- Center the whole study-navigation group and each wrapped row within its parent. Centering the text inside each button is a different requirement. Preserve the established mobile grid and full-width odd final item.
- Center constrained artwork-and-description compositions within the full content canvas. Their parent `.gc-heading` can be narrower than the section; centering only the image inside that left-aligned parent does not fix the group. Inspect all five body compositions; preserve already full-width compositions and intrinsic image proportions.
- Inspect the **Session dropdown** chevron. Wyatt clarified this was the arrow he reported, not Continue or the archive pill. A browser-native chevron sat approximately 4 pixels from the right border despite input padding. Reuse the established full-image-viewer select treatment: native semantic select, custom chevron with explicit inset and reserved text space, retained height, focus and keyboard behavior. Do not conflate ordinary text-arrow padding with the dropdown glyph.
- Filter with single, two and multiple nonconsecutive results, combined session/text filters, no match and reset. Physical `nth-child` counts hidden cards: October's Oaks search left a 378-pixel card beside roughly 793 pixels of empty row. Count only visible children for row balance, reset inherited physical-index spans, and preserve unfiltered/archive geometry.
- Recheck hero/picture/Continue rectangles against the published baseline. Whitespace correction never authorizes moving Continue or resizing the hero. Inspect the pixels as well as rectangles.

## Meaningful prevention checks

Run applicable source, runtime, panel inventory, content-audit, native-review and exact CSS/cache-binding checks. The browser regression `tools/conference_alignment_browser_qa.js` checks wide/ordinary desktop and phone, every navigation row, all five body groups, dropdown inset and locked opening geometry. It must reject the genuinely defective released CSS and a deliberately broken arrow placement. A test that only mirrors desired declarations is insufficient; preserve actual rendered geometry checks and negative controls.

The original source/runtime tests retain exact current/archive identities, isolated filtering, contained native posters, no-match/reset and nested summary behavior. Keep source and visual tests separate. A successful full-site screenshot count, overflow check or stylesheet hash does not prove composition, accurate content or owner visual acceptance.

## Release and durable completion

Freeze the final candidate. Require independent Fermi/Newton committed-blob manifests to agree with each other and actual Git blobs, plus UI1/UI2/root rendered concurrence. Push a reviewable PR, pass exact-head CI, mark ready, and merge with an expected-head guard. Confirm merged tree equals reviewed tree. Require main QA and deployment success, then two independently executed ordinary public GET comparisons for every changed public path, using exact merged bytes/length/SHA-256 and no cache-busting query. Personally check the ordinary live desktop/phone page and original failure triggers.

Use fresh revision guards for additive 00B/Focus/START/Run Log closeouts; cold-read the exact new record, all prior text and tab topology. Preserve original failed checks and owner corrections as history, with newest scoped instructions first. Save evidence paths, candidate/merge/tree/run IDs, finite coverage, limitations, rollback, assignments and next action. A candidate, merged PR, deployment receipt or saved handoff alone is not public proof. Owner visual acceptance and physical-device/full-playback testing remain separate.

October recovery: PR464 published merge `317200dc4ceec0c0b17989873f5d44c94b3cae08`; the later owner-reported centering/Session-chevron corrections are tracked in the newest canonical Focus record. Original source evidence is under `C:/Users/wyatt/Documents/Codex/2026-10-07/conti/work`; continuation and correction evidence is under `C:/Users/wyatt/Documents/Codex/2026-10-07/focus-october-conference-publication/work`. Consult final live records for the newest release, not this historical base.

After the correction is complete, preserve a user-authorized memory pointer to this guide and the canonical release record. For the April 2027 update, read that guide before editing, refresh official sources and applicable controls, and repeat the finite acceptance gates without rediscovering already verified causes. Never promise that stored lessons alone guarantee no future defects.
