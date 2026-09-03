# Ask Background Operations

The live Ask path stays deliberately small: reviewed local answer, bounded official Church retrieval, one verifier, and Groq research only for an index miss or an external general question. Crew-style multi-agent work belongs outside a visitor request.

## Nightly regression

`.github/workflows/nightly-ai-regression.yml` runs the five-class baseline once per night so recurring assurance does not consume the full free AI allocation. A failure remains visible in GitHub Actions and blocks any claim that Ask is verified. The deployment gate and manual release audit run the full semantic matrix with three time-separated rounds, unique paraphrases, safety and near-neighbor controls, follow-up and reset checks, cold and warm cache checks, and a three-request burst. Capacity calculations subtract the measured nightly baseline before estimating visitor capacity.

## Church-source index

`tools/build_church_source_index.py` refreshes the deterministic discovery-only index from the official English sitemap. It stores URLs and ranking metadata, not article bodies, and reserves representation across Gospel Topics, scripture guides, Saints, women’s history, manuals, official explainers, and Church-history collections. `tools/audit_church_source_freshness.py` compares the current robots hash, sitemap revision, and combined sitemap hash with the approved artifact. `church-source-index-review.json` expires after eight days so an unchanged but unreviewed index cannot be promoted indefinitely. The weekly workflow rebuilds the full artifact and fails if review is required.

The live Worker keeps a one-hour edge cache of a bounded, sanitized official-page excerpt pack keyed only by canonical Church URL. It never caches a visitor question, conversation, or generated answer. Public receipts distinguish cache hits, cache misses, and actual network attempts so cold and warm behavior can be measured.

## Capacity, abuse, and provider data

- The Cloudflare rate-limit binding permits at most 20 AI-path requests per client address per minute at each Cloudflare location. Safety-blocked input is rejected before the limiter and before any source or model call. The address is used only as the ephemeral limiter key and is not logged or sent to an AI provider.
- The release matrix uses Cloudflare’s published model-token neuron conversion and reserves 20 percent of the 10,000-neuron daily free allocation. The reported visitor capacity also subtracts the measured five-class nightly baseline. This is a bounded free-envelope estimate, not an unlimited traffic claim.
- Cloudflare states that Workers AI customer content is not used to train models or improve Cloudflare or third-party services without explicit consent: https://developers.cloudflare.com/workers-ai/platform/data-usage/
- Groq states that ordinary inference is not retained by default, but inputs and outputs may be retained for up to 30 days for reliability or abuse review unless Zero Data Retention is enabled: https://console.groq.com/docs/your-data
- The repository cannot prove the private Groq console’s Zero Data Retention toggle. An account administrator should verify that setting before representing ZDR as enabled. The public disclosure therefore accurately says limited recent context may be sent to external AI providers and does not promise zero retention.

## Candidate-answer review

1. Use recurring unanswered or weakly answered questions from regression evidence to draft a candidate.
2. Pin every doctrinal or historical claim to an approved official Church URL and verify the exact relevant passage.
3. Run source-integrity, safety, follow-up, subject-switching, and rendered-page tests.
4. Require human or explicitly authorized source review.
5. Promote only the reviewed entry to `reviewed-ask-knowledge.js`.

AI output never promotes itself into reviewed doctrine or history.

## Planning lanes

- Content planning may group recurring respectful questions and identify missing official-source coverage.
- Artwork planning remains separate from Ask reliability and follows the approved realistic mission-page visual language.
- Shorts production may use reviewed source-grounded content, but it cannot become an authority source for Ask.
- Background agents may critique candidates, regression failures, artwork prompts, and Shorts scripts. They never receive live visitor conversations and never sit in the visitor response path.
