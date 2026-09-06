# Production closeout: named Gospel Topic evidence

Owner requested completion of remaining site work before closing, and selected the original First Vision artwork. All three enhancement experiments remain unapproved previews. The approved image and responsive variants are unchanged.

## Observed defect
The production respectful-interfaith question returned a verification fallback on Worker policy .53. A focused raw response showed verifier approved true, two source indexes and an895-character candidate, but the final publication guard rejected it. The old response did not expose which publication rule failed, so the exact guard reason cannot be asserted from that receipt.

Independent source review found a concrete retrieval defect: the Religious Freedom article was truncated to700 characters, cutting a paragraph midword and excluding its explanation about defending other people's religious freedom. A second source, Religious Beliefs in Joseph Smith's Day, matched generic words but was less relevant to the question. Official source: https://www.churchofjesuschrist.org/study/manual/gospel-topics/religious-freedom?lang=eng

## Correction
On main Ask, when the highest-ranked Gospel Topic has a unique fully matched multiword title, retrieve that named article alone. Explicit comparisons, multiple matched titles, scripture references and dedicated history routing retain their existing source-selection behavior. Select complete relevant paragraphs within the existing4200-character scripture budget and use question-specific cache keys. The actual official HTML produced3811 characters cold and3366 warm; both retain the directly responsive interfaith passage and intact paragraph endings, including source footnote numbers.

The publication guard now returns a diagnostic reason internally and exposes only its bounded reason code on fallback. It still rejects unapproved, empty, unsupported-source, known-false, excessively copied and insufficient-depth responses under the same criteria. No provider, model, spending policy or answer-depth requirement changed. Worker policy and excerpt cache version .54 invalidate stale truncated packs. The live interfaith gate additionally requires the named source route, one evidence source and at most one official fetch.

## Acceptance
Independent review and required local checks precede commit. Production Worker deployment runs the full live AI response matrix. A successful static-site deployment alone does not establish AI acceptance. Exact final PR, deployment and live matrix receipts belong in Focus Current State and Run Log after verification. Keep a remaining limitation explicit if any gate fails; do not weaken or repeatedly rerun unchanged tests to create a pass.
