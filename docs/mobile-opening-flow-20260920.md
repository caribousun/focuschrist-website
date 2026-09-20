# Mobile opening flow and Answers card completion

Owner scope: preserve the approved mobile hero work; make pills and Continue/down arrow flow well within the first opening section. Complete the empty card position shown in the Answers screenshot and inspect analogous rows.

Baseline: 6e93cc5443619de307d0c428ce7c5a270738573e (PR341). This is the rollback baseline. On a short phone, the full hero plus introduction pushes controls below the initial viewport; the sampled controls were not internally clipped. The opening is allowed to grow, while all controls remain inside it. One opening section is not a guarantee that every element fits on one screen.

Changes: mobile Continue follows the introduction in normal flow with a centered gold-outline touch target, 24px separation, and bottom safe-area padding. Topic-page cues live inside the introduction rather than forming a third hero-grid row. Desktop presentation and hero sizes/artwork are preserved. Answers adds Atonement and Look Unto Me destination cards to complete its three- and seven-card groups. No new artwork or doctrinal teaching is introduced.

Audit: sitemap-driven review covered 41 canonical routes. Other odd shared study grids already span their final item or use deliberate three-column/flexible layouts; the Look Unto Me final Act card is already full width. No blanket grid override was added. Earlier geometry/overflow checks did not catch incomplete directory rows; the new structural gate checks all Answers two-column rows and all 40 canonical opening cue destinations (Search has no opening).

Rendered local checks: all 41 routes at 320x568, 390x664 and 430x932, no horizontal overflow or cue containment failure. Narrow-phone opening buttons retain at least 44px touch height. Seven distinct templates with text doubled passed cue/control containment and label-overflow checks. Continue keyboard activation reached the topic main-content anchor; after smooth scrolling settled, its top was 80px below the viewport top. Desktop Answers has complete 4/4/8/2/2 card groups and hides the mobile cue. Screenshots inspected the mobile controls and both completed Answers rows.

Independent review approved the mobile approach and destination relevance, with a correction from praying to sharing what you learn to match the Look/Remember/Talk/Rejoice/Act sequence. Cache references refreshed on every consumer. Semantic and stylesheet preservation ledgers updated only for reviewed changes. The optional reflection remains conditional on available space; its appearance is not guaranteed.

Validation: 88 extracted local workflow commands run. The two initial failures correctly identified changed reviewed stylesheet bytes and Answers wording; their scoped review records were reconciled and both checks passed on rerun. Hosted full CI, deployment and public verification remain separate release gates.

Control applicability: shared regression gate, stylesheet/content review records and project continuity apply. Master already contains the mobile hero and pill containment directive, so no duplicate governance or foundation change is needed. Brain Map routing remains valid. Schedules, providers and commercial controls are not affected.
