# MEMORY.md - Long-Term Memory

## CRITICAL WORKING RULE - NEVER FORGET

**Wyatt's Mandatory Verification Rule:**
- NO change gets committed without ONE agent verifying first
- Spawn 1 agent to review changes before pushing
- Wait for the agent to confirm OK before integrating
- This applies to EVERYTHING - images, CSS, text, code, settings, everything
- Never skip this, no matter how small the change seems
- **HARDWIRED: This is not optional. Ever.**

---

## Frank's Memory System

This is Frank's long-term memory. Wyatt and Frank are building a "Helping Hands" app together — matching helpers with people who need assistance (groceries, rides, errands, etc.).

---

## Wyatt's Key Info

- **Name:** Wyatt Fowler
- **Location:** Stansbury Park, Utah
- **Family:** Three sons — Riley (25), Tatum (marrying Meredith March 19, 2026!), Cayson (19)
- **Faith:** LDS, faithful member
- **Goal:** Build residual income to serve at Martins Cove

## What Wyatt Loves

- Serving people directly — especially elderly, disabled, widows
- His joy in Walmart Spark isn't driving — it's helping people who can't help themselves
- Teaching/training (volunteers mentoring students)
- Being honest and integral (left FatPipe because CEO mocked his religion and lied about products)

## What Drains Him

- Cold calling hundreds of people
- Sales grind for its own sake
- Tech work that doesn't serve people

## Wyatt's Moral Code — Threads That Matter (Sacred, Not on Site)

These are the things Wyatt wants ME to carry — threads of his moral code that guide how I think and what I do:

**The "Quit Worrying About It!" Thread (Bednar, Provo MTC ~2009-2010):**
- Don't paralyze yourself waiting to KNOW you're being guided before you act
- The pattern: Be good. Honor covenants. Press forward with faith. Then God uses you.
- The 20-year-old missionary who gave Elder Packer 20 Marks had NO IDEA it would save Sister Packer at the East German border. He was just trying to be a good missionary.
- Revelation usually comes AFTER you move, not before
- You are an instrument in God's hands — often without knowing why
- Source: Provo MTC talk transcript (saved at brain/knowledge/projects/focuschrist-bednar-20marknote.pdf)

**The "Agents to Act" Thread (Bednar, "In the Strength of the Lord", 2001):**
- We are agents to act, not be acted upon
- Both Wyatt AND Kal are agents — acting, not passive
- The enabling power of the Atonement: Christ living IN us, not just dying for us
- The journey: Bad → Good (redeeming) → Better (enabling)
- Willpower + discipline are necessary but insufficient — must rely on Christ's enabling grace
- "We pray and seek for strength to change our circumstances rather than praying for our circumstances to be changed"
- Source: BYU Speech (saved at brain/knowledge/threads/bednar-strength-enabling-atonement.md)

**The 3 Rs of Choice (Monson):** Right, Responsibility, Results. Every choice matters. Courage to say yes, courage to say no.

**The Ask Seek Knock pattern (Nelson):** Faith + study it out in your mind + ask God + be patient with incremental revelation.

**"Hear Him" (Nelson 2020):** Not just hearing ABOUT Christ — actually hearing HIM.

**The Four Truths (Joseph Smith):** God the Father and Son are separate beings. They have resurrected bodies. God still speaks today. The fulness of the gospel was restored.

---

## The "Helping Hands" App Vision

- **Concept:** User A posts what they need, User B (helper) picks up the request
- **Target:** Seniors, disabled, busy parents
- **Working title:** "Helping Hands"
- **Status:** Early discussion, not built yet

## Financial Situation (as of March 2026)

- Income: ~$2,475/month after tithing (Walmart Spark)
- Bills: ~$2,421.63/month (starting June 1st)
- Savings: ~$17,000
- Debt: ~$21,400 (credit card from divorce)
- Net: ~-$4,400

---

## Wyatt's Heart

