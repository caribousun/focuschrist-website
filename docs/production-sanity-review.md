# Production sanity review and independent challenge

The owner clarified that URL advertising means correct exposure through search, sitemaps, internal links, social previews and existing relevant channel links. This review does not assert a new advertising campaign, universal indexing, or measured audience growth.

## Bounded execution

1. Executed `full-production-sanity-prompt.md` across the 25 content pages, utility recovery, live Ask, artwork behavior and URL discovery.
2. Corrected stale sitemap dates to the actual September 6 substantive update and repaired pioneer route chronology. Church History's Pioneer Sketches exhibit documents William Clayton at Independence Rock on June 21, 1847. Three other geographic stops no longer assert unsupported July arrival dates.
3. Executed `production-verdict-challenge-prompt.md` independently. The challenger caught a new source link inside a card whose capture handler prevents navigation. `production-follow-up-repair-prompt.md` moved the source into static trail introductory text, preserving the controls.
4. In the same bounded follow-up batch, a rendered live Ask answer about Alma 32 introduced unsupported gardening details and described faith itself as the seed. Added a reviewed, narrowly matched chapter-level explanation preserving Alma's word/seed relationship, requiring the exact retrieved official chapter and substantive relevant source content. Unrelated, verse-specific and personal questions remain on the normal evidence route. Strengthened the verifier instruction against invented metaphor details and added negative/source-failure regression tests plus a live semantic regression. A source link and a model's verified flag alone do not prove semantic correctness.

## Evidence and limits

| Area | Observed result |
| --- | --- |
| Content breadth and LDS foundation | Independent review covers all 25 content pages. Core Savior, bodily Resurrection, Atonement, Restoration, scripture and ordinance teachings checked against official Church material. Site remains explicitly independent, not Church endorsed or exhaustive. |
| HTTP discovery | All 25 sitemap pages returned 200, with titles, canonical tags and no noindex response header. robots.txt and sitemap.xml returned 200. Deliberately nonexistent URL returned 404. Machine receipt: production-evidence/http-audit.json. |
| Search and share setup | All 25 pages have complete sitemap coverage, matching canonical/social URLs, descriptions, titles, share-image targets and valid JSON syntax. Discovery gate added to CI. Sitemap date truth follows actual content changes, not a recurring current-date stamp. |
| Public search evidence | Search returned Home, Ask, Answers, individual studies, Art and About, plus YouTube and Instagram references to focuschrist.com. Some search excerpts retain older page wording. This establishes some discovery, not every page's current Google indexing or traffic. |
| Source destinations | 77 of 85 unique study primary-source URLs returned HTTP 200 on bounded HEAD checks. Eight timed out; all eight were then successfully retrieved through web search/open, confirming their named resources. No failed destination was silently labeled a broken link or a verified HTTP success. Machine HEAD receipt: production-evidence/source-reachability.json. |
| Visual and interaction evidence | Earlier PR148 live verification covered Home, Christian identity, comparison, Art viewer/Good Shepherd/prayer, and History. This review added Mission → Jesus belief study, child-loss resource navigation and a rendered live Ask question. Inspected desktop layouts had no horizontal overflow. Approved images and working viewers remain preserved. |
| Mobile and performance | Responsive CSS reviewed; actual mobile viewport rendering and field Core Web Vitals were unavailable. No universal beauty, optimality or performance score is claimed. |
| Search Console | Available signed-in browser account exposes only another project's property. focusChrist indexing totals, submission receipts and search traffic could not be inspected. Existing verification file and crawl discovery remain in place. No duplicate property was created under the wrong project account. |
| Live AI baseline | Five baseline cases passed with p95 1602 ms and actual-source checks. This alone was insufficient: separate rendered semantic inspection found the Alma 32 issue described above. |
| Initial full AI matrix | Fifteen core requests completed; execution then aborted during external official-evidence validation. The pre-fix full matrix is NOT a pass. Raw receipt retained in production-evidence/ask-initial-full-matrix.jsonl. The release workflow runs the unchanged complete gate with the additional observed semantic regression after deployment. |

## Primary references

- [Pioneer Sketches, Church History](https://history.churchofjesuschrist.org/exhibit/historic-sites/wyoming/passing-through-the-sweetwater?lang=eng): Independence Rock date and landscape context.
- [Alma 32](https://www.churchofjesuschrist.org/study/scriptures/bofm/alma/32?lang=eng): especially verses 21, 27-36 and 37-43 for the corrected explanation.
- [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap): accurate modification dates and sitemap discovery, with no indexing guarantee.
- [Existing YouTube study referral](https://www.youtube.com/shorts/fPSuW-eML9c) and [existing Instagram referral](https://www.instagram.com/p/Dc2QIMyFefB/): observed in public search results; direct web retrieval was throttled/unavailable, so fresh post-body or engagement claims are not made.

This is the pre-release review checkpoint. Independent approval, exact commit, deployment and final gate results are recorded in Focus Current State after publication. Any external limitation remains explicit rather than being converted into a claim that everything on the internet was checked.

The first PR check exposed a legacy QA assertion requiring eight literal August 30 sitemap dates. That assertion rejected truthful later updates. The correction retains the original minimum release date per core URL, validates date syntax, and allows later substantive updates; the discovery gate separately rejects future dates. No production gate was skipped.
