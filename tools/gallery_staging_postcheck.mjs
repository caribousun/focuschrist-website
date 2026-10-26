#!/usr/bin/env node
// A041 gallery staging postcheck and final receipt (failure-safe).
//
// Runs after the upload step whether the upload succeeded, failed, or
// ended uncertainly, and reconciles the attempt:
//   - It reads the upload-attempt marker written before the upload.
//     No marker means the upload never started: verdict NO_ATTEMPT.
//   - It re-reads the Worker's active deployment through the same
//     validated metadata path as the preflight and compares it with
//     the preflight record. Any change fails the reconciliation.
//   - It records the upload step outcome exactly as reported, and
//     captures the exact version id from the upload output when one
//     is present. When no version id can be captured, the upload's
//     effect is recorded as UNKNOWN, honestly. Nothing here retries,
//     deploys, rolls back, or cleans up, on any outcome.
//   - When a version id is captured, the receipt records the
//     supported exact-version cleanup operation for the cleanup
//     owner (never executed here):
//       DELETE /accounts/{account_id}/workers/workers/{worker_id}/versions/{version_id}
//     The API permits the Worker ID or its name, so "workspace"
//     suffices as {worker_id}; the version is the exact full UUID
//     captured from the upload output, never "latest" or a prefix.
//   - The original upload failure is preserved: this step exits 1
//     when the upload outcome was not success or the deployment
//     changed, after the final receipt has been written.
//
// Output: final-receipt.json in the working directory (non-secret).

import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import {
  assessPreflight,
  readState,
} from "./gallery_staging_preflight.mjs";

const UUID_RE = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;

export function parseUploadOutput(text) {
  const versionMatch = text.match(new RegExp(`version[^\\n]*?(${UUID_RE.source})`, "i")) ||
    text.match(UUID_RE);
  const aliasMatch = text.match(/https?:\/\/[^\s"']*workers\.dev[^\s"']*/i);
  return {
    version_id: versionMatch ? versionMatch[1] ?? versionMatch[0] : null,
    alias_url: aliasMatch ? aliasMatch[0] : null,
  };
}

export function sameDeployment(a, b) {
  if (!a || !b) return false;
  return JSON.stringify(a) === JSON.stringify(b);
}

export function reconcile({ marker, uploadOutcome, uploadOutput, before, after }) {
  const receipt = {
    tool: "gallery_staging_postcheck",
    checked_at: new Date().toISOString(),
    run: marker ? { id: marker.run_id ?? null, attempt: marker.run_attempt ?? null, head: marker.head_sha ?? null } : null,
    upload_attempted: Boolean(marker),
    upload_outcome: uploadOutcome ?? null,
    version_id: null,
    alias_url: null,
    effect: "NO_ATTEMPT",
    deployment_before: before ?? null,
    deployment_after: after ?? null,
    deployment_unchanged: null,
    cleanup: null,
    verdict: "OK",
    problems: [],
  };
  if (!marker) {
    receipt.verdict = "NO_ATTEMPT";
    return receipt;
  }
  const parsed = parseUploadOutput(uploadOutput ?? "");
  receipt.version_id = parsed.version_id;
  receipt.alias_url = parsed.alias_url;
  receipt.deployment_unchanged = sameDeployment(before, after);
  if (receipt.deployment_unchanged !== true) {
    receipt.problems.push("active deployment changed or could not be compared");
  }
  if (uploadOutcome === "success" && parsed.version_id) {
    receipt.effect = "VERSION_CREATED";
    receipt.cleanup = {
      operation: "DELETE /accounts/{account_id}/workers/workers/{worker_id}/versions/{version_id}",
      worker_id: "workspace (Worker name permitted in place of the ID)",
      version_id: parsed.version_id,
      note: "Exact full version UUID from the upload output. Never latest, never a prefix, never whole-Worker deletion, never disabling previews, never branch deletion alone. Not executed by this workflow; cleanup is the named owner's later, separately recorded action.",
    };
  } else if (uploadOutcome === "success") {
    receipt.effect = "UNKNOWN";
    receipt.problems.push("upload reported success but no version id could be captured from its output");
  } else {
    receipt.effect = "UNKNOWN";
    receipt.problems.push(`upload outcome was ${uploadOutcome ?? "unreported"}; its effect is unknown and is recorded as unknown`);
  }
  if (receipt.problems.length > 0 || receipt.deployment_unchanged !== true) {
    receipt.verdict = "FAILED";
  }
  return receipt;
}

async function readJsonOrNull(path) {
  try {
    return JSON.parse(await readFile(path, "utf8"));
  } catch {
    return null;
  }
}

async function main() {
  const marker = await readJsonOrNull("upload-attempt.json");
  const beforeReceipt = await readJsonOrNull("preflight-before.json");
  let uploadOutput = "";
  try {
    uploadOutput = await readFile("upload-output.txt", "utf8");
  } catch { /* output may be absent when the upload never ran */ }

  let after = null;
  const token = process.env.CLOUDFLARE_API_TOKEN;
  const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
  if (marker && token && accountId) {
    const state = await readState(token, accountId);
    after = assessPreflight(state).active_deployment;
  }
  const receipt = reconcile({
    marker,
    uploadOutcome: process.env.UPLOAD_OUTCOME ?? null,
    uploadOutput,
    before: beforeReceipt?.active_deployment ?? null,
    after,
  });
  await writeFile("final-receipt.json", JSON.stringify(receipt, null, 2));
  console.log(JSON.stringify(receipt, null, 2));
  if (receipt.verdict === "FAILED") {
    process.exit(1);
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  main().catch(async (error) => {
    try {
      await writeFile("final-receipt.json", JSON.stringify({
        tool: "gallery_staging_postcheck",
        checked_at: new Date().toISOString(),
        verdict: "FAILED",
        problems: [`postcheck error: ${String(error?.message ?? error)}`],
      }, null, 2));
    } catch { /* receipt write failure itself fails the step */ }
    console.error(error);
    process.exit(1);
  });
}
