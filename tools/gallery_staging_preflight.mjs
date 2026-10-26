#!/usr/bin/env node
// A041 gallery staging preflight (read-only), corrected revision.
//
// Purpose: before any staging upload, prove from supported non-secret
// Cloudflare JSON metadata that the expected Worker already exists on
// the expected account, record its deployment state and binding types,
// and STOP (exit 2) before any upload if a finite stop condition holds.
//
// API contract (corrected per A-2026-10-26-GALLERY-M697-FINITE-
// CORRECTIONS-01): GET /accounts/{id}/workers/scripts/{name} returns
// raw script content, not a JSON envelope, so it is never used here.
// Existence, bindings, deployments, and subdomain state are read from
// the supported JSON metadata endpoints:
//   GET /accounts/{id}/workers/scripts/{name}/settings
//   GET /accounts/{id}/workers/scripts/{name}/deployments
//   GET /accounts/{id}/workers/scripts/{name}/subdomain
//   GET /accounts/{id}/workers/subdomain            (account record)
// Every response shape is validated. Missing or malformed data is a
// stop, never a default. It never prints the API token or the account
// ID. It performs GET requests only. It creates nothing, changes
// nothing, and expands no credential scope.
//
// Stop conditions (any one stops the run before upload):
//   S1  CLOUDFLARE_API_TOKEN or CLOUDFLARE_ACCOUNT_ID missing.
//   S2  The Worker named by EXPECTED_WORKER does not exist on the
//       account, or its settings cannot be read as valid JSON
//       metadata (versions upload cannot create a Worker).
//   S3  The Worker's deployment state cannot be read, is malformed,
//       or has no valid active deployment whose version traffic
//       totals exactly 100.
//   S4  The existing Worker's bindings cannot be validated, include
//       an unresolved "inherit" binding (not demonstrably
//       assets-only), or include any binding type other than
//       "assets".
//   S5  Preview URLs are not provably usable: the per-Worker
//       subdomain record is missing, malformed, or reports
//       previews_enabled other than true, or the account workers.dev
//       subdomain record cannot be read. An account subdomain alone
//       does not prove usable preview URLs.
//
// Output: preflight-receipt.json in the working directory containing
// only non-secret fields.

import { writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

export const EXPECTED_WORKER = "workspace";
const API_BASE = "https://api.cloudflare.com/client/v4";

function isPlainObject(v) {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

function envelope(payload) {
  if (!isPlainObject(payload) || payload.success !== true) return null;
  if (!isPlainObject(payload.result)) return null;
  return payload.result;
}

export function validateSettings(payload, status) {
  const stops = [];
  if (status === 404) {
    return { exists: false, bindings: null, stops: ["S2: expected Worker does not exist on this account"] };
  }
  if (status !== 200) {
    return { exists: null, bindings: null, stops: [`S2: settings read returned status ${status}`] };
  }
  const result = envelope(payload);
  if (!result) {
    return { exists: null, bindings: null, stops: ["S2: settings response is not a valid success envelope"] };
  }
  if (!Array.isArray(result.bindings)) {
    return { exists: true, bindings: null, stops: ["S4: settings result has no bindings array; binding state cannot be validated"] };
  }
  const bindings = [];
  for (const b of result.bindings) {
    if (!isPlainObject(b) || typeof b.name !== "string" || typeof b.type !== "string") {
      return { exists: true, bindings: null, stops: ["S4: a binding entry is malformed (name and type must be strings)"] };
    }
    bindings.push({ name: b.name, type: b.type });
  }
  const inherit = bindings.filter((b) => b.type === "inherit");
  if (inherit.length > 0) {
    stops.push(`S4: unresolved inherit binding(s) present (${inherit.map((b) => b.name).join(", ")}); not demonstrably assets-only`);
  }
  const offenders = bindings.filter((b) => b.type !== "assets" && b.type !== "inherit");
  if (offenders.length > 0) {
    stops.push(`S4: existing Worker carries non-assets binding types: ${offenders.map((b) => `${b.name}:${b.type}`).join(", ")}`);
  }
  return { exists: true, bindings, stops };
}

export function validateDeployments(payload, status) {
  if (status !== 200) {
    return { active: null, stops: [`S3: deployments read returned status ${status}`] };
  }
  const result = envelope(payload);
  if (!result || !Array.isArray(result.deployments)) {
    return { active: null, stops: ["S3: deployments response is malformed (no deployments array)"] };
  }
  if (result.deployments.length === 0) {
    return { active: null, stops: ["S3: no deployments recorded for the existing Worker"] };
  }
  const d = result.deployments[0];
  if (!isPlainObject(d) || typeof d.id !== "string" || d.id.length === 0) {
    return { active: null, stops: ["S3: active deployment has no valid id"] };
  }
  if (!Array.isArray(d.versions) || d.versions.length === 0) {
    return { active: null, stops: ["S3: active deployment has no versions array"] };
  }
  const versions = [];
  for (const v of d.versions) {
    if (!isPlainObject(v) || typeof v.version_id !== "string" || v.version_id.length === 0 ||
        typeof v.percentage !== "number" || !Number.isFinite(v.percentage)) {
      return { active: null, stops: ["S3: a deployment version entry is malformed"] };
    }
    versions.push({ version_id: v.version_id, percentage: v.percentage });
  }
  const total = versions.reduce((s, v) => s + v.percentage, 0);
  if (Math.round(total * 1000) !== 100000) {
    return { active: null, stops: [`S3: active deployment version traffic totals ${total}, not 100`] };
  }
  return {
    active: {
      id: d.id,
      source: typeof d.source === "string" ? d.source : null,
      strategy: typeof d.strategy === "string" ? d.strategy : null,
      versions,
      traffic_total: 100,
      created_on: typeof d.created_on === "string" ? d.created_on : null,
    },
    stops: [],
  };
}

export function validateWorkerSubdomain(payload, status) {
  if (status !== 200) {
    return { enabled: null, previews_enabled: null, stops: [`S5: per-Worker subdomain read returned status ${status}`] };
  }
  const result = envelope(payload);
  if (!result || typeof result.enabled !== "boolean" || typeof result.previews_enabled !== "boolean") {
    return { enabled: null, previews_enabled: null, stops: ["S5: per-Worker subdomain response is malformed (enabled and previews_enabled must be booleans)"] };
  }
  const stops = [];
  if (result.previews_enabled !== true) {
    stops.push("S5: per-Worker subdomain record reports previews_enabled other than true; preview URLs are not provably usable");
  }
  return { enabled: result.enabled, previews_enabled: result.previews_enabled, stops };
}

export function validateAccountSubdomain(payload, status) {
  if (status !== 200) {
    return { subdomain: null, stops: [`S5: account subdomain read returned status ${status}`] };
  }
  const result = envelope(payload);
  if (!result || typeof result.subdomain !== "string" || result.subdomain.length === 0) {
    return { subdomain: null, stops: ["S5: account workers.dev subdomain record is missing or empty"] };
  }
  return { subdomain: result.subdomain, stops: [] };
}

// Pure assessment over already-fetched responses. Each response is
// {status, payload}. Returns the receipt body (without timestamps).
export function assessPreflight({ settings, deployments, workerSubdomain, accountSubdomain }) {
  const receipt = {
    tool: "gallery_staging_preflight",
    expected_worker: EXPECTED_WORKER,
    account_id_recorded: false,
    token_recorded: false,
    stop_conditions: [],
    worker_exists: null,
    bindings: null,
    active_deployment: null,
    worker_subdomain: null,
    workers_dev_subdomain: null,
  };
  const s = validateSettings(settings.payload, settings.status);
  receipt.worker_exists = s.exists;
  receipt.bindings = s.bindings;
  receipt.stop_conditions.push(...s.stops);
  if (s.exists === true) {
    const d = validateDeployments(deployments.payload, deployments.status);
    receipt.active_deployment = d.active;
    receipt.stop_conditions.push(...d.stops);
    const w = validateWorkerSubdomain(workerSubdomain.payload, workerSubdomain.status);
    receipt.worker_subdomain = { enabled: w.enabled, previews_enabled: w.previews_enabled };
    receipt.stop_conditions.push(...w.stops);
  }
  const a = validateAccountSubdomain(accountSubdomain.payload, accountSubdomain.status);
  receipt.workers_dev_subdomain = a.subdomain;
  receipt.stop_conditions.push(...a.stops);
  receipt.verdict = receipt.stop_conditions.length === 0 ? "PROCEED" : "STOP";
  return receipt;
}

export async function fetchJson(path, token) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }
  return { status: response.status, payload };
}

