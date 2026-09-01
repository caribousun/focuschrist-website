# FocusChrist Website Production Checklist

Use this checklist for every repository change that can affect `https://focuschrist.com`.

## Before changing production
1. Re-read the current Focus project memory and verify the owner-authorized scope.
2. Re-fetch the current `main` branch; do not work from a stale copy.
3. Create an isolated change branch for material edits.
4. Preserve existing functionality and content unless the owner explicitly authorized changing it.
5. Never expose Cloudflare/Groq secrets or other credentials in repository files, commits, logs, or documentation.

## Protected production controls
Do not remove or weaken these without a verified replacement and explicit reason:
- `google3fa84a4b37862f36.html` — Google Search Console ownership verification.
- `robots.txt` and `sitemap.xml` — search discovery controls.
- `Jesus.png` — site-wide banner/social image.
- independence disclosures on all five core pages and the fuller About disclosure.
- `openai/gpt-oss-20b` direct model request in Ask/Pioneers plus the Cloudflare compatibility fallback.
- `tools/site_qa.py`, `.github/workflows/site-qa.yml`, and the QA step in `deploy-pages.yml`.
- `reviewed-ask-knowledge.js` and its SHA-256 records in `answer-audit.json` — the shared local-first answer contract.
- `tools/reviewed_ask_knowledge_qa.js`, `tools/pioneer_ask_runtime_qa.js`, `tools/church_history_ask_runtime_qa.js`, and `tools/study_intelligence_v3_runtime_qa.js` — final-owner and intent-boundary gates.

## Required verification
Run:
```bash
python tools/site_qa.py
node tools/reviewed_ask_knowledge_qa.js
node tools/pioneer_ask_runtime_qa.js
node tools/church_history_ask_runtime_qa.js
node tools/study_intelligence_v3_runtime_qa.js
```

For Art additions, also follow `IMAGE-UPLOAD-GUIDE.md` and build thumbnails before QA.

The site QA must pass before merge. A pull request to `main` runs the same QA automatically. Production deployment also runs QA before GitHub Pages is published.

## Review the actual diff
Confirm that:
- only intended files changed;
- no existing artwork/content was unintentionally removed;
- no retired Groq model was reintroduced;
- no local asset reference is broken or zero bytes;
- Search Console verification and sitemap controls remain present;
- external `target="_blank"` links retain `rel="noopener noreferrer"`;
- AI/source transparency and independent-site disclosures remain intact.

## After merge
1. Confirm the **Deploy GitHub Pages** workflow completes successfully.
2. Verify the affected production page/function directly.
3. For Ask/Pioneers/Church History changes, test the actual live composer after every script is loaded. At minimum verify the sky, Joseph Smith death, handcart start-year, Pioneer Exodus, First Vision, Church organization, and negative-control families recorded in `docs/all-page-ai-ask-executive-prompt.md`.
4. Confirm reviewed-local answers make zero Worker requests and still answer when the Worker is unavailable.
5. For Art changes, test preview + full-resolution modal + keyboard controls.
6. Record material production changes and verification evidence in Focus Current State and Decision & Change Log.

## Recovery
Git history is the primary restore mechanism. If a production defect is found:
1. identify the last verified-good commit;
2. revert only the defective change when possible;
3. run `python tools/site_qa.py`;
4. deploy through the normal QA-gated Pages workflow;
5. verify production again.

Do not bypass QA merely to make a deployment faster.


## Hardened presentation gates
Before merging a presentation/release pass, also verify:
- every core hero resolves to a repository-local approved production asset and meets the recorded resolution floor;
- no runtime HTML/CSS/JS depends on editable `lh3.googleusercontent.com/d/...` project assets;
- Watch concrete video cards have corresponding thumbnails and verified destinations;
- Pioneer Journey, Trail, handcart, and journal items are chronological within their sections;
- Art “Study this artwork” offers official Church topic study/search and contextual Ask, not a generic YouTube/channel substitute;
- contextual Art -> Ask -> Art navigation returns to and reopens the exact artwork;
- core page Open Graph/Twitter images use the matching local high-resolution hero;
- `python tools/production_hardening_qa.py` passes in addition to all existing QA.

Any newly discovered presentation defect should be converted into a regression check when practical.
