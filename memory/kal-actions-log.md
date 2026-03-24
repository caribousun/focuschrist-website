# Kal's Action Log - Reference for Wyatt

## Today's Actions (March 23, 2026)

### Cron Jobs - ALL DELETED
- ❌ resource-monitor: Every 5 min - DELETED (caused notifications)
- night-research-ask: 11pm daily - Q&A research (ACTIVE)
- night-research-pioneer: 11:30pm daily - Pioneer research (ACTIVE)
- daily-brain-backup: 3am daily (ACTIVE)
- daily-website-backup: 4am daily (ACTIVE)

### Website Changes Made
- Ask page: Q&A working
- Pioneer page: Banner added, spacing fixed, Q&A added
- All pages: Hamburger auto-close on navigation (mobile)
- Art page: Lightbox with arrows working

### Fixes Applied
- Mobile hamburger stays open when navigating: FIXED
- Pioneer encoding weird chars (Gï¿½ï¿½): FIXED  
- Pioneer page spacing: FIXED

### What NOT to Do
- DO NOT create resource-monitor cron - causes notifications!
- Always verify with agent before pushing

### OpenClaw Updates
- Updated to latest version
- Memory search disabled (caused errors)

---
## Reference: How to Check Cron Jobs
```
openclaw cron list
```
To delete: `openclaw cron delete <name>`
