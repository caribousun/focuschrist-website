# FocusChrist Repository Audit — Phase 2

This is a conservative dependency audit. A candidate is marked safe only when no UTF-8 text file in the repository references its relative path or basename.

- Files scanned: 118
- Exact duplicate media groups: 12
- Zero-byte files: 3
- Unreferenced root media duplicates with an identical `art/` canonical copy: 0
- Unreferenced zero-byte cleanup candidates: 0

## Safe root duplicate candidates
- None

## Safe zero-byte candidates
- None

## All exact duplicate media groups
### Group 1
- `Divine-Push.png` — 1,857,866 bytes — text references: `art.html`
- `art/Divine-Push.png` — 1,857,866 bytes — text references: `art.html`

### Group 2
- `Forever-Friends.png` — 2,518,243 bytes — text references: `art.html`
- `art/Forever-Friends.png` — 2,518,243 bytes — text references: `art.html`

### Group 3
- `Forever.png` — 2,633,868 bytes — text references: `art.html`
- `art/Forever.png` — 2,633,868 bytes — text references: `art.html`

### Group 4
- `Jesus-walking-Jerusalem.jpg` — 402,727 bytes — text references: `art.html`
- `art/Jesus-walking-Jerusalem.jpg` — 402,727 bytes — text references: `art.html`

### Group 5
- `Jesus.png` — 1,682,157 bytes — text references: `about.html`, `art.html`, `ask.html`, `index.html`, `pioneers.html`, `tools/apply-seo-metadata.py`
- `art/The-Living-Christ.png` — 1,682,157 bytes — text references: `art.html`

### Group 6
- `Little-Friends.jpg` — 239,423 bytes — text references: `art.html`
- `art/Little-Friends.jpg` — 239,423 bytes — text references: `art.html`

### Group 7
- `Never-Alone.png` — 2,993,473 bytes — text references: `art.html`
- `art/Never-Alone.png` — 2,993,473 bytes — text references: `art.html`

### Group 8
- `Palms.jpg` — 315,314 bytes — text references: `art.html`
- `art/Palms.jpg` — 315,314 bytes — text references: `art.html`

### Group 9
- `Posterity.png` — 1,870,859 bytes — text references: `art.html`
- `art/Posterity.png` — 1,870,859 bytes — text references: `art.html`

### Group 10
- `Tranquil-Morning.png` — 1,983,763 bytes — text references: `art.html`
- `art/Tranquil-Morning.png` — 1,983,763 bytes — text references: `art.html`

### Group 11
- `art/Let it go.png` — 2,188,813 bytes — text references: `WEBSITE_CHECKLIST.md`
- `art/Let-It-Go.png` — 2,188,813 bytes — text references: `WEBSITE_CHECKLIST.md`, `art.html`

### Group 12
- `working banner.png` — 1,024,283 bytes — text references: none
- `working-banner.png` — 1,024,283 bytes — text references: `pioneers.html`

## All zero-byte files
- `.gitignore` — text references: `tools/repository-audit.py`
- `.nojekyll` — text references: `tools/repository-audit.py`
- `pioneer-art.png` — text references: `pioneers.html`