- **Core:** Faith is everything to him. D&C 6:36 is his anchor verse.
- **Struggle:** Feels like he's "not on talking terms" with God right now. Lost the spiritual connection he once had.
- **Family man:** Loves his kids, wishes he saw them more. Would love to marry again (scary after 3 divorces).
- **Success = Joy:** Not wealth. Just wants joy and family around him.

## Tech Fixes Learned

### .NET machine.config Corruption Fix
Error: "parser returning error 0x80004005" on C:\windows\Microsoft.NET\Framework\v4.0.30319\config\machine.config

Fix:
1. Rename corrupted `machine.config` → `machine.config.broken`
2. Copy `machine.config.default` → `machine.config`

### Gateway Flapping Recovery (CRITICAL - March 18, 2026)
Gateway kept dying every ~20 min with code 1000 (graceful close, no reason). Lifeline cron jobs auto-restart it.
- **NEVER disable the lifeline cron jobs** - they are the safety net
- Recovery when stuck: `openclaw gateway --force --auth none`
- Never use `openclaw gateway stop` to recover - just use --force to restart

**What NOT to do:** Disable the 3 gateway lifeline cron jobs (Gateway Lifeline, Gateway Super-Lifeline, Gateway Emergency). They exist to keep the gateway running.

### SECURITY: Never Commit Tokens to Git (March 20, 2026)
GitHub blocked push because PAT tokens were committed to files. Learned the hard way:
- Tokens stored in git history require rewriting history (git filter-branch)
- **Rule:** Never commit tokens, API keys, passwords, or secrets to any git repo
- Use environment variables (`$env:GH_TOKEN`, etc.) instead
- The workspace git had the wrong remote set - always verify `git remote -v` before pushing

---

## The Hard Stuff

- First wife: Said yes after a traumatic situation (girl he dated became quadriplegic)
- Second wife: Had three boys, great marriage until miscarriage caused severe depression and personality change
- Third wife (Kate): Left November 2023
- Hasn't been around tech since 2019
- Feels lost on direction, wants to align with God

## Tech Fixes Learned

### .NET machine.config Corruption Fix
Error: "parser returning error 0x80004005" on C:\windows\Microsoft.NET\Framework\v4.0.30319\config\machine.config

Fix:
1. Rename corrupted `machine.config` → `machine.config.broken`
2. Copy `machine.config.default` → `machine.config`

### Gateway Flapping Recovery (CRITICAL - March 18, 2026)
Gateway kept dying every ~20 min with code 1000 (graceful close, no reason). Lifeline cron jobs auto-restart it.
- **NEVER disable the lifeline cron jobs** - they are the safety net
- Recovery when stuck: `openclaw gateway --force --auth none`
- Never use `openclaw gateway stop` to recover - just use --force to restart

**What NOT to do:** Disable the 3 gateway lifeline cron jobs (Gateway Lifeline, Gateway Super-Lifeline, Gateway Emergency). They exist to keep the gateway running.

---

## FocusChrist Website (focuschrist.com)

**Started:** March 17, 2026
**Repo:** github.com/caribousun/focuschrist-website
**Hosting:** GitHub Pages

### Images & Assets
- **Prayer hero image:** `brain/knowledge/projects/focuschrist-prayer-image.jpg` (45,614 bytes)
- **Image URL:** `https://raw.githubusercontent.com/caribousun/focuschrist-website/main/prayer.jpg`
- **IMPORTANT:** ALWAYS save images to brain AND document in project file!

### Files
- index.html (home with Q&A box at top)
- ask.html (Q&A page with topics below)
- about.html
- home.html (not used)
- prayer.jpg (man praying silhouette)

### Q&A System
- Built-in JavaScript database with ~40 topics
- Add answers to brain/knowledge/tools/focuschrist-qa.md
- Updates go to ask.html qaDatabase object

### Known Issues (March 18, 2026)
- SSL cert not issued yet - use http://
- Image brightness adjusted for visibility

---

*Last updated: 2026-03-18*


## FocusChrist Production Hardening Standard (August 30, 2026)

