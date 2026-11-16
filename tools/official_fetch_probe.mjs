// One fixed production observation. No retries, credentials, source-policy changes or deployment.
import { pathToFileURL } from 'node:url';

export const ENDPOINT = 'https://focuschrist-groq-proxy.caribousun.workers.dev';
export const FAILURE_CLASSES = Object.freeze(['budget','timeout','network','http429','http5xx','httpOther','contentType','oversize','noEvidence']);
export const REQUEST = Object.freeze({
  focuschrist_page: 'pioneers',
  focuschrist_profile: 'pioneer-study',
  focuschrist_pioneer_topic: 'willie-july',
  messages: [{ role: 'user', content: 'Explain Willie and Martin handcart companies: late departure in 1856 and its consequences' }]
});
const COUNTERS = Object.freeze({
  fetchCalls: 'focuschrist_official_fetch_calls',
  cacheHits: 'focuschrist_official_cache_hits',
  cacheMisses: 'focuschrist_official_cache_misses',
  transportFailures: 'focuschrist_source_transport_failures'
});
function count(payload, key) {
  if (!Object.hasOwn(payload, key)) return { state: 'missing', value: null };
  const value = payload[key];
  return Number.isInteger(value) && value >= 0 && value <= 1000
    ? { state: 'present', value } : { state: 'invalid', value: null };
}
function boundedString(payload, key) {
  const value = payload[key];
  return typeof value === 'string' && /^[a-zA-Z0-9._-]{1,80}$/.test(value) ? value : null;
}
export function summarize(payload) {
  const classes = Object.fromEntries(FAILURE_CLASSES.map(kind => [kind, count(payload, 'focuschrist_official_failure_' + kind)]));
  const counters = Object.fromEntries(Object.entries(COUNTERS).map(([name,key]) => [name,count(payload,key)]));
  return {
    gatewayMode: boundedString(payload, 'focuschrist_gateway_mode'),
    policy: boundedString(payload, 'focuschrist_source_policy'),
    classes, counters,
    diagnosticFieldsComplete: Object.values(classes).every(x => x.state === 'present'),
    invalidNumericField: [...Object.values(classes), ...Object.values(counters)].some(x => x.state === 'invalid')
  };
}
export async function observe(fetchImpl = fetch, now = () => performance.now()) {
  const started = now();
  try {
    const response = await fetchImpl(ENDPOINT, {
      method: 'POST', headers: { Origin: 'https://focuschrist.com', 'Content-Type': 'application/json' },
      body: JSON.stringify(REQUEST), signal: AbortSignal.timeout(26000)
    });
    const base = { topic: 'willie-july', status: response.status, elapsedMs: Math.round(now()-started) };
    if (!response.ok) return { ...base, observation: 'http-failure', diagnostic: null };
    let payload;
    try { payload = await response.json(); }
    catch { return { ...base, observation: 'invalid-json', diagnostic: null }; }
    if (!payload || typeof payload !== 'object' || Array.isArray(payload))
      return { ...base, observation: 'invalid-payload', diagnostic: null };
    return { ...base, observation: 'response-received', diagnostic: summarize(payload) };
  } catch (error) {
    return { topic: 'willie-july', status: null, elapsedMs: Math.round(now()-started),
      observation: ['AbortError','TimeoutError'].includes(error?.name) ? 'client-timeout' : 'client-network-failure', diagnostic: null };
  }
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const result = await observe();
  console.log(JSON.stringify(result));
  // A captured fallback remains a fallback. Exit status assesses diagnostic capture only.
  if (result.observation !== 'response-received' || !result.diagnostic?.diagnosticFieldsComplete || result.diagnostic.invalidNumericField)
    process.exitCode = 1;
}

