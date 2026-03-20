# MEMORY.md - Long-Term Memory

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
