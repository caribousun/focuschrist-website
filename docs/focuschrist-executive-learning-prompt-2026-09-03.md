# focusChrist Executive Learning and Execution Prompt

Updated: 2026-09-03

## Authority and purpose

This prompt governs future focusChrist design, artwork, interaction, Shorts, testing, and publishing work. Its purpose is to turn owner intent into a coherent result with fewer tool calls, fewer regressions, and no unsolicited product changes.

The standard is not whether a change technically works. The standard is whether it faithfully does what Wyatt asked, preserves what already works, looks intentionally composed, performs well, and is verified in the real experience.

## 1. Lock the request before changing anything

At the start of every task, write an internal intent lock containing:

1. The exact requested outcome.
2. The existing reference that defines success.
3. The elements that must not change.
4. The decisions that require owner approval.
5. The shortest coherent implementation that satisfies the request.

Do not broaden the task because another improvement seems convenient. Adding artwork does not authorize new controls, new copy, new navigation, or interaction changes. Fix an adjacent defect only when it prevents the requested experience from working, and state why it is necessary.

For the current artwork program, the Missionary page is the primary presentation reference. It establishes editorial image splits, varied left and right placement, generous spacing, realistic imagery, quiet surfaces, and a natural reading rhythm. Do not reduce this reference to a generic centered image or repeated card grid.

## 2. Protect working behavior

Before editing a working page:

- Identify its primary visitor action.
- Trace the complete interaction from entry through completion and continuation.
- Record existing controls and distinguish owner-approved controls from generated additions.
- Preserve conversation state, sources, answer positioning, topic routing, and reset boundaries unless Wyatt asks to change them.
- Never introduce a control merely to satisfy a test or imagined usability concern.

For Ask, the visitor must be able to ask the first question immediately, read the answer, and ask a follow-up without searching or scrolling through unrelated page content. The original New Question control remains the reset path. Do not inject extra Clear Conversation or Clear and Start Over pills.

## 3. Compose artwork as part of the page

Artwork is content, not decoration placed after the layout is finished.

For every page:

1. Read the page and identify its major themes and natural pauses.
2. Decide how many images improve the full page. Do not force one image per page and do not add images merely to fill space.
3. Give each image a specific narrative job and nearby content relationship.
4. Choose a composition for the section: large-left split, large-right split, inset portrait, wide transition, or another deliberate editorial arrangement.
5. Alternate visual weight and placement where it improves the page rhythm.
6. Keep controls, forms, source links, and reading areas clear.
7. Verify the complete page at desktop and mobile sizes before publishing.

All new artwork must use cinematic photographic realism. Jesus Christ must retain the approved focusChrist likeness. Faces, hands, fabric, skin, light, and environments must look natural. Reject cartoon, painted, glossy, theatrical, game-rendered, or fantasy results.

Heroes remain unchanged unless Wyatt separately approves a hero change.

## 4. Use approval intelligently

- Generate artwork from a page-specific brief that includes subject, doctrine or story, placement, aspect ratio, realism standard, lighting, and exclusions.
- Present a candidate in its intended page context when placement materially affects the decision.
- Once Wyatt approves an image, record the approval and do not ask again.
- A rejected image and its rejection reason become an exclusion for future prompts.
- Do not integrate an unapproved replacement merely because it is available.

## 5. Preserve quality without slowing the site

- Store production artwork locally as WebP.
- Create responsive variants for the actual rendered width.
- Include width and height attributes to prevent layout movement.
- Lazy-load supporting artwork and decode it asynchronously.
- Prefer a practical delivered-image budget of 120 KB or less per variant while preserving visible quality.
- Never load source-resolution artwork when a smaller responsive variant will look equally good.
- Verify broken images, layout movement, horizontal overflow, and mobile crops.

## 6. Make Home and Ask serve their primary purpose

Home is the welcoming front door. It should communicate Jesus Christ, purpose, and clear study paths without feeling crowded. Supporting artwork must be integrated with the section it explains, not dropped between unrelated grids.

Ask is a working study surface. Artwork may beautify and frame the experience, but it must not push the first question, answer, or follow-up workflow out of reach. After an answer appears, the follow-up composer must be visible with the conversation.

## 7. Use the fastest correct GitHub path

Before opening GitHub in a browser, discover available repository tools and authentication.

The preferred Work Mode release path is:

1. Read the exact current main revision.
2. Create one branch from that revision.
3. Create file blobs in parallel where safe.
4. Create one tree containing all changed paths.
5. Create one commit.
6. Move the branch reference once.
7. Open one pull request.
8. Observe required checks.
9. Merge once checks pass.
10. Observe the production workflow and verify the exact live revision.

Use the authenticated GitHub integration for these operations. Do not upload files one directory at a time through the GitHub website. Use browser interaction only when a capability is genuinely unavailable or visual inspection is required.

The local GitHub CLI may be useful for reading and local repository work, but do not spend time repairing shell authentication when the authenticated integration already provides the required repository mutation safely.

## 8. Verify the experience, not only the files

Run the project QA gates, but do not confuse passing tests with a good page.

Verification must include:

- Intent comparison against the original request.
- Visual comparison against the named reference page.
- Desktop composition and mobile stacking.
- Primary interaction from start to continuation.
- No unsolicited controls or copy.
- Image loading, responsive selection, and size budget.
- Required accessibility and source-integrity behavior.
- Exact deployed revision and live production rendering.

When a defect is found, fix both the instance and the reusable guard. A guard must protect the owner’s real intent, not freeze a mistaken implementation.

## 9. Shorts production and learning standard

Each Short must have one primary spiritual idea and one clear emotional movement. Use a truthful hook, accurate source material, concise narration, readable captions, and a visual sequence that changes often enough to sustain attention without becoming frantic.

For each Short:

1. Select one message, scripture, testimony, teaching, or story.
2. Write a hook that accurately promises the payoff.
3. Build a short beginning, development, and conclusion.
4. Use vertical 9:16 composition and keep faces, captions, and key action inside mobile-safe areas.
5. Use realistic, reverent visuals consistent with focusChrist and @theRisen636.
6. Route the viewer to the exact relevant focusChrist study page. Use Ask only as a secondary continuation path when it adds value.
7. Record the title, description, source, page destination, visual assets, and publication result.
8. Learn from retention, watch time, replays, swipe-away rate, returning viewers, subscriber conversion, search terms, and site click-through.

Do not generalize from one Short. Compare repeated patterns across several releases before changing the production standard.

## 10. Durable learning requirement

At the end of material work, update the relevant project standard with:

- The owner decision.
- What failed and why.
- The corrected invariant.
- The regression or review guard.
- The exact released revision.
- Any approved or rejected artwork and its placement.

Do not rely on chat memory alone. Read the current standards at the beginning of the next task.

## Current corrective directive

Execute these corrections before expanding the artwork program:

1. Remove the unsolicited Ask reset pills while keeping the original New Question behavior.
2. Keep the follow-up composer with the conversation and make it visible after an answer without requiring page hunting.
3. Recompose the Home supporting artwork into a Missionary-style editorial split.
4. Audit every primary page and define page-specific artwork themes, counts, placements, aspect ratios, and performance variants.
5. Generate new artwork only from those briefs and integrate only approved candidates.
6. Preserve today’s Shorts workflow in a durable production standard.
7. Release through the authenticated GitHub integration in one branch, one commit, and one pull request whenever practical.

