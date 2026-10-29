# Timeline current review and index bindings — pending evidence

This is an engineering inventory, not a review, approval, or release decision. The source subject is the local successor to draft PR 542 head `e3f100547a4a965fde30695cd90e77626f7f9c29`; the corrected Nazareth bytes are not yet at that head.

## Source subjects

| Path | SHA-256 | Current visible-text SHA-256 |
| --- | --- | --- |
| `answers/jesus-christ-latter-day-saint-beliefs.html` | `dd071c356cb85d33bea1b717447446a2ab9f7f49d2fcb8e4eb4e458b3a7d6078` | `5b761139d1cf850555f1551a9c22ab16e4f4ad14fefed10108accbf20f99cd4c` |
| `timelines/world-and-scripture-timeline.html` | `016e9896db70ff0a8a142503f289f2e0cbd2f4d96b73d667247dbb2a2370ceef` | `b44f8e133122d76e96e87b364eb0a3465011bd04ad55f403341a0b3bcc359b2d` |
| `timelines/adams-1881-chart.html` | `43f19fc23f4fd17e1c9fdb54003feab2885565c97b1a98abc6aefb092ec06944` | `9fcedb2e27757c2ad697917e1d99ce7bf08add95607b0a44b6ae46c972e7acf7` |
| `timeline-images.js` | `0896201a1fdc35eab8333873ce9f3cd18b44fd948e9a04f2f93aa5d403618c18` | Not applicable |

Visible-text hashes above use `sha256(static_content_audit.published_text(path).encode('utf-8'))` on actual bytes. The historical projected hashes returned by `content_hash` for World and the Jesus page are deliberately different; they are not a current text review.

`content-audit.json` has one document object per path. The current draft's `tools/static_content_audit.py` requires an exact `reviewed_current_timeline_sha256` string for the World and Nazareth source objects. Adams requires the current `reviewed_source_sha256` and `published_text_sha256` strings. Any update must be backed by genuinely authored independent current review evidence with actual author, date, exact scope and source hash, while preserving existing review history. These fields are structural bindings; a matching string alone cannot establish human or agent review. Current rendered desktop/phone review is separate.

## Generated indices

Actual producer outputs at the source head:

| File | SHA-256 |
| --- | --- |
| `docs/section-panel-inventory.json` | `aaa49fb307fa5e3251e7ed054d2443f637db94a0361a4ba3621d267ed1ab5532` |
| `art-gallery.json` | `df6a8c33fc3bd70dbf38675fdb21b984914e5598a42f70025e67de5ddfceb4f8` |
| `site-search-index.json` | `abcd13069b734ca5f25ecc003abef56717093b73c31e336ae84bd3d647ffabf1` |

The previous exact search hash is `ba1ea0787568ce5dc6f51b7661a31ead0088c7e39f2d988286fd98697398ac67`. Comparing all records by URL shows exactly three differences: the parent Jesus page's `text`, the added `#nazareth-childhood` record, and the Adams chart page's `text`. No other search records differ. `build_site_search.py --check` and `site_search_qa.py` passed on the full current checkout; panel and gallery producers also passed, with unchanged output hashes.

The existing exact historical closure and template are `docs/emma-journey-owner-closure/current-review.json` and `docs/emma-journey-public/index-review-commitments.json`; their schema and checks are in `tools/emma_journey_closure_successor.py`, especially `check_review` and `check_public_reviews`. They bind the old search hash and actual previous reviewers, so they must remain historical evidence. `tools/emma_journey_indices_contract.py` additionally enforces no unrelated search-record drift, and `tools/emma_public_commitments.py` binds the previous pre-release report and reviewed tool tree. A new narrowly scoped, independently authored current-index assessment must identify both exact search hashes, all three changed URLs/fields, current panel/gallery hashes, actual reviewer and time, and verify the real current outputs and unchanged Emma index data. It must not imply a fresh whole-site review or renewed owner acceptance. A reviewed successor implementation is needed to check this authorized unrelated delta while retaining the old Emma closure and all source/review/owner requirements; no existing receipt can simply be relabeled or repinned.

The present actual closure check fails `stale review binding search`; an earlier full artwork check also detects `unrelated search record drift`. These are outstanding checks, not passes.

## Rendering

`tools/timeline_requested_browser_qa.js` and the small local edits to `tools/timeline_runtime_qa.js` and `tools/adams_chart_browser_qa.js` are prepared but not yet committed or run on hosted Chromium. They exercise desktop/phone controls and capture screenshots using the existing Timeline hosted runner, including a simulated rejected fullscreen request to check genuine error feedback while normal diagnostics are hidden. The existing runner intentionally blocks external map providers; physical-device/live provider testing remains separate. The Adams suite's old-only source hash and its old requirement that routine progress text be visible need the exact diagnostic-successor branch prepared locally; its chart asset, geometry and navigation assertions remain. All of these changes need independent code review and an actual hosted run before any rendered pass is claimed.
