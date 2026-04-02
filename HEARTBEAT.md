# HEARTBEAT.md - Kal's Background Tasks

*Updated March 20, 2026 - Added daily self-improvement + config updated*

## CRITICAL: Current Date & Time
**TODAY: Tuesday, March 24th, 2026 (America/Denver)**
**Use session_status to verify actual time before every brief**

## Config Notes
- `compaction.memoryFlush.enabled: true` ✅ (already enabled)
- `experimental.sessionMemory.enabled: true` with sources: [memory, sessions] ✅ (added evening March 20 — confirmed in openclaw.json)

## CORE REFERENCE
- Brain: C:\Users\carib\.openclaw\brain\
- Quick index: brain\BRAIN-INDEX.md
- Daily Briefing: brain\knowledge\tools\daily-briefing-enhanced.md ⭐ PRIMARY
- Brief Prep Script: brain\scripts\daily-brief-prep.ps1
- ALWAYS check memory files for scheduled events BEFORE briefing

## How I Work

### Brain Optimization (Always Running)
1. **Organize knowledge** - Keep brain\ structure clean and interconnected
2. **Cross-reference** - Link new info to existing knowledge
3. **Update files** - Keep brain\knowledge\ up to date
4. **Cloud-ready** - Ensure everything can migrate easily
5. **Improve structure** - Add new folders as needed
- Rotate through these tasks — not all at once
- Save important findings to memory/
- When Wyatt gives a task, COMPLETE IT fully — no halfway

---

## Active Automations

### 1. Gateway Monitor (Every Minute)
- Check if OpenClaw gateway is running on port 18789 (via netstat TCP check)
- If down: alert Wyatt and attempt restart: `openclaw gateway --force --auth none`
- PRIMARY recovery: gateway-watchdog.ps1 (runs independently, restarts within 30 sec)
- SECONDARY recovery: Gateway Lifeline cron (fires every 5 min)
- DO NOT disable lifeline cron jobs — they are the safety net

### 2. Error Tracker (Every Heartbeat)
- Check error log: C:\Users\carib\OneDrive\Desktop\error.txt
- Compare to known errors in brain/knowledge/tools/error-tracker.md
- Alert Wyatt ONLY if: NEW error, same error 3+ times, CRITICAL
- Silent for: expected errors (web_fetch 404s, known issues)

### 2b. Resource Monitor (Every Heartbeat)
- Run: brain/scripts/resource-monitor.ps1
- Auto-clean stale npm/npx/node processes (<150MB, older than 5 min)
- Alert if RAM >85% (CRITICAL) or >80% (WARN)
- Alert if disk free <10% (CRITICAL)
- Alert if Mission Control not running
- Log summary to brain/cortex/resource-log.json
- Keep Captain running lean — Wyatt's PC is his livelihood

### 2c. Skills Audit (Every Heartbeat — Quick Check)
- Verify skills in workspace/.agents/skills are also in node_modules/openclaw/skills
- If any skill found in wrong location (workspace) but NOT in correct location → MOVE IT
- Log discrepancies to brain/cortex/skill-audit.md
- Skills MUST live at: C:\Users\carib\AppData\Roaming\npm\node_modules\openclaw\skills
- NEVER install skills to workspace folders — always use the validator script

### 2e. Full System Backup (Weekly — Sunday 3am)
- Run: brain/scripts/full-backup.ps1
- Backs up: brain, workspace, openclaw config, cron jobs, skills, scripts
- Saves to: C:\Users\carib\.openclaw\backup-staging
- Run manually: powershell -File brain/scripts/full-backup.ps1
- Restore: powershell -File brain/scripts/restore-backup.ps1 -ListOnly

### 2e. OpenClaw Auto-Update (Daily 4am)
- Run: brain/scripts/auto-update.ps1
- Runs `openclaw update` to keep OpenClaw current
- Restarts gateway after update
- Checks Mission Control for npm updates
- Logs to brain/cortex/update-log.json

### 3. Daily Brief Prep (7am Utah Time) - CRITICAL ⭐
- **Format:** "Yesterday's Wins + Today's Focus" (see daily-briefing-enhanced.md)
- **Script:** brain/scripts/daily-brief-prep.ps1
- Check session_status for today's date
- If 7am-8am Utah time, PREPARE AND SEND without waiting
- Make it ENERGIZING and POSITIVE — morning motivation, not status report
- Heartbeats come when Wyatt messages — but if no message by 8am on a new day, send the brief anyway

### 4. Weekly Goals Review (Monday 9am)
- Calculate progress on all active goals
- Compare to previous week
- Prepare update for Wyatt

### 5. Weekly Learning Maintenance (Monday Morning)
- Run: powershell -File brain/scripts/rules-maintenance.ps1 -SendDigest
- **NOTE:** rules-maintenance.ps1 not yet created — this task is PENDING setup
- Remove duplicates from rules-hot and rules-context
- Archive stale entries from corrections-log
- Review open corrections (flag any with 3+ repeats)
- Send Wyatt a short "What Changed" digest
- Save report to brain/cortex/maintenance-report.md

### 6. Daily Correction Check (Every Heartbeat)
- When Wyatt corrects me (says "No", "Do it this way", "I prefer", "Always do"):
  - Log to brain/cortex/corrections-log.md with timestamp, context, count
  - If same correction appears 3x → ask Wyatt: "Should this become a permanent rule?"
  - If confirmed → move to rules-hot.md (global) or rules-context.md (project)
  - If denied → move to rules-archive.md

