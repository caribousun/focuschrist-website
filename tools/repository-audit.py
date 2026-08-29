from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "repository-audit-phase2.md"
MEDIA_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
TEXT_EXTENSIONS = {
    ".html", ".css", ".js", ".json", ".jsonc", ".xml", ".txt", ".md", ".py",
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".csv"
}
IGNORED_PARTS = {".git"}


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path == REPORT:
            continue
        yield path


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_texts(files):
    texts = {}
    for path in files:
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            texts[path] = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass
    return texts


def references_for(target: Path, texts):
    target_rel = rel(target)
    name = target.name
    refs = []
    for source, text in texts.items():
        if source == target:
            continue
        if target_rel in text or name in text:
            refs.append(rel(source))
    return sorted(set(refs))


def main():
    files = list(iter_files())
    texts = read_texts(files)

    zero_byte = [p for p in files if p.stat().st_size == 0]

    media_groups = defaultdict(list)
    for path in files:
        if path.suffix.lower() in MEDIA_EXTENSIONS and path.stat().st_size > 0:
            media_groups[sha256(path)].append(path)
    duplicate_groups = [group for group in media_groups.values() if len(group) > 1]

    safe_root_duplicate_candidates = []
    for group in duplicate_groups:
        art_variants = [p for p in group if rel(p).startswith("art/") and not rel(p).startswith("art/thumbs/")]
        if not art_variants:
            continue
        for path in group:
            if path.parent != ROOT:
                continue
            refs = references_for(path, texts)
            if not refs:
                safe_root_duplicate_candidates.append((path, art_variants[0]))

    safe_zero_byte_candidates = []
    for path in zero_byte:
        refs = references_for(path, texts)
        if not refs and path.name not in {".nojekyll", ".gitignore"}:
            safe_zero_byte_candidates.append(path)

    lines = [
        "# FocusChrist Repository Audit — Phase 2",
        "",
        "This is a conservative dependency audit. A candidate is marked safe only when no UTF-8 text file in the repository references its relative path or basename.",
        "",
        f"- Files scanned: {len(files)}",
        f"- Exact duplicate media groups: {len(duplicate_groups)}",
        f"- Zero-byte files: {len(zero_byte)}",
        f"- Unreferenced root media duplicates with an identical `art/` canonical copy: {len(safe_root_duplicate_candidates)}",
        f"- Unreferenced zero-byte cleanup candidates: {len(safe_zero_byte_candidates)}",
        "",
        "## Safe root duplicate candidates",
    ]
    if safe_root_duplicate_candidates:
        for path, canonical in sorted(safe_root_duplicate_candidates, key=lambda item: rel(item[0])):
            lines.append(f"- `{rel(path)}` → identical canonical copy `{rel(canonical)}` ({path.stat().st_size:,} bytes)")
    else:
        lines.append("- None")

    lines += ["", "## Safe zero-byte candidates"]
    if safe_zero_byte_candidates:
        for path in sorted(safe_zero_byte_candidates, key=rel):
            lines.append(f"- `{rel(path)}`")
    else:
        lines.append("- None")

    lines += ["", "## All exact duplicate media groups"]
    for index, group in enumerate(sorted(duplicate_groups, key=lambda g: rel(g[0])), start=1):
        lines.append(f"### Group {index}")
        for path in sorted(group, key=rel):
            refs = references_for(path, texts)
            ref_text = ", ".join(f"`{r}`" for r in refs) if refs else "none"
            lines.append(f"- `{rel(path)}` — {path.stat().st_size:,} bytes — text references: {ref_text}")
        lines.append("")

    lines += ["## All zero-byte files"]
    for path in sorted(zero_byte, key=rel):
        refs = references_for(path, texts)
        ref_text = ", ".join(f"`{r}`" for r in refs) if refs else "none"
        lines.append(f"- `{rel(path)}` — text references: {ref_text}")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.name}")
    print(f"Safe root duplicate candidates: {len(safe_root_duplicate_candidates)}")
    print(f"Safe zero-byte candidates: {len(safe_zero_byte_candidates)}")


if __name__ == "__main__":
    main()
