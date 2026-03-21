# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Desktop Location
**Primary Desktop:** `C:\Users\carib\OneDrive\Desktop`

All shortcuts/bat files go here. Kal's Tools folder is at this location.

## Tool Locations

### CLI Tools
- **jq** → `C:\Users\carib\AppData\Local\Microsoft\WinGet\Packages\jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe\jq.exe` (v1.8.1)
- **rg** (ripgrep) → `C:\Users\carib\AppData\Local\Microsoft\WinGet\Packages\BurntSushi.ripgrep.MSVC_Microsoft.Winget.Source_8wekyb3d8bbwe\ripgrep-15.1.0-x86_64-pc-windows-msvc\rg.exe` (v15.1.0)
- **gh** (GitHub CLI) → `C:\Users\carib\OneDrive\Desktop\gh.exe`
- **python** → `C:\Python312\python.exe`

### Session Logs
- Location: `C:\Users\carib\.openclaw\agents\main\sessions\`
- Skill: `openclaw/skills/session-logs` — search conversation history with jq/rg

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Automation & Workflows

### Apify (Web Scraping)
- **URL:** https://www.apify.com
- **Purpose:** Web scraping & automation
- **Use for:** FocusChrist research, competitor analysis

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
