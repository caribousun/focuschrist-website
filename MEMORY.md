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
