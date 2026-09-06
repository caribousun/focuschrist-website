# Pioneer timeline answer repair

The owner rejected the repeated short summary and required substantive answers that survive collapse and reopening across all29 controls. PR164 fixed one destructive redraw but did not solve misleading initial presentation or evidence mismatches. Its successful structural checks did not establish end-to-end answer acceptance.

The follow-on replaces duplicated summary answers with explicit pending, verified-complete, and recoverable-error states. Reopening preserves the response and pending request. Explicit Retry handles failure. Verified answers include official source links. Ordinary card descriptions remain visible. Existing local biography and free-form Ask behavior remain separate.

## Reviewed source routes

`groq-proxy/src/pioneer-topic-sources.js` maps every visible data-topic ID to an exact official source and neutral subject. The server ignores client-provided factual assertions for fixed cards. It does not accept a source URL from the client. Narrow exact URLs cover Church Headquarters for Temple Square, the relevant historical articles, manual chapters25/26/28, an Ensign rescue account for Martin's Cove, and two official Newsroom pages for Echo Canyon and Pioneer Day. An independent source review verified all routes against actual article text. The existing verification, source-copying, response-depth, provider and time budgets remain intact.

Pioneer-specific evidence retains complete relevant paragraphs within the existing4200-character budget. Focal landmark/company phrases keep relevant paragraphs from being crowded out by generic migration language; question-specific caches preserve distinct topics sharing a manual chapter.

Two official Newsroom bodies were lost by the previous hidden-element expression: a void input with type=hidden was treated as a paired container and consumed the remaining HTML. Excluding HTML void tags from paired-container matching restores body text while retaining hidden-container and prompt-injection filtering.

## Source discrepancy

The official chapter26 body incorrectly calls Chimney Rock a landmark in Wyoming, while its caption correctly locates it in western Nebraska. For these fixed Pioneer routes, omit that exact conflicting paragraph whole, retain the correct caption and other context, and test both cold and warm extraction. Do not silently rewrite a quoted source. The Sweetwater query does not add a Devil's Gate claim unsupported by its selected chapter.

## Acceptance requirements

Required checks include all29 topic IDs and exact source routing; unknown IDs and other-page isolation; loading, completed answer, pending collapse/reopen, hidden completion, failure and explicit retry; source links; and retaining the existing biography/safety contracts. The deployment workflow additionally tests every fixed topic against production. Fallbacks, unverified answers, wrong sources and responses below the substantive minimum fail that gate. Record the final production results and any remaining limitation in the Focus brains before claiming completion. The requested gold timeline redesign follows functional acceptance.

## Live content correction

PR165 restored substantive answers and exact reopen retention in production, but reading the actual handcart answer exposed an unsupported causal link: it attributed a late1856 departure to a separate1855 travel-route policy. Restrict focal-source packs to the named-topic paragraphs and immediate context, remove the generic Liverpool anchor, and keep the same rule in cold and warm extraction. An unbounded nationwide death-toll comparison in chapter28 is omitted as a whole paragraph rather than treated as independently established fact. Pioneer-specific writing instructions apply to initial and repair prompts and prohibit inferred causation, present-day claims, invented sensory detail and repeated context-summary padding. A successful verification receipt alone does not establish factual accuracy.

The final review also found a returned answer mixing the earlier 1846 Pueblo/Mississippi narrative into the 1847 Chimney Rock entry. Fixed landmark retrieval now selects only the visible Journey of the Pioneer Company section of chapter 26, ending before Establishing a Settlement in the Valley. Section selection runs after hidden-content removal, retains the source wording, and fails closed if those headings disappear. Regression coverage excludes the earlier company and ensures hidden section headings cannot introduce evidence. Gold frames, date badges, visible expand indicators, and coordinated answer panels now apply to all 29 timeline controls.

Final production follow-up (.57): chapter 26 landmark packs retain direct place paragraphs and the explicit 1847 route overview, rather than adjacent recollections that a writer could wrongly connect to the landmark. The broader AI gate exposed intermittent ordered-fragment overlap on Relief Society and Hyrum follow-ups. Initial and existing single-repair instructions now explicitly require an independently structured explanation. Overlap thresholds, deadlines, provider-call bounds, and fail-closed behavior remain unchanged; a failed fragmented-overlap repair is regression-tested to stop after two calls.
