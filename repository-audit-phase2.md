# FocusChrist Repository Audit — Phase 2

This is a conservative dependency audit. Root filenames are considered referenced only when used as root files, not when the same basename appears under a subdirectory such as `art/`.

- Files scanned: 120
- Exact duplicate media groups: 12
- Zero-byte files: 2
- Unreferenced root media duplicates with an identical `art/` canonical copy: 10
- Unreferenced zero-byte cleanup candidates: 0

## Safe root duplicate candidates
- `Divine-Push.png` → identical canonical copy `art/Divine-Push.png` (1,857,866 bytes)
- `Forever-Friends.png` → identical canonical copy `art/Forever-Friends.png` (2,518,243 bytes)
- `Forever.png` → identical canonical copy `art/Forever.png` (2,633,868 bytes)
- `Jesus-walking-Jerusalem.jpg` → identical canonical copy `art/Jesus-walking-Jerusalem.jpg` (402,727 bytes)
- `Jesus.png` → identical canonical copy `art/The-Living-Christ.png` (1,682,157 bytes)
- `Little-Friends.jpg` → identical canonical copy `art/Little-Friends.jpg` (239,423 bytes)
- `Never-Alone.png` → identical canonical copy `art/Never-Alone.png` (2,993,473 bytes)
- `Palms.jpg` → identical canonical copy `art/Palms.jpg` (315,314 bytes)
- `Posterity.png` → identical canonical copy `art/Posterity.png` (1,870,859 bytes)
- `Tranquil-Morning.png` → identical canonical copy `art/Tranquil-Morning.png` (1,983,763 bytes)

## Safe zero-byte candidates
- None

## All exact duplicate media groups
### Group 1
- `Divine-Push.png` — 1,857,866 bytes — text references: none
- `art/Divine-Push.png` — 1,857,866 bytes — text references: `art.html`

### Group 2
- `Forever-Friends.png` — 2,518,243 bytes — text references: none
- `art/Forever-Friends.png` — 2,518,243 bytes — text references: `art.html`

### Group 3
- `Forever.png` — 2,633,868 bytes — text references: none
- `art/Forever.png` — 2,633,868 bytes — text references: `art.html`

### Group 4
- `Jesus-walking-Jerusalem.jpg` — 402,727 bytes — text references: none
- `art/Jesus-walking-Jerusalem.jpg` — 402,727 bytes — text references: `art.html`

### Group 5
- `Jesus.png` — 1,682,157 bytes — text references: none
- `art/The-Living-Christ.png` — 1,682,157 bytes — text references: `art.html`

### Group 6
- `Little-Friends.jpg` — 239,423 bytes — text references: none
- `art/Little-Friends.jpg` — 239,423 bytes — text references: `art.html`

### Group 7
- `Never-Alone.png` — 2,993,473 bytes — text references: none
- `art/Never-Alone.png` — 2,993,473 bytes — text references: `art.html`

### Group 8
- `Palms.jpg` — 315,314 bytes — text references: none
- `art/Palms.jpg` — 315,314 bytes — text references: `art.html`

### Group 9
- `Posterity.png` — 1,870,859 bytes — text references: none
- `art/Posterity.png` — 1,870,859 bytes — text references: `art.html`

### Group 10
- `Tranquil-Morning.png` — 1,983,763 bytes — text references: none
- `art/Tranquil-Morning.png` — 1,983,763 bytes — text references: `art.html`

### Group 11
- `art/Let it go.png` — 2,188,813 bytes — text references: none
- `art/Let-It-Go.png` — 2,188,813 bytes — text references: `art.html`

### Group 12
- `working banner.png` — 1,024,283 bytes — text references: none
- `working-banner.png` — 1,024,283 bytes — text references: `.github/workflows/repair-pioneer-and-strengthen-qa.yml`, `pioneers.html`

## All zero-byte files
- `.gitignore` — text references: `tools/repository-audit.py`
- `.nojekyll` — text references: `tools/repository-audit.py`
