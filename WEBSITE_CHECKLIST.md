# FocusChrist Website Update Checklist

## BEFORE Making ANY Changes

1. ✅ Check git status: `git status`
2. ✅ Create restore point FIRST (optional but recommended):
   ```bash
   git add -A
   git commit -m "Restore point before [change]"
   git tag "restore-point-YYYY-MM-DD-HHMM"
   ```

## ADDING IMAGES TO ART PAGE

1. ✅ Copy image to `art/` folder first
2. ✅ Edit ONLY art.html — do NOT touch ask.html
3. ✅ Stage ONLY the files you need:
   ```bash
   git add art.html "art/filename.png"
   ```
4. ✅ Check status shows ONLY art.html and the image
5. ✅ Commit with clear message
6. ✅ Push and verify

## NEVER DO

- ❌ `git add -A` unless you want to commit EVERYTHING
- ❌ Edit ask.html and art.html in the same session
- ❌ Continue through git conflicts without checking first

## IF ASK PAGE BREAKS

1. Find last working commit: `git log --all --oneline`
2. Checkout that version: `git checkout [commit-hash] -- ask.html`
3. Commit the restore
4. Push

---

**Key commits:**
- Working ask page: `965598f` (24 atonement entries)
- Working art page with "Let It Go": `39e8db2`