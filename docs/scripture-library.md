# Verified scripture library

The reader, Ask and Pioneer share a source-checked English library: 1,582 numbered chapters and both unnumbered Official Declarations. Bible wording follows the Church's English King James edition. The Book of Mormon, Doctrine and Covenants and Pearl of Great Price come from the official English scripture pages. Each file retains its official URL and verification date. The source ledger binds the downloaded source HTML, extracted text and verse count to SHA-256 hashes.

The previous builder discovered only literal chapter URLs. Come, Follow Me creates chapter links dynamically, so valid Proverbs and Ecclesiastes links could lack reader data. The complete inventory now defines coverage; tests also expand every actual CFM assignment and require its chapters. No chapter can silently disappear because a source fetch failed. Official Declarations preserve their source paragraphs, headings, introduction and accompanying material without fabricated verse numbers.

## Runtime contract

- Download only the requested chapter. Keep a bounded cache of 32 verified chapters; reject a missing file, source mismatch or hash mismatch and permit retry. The full corpus is not bundled into page JavaScript or downloaded on every visit. This is a site-hosted library, not a promise of offline availability.
- Resolve canonical book, chapter, verse, lists and ranges before displaying scripture. Invalid and ambiguous references fail closed. Single-chapter shorthand is supported; explicit invalid chapter numbers are not reinterpreted as verses. Cross-chapter citations in generated answers must be written as separate complete references.
- AI selects a supported reference with `[[SCRIPTURE:John 3:16]]`; application code supplies its actual words. Existing explicit quotations are checked against the selected source wording, allowing only typographic quote/whitespace normalization and complete-word excerpts. Interpretation and relevance still require the existing source-grounded verifier.
- The Worker checks every final answer at `jsonResponse`, regardless of upstream approval, general/faith classification or reviewed recovery. The browser checks displayed local, reviewed, legacy and remote answers too. An old verification flag is never a substitute for the current library check.
- Scripture labels, source URLs and inline reader links must resolve consistently. Exact complete declaration readings are verified against the entire source text before publication; this preserves historical quotations inside the official document without treating them as AI commentary.
- Exact scripture requests can be answered directly without a research or verifier model call. Missing evidence produces a helpful refusal rather than guessed scripture. Diagnostic responses contain bounded reason codes and catalog versions, not a new log of personal questions.
- Keep the source reader, Close, retry, keyboard behavior, focus return, approved heroes and existing presentation intact.

## Build and release

Run `python tools/build_scripture_reader_data.py` to resume/build missing chapters. `--refresh` deliberately rechecks upstream content. Run `python tools/build_scripture_catalog.py` after a verified build. Never hand-edit scripture wording to satisfy an assertion. A source update must pass source extraction, full inventory/hash validation and release review.

Required gates: complete library/catalog check; `tools/scripture_library_qa.js`; real DOM display/reader checks in `tools/scripture_display_runtime_qa.js`; existing reader, CFM, Ask/Pioneer, source and full-site checks; independent review; actual phone/desktop journeys. Negative tests include invented chapters/verses, wrong quotation and attribution, short/multiline quotes, incorrect source labels, edition mismatch, approval bypass, malformed tokens, time/reference collisions, source outages and retry.

Publish Pages before activating the new Worker. The Worker workflow waits until the public catalog hash matches the committed catalog. Preserve the previous deployment if that prerequisite fails. After both deploy, repeat the reported CFM path, direct Ask/Pioneer lookup and live AI verification. Do not describe deterministic citation checks as a guarantee that AI interpretations are infallible.
