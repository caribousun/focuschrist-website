// Fixed aggregate classes only: never retain a URL, visitor text, header or error message.
const CLASSES = Object.freeze(['budget', 'timeout', 'network', 'http429', 'http5xx', 'httpOther', 'contentType', 'oversize', 'noEvidence']);
function recordOfficialFailure(counters, kind) {
  if (!counters || !CLASSES.includes(kind)) return;
  if (!counters.officialFailureClasses) counters.officialFailureClasses = Object.create(null);
  const prior = counters.officialFailureClasses[kind];
  counters.officialFailureClasses[kind] = Math.min(1000, (Number.isInteger(prior) && prior >= 0 ? prior : 0) + 1);
}
function mergeOfficialFailureDiagnostics(target, counters) {
  if (!target) return;
  for (const kind of CLASSES) {
    const key = `focuschrist_official_failure_${kind}`;
    const prior = target[key];
    const count = counters?.officialFailureClasses?.[kind];
    target[key] = Math.min(1000, (Number.isInteger(prior) && prior >= 0 ? prior : 0)
      + (Number.isInteger(count) && count >= 0 ? count : 0));
  }
}
export { CLASSES, recordOfficialFailure, mergeOfficialFailureDiagnostics };
