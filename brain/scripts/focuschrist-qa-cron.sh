#!/usr/bin/env bash
# focusChrist Q&A Cron Script (Bash/WSL/macOS/Linux)
# Runs every 15 minutes via crontab
#
# Install crontab entry:
#   crontab -e
#   */15 * * * * /path/to/focuschrist-qa-cron.sh >> ~/focuschrist-qa-cron.log 2>&1
#
# Or on Windows via Git Bash / WSL:
#   powershell.exe -ExecutionPolicy Bypass -File "C:/Users/carib/.openclaw/brain/scripts/focuschrist-qa-cron.ps1"

set -euo pipefail

# ─── Config ────────────────────────────────────────────────────────────────────
BRAIN_DIR="${BRAIN_DIR:-$HOME/.openclaw/brain}"
SCRIPTS_DIR="$BRAIN_DIR/scripts"
PENDING_FILE="$BRAIN_DIR/knowledge/projects/focuschrist-pending-questions.md"
PIPELINE_FILE="$BRAIN_DIR/knowledge/projects/focuschrist-qa-pipeline.md"
LOG_FILE="${LOG_FILE:-$SCRIPTS_DIR/focuschrist-qa-cron.log}"
STATE_FILE="$SCRIPTS_DIR/focuschrist-qa-cron-state.json"
SUMMARY_FILE="$SCRIPTS_DIR/focuschrist-qa-cron-lastrun.txt"
ASK_HTML_LOCAL="$BRAIN_DIR/knowledge/projects/focuschrist-ask.html"

GITHUB_TOKEN="${GITHUB_TOKEN:-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}"
REPO_OWNER="caribousun"
REPO_NAME="focuschrist-website"

# ─── Logging ────────────────────────────────────────────────────────────────────
log() {
    local level="${1:-INFO}"
    local msg="${2:-}"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $msg" | tee -a "$LOG_FILE" 2>/dev/null || true
}