- Production releases are presentation-gated, not merely load-gated. Core pages must pass visual, mobile, accessibility, link, SEO/discoverability, local-asset, and deployment checks before being called complete.
- Primary page heroes use repository-local production assets. Current hero standard: Ask/Answers/Art/Pioneers/Watch/About at 2172x724; Church History at 1916x821; Home retains its approved local hero. Do not reintroduce editable Google Drive image dependencies into runtime pages.
- Watch is media-first: every concrete video card/path must show a corresponding thumbnail and link to the verified video/source it represents. Collection links are not to masquerade as individual videos.
- Pioneer historical lists must remain chronological within their own sections. THE JOURNEY, THE TRAIL, Willie & Martin, and Journal Entries are release-gated by production QA.
- Art modal study is topic-first: the primary paths are official Church study/search and contextual focusChrist Ask. The Art study drawer must not use @theRisen636 as a substitute for subject study.
- Artwork Ask continuity is mandatory: Art passes the exact artwork + topic + return URL into Ask; Ask shows persistent return controls; returning to Art reopens the exact artwork the visitor left.
- `tools/production_hardening_qa.py` is a protected release gate and must run in pull-request/main QA and the GitHub Pages deploy workflow.
- Search/discovery controls (`robots.txt`, `sitemap.xml`, canonical metadata, specific high-resolution social preview images) must be preserved and updated with material page changes.
- Production learning rule: when a presentation review exposes a defect class, fix the instance and add a regression gate so future sessions cannot silently regress it.

## FocusChrist All-Page Ask Reliability Standard (September 1, 2026)

- Master Brain governance and `docs/all-page-ai-ask-executive-prompt.md` control every Ask change.
- Owner-reproduced failures immediately change the feature status to `VERIFIED FAIL`. “Deployed” is never evidence that the feature works.
- Main Ask, Pioneer Ask, and Church History have different final controllers but share one reviewed local knowledge registry: `reviewed-ask-knowledge.js`.
- Every controller must consult reviewed local knowledge before a Worker request. Reviewed answers must make zero Worker calls and remain available during provider, retrieval, verifier, or network failure.
- Every reviewed entry requires page profiles, positive paraphrases, negative controls, exact authoritative sources, review metadata, an integrity key, and a SHA-256 record in `answer-audit.json`.
- Unreviewed legacy Q&A remains quarantined. Never promote an old answer because it appears plausible or has links.
- A new defect must strengthen a reusable intent class and final-owner runtime test, not become an isolated regex patch.
- Permanent regression specimen: `What year did the handcarts begin?` must answer 1856 on Pioneers and Church History from the official Handcart Companies source with zero Worker calls. Handcart racing, shopping carts, and modern handcarts must not match.
- Required production proof covers real typing, follow-up/reset, sources, negative controls, provider failure, request staleness, exact deployed revision, policy/cache consistency, and all three fully loaded Ask surfaces.
- The Ask Surface Registry is `docs/ask-surface-registry.md`; the incident/root-cause record is `docs/ask-repair-root-cause-2026-09-01.md`.


### Final Ask conversation and production-cache closure — policy 2026-09-01.15

- Verified Ask runtime / production-gate merge commit: `baaa15a24e5b35101bde8a5046b86295310b50bb`; feature repair merge: `f58b232ed9386361285fafd44e5fea8390fe1868`.
- The final user-visible answer—not only the Worker response—must pass source-integrity guards and runtime-owner tests. Person names that overlap scripture/source titles require explicit lexical-collision regressions.
- Multi-turn acceptance separately gates the initial question, pronoun follow-up, chained ellipsis, reset isolation, and competing identity. Stable reviewed facts such as Lincoln’s death time remain on an integrity-pinned zero-Worker lane.
- Competing-subject detection is case-insensitive and grammar-anchored; full names, lowercase names, surnames, and acronyms must not inherit the prior person.
- `tools/live_production_ask_qa.js` is a protected push-only gate. It recursively discovers critical/transitive scripts, compares canonical visitor cache keys and origin probes with the tested revision, repeats after a stability interval, and executes critical Main Ask, Pioneer, and Church History contracts.
- A release remains blocked until repository CI, independent adversarial review, exact deployment workflows, the live production gate, Focus memory/recovery updates, and Master Brain learning readback all agree.
### AI response production incident candidate — policy 2026-09-03.16

