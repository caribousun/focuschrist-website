# Exact Adams delivery successor

This explicitly named delivery layer registers **three exact files**:
`timeline.html`, `art-gallery.json` and `site-search-index.json`. It replaces
an uncommitted index-only proposal; no adopted family is silently expanded.
The existing Emma helper, manifest, pins and earlier historical expectations
remain unchanged.

This V2 proposal supersedes only the unmerged V1 data binding; original V1
source/test results remain historical, not V2 test results. Actual V8 source
is draft `1a13c567ba39d1e11632c046c75c5084be98bc50`. CI run **40482829846**
generated the two indices at merge `f9d139b0cf140e784aab1bcc15f9f1859df3b8ae`,
tree `cea2db2b95e2de51549a796d9c4756c60a76d582`. Fresh Git commit metadata
confirms parents `b4e023cfbe5e98b1191571f8ed3ca97c5a9f0c8b` and that draft;
the diagnostic's blank shallow-checkout parent line is not used as proof.
Artifact12723790962 ZIP768541 bytes/SHA256
`0d0c4009f61a3e7819bb8618b005672234fff93743feabaa71c665e89b152525`.
Normal generator checks against the eventual composed checkout remain required.

| File | Predecessor UTF-8 bytes / SHA256 | Actual delivery UTF-8 bytes / SHA256 |
| --- | --- | --- |
| Landing | 7610 / `dc00d3d589a6e50c7359c98f8228d2491926b8a5a9ed764628b0ac9c31264e8f` | 8051 / `fa3b12da544899f8935874508b9abe64b84b6fd2af1e5bfec8a368ce6a638578` |
| Gallery | 997024 / `87d40761a71174a62c1686af62967f9904d1fee762333859f91bea11e0754a96` | 997064 / `21e3ca0c843117371bae82010c3faea37ea9e4394df44975019220a7f4c8cea3` |
| Search | 3381272 / `eb85bd29a11eee569749064667a00c5640687c08ea6d7ff413ca7a606d8831a0` | 3382864 / `edbd12a7385703fa632e69af0366ce3fb7e61a23dce7a73680b225a6c3a83f76` |

## Exact change

The landing adds the reviewed Adams introduction sentence, navigation link
and explanatory paragraph; everything else is byte-preserved. Both index
`pages` arrays add only `/timelines/adams-1881-chart.html`. Gallery's 1064
artwork records, order and statistics remain unchanged. Search adds one
viewer record and changes only the `text` field of `/timeline.html` and
`/timeline.html#choose-timeline` to include the new landing text. All other
records/fields and old relative order remain unchanged. Source/semantic
acceptance is separate from mechanical byte reconstruction.

The manifest contains three landing spans, one gallery span and three
search spans. Each transform requires the exact filename and complete
current/predecessor hash, exact slice bytes, typed bounds, byte sizes and
final hash. Unknown, extra or changed bytes are not normalized. The current
gate requires **all three actual current files** and all round trips.

## Historical checks remain historical

The delivery inverse composes outermost in motion and the direct search
path. The two manual motion page comparisons independently remove this
exact layer before their unchanged historical chain; their old expected
hashes and actual-current call to the full inverse remain unchanged.

Emma's own helper and manifest are byte-identical. Before its historical
check/tests, `predecessor_view` requires all three actual Adams files to pass
their own complete hashes and round trips. It reconstructs only the two
exact Emma index predecessors into a temporary three-file view, alongside
the unchanged Emma manifest. The real checkout remains read only. This
view verifies the historical layer, **not equality of current files to old
Emma pins**. The old direct Emma check intentionally rejects raw Adams
indices; a test asserts that distinction. Mixed pairs or changed current
landing/index bytes fail before any historical view is entered.

Run the Adams delivery tests, preserved Emma tests and Adams delivery check,
then all existing hosted QA and generator checks. The new tests cover all
three current files, exact inverse/forward reconstruction, wrong paths,
extra/inside/outside bytes, missing/corrupt mappings, invalid spans, mixed
current/predecessor files and temporary-view isolation. No fixture pass
certifies source import, rights, pixels, layout, interactions or release.
Future combinations need their own separately reviewed exact registration.

## V2 actual-output delta

Versus prior V1, gallery and landing bytes are unchanged. Actual V8 search differs only in records[1351].text: the visible `FocusChrist Home` label is inserted after `Back to timelines`. All other JSON values are equal. The final existing search span grows17bytes; earlier spans and every immutable Emma predecessor pin remain unchanged. No H1 extraction change is inferred: the actual output comparison establishes only this field delta. The validator algorithm and all twelve test methods are unchanged; only exact current-search/manifest pins and producer description change. Source proposal is NOT RUN and not publication approval.