# ─── State ─────────────────────────────────────────────────────────────────────
read_state() {
    if [[ -f "$STATE_FILE" ]] && command -v python3 &>/dev/null; then
        python3 -c "import json; print(json.load(open('$STATE_FILE')).get('lastRun',''))" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

write_state() {
    local last_run="$1"
    local run_count="${2:-1}"
    mkdir -p "$(dirname "$STATE_FILE")"
    cat > "$STATE_FILE" <<EOF
{
  "lastRun": "$last_run",
  "runCount": $run_count
}
EOF
}

# ─── Rate Limit ────────────────────────────────────────────────────────────────
can_run() {
    local last_run
    last_run=$(read_state)
    if [[ -z "$last_run" ]]; then return 0; fi

    local last_epoch
    last_epoch=$(date -d "$last_run" +%s 2>/dev/null) || last_epoch=0
    local now_epoch
    now_epoch=$(date +%s)
    local diff=$((now_epoch - last_epoch))
    local min_interval=${MIN_INTERVAL:-900}  # 15 minutes in seconds

    if (( diff >= min_interval )); then
        return 0
    else
        log "WARN" "Rate limited: last run was ${diff}s ago (min=${min_interval}s)"
        return 1
    fi
}

# ─── Get Pending Questions ─────────────────────────────────────────────────────
get_pending_questions() {
    if [[ ! -f "$PENDING_FILE" ]]; then
        log "WARN" "Pending file not found: $PENDING_FILE"
        return 0
    fi

    # Extract pending questions from markdown
    grep -A 10 "Status.*pending" "$PENDING_FILE" 2>/dev/null | \
        grep -E "^\- \*\*Question:" | \
        sed 's/^- \*\*Question:\*\* //' | \
        sed 's/[""]//g' | \
        while IFS= read -r q; do
            echo "$q"
        done
}

# ─── Count Pending Questions ───────────────────────────────────────────────────
count_pending() {
    local count=0
    while IFS= read -r _; do ((count++)); done < <(get_pending_questions)
    echo $count
}

# ─── Write Summary for Main Agent ──────────────────────────────────────────────
write_summary() {
    local pending_list=("$@")
    mkdir -p "$SCRIPTS_DIR"
    cat > "$SUMMARY_FILE" <<EOF
=== focusChrist QA Cron Summary ===
Run at: $(date '+%Y-%m-%d %H:%M:%S')
Pending questions found: ${#pending_list[@]}

Questions needing answers:
EOF
    for q in "${pending_list[@]}"; do
        echo "  - $q" | tee -a "$SUMMARY_FILE" 2>/dev/null || true
    done
    cat >> "$SUMMARY_FILE" <<EOF

ACTION NEEDED: Run the Q&A pipeline for each question above.
See: brain/knowledge/projects/focuschrist-qa-pipeline.md

To acknowledge and queue for next session, start a chat with the main agent.
EOF
    log "INFO" "Summary written to $SUMMARY_FILE"
}

# ─── Mark Question In Progress ─────────────────────────────────────────────────
mark_in_progress() {
    local question="$1"
    if [[ ! -f "$PENDING_FILE" ]]; then return 1; fi

    # Use perl for safe in-place editing (cross-platform)
    if command -v perl &>/dev/null; then
        perl -i -pe 's/(Status:\s*)pending/$1in-progress/ if !$done++' "$PENDING_FILE"
    else
        sed -i 's/Status: pending/Status: in-progress/' "$PENDING_FILE"
    fi
    log "INFO" "Marked in-progress: $question"
}

# ─── Mark Question Answered ────────────────────────────────────────────────────
mark_answered() {
    local question="$1"
    if [[ ! -f "$PENDING_FILE" ]]; then return 1; fi
    sed -i 's/Status: in-progress/Status: answered/' "$PENDING_FILE"
    log "INFO" "Marked answered: $question"
}

# ─── GitHub Commit ──────────────────────────────────────────────────────────────
github_commit() {
    local local_path="$1"
    local repo_path="$2"
    local commit_msg="$3"
    local branch="${4:-main}"

    if [[ ! -f "$local_path" ]]; then
        log "ERROR" "File not found for commit: $local_path"
        return 1
    fi

    # Get current SHA if file exists
    local sha=""
    local get_resp
    get_resp=$(curl -s -w "%{http_code}" -o /tmp/github_get.json \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/contents/$repo_path")

    if [[ "$get_resp" == "200" ]] && command -v python3 &>/dev/null; then
        sha=$(python3 -c "import json; print(json.load(open('/tmp/github_get.json')).get('sha',''))" 2>/dev/null) || true
    fi

    # Base64 encode
    local encoded
    encoded=$(base64 -w 0 "$local_path" 2>/dev/null) || encoded=$(base64 "$local_path" | tr -d '\n')

    # Build JSON body
    local json_body
    json_body=$(python3 -c "
import json, base64, sys
content = open('$local_path', 'rb').read()
b64 = base64.b64encode(content).decode()
body = {'message': '$commit_msg', 'content': b64, 'branch': '$branch'}
if '$sha': body['sha'] = '$sha'
print(json.dumps(body))
" 2>/dev/null) || {
        log "ERROR" "Failed to build JSON for GitHub API"
        return 1
    }

    # Send to GitHub
    local resp
    resp=$(curl -s -X PUT \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$json_body" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/contents/$repo_path")

    if echo "$resp" | grep -q '"commit"'; then
        log "INFO" "Committed to GitHub: $repo_path"
        return 0
    else
        log "ERROR" "GitHub commit failed: $resp"
        return 1
    fi
}

# ─── Main ───────────────────────────────────────────────────────────────────────
main() {
    log "INFO" "=== focusChrist QA Cron started ==="

    # Rate limit
    if ! can_run; then
        log "INFO" "Exiting: rate limited"
        exit 0
    fi

    # Update state
    local now
    now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local prev_count
    prev_count=$(read_state | grep -c . 2>/dev/null || echo 0)
    write_state "$now" $((prev_count + 1))

    # Check for pending questions
    mapfile -t pending_array < <(get_pending_questions)
    local count=${#pending_array[@]}

    if (( count == 0 )); then
        log "INFO" "No pending questions found. Exiting."
        exit 0
    fi

    log "INFO" "Found $count pending question(s):"
    for q in "${pending_array[@]}"; do
        log "INFO" "  - $q"
    done

    # Mark all as in-progress
    for q in "${pending_array[@]}"; do
        mark_in_progress "$q"
    done

    # Write summary for main agent
    write_summary "${pending_array[@]}"

    log "INFO" "=== Cron run complete ==="
    exit 0
}

main "$@"
