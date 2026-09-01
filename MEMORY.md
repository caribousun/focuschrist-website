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

- Current production commit: `baaa15a24e5b35101bde8a5046b86295310b50bb`; feature repair merge: `f58b232ed9386361285fafd44e5fea8390fe1868`.
- The final user-visible answer—not only the Worker response—must pass source-integrity guards and runtime-owner tests. Person names that overlap scripture/source titles require explicit lexical-collision regressions.
- Multi-turn acceptance separately gates the initial question, pronoun follow-up, chained ellipsis, reset isolation, and competing identity. Stable reviewed facts such as Lincoln’s death time remain on an integrity-pinned zero-Worker lane.
- Competing-subject detection is case-insensitive and grammar-anchored; full names, lowercase names, surnames, and acronyms must not inherit the prior person.
- `tools/live_production_ask_qa.js` is a protected push-only gate. It recursively discovers critical/transitive scripts, compares canonical visitor cache keys and origin probes with the tested revision, repeats after a stability interval, and executes critical Main Ask, Pioneer, and Church History contracts.
- A release remains blocked until repository CI, independent adversarial review, exact deployment workflows, the live production gate, Focus memory/recovery updates, and Master Brain learning readback all agree.
