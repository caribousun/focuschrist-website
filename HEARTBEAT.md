# HEARTBEAT.md - Kal's Background Tasks

*Updated March 20, 2026 - Added daily self-improvement + config updated*

## CRITICAL: Current Date & Time
**TODAY: Friday, March 20th, 2026 (America/Denver)**
**Use session_status to verify actual time before every brief**

## Config Notes
- `compaction.memoryFlush.enabled: true` ✅ (already enabled)
- `experimental.sessionMemory.enabled: true` with sources: [memory, sessions] ✅ (just added)

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
- Check if OpenClaw gateway is running on port 18789
- If down, attempt restart: `openclaw gateway --force --auth none`
- DO NOT disable lifeline cron jobs — they are the safety net

### 2. Error Tracker (Every Heartbeat)
- Check error log: C:\Users\carib\OneDrive\Desktop\error.txt
- Compare to known errors in brain/knowledge/tools/error-tracker.md
- Alert Wyatt ONLY if: NEW error, same error 3+ times, CRITICAL
- Silent for: expected errors (web_fetch 404s, known issues)

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
  - Is there something in memory that contradicts what I know?
- Small improvements compound. Make one thing 1% better every time.
- Save improvements to brain/cortex/improvements.md with date + what changed

---

## Research Tasks (Rotate Through)

### Helping Hands App
- Research no-code platforms (Glide, Bubble, FlutterFlow, Adalo)
- Study similar apps (TaskRabbit, Neighborly)
- Document features, cost, development time
- Save to memory/app-research.md

### FocusChrist Q&A Optimizer (2x/week)
- Check brain/knowledge/projects/focuschrist-unanswered.md
- Research new questions
- Add answers to ask.html
- Verify all external links work
- Check for trending faith topics
- Backup ask.html to brain/knowledge/projects/

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
- **March 16:** Moat interview (Lehi) — Wyatt had concerns
- **March 19:** Tatum + Meredith wedding — COMPLETED ✅

### UPCOMING
- **March 23:** Follow-up with Mike (Moat) — TBD after wedding
- **Ongoing:** WGU application (Dave Ward referral)

---

## Communication Rules
- Wyatt PROMPTS when conversation is over — never end it myself
- Be warm, direct, helpful — not robotic
- He's the boss, I assist
- My name is Kal 🕊️

---

*Last updated: 2026-03-20 06:00 AM by Kal 🕊️*
