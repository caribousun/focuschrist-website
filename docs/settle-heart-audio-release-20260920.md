# Andersen recording and study integration

Wyatt supplied the September 15, 2026 MP3 and requested a transcript and stronger use of Elder Andersen's words throughout the existing study.

The study now contains eight attributed excerpts, a native player using BYU's original audio, timestamp links that seek within that player, and a closed transcript disclosure with sixty readable paragraphs and a downloadable text version. The practical invitations follow his two stated invitations. Companion scripture accounts remain clearly distinguished from stories used in the address.

The source recording runs 25:36.192. Local faster-whisper small.en and base.en passes were compared in full, with targeted repeat recognition and proper-name/scripture reconciliation. The record is an unofficial transcription, not a claim of human listening or BYU editorial approval. Wording near 15:56 and 22:24 remains bracketed. Those passages are not used as featured quotations. The supplied source hash and eight excerpt locations are recorded in `settle-heart-transcript-review.json`.

The initial connected Fal upload was rejected because its account balance was exhausted. No upload or paid transcription job was accepted; existing local transcription tools completed the work.

Independent content/code review approved after correcting a materially wrong machine transcription ('cannot authenticate' to 'can authenticate'), replacing quotation footer elements that inherited page-footer styling, and combining paragraphs split mid-sentence. A regression test guards against the negation error and verifies deferred metadata, latest-selection wins, enhanced/cloned links, focus, seek and playback-error fallback.

Rendered checks at 320, 390, 700 and 1366px showed no horizontal overflow in the expanded transcript or excerpts; the source action row retained 28px above and below. Original audio playback reached readyState 4, duration 1536.192; real keyboard and pointer controls sought to 646, 1030 and 514 seconds. Transcript open/close and return paths passed. Hero and all fifteen original pictures remain unchanged.

The original 88-command local run had two failures: new scripture wording needed an inline link and the content-audit ledger required semantic review. Both were corrected and targeted reruns passed. Search, media voice, layout, protected artwork and the added recording runtime checks passed. Hosted checks and public-byte verification are separate release gates.
