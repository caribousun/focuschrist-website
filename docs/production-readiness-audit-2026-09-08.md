# focusChrist production-readiness audit — September 8, 2026

## Scope

The audit used `sitemap.xml` as the public inventory: 33 routes, including 18 permanent Answer studies and four Art study pages. It also inspected 36 HTML documents for metadata, accessibility, local references and shared experience requirements.

## Defects repaired

1. Cross-site Ask links ended in `#ask-question`, but the Ask composer did not expose that fragment target. The composer now owns the anchor and includes a fixed-header scroll offset.
2. Eighteen Pioneer category actions were links to `#`. They are now semantic buttons, preventing jump-to-top behavior and accurately representing their in-page action.
3. The Doctrine and Covenants 6 study existed as a permanent page but was absent from the Answer Library hub. It now has both a jump link and a full descriptive study card.
4. The same study used a shortened custom resource menu. It now preserves its page-specific resources while also exposing the complete canonical site resource set.
5. Answer QA depended on a hand-maintained list that had omitted two permanent pages. It now discovers every `answers/*.html` page automatically and requires each one on the hub.
6. The Doctrine and Covenants 6 signature study did not opt into the shared responsive topic-opening layout, leaving its actions below the desktop viewport. It now uses the same responsive opening contract while retaining its signature-study styling.

## New release protections

`tools/site_flow_qa.py` is now required by both general CI and the Pages deployment workflow. It blocks release when a sitemap route is missing, a local destination or fragment is unresolved, a public `href="#"` control is inert, or a page lacks at least two meaningful local continuation paths.

The existing content, caption, source-integrity, responsive-layout, runtime, accessibility, discovery and production-hardening gates remain in force. Generic image and introduction placeholders continue to be release-blocking patterns.

The responsive review harness now audits both the shared opening layout and custom H1-based pages, tolerates verified subpixel/scrollbar rounding without weakening its substantive checks, and skips non-resource uses of the shared study-feature class instead of aborting the matrix.

## Verification evidence

- Site QA: PASS — 9 core pages, 18 automatically discovered Answer pages, four Art studies and 44 gallery images.
- Site-flow QA: PASS — all 33 routes, destinations and fragments; no inert public links; multiple continuation paths on every route.
- Static content audit: PASS — 36 documents.
- Unified experience QA: PASS — all 33 public pages.
- Production hardening QA: PASS.
- Church source freshness: PASS — revision `2026-07-15T14:36:25Z`.
- Pioneer runtime failure, stale-response and local-first controls: PASS.
- Whitespace/error scan: PASS.

Independent review, hosted CI and post-deployment live interaction checks remain mandatory before the release is declared complete.
