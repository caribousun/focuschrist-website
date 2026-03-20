# Pending Questions - focusChrist Q&A

*Questions awaiting research and answer drafting via the Q&A pipeline*
*See: `brain/knowledge/projects/focuschrist-qa-pipeline.md`*

---

## Format

```markdown
## YYYY-MM-DD | Priority: high|normal|low
- **Question:** "question text here"
  - Asked: YYYY-MM-DD
  - Status: pending | in-progress | answered | skipped
  - Research started: YYYY-MM-DD HH:MM | --
  - Research completed: YYYY-MM-DD HH:MM | --
  - Published: YYYY-MM-DD | --
  - Mentor voice: Mentor Name | TBD
  - Notes: any context or notes
```

**Status values:**
- `pending` — queued for research
- `in-progress` — being researched by agent
- `answered` — answer published to ask.html
- `skipped` — deliberately skipped (inappropriate/not answerable)

**Priority values:**
- `high` — featured question, should be answered first
- `normal` — standard priority
- `low` — nice to have but can wait

---

## Current Queue

(no questions currently pending — all have been answered)

---

## How It Works

1. Question added here manually or detected as "not found" by ask.html
2. Cron script (`brain/scripts/focuschrist-qa-cron.ps1`) runs every 15 min
3. If pending questions exist, cron writes summary to `brain/scripts/focuschrist-qa-cron-lastrun.txt`
4. Main agent picks up the summary and runs through the pipeline:
   - STAGE 1: Confirm question intake (question already in this file ✓)
   - STAGE 2: Research using Tavily/web search
   - STAGE 3: Draft answer in mentor-voice format
   - STAGE 4: Quality check
   - STAGE 5: Publish to ask.html qaDatabase
   - STAGE 6: Commit to GitHub, mark as answered here

---

## Recent Completions Log

| Date | Question (truncated) | Mentor | Status |
|------|--------------------|--------|--------|
| 2026-03-19 | holy ghost is a person | Bednar | ✓ answered |
| 2026-03-19 | receiving recognizing responding holy ghost | Bednar | ✓ answered |
| 2026-03-19 | discerning spirits | Bednar | ✓ answered |
| 2026-03-19 | three rs of choice | Monson | ✓ answered |
| 2026-03-19 | keep the commandments 100 percent | Monson | ✓ answered |
| 2026-03-19 | lucifer | Monson | ✓ answered |
| 2026-03-19 | repentance | Monson | ✓ answered |
| 2026-03-19 | ask seek knock | Nelson | ✓ answered |
| 2026-03-19 | hear him | Nelson | ✓ answered |
| 2026-03-19 | personal revelation | Nelson | ✓ answered |
| 2026-03-19 | spiritual discernment | Nelson | ✓ answered |
| 2026-03-19 | first vision meaning | Joseph Smith | ✓ answered |
| 2026-03-19 | does God speak today | Joseph Smith | ✓ answered |
| 2026-03-19 | three degrees of glory | Joseph Smith | ✓ answered |
| 2026-03-19 | baptism for the dead | Joseph Smith | ✓ answered |
| 2026-03-19 | only true church | Joseph Smith | ✓ answered |
| 2026-03-19 | still small voice | Bednar/Nelson | ✓ answered |
| 2026-03-19 | agency | Monson/Bednar/Nelson | ✓ answered |
| 2026-03-19 | daily bread | Christofferson | ✓ answered |
| 2026-03-19 | prayer not answered | Christofferson | ✓ answered |
| 2026-03-19 | manna | Christofferson | ✓ answered |

---

*Last updated: 2026-03-19*