export async function readState(token, accountId) {
  const scriptPath = `/accounts/${accountId}/workers/scripts/${EXPECTED_WORKER}`;
  const settings = await fetchJson(scriptPath + "/settings", token);
  let deployments = { status: 0, payload: null };
  let workerSubdomain = { status: 0, payload: null };
  const probe = validateSettings(settings.payload, settings.status);
  if (probe.exists === true) {
    deployments = await fetchJson(scriptPath + "/deployments", token);
    workerSubdomain = await fetchJson(scriptPath + "/subdomain", token);
  }
  const accountSubdomain = await fetchJson(`/accounts/${accountId}/workers/subdomain`, token);
  return { settings, deployments, workerSubdomain, accountSubdomain };
}

async function main() {
  const token = process.env.CLOUDFLARE_API_TOKEN;
  const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
  let receipt;
  if (!token || !accountId) {
    receipt = {
      tool: "gallery_staging_preflight",
      expected_worker: EXPECTED_WORKER,
      checked_at: new Date().toISOString(),
      account_id_recorded: false,
      token_recorded: false,
      stop_conditions: ["S1: missing CLOUDFLARE_API_TOKEN or CLOUDFLARE_ACCOUNT_ID"],
      worker_exists: null,
      verdict: "STOP",
    };
  } else {
    const state = await readState(token, accountId);
    receipt = assessPreflight(state);
    receipt.checked_at = new Date().toISOString();
  }
  await writeFile("preflight-receipt.json", JSON.stringify(receipt, null, 2));
  console.log(JSON.stringify(receipt, null, 2));
  if (receipt.verdict === "STOP") {
    process.exit(2);
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  main().catch(async (error) => {
    const receipt = {
      tool: "gallery_staging_preflight",
      expected_worker: EXPECTED_WORKER,
      checked_at: new Date().toISOString(),
      account_id_recorded: false,
      token_recorded: false,
      stop_conditions: [`S0: preflight error: ${String(error?.message ?? error)}`],
      verdict: "STOP",
    };
    try {
      await writeFile("preflight-receipt.json", JSON.stringify(receipt, null, 2));
    } catch { /* receipt write failure itself stops the run via exit code */ }
    console.error(error);
    process.exit(2);
  });
}
