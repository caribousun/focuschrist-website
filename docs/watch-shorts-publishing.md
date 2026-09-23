# Keep the Watch page's four Shorts current

Wyatt requested the four latest public Shorts from @theRisen636 with a link to the full collection. The website uses a reviewed, date-stamped selection. It does not claim an unattended YouTube sync.

After a new owner-approved Short is actually published on YouTube:

1. Reload the public channel's Shorts tab with **Latest** selected: https://www.youtube.com/@theRisen636/shorts. Confirm the newest four public entries and their order. A Studio draft, processing status or local export does not qualify.
2. Update `docs/watch-shorts.json` with exactly those four IDs, accurate titles, speaker names and native portrait thumbnail URLs observed on YouTube. Update `verified_at`. Keep descriptions short and grounded in the actual message; do not invent quotations or details. Do not change video pixels or overwrite approved local masters.
3. Run `python tools/build_watch_shorts.py`, then `python tools/build_watch_shorts.py --check` and `python tools/watch_shorts_qa.py`. Run the Shorts runtime checks with the existing jsdom dependency. Review the changed visible wording and retain the prior Watch content-audit review when updating its hash.
4. Rebuild the site search index. Inspect all four previews at phone, tablet and desktop sizes; test one-player-at-a-time playback, Close/focus return, direct YouTube links, the full-collection link and failure recovery. A provider-blocked embed must retain a visible preview and direct YouTube alternative; do not certify actual playback from a test stub.
5. Follow the existing reviewed website release process. Verify the public Watch page after deployment, including the actual IDs and thumbnails, and record the public release. Preserve the previous selection in Git history. Do not publish a new Short merely to update the website, and do not create a recurring job without a separate scheduling request.

The existing Church video library, sources, approved hero and artwork are separate from this four-item channel selection and remain protected.