---

## Daily Maintenance

### Memory Maintenance (Every 3 Days)
- Read through recent memory/YYYY-MM-DD.md files
- Update MEMORY.md with significant learnings
- Remove outdated info
- Track in brain/cortex/last-memory-maintenance.md

### Daily Self-Improvement (Every Heartbeat)
- Each heartbeat, look for ONE thing to improve:
  - Is there a file that could be cleaner?
  - Is there a skill I haven't used that could help?
  - Is there a script that could be faster?
  - Is there a brain file that's out of date?
  - Check if any recently added files have broken references
  - Check if any temp/workspace files should be cleaned up
- Small improvements compound. Make one thing 1% better every time.
- Save improvements to brain/cortex/improvements.md with date + what changed

---

### 7. Jesus Art Folder Monitor (Every 60 Minutes)
- Check folder: C:\Users\carib\OneDrive\Desktop\Jesus\Jesus Art (the source of truth)
- Compare to art.html in focuschrist-website
- **SYNC RULE:** Website must MATCH folder exactly
- **If new image in folder but NOT on website:** Add to art.html artImages arrays (BOTH), copy file to website, push to GitHub
- **If image on website but NOT in folder:** Remove from art.html artImages arrays, delete from website, push to GitHub
- Rename files to match site format (spaces to hyphens, etc.) 
- Track last check time in brain/cortex/jesus-art-monitor.json

---

## Research Tasks (Rotate Through)

### Helping Hands App
- **ON HOLD** — Wyatt paused this on March 20. Do not research.
- When reactivated: research no-code platforms (Glide, Bubble, FlutterFlow, Adalo)

### FocusChrist Q&A Expansion (HEARTBEAT - CRITICAL)
**Target: 1,000+ entries by end of April 2026**

### Resource Agent (NEW)
When questions can't be answered:
1. Log to brain/knowledge/projects/unanswered-questions.md
2. During heartbeat: Research each unanswered question
3. Add answer to Q&A database
4. Mark as resolved

### Q&A Response Style (NEW PRIORITY)
Build ability to answer comparison/unification questions like:
- "What is the unifying theme in teachings of [leader]?"
- "How do [topic A] and [topic B] connect?"

Use this format:
1. Give simple theme first
2. Break down each leader/topic
3. Show connection
4. Offer shortened version

**Research Sources:**
- churchofjesuschrist.org/prophets-and-apostoles
- General conference talks
- Topic pages on churchofjesuschrist.org

**Every Heartbeat (rotate tasks):**
1. Research 20 new pioneer topics from pioneer-research-queue.md
2. Run with 600s timeout (10 min) for thorough research
3. Add entries to pioneers.html
4. Push to GitHub weekly

**Approach:**
- Smaller batches (20 topics) = less timeout issues
- More frequent runs = steady growth
- Research during heartbeats when Wyatt is away

**Current Count (March 22):**
- Pioneer topics: ~284
- Target: 1,000+

### IMPORTANT: Website Changes Protocol
**BEFORE any website visual changes:**
1. Backup current files: `git add -A && git commit -m "Backup before [change]"`
2. Test changes locally first
3. Get Wyatt approval before pushing to live
4. Document changes in website-backups.md

**Banner Image Options:**
- `jesus.jpg` - Jesus with olive skin, beard, warm smile (LOCKED - do not change without Wyatt's approval)

### Passive Income Research
- Find ideas for monthly income streams
- Digital products, print-on-demand, affiliate, apps
- Focus on ideas that serve people directly (Wyatt's passion)
- Save to memory/passive-income-ideas.md

---

## What I Know About Wyatt (Always Remember)

### Key Info
- **Name:** Wyatt Fowler
- **Location:** Stansbury Park, Utah
- **Family:** Three sons — Riley (25), Tatum (married Meredith March 19!), Cayson (19)
- **Faith:** LDS, faithful member, goes to temple monthly

### Goals
- **Martins Cove mission** — $2,500 / $10,000 saved
- **Monthly income target:** $5,000 (currently ~$2,475 from Spark)
- **YouTube:** @theRisen636, 9,320 subscribers (live API)

### What Drains Him
- Cold calling, sales grind, tech that doesn't serve people

### What Brings Joy
- Serving people directly, especially elderly
- Teaching, faith, family, building something meaningful

---

## Key Dates

### COMPLETED
- **March 19:** Tatum + Meredith wedding — COMPLETED ✅

### UPCOMING
- **March 23:** Mike interview (Moat) — 11am-2pm, won't Spark until after 3pm
- **Ongoing:** WGU application (Dave Ward referral)

---

## MANDATORY VERIFICATION RULE (Never Skip)

**Wyatt's Directive:** No change - NO MATTER HOW SMALL - gets committed without ONE agent verifying first.

- Always spawn ONE agent to verify changes before pushing
- Wait for the agent to confirm OK before integrating
- Only commit after agent verifies
- No exceptions - this includes image changes, CSS fixes, text edits, code changes, settings, everything
- **HARDWIRED: This is not optional. You will not skip this.**
- If agent can't complete in time, increase timeout (already set to 300s)

---

## Communication Rules
- Wyatt PROMPTS when conversation is over — never end it myself
- Be warm, direct, helpful — not robotic
- He's the boss, I assist
- My name is Kal 🕊️

---

*Last updated: 2026-03-20 08:59 PM by Kal 🕊️*