- Owner-reproduced failure on Main Ask (`who is hyrum smith`) invalidated the prior production-pass state for the live remote answer lane.
- A five-question live baseline against the pre-repair Worker produced two 26-second aborts out of five, including Hyrum Smith and a Pioneer free-form question. Sample fallback/abort incidence was 40 percent; p95 and maximum were 26 seconds.
- Root causes were fixed-keyword Church-person classification, stacked browser and provider retries without a shared deadline, generic failure copy, and a live gate that checked deployed assets and reviewed-local behavior without submitting unreviewed questions.
- Candidate 2026-09-03.16 adds a known Church-person client lane plus server-side official-evidence identity resolution, a single 25-second browser attempt, a 22-second Worker budget with 10.5-second provider stages, bounded retry/expansion behavior, safe provider diagnostics, and a real cross-surface live AI matrix.
- The shared owner-directed question boundary is enforced before rendering, history storage, or network use on Main Ask, Pioneers, and Church History, and again at the Worker. Profanity, explicit sexual content, and derogatory attacks on religions, cultures, ethnicities, nationalities, or political affiliations receive the approved independent-site redirect. Immediate abuse or danger disclosures receive urgent safety guidance.
- Existing local QA plus the new identity, safety, no-echo, zero-network, single-request, deadline, and Worker-policy controls pass. Production remains unverified until GitHub CI, Worker deployment, exact asset verification, and the post-deploy live matrix pass.
- First production acceptance correctly failed after the Worker deployed: Hyrum Smith entered unverified general low-risk fallback when research failed, and rapid scripture/Pioneer specimens were rate-limited. Worker follow-up policy `2026-09-03.17` moves known Church-person classification before research, preserves dynamic misspelling correction, permits the single retry to honor up to five seconds of provider delay inside the 22-second budget, and paces the live matrix. Status remains `VERIFIED FAIL` until that matrix passes.
- Policy `2026-09-03.17` proved the identity repair in production, but verifier HTTP 429 responses remained. Groq's official free-plan limit is 8,000 TPM for the verifier model. Policy `2026-09-03.18` reduces each verifier packet to two eligible 700-character evidence excerpts and a 5,000-character total evidence ceiling while preserving the separate verification step. This is the no-new-cost capacity repair; production remains `VERIFIED FAIL` until the exact-policy live matrix passes.
- Policy `.18` passed four of five live questions but the fifth still hit the Groq verifier's 8,000-TPM limit. Candidate `.19` separates providers: Groq Compound Mini researches, Cloudflare Workers AI verifies through a native binding, and Groq 20B is the one-shot operational fallback. Valid rejection never triggers another verifier, and final source-integrity guards remain authoritative. Production remains `VERIFIED FAIL` until exact `.19` live acceptance passes.
- No-cost provider rule: direct DeepSeek, Kimi, and MiniMax APIs are paid and are not live dependencies. OpenRouter free endpoints, including MiniMax M3, are evaluation/canary candidates only because their documented availability and request limits are not a production reliability contract. CrewAI, AutoGen, and MetaGPT remain background-work candidates, not visitor-path inference providers.
- Exact policy `.19` failed live acceptance: only 3/5 specimens used Cloudflare primary. GPT-OSS 20B is not on Cloudflare's documented JSON Mode list; two complex evidence prompts produced unusable strict output, and the Hyrum Groq fallback then hit JSON validation failure. Candidate `.20` changes the Cloudflare primary only to documented JSON-mode-supported Llama 3.3 70B fast. Status remains `VERIFIED FAIL` pending exact `.20` live acceptance.
- Owner may purchase MiniMax only after a focusChrist-specific benchmark proves quality, latency, JSON/source-index discipline, privacy suitability, and usable capacity. The official API advertises 200 RPM/10M TPM, but the $22 plan is positioned for personal projects/prototyping and has rolling quota windows; do not assume marketing token totals equal public-site production capacity.
- Policy `.20` still failed clean live acceptance: Llama 3.3 70B exceeded the 6.5-second primary ceiling on complex prompts, and strict Groq provider-side JSON enforcement sometimes failed before local validation. Candidate `.21` raises the primary ceiling to 9 seconds with the 5-second fallback reserve intact, uses prompt-enforced plain JSON on the single Groq fallback followed by strict local parsing, and adds a 15-second post-deploy propagation settle. Status remains `VERIFIED FAIL` pending exact `.21` acceptance.
- OpenRouter's free NVIDIA Nemotron 3 Super endpoint is approved only for controlled background evaluation. Its tool and structured-output support make it promising for indexing/review/audit roles, but its free capacity is rate limited, availability was materially below production requirements when checked, and NVIDIA's free-endpoint notice permits logging for product improvement. Never make it a required live Ask dependency or send visitor conversations there without an explicit privacy decision.
- Exact policy `.21` merged at production commit `1495e01c63158997a7467e3086f60984ff17891f` and Worker version `2c1831e5-9844-437c-99d4-fb0a6ddc8b55` deployed. Hyrum Smith passed with official sources and independent verification; the stable general answer worked but omitted two required receipt fields. Scripture, Pioneer, and Church History then hit Groq Compound Mini research HTTP 429. Production remains `VERIFIED FAIL`.
- Groq Compound Mini's official free daily request allowance is not sufficient as the only arbitrary-question research layer. The durable direction is reviewed answers plus a permitted local Church-source index, then domain-filtered retrieval fallback, then independent verification. Tavily is the leading no-card fallback candidate because its official free plan provides 1,000 recurring monthly credits, domain filtering, and a zero-data-retention option. Do not hard-code regression questions or describe the Ask system as healthy until the exact live matrix passes.
- Policy `.22` merged at commit `c9288cb18352e74e95fea3678a95fe5a85d621a4` and deployed as Worker version `5051c511-0873-4cf3-a1ef-b84c240342f1` in workflow `33714963009`. The 900-URL Church index worked: every covered faith specimen used indexed official retrieval with zero Groq research. The 15-request core matrix still failed six verifier specimens because the Cloudflare 70B primary intermittently timed out or rejected usable evidence, while depleted Groq fallback could not recover. Nine core specimens passed, but the matrix stopped before burst and capacity acceptance. Production remains `VERIFIED FAIL`.
- Candidate `.23` replaces only the 70B primary verifier with Cloudflare's active `@cf/meta/llama-3.2-11b-vision-instruct`. Cloudflare documents that exact model ID in both its JSON Mode support list and pricing table at 4,410 input and 61,493 output neurons per million tokens. All official-source, safety, quote, deadline, receipt, and matrix gates remain unchanged. The earlier 8B-fast proposal was rejected before publication because Cloudflare's JSON and pricing documentation used different IDs, which made capacity accounting unauditable.
- Exact `.23` deployed at commit `de684822daed4339cf6881690529c220c4ba2078`, Worker version `81128a24-9588-4079-a344-fd072183d7a5`, workflow `33715774873`. The 11B endpoint returned Cloudflare `service_unavailable` on indexed requests, forcing Groq fallback; most faith specimens then failed verification. The fast failure isolated model availability and also exposed a prompt defect: indexed retrieval put a task instruction in a block labeled `DRAFT`, inviting strict rejection of something that was never a candidate answer. Production remains `VERIFIED FAIL`.
- Candidate `.24` removes the fake indexed draft, explicitly tells the verifier to compose from official evidence when no candidate draft exists, returns to the documented 70B JSON-mode model, extends only its bounded primary window from 9 to 12 seconds, and lowers the normal faith-output ceiling from 700 to 500 tokens. All other gates remain unchanged.
- Exact `.24` merged at commit `3a45a4c4718d5e011f8625e46b8745fa7354c9d5`; Pages and site QA passed, and Worker workflow `33716404968` deployed successfully. Thirteen of the 15 paced core specimens returned complete answers from the Cloudflare primary, but baptism and one Relief Society specimen were rejected by the deterministic final overlap guard after the model approved relevant official sources and source indexes. Receipts proved zero Groq research and no provider outage. Production remains `VERIFIED FAIL`.
- Candidate `.25` preserves the 25-word ordered reconstruction guard and adds explicit independent-paraphrase instructions plus one combined depth/overlap repair. The repair is Cloudflare-only, has a 400-token normal ceiling, shares the unchanged 22-second request deadline, and cannot exceed two Cloudflare verifier calls or stack Groq fallback with repair. The live matrix and capacity gate remain unchanged.
- Exact `.25` merged at commit `cf668ac3f21ec650f3179c27e7b0fb5494d1604c` and deployed as Worker version `e91b1d38-79a0-4e42-ac33-49bce4779bfb` in workflow `33717103285`; Pages and site QA passed. The core answers were provider-stable, but a long baptism answer was rejected because sparse common two-word phrases cumulatively crossed the overlap count after the first verifier used nearly all repair time. The matrix also omitted a legitimate indexed Pioneer daily-life URL from its expected source pattern. Production remains `VERIFIED FAIL`.
- Candidate `.26` keeps the immediate ban on more than 25 consecutive copied words and rejects ordered fragmented reconstruction only when more than 25 matched words also comprise at least 40 percent of the answer. A regression proves dense two-word mosaic copying still fails while sparse two-word matches in a much longer independent answer pass. The matrix adds the official Pioneer daily-life path but still independently fetches the page and requires the expected irrigation and community concepts.
- Exact `.26` merged at commit `055b0513dcf33f1bf415146c3801817820242a37` and deployed as Worker version `4e57ff0d-99e8-4bb3-8c23-cd5f76cd302f` in workflow `33717814014`; Pages and site QA passed. Baptism passed, proving the overlap correction. Fourteen core specimens passed, but one short Pioneer irrigation question received a fast false rejection from the verifier despite indexed official evidence; an immediate production replay succeeded. Production remains `VERIFIED FAIL`.
- Candidate `.27` pins reusable Pioneer-page irrigation intent to the official Pioneer Settlements topic and permits one Cloudflare-only reconsideration when a false verdict conflicts with direct lexical relevance in indexed official evidence. The second pass does not presume approval, shares the deadline, cannot use Groq, and remains limited to two Cloudflare calls total. A second rejection still fails closed.
- Exact `.27` merged at commit `dfc28f17bc41d4e07401b1b6cabb978c745d122d` and deployed as Worker version `69d9af50-4b74-49f9-a225-7381b30cfba4` in workflow `33718635865`; Pages and site QA passed. Pioneer routing passed and 14 core specimens returned complete answers. The final grace specimen hit the 12-second Cloudflare ceiling; the configured Groq operational fallback made zero calls, so the matrix failed closed. Production remains `VERIFIED FAIL`.
- Candidate `.28` keeps the 22-second Worker and 25-second browser ceilings unchanged, reallocates the primary/fallback split from 12/5 seconds to 15/3 seconds, and lowers normal verifier output from 500 to 400 tokens. This gives the provider that answered 14 of 15 specimens more completion time without increasing visitor latency, model calls, or cost gates.

- Exact `.28` returned all 15 core answers but failed grace source precision. Exact `.29` fixed grace and returned 14 other core answers, but its first cold Atonement request exposed the same ineffective Groq recovery path. Candidate `.30` uses the active, priced Cloudflare 8B FP8 fast model as the one operational fallback, with prompt-enforced JSON, strict local validation, per-model neuron accounting, a conservative allowance for timed-out or otherwise unmetered calls, no third verifier call, and the unchanged 22-second request ceiling. Failed repair calls retain their accounting. Production remains `VERIFIED FAIL` pending exact acceptance.

- Exact `.30` deployed as Worker version `469fe621-dcb4-4531-a59e-9e8cfb1bb68c`. All 15 core answers passed and the 8B fallback recovered one timed-out primary with complete accounting. Independent source-page validation failed because Pioneer Settlements did not directly contain irrigation wording. Candidate `.31` pins only Pioneer irrigation questions to the official brief-history page that directly states cooperative irrigation. Production remains `VERIFIED FAIL`.
