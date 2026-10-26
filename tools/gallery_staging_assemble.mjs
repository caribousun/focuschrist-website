#!/usr/bin/env node
// A041 gallery staging assembly (fail-closed), corrected revision.
//
// Copies ONLY the positively enumerated files from
// tools/a041-staging-manifest.json into staging-dist/, verifying each
// file against the manifest before the upload step may run:
//   - byte size must match the manifest for every file;
//   - the Git blob hash (SHA-1 of "blob <bytes>\0" + content) must
//     match wherever the manifest records one, which is every
//     existing-source row (220 of 222). A same-size byte change in a
//     binary file therefore fails the assembly;
//   - sha256 must match wherever the manifest records one (the
//     candidate art.html, the staging wrapper, and every text row);
//   - the assembled directory must contain exactly the manifest set:
//     no missing file, no extra file.
// Any mismatch exits nonzero and no upload happens.

import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile, readdir, rm, stat } from "node:fs/promises";
import path from "node:path";

const MANIFEST_PATH = "tools/a041-staging-manifest.json";
const OUT_DIR = "staging-dist";

export function gitBlobSha(data) {
  const header = Buffer.from(`blob ${data.length}\0`, "utf8");
  return createHash("sha1").update(Buffer.concat([header, data])).digest("hex");
}

async function listFiles(dir, prefix = "") {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      out.push(...(await listFiles(path.join(dir, entry.name), rel)));
    } else if (entry.isFile()) {
      out.push(rel);
    }
  }
  return out;
}

export async function assemble(manifestPath = MANIFEST_PATH, outDir = OUT_DIR) {
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  const rows = manifest.files;
  await rm(outDir, { recursive: true, force: true });
  await mkdir(outDir, { recursive: true });

  const problems = [];
  for (const row of rows) {
    const dest = path.join(outDir, row.path);
    await mkdir(path.dirname(dest), { recursive: true });
    let data;
    try {
      data = await readFile(row.path);
      await copyFile(row.path, dest);
    } catch {
      problems.push(`missing in checkout: ${row.path}`);
      continue;
    }
    const info = await stat(dest);
    if (info.size !== row.bytes || data.length !== row.bytes) {
      problems.push(`size mismatch: ${row.path} ${info.size} != ${row.bytes}`);
      continue;
    }
    if (row.blob) {
      const blob = gitBlobSha(data);
      if (blob !== row.blob) {
        problems.push(`git blob mismatch: ${row.path} ${blob} != ${row.blob}`);
      }
    }
    if (row.sha256) {
      const digest = createHash("sha256").update(data).digest("hex");
      if (digest !== row.sha256) {
        problems.push(`sha256 mismatch: ${row.path}`);
      }
    }
    if (!row.blob && !row.sha256) {
      problems.push(`manifest row carries no pin: ${row.path}`);
    }
  }

  const assembled = (await listFiles(outDir)).sort();
  const expected = rows.map((r) => r.path).sort();
  if (JSON.stringify(assembled) !== JSON.stringify(expected)) {
    problems.push(
      `assembled set differs from manifest: assembled=${assembled.length} expected=${expected.length}`,
    );
  }

  const total = rows.reduce((sum, r) => sum + r.bytes, 0);
  return { ok: problems.length === 0, problems, count: rows.length, total };
}

async function main() {
  const result = await assemble();
  if (!result.ok) {
    console.error("assembly FAILED");
    for (const p of result.problems) console.error(` - ${p}`);
    process.exit(1);
  }
  console.log(
    `assembly OK: ${result.count} files, ${result.total} bytes, all manifest checks passed (size, git blob, sha256)`,
  );
}

import { fileURLToPath } from "node:url";
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
