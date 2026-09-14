# Mobile opening viewport preview

Owner request: keep the first section on each mobile page filling the visible screen, with the following section appearing after scrolling. This supersedes the older content-height-only mobile opening direction for this scoped preview.

Status: owner approved publication; release checks in progress. Production baseline remains `75bf0522267eff4ca7801a0ced9bad6dcb9fb631` (PR273) until deployment verification. Branch: `fix/mobile-opening-viewport`.

The mobile stylesheet supplies a viewport minimum, and the shared controller measures the opening's actual flow position. This handles normal heroes, naturally proportioned Art study images, topic wrappers, the gallery, Come Follow Me and General Conference. Introductory copy and buttons remain grouped. Long content can extend naturally beyond a short screen. Standard hero images stay at 300px; flexible topic and Come Follow Me artwork can adjust with viewport height under their existing sizing rules. No artwork files or content were edited.

Verification:

- 144 completed real in-app-browser cases: all 35 sitemap pages plus 404 at 360x640, 390x844, 432x810 and 700x500. Every opening reached at least the viewport bottom, with no horizontal overflow.
- 16 production/local geometry comparisons across eight representative page families at requested widths 701 and 1440, height 900: identical opening position and height. Browser pixel rounding produced 702 CSS px for the requested 701-width case; both sides used the same actual width.
- Home and Answers mobile screenshots inspected. Answers Continue revealed the topic navigation; actual scroll position was 788.8px at 390x844.
- Site QA, site flow QA and media voice QA passed. JavaScript syntax, question safety regression and whitespace checks passed.
- Independent read-only review accepted the final two-file implementation without blocking findings.

Failures retained: first constant-height approach undersized four natural-ratio Art openings; actual flow measurement fixed it. Short landscape topic wrappers exposed the next section because their existing short-window rule removed the viewport minimum; the wrapper minimum fixed it. Initial production comparison attempts encountered an about:blank evaluation context on the gallery; bounded reload recovered it and the complete comparison was rerun. An initial Continue selector used displayed text rather than its accessible label; the observed accessible label completed the interaction.

Limits: browser viewport testing is not physical Android/iOS toolbar certification. No public deployment, universal crop identity across changing toolbar states, or owner visual acceptance is claimed.

Release authorization: Wyatt explicitly instructed "Publish" after reviewing the prepared result. Shared CSS and JavaScript references are versioned in the public HTML so returning browsers request the approved files. Required release checks, GitHub Pages publication and exact public-byte/mobile verification follow. Preserve other active Focus work. Existing production is the rollback baseline.
