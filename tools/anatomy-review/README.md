# Anatomy Review Desk

A local reference and review tool for artwork. It makes reviewers trace complete limbs, name the person and anatomical side, distinguish palm/back/edge views, inspect contact, record occlusion and compare exact candidate bytes against rejections.

**This is not an automatic image-anatomy detector, a medical model or a rescue-safety validator. A complete review is not a claim that the image is anatomically correct.** Generated pixels still require direct comparison with an established pose and the owner's feedback.

## Use

Open index.html through a local web server. Load a candidate and pose references. Files stay in the browser; no uploads, accounts or external libraries are used. For each participant, map the complete arm or leg and explicitly describe any obscured landmark. Zoom to inspect digits and return to the whole pose. Describe each contact and complete the actual-image checks. Save the JSON review with its exact candidate SHA-256.

The optional references.json supplies local reference previews. Private owner-supplied images belong in the local deliverable package, not the public website repository.

For repeatable verification:

```
node tools/anatomy-review/core.test.js
node tools/anatomy-review/audit.js review.json candidate.png tools/anatomy-review/rejected-hashes.json
```

The audit blocks incomplete reviews, incompatible annotations, mismatched candidate bytes and explicitly rejected hashes. Hidden anatomy is not inferred. Foreshortening and oblique surfaces require a posed reference and human judgment. Do not mirror an isolated hand to change its side.

## Before generation

1. Lock each identity to actual approved reference pixels. Record anatomical left/right, visible surfaces, and which hand touches what.
2. Establish both complete limb chains and contact in a physical or trustworthy illustrated/3D pose reference. Do not substitute a plausible-looking isolated hand.
3. If two local repairs fail, reject them and rebuild the complete interacting pose. Keep rejected sources and hashes so later sessions cannot select them by accident.
4. Inspect a clear pose study before returning it to a detailed scene. For a reciprocal forearm grasp, two forearms overlap beside each other; each continues to its own wrist and hand. A single shaft with two disconnected wraps is a failure.
5. Compare the final full scene, close limbs/digits and phone presentation. Technical review is separate from explicit owner acceptance.

## Current Peter rescue correction

Wyatt specified Peter's LEFT arm. Christ's original right-arm pose was an assistant assumption, not an owner-locked requirement; a complete shoulder-to-hand repose may use His left arm if that establishes the supplied grasp naturally. Wyatt supplied three example grasp images. The attempts recorded in rejected-hashes.json were rejected or superseded, including technically passed drafts that the owner rejected. Do not treat earlier agent anatomy passes as owner acceptance.

Preserve Christ's approved face and the scene while rebuilding BOTH interacting arms. This mortal-ministry scene has no Crucifixion scars. The website-wide ten-picture enrichment mandate is a separate queued rollout; consult docs/enriched-picture-owner-mandate.md.

## References

- https://openstax.org/books/anatomy-and-physiology-2e/pages/8-2-bones-of-the-upper-limb
- https://openstax.org/books/anatomy-and-physiology-2e/pages/9-5-types-of-body-movements
- https://www.assh.org/handcare/anatomies

These establish anatomy terminology and continuity. They do not establish any generated grip as correct or load safe.

## Approved final rescue scene

Wyatt approved the final expression variant exec-40def308-5c69-4658-8167-4b0d512a91db.png on 2026-09-19. The image and source hashes, exact owner approval, approved grip-reference hash and rejected predecessors are recorded in docs/sitewide-narrative-supporting-review.json. The approved full/thumbnail sibling assets preserve the previous image bytes. The private workbench includes the exact owner-approved grip reference; it must not be added to this public source folder.
