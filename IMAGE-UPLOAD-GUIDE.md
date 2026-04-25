# FocusChrist Art Image Upload Guide

## When Wyatt says "upload a new image" — do this:

### Step 1: Get the image file
- Place image in: `C:\Users\carib\OneDrive\Desktop\focuschrist-website\art\`
- **Filename rules:**
  - NO spaces — use hyphens: `My Image.png` → `My-Image.png`
  - Check actual extension (`.png`, `.jpg`, `.jpeg`) — don't guess!
  - Use title-case with hyphens: `The-Good-Shepherd.png`

### Step 2: Verify file exists locally
```bash
ls art/
```
Check the exact filename and extension.

### Step 3: Add to art.html
The HTML uses format:
```html
<img src="art/FILENAME.EXT" alt="Display Name">
```

Find where to insert (alphabetically or at end), add:
```html
<div class="gallery-item" onclick="openModal(this)">
    <img src="art/YOUR-FILENAME.EXT" alt="Your Display Name">
    <div class="caption">Your Display Name</div>
</div>
```

### Step 4: Commit & Push
```bash
git add art.html
git commit -m "Add: Your image name"
git push
```

### Step 5: Verify on live site
URL format: `https://focuschrist.com/art/FILENAME.EXT`

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---------|-----|
| Spaces in filename | Replace with hyphens |
| Wrong extension (.png vs .jpg) | Check actual file extension |
| Missing `/art/` prefix | Must be `art/filename.png` |
| Forgot to push | Run `git push` |

---

## Quick Commands
```bash
# Check files in art folder
git ls-tree -r HEAD --name-only | rg "^art/"

# Check what art.html references
rg "src=" art.html
```