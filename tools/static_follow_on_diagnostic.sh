#!/usr/bin/env bash
# Diagnostic only. Existing release gates remain unchanged and authoritative.
set -u
set -o pipefail
out=.qa-artifacts/static-follow-on
mkdir -p "$out"
actual=$(git rev-parse HEAD) || exit 1
{
  printf 'scope=diagnostic only; not release acceptance\n'
  printf 'expected_checkout=%s\nactual_checkout=%s\n' "${EXPECTED_CHECKOUT_SHA:-UNSET}" "$actual"
  git log -1 --format='parents=%P'
  sha256sum tools/qa-requirements.txt "$0"
} > "$out/evidence.txt"
if [[ -z "${EXPECTED_CHECKOUT_SHA:-}" || "$actual" != "$EXPECTED_CHECKOUT_SHA" ]]; then
  echo 'Checkout differs from the pull-request event merge SHA; no checks run.' | tee -a "$out/evidence.txt"
  exit 1
fi
checks=(
  desktop_hero_preservation_qa
  discovery_qa
  connected_study_qa
  artwork_reference_repairs_qa
  resource_thumbnail_qa
  complete_card_rows_qa
  study_layout_uniformity_qa
  study_section_balance_qa
)
failed=0
for check in "${checks[@]}"; do
  printf '%s\n' "Running $check (60-second limit)"
  sha256sum "tools/$check.py" >> "$out/evidence.txt"
  timeout --signal=TERM --kill-after=5s 60s python "tools/$check.py" > "$out/$check.log" 2>&1
  status=$?
  if (( status == 0 )); then state=PASS; elif (( status == 124 )); then state=TIMEOUT; elif (( status == 137 )); then state=KILLED_OR_TIMEOUT; else state=FAIL; fi
  printf '%s\t%s\texit=%s\n' "$check" "$state" "$status" | tee -a "$out/results.tsv"
  cat "$out/$check.log"
  (( status == 0 )) || failed=1
done
printf 'Nonzero exit, if any, is diagnostic; all existing release gates still must pass.\n' | tee -a "$out/evidence.txt"
exit "$failed"
