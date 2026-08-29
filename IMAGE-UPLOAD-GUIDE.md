# FocusChrist Art Image Update Guide

This is the canonical repository procedure for future Art-page additions.

## Owner intent
- New artwork is **added to the existing gallery** unless the owner explicitly directs a replacement or deletion.
- Preserve the supplied original artwork exactly. Do not regenerate, crop, recolor, or otherwise alter the original unless specifically authorized.
- Keep existing gallery items, ordering, captions, modal behavior, and accessibility intact unless a change is explicitly requested.

## Controlled workflow

### 1. Work away from production
Create an isolated branch from current `main`. Do not make an unverified Art change directly on production.

### 2. Store the full-resolution original
Place new repository-hosted artwork under `art/`.

Filename rules:
- Use hyphens instead of spaces.
- Preserve the real extension (`.png`, `.jpg`, `.jpeg`).
- Use a descriptive, stable filename such as `Christ-Calms-the-Storm.png`.

### 3. Append the gallery card
Add the new item to `art.html` without removing or reordering existing items unless instructed.

Initial source format before thumbnail generation:
```html
<div class="gallery-item" onclick="openModal(this)">
    <img src="art/Christ-Calms-the-Storm.png"
         alt="Christ Calms the Storm"
         loading="lazy"
         decoding="async">
    <div class="caption">Christ Calms the Storm</div>
</div>
```

Use meaningful alt text and a concise visitor-facing caption.

### 4. Build lightweight gallery thumbnails
The Art page uses small WebP previews while retaining the full-resolution original for the fullscreen viewer.

```bash
python -m pip install pillow
python tools/build-art-thumbnails.py
```

The builder creates `art/thumbs/*.webp`, changes the gallery preview to the thumbnail, and records the original in `data-full-src`. The full-resolution original remains untouched.

### 5. Run permanent site QA
```bash
python tools/site_qa.py
```

QA must pass before merge. It verifies, among other controls:
- at least 38 gallery items remain present;
- all Art images have alt text;
- gallery previews lazy-load and decode asynchronously;
- local Art previews use valid WebP thumbnails;
- every local thumbnail still maps to a nonempty full-resolution original;
- no zero-byte media exists;
- core pages, sitemap, Search Console verification, AI model migration, disclosures, and local references remain intact.

### 6. Review through a pull request
Open a PR to `main`. The permanent **FocusChrist Site QA** workflow must pass. Merge only after the diff shows the intended artwork addition and generated thumbnail changes.

### 7. Verify production
The production Pages workflow runs the same QA again before deployment. After successful deployment, verify:
- the new gallery card appears;
- the preview loads correctly;
- clicking/keyboard activation opens the full-resolution artwork;
- previous/next/Escape modal controls still work;
- existing artwork remains unchanged.

## Important protected assets
- `Jesus.png` is the site-wide banner/social image. Do not remove it merely because its bytes match another Art file.
- `google3fa84a4b37862f36.html` must remain at the repository root to preserve Google Search Console verification.
- Do not expose API secrets. The Groq key remains a Cloudflare secret, not repository content.

## External-image exception
Some existing owner-supplied additions are hosted through Google image URLs. Preserve those existing items. For future additions, prefer a repository-local canonical original plus generated thumbnail when practical because that gives FocusChrist direct control over availability and QA.
