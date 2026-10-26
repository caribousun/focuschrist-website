#!/usr/bin/env node
// A041 gallery staging trigger guard (no secrets used or needed).
//
// Runs before every secret-bearing step of the staging workflow and
// binds the run to the reviewed payload:
//   G1  The branch is exactly the reviewed staging branch.
//   G2  This is the first attempt of the run (run_attempt == 1);
//       a re-run cannot perform a second upload attempt.
//   G3  tools/a041-staging-manifest.json hashes to the reviewed
//       manifest pin carried by the workflow (REVIEWED_MANIFEST_SHA256).
//   G4  The candidate art.html and the staging wrapper hash to their
//       reviewed pins (REVIEWED_CANDIDATE_SHA256, REVIEWED_FRAME_SHA256).
//   G5  The delta against the base ref (REVIEWED_BASE_REF, the site
//       main head the manifest was built against) is exactly the
//       reviewed file set: no extra file, no missing file.
// The pins live in the workflow file, not inside the payload they
// check, so nothing here is self-referential. Any failure exits 1
// before any secret is read.

import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const run = promisify(execFile);

export const EXPECTED_BRANCH = "staging/a041-gallery-close-v2";
export const EXPECTED_DELTA = [
  ".github/workflows/gallery-staging-preview.yml",
  "a041-frame.html",
  "art.html",
  "tools/a041-staging-manifest.json",
  "tools/gallery_staging_assemble.mjs",
  "tools/gallery_staging_guard.mjs",
  "tools/gallery_staging_postcheck.mjs",
  "tools/gallery_staging_preflight.mjs",
  "wrangler.staging.jsonc",
];

async function sha256File(path) {
  return createHash("sha256").update(await readFile(path)).digest("hex");
}

export async function checkGuard(env, deps) {
  const failures = [];
  if (env.GITHUB_REF_NAME !== EXPECTED_BRANCH) {
    failures.push(`G1: branch ${env.GITHUB_REF_NAME ?? "(unset)"} is not ${EXPECTED_BRANCH}`);
  }
  if (env.GITHUB_RUN_ATTEMPT !== "1") {
    failures.push(`G2: run attempt ${env.GITHUB_RUN_ATTEMPT ?? "(unset)"} is not 1; re-runs may not upload`);
  }
  const manifestSha = await deps.sha256File("tools/a041-staging-manifest.json");
  if (manifestSha !== env.REVIEWED_MANIFEST_SHA256) {
    failures.push(`G3: manifest sha256 ${manifestSha} does not match the reviewed pin`);
  }
  const candidateSha = await deps.sha256File("art.html");
  if (candidateSha !== env.REVIEWED_CANDIDATE_SHA256) {
    failures.push(`G4: candidate art.html sha256 ${candidateSha} does not match the reviewed pin`);
  }
  const frameSha = await deps.sha256File("a041-frame.html");
  if (frameSha !== env.REVIEWED_FRAME_SHA256) {
    failures.push(`G4: wrapper sha256 ${frameSha} does not match the reviewed pin`);
  }
  const base = env.REVIEWED_BASE_REF;
  if (!base) {
    failures.push("G5: REVIEWED_BASE_REF is not set");
  } else {
    const delta = await deps.deltaFiles(base);
    const a = [...delta].sort();
    const b = [...EXPECTED_DELTA].sort();
    if (JSON.stringify(a) !== JSON.stringify(b)) {
      failures.push(`G5: delta against the reviewed base differs from the reviewed file set (got ${a.length} files, expected ${b.length})`);
    }
  }
  return failures;
}

async function deltaFiles(base) {
  const { stdout } = await run("git", ["diff", "--name-only", `${base}...HEAD`]);
  return stdout.split("\n").map((s) => s.trim()).filter(Boolean);
}

async function main() {
  const failures = await checkGuard(process.env, { sha256File, deltaFiles });
  if (failures.length > 0) {
    console.error("staging guard FAILED");
    for (const f of failures) console.error(` - ${f}`);
    process.exit(1);
  }
  console.log("staging guard OK: branch, attempt, manifest pin, candidate pins, and reviewed delta all match");
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
