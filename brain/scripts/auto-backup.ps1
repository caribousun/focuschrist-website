# Kal's Brain Auto-Backup Script
# Runs daily to commit and push brain changes to GitHub
# Non-destructive: only adds, never deletes
# Includes secret scanning before commit

$ErrorActionPreference = "Stop"

$BrainDir = "C:/Users/carib/.openclaw/brain"
$RepoUrl = "https://github.com/caribousun/kal-brain-backup.git"
$Token = $env:GH_TOKEN

# Secret patterns to scan for
$SecretPatterns = @(
    'ghp_[a-zA-Z0-9]{36}',           # GitHub Personal Access Token
    'gho_[a-zA-Z0-9]{36}',           # GitHub OAuth
    'github_pat_[a-zA-Z0-9]{22,}',  # GitHub Fine-grained PAT
    'AIza[a-zA-Z0-9_-]{35}',         # Google API Key
    'sk-[a-zA-Z0-9]{48}',            # OpenAI API Key
    'sk-ant-[a-zA-Z0-9_-]{50,}',     # Anthropic API Key
    'xAI-[a-zA-Z0-9]{20,}',          # xAI API Key
    'AKIA[a-zA-Z0-9]{16}',           # AWS Access Key
    'sq0[a-z]{3}-[a-zA-Z0-9_-]{22}', # Square API
    'mid-[a-zA-Z0-9_-]{20,}',        # Midjourney
    'nv-[a-zA-Z0-9_-]{20,}',         # NVIDIA
    'Bearer [a-zA-Z0-9_-]{10,}',     # Generic Bearer token
    'token=[a-zA-Z0-9_-]{10,}',      # Generic token param
    'password\s*=\s*["\''][^"\']{4,}', # Password in config
    'api[_-]?key\s*=\s*["\''][^"\']{8,}', # Generic API key
    'BEGIN.*PRIVATE KEY',             # Private key blocks
    '-----BEGIN OPENAI',             # OpenAI key block
    'slack_token',                    # Slack tokens
    'telegram_token',                # Telegram tokens
    'discord.*token',                # Discord tokens
    '8705501920:[a-zA-Z0-9_-]{35}', # Telegram bot token (our specific one)
    '4035c7349be05fd01d02802cbc3e9623ed772c92c8020283' # Our gateway token
)

function Test-ContainsSecret {
    param([string]$Content, [string]$FilePath)
    
    $found = @()
    foreach ($pattern in $SecretPatterns) {
        if ($Content -imatch $pattern) {
            $found += $pattern
        }
    }
    
    if ($found.Count -gt 0) {
        Write-Warning "[SECRET DETECTED] Skipping $FilePath - contains: $($found -join ', ')"
        return $true
    }
    return $false
}

try {
    Set-Location $BrainDir

    # Check if this is a git repo
    if (-not (Test-Path ".git")) {
        Write-Error "[auto-backup] Not a git repository: $BrainDir"
        exit 1
    }

    # Check for changes
    $status = git status --porcelain
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[auto-backup] git status failed"
        exit 1
    }

    if (-not $status) {
        Write-Host "[auto-backup] No changes to commit. Exiting."
        exit 0
    }

    Write-Host "[auto-backup] Changes detected. Scanning for secrets..."

    # Get list of changed files
    $changedFiles = $status | ForEach-Object { $_.Trim().Substring(3) } | Where-Object { $_ -notmatch '^temp/' }

    # Scan each file for secrets
    $skipFiles = @()
    foreach ($file in $changedFiles) {
        if (Test-Path $file -PathType Leaf) {
            $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
            if ($content -and (Test-ContainsSecret -Content $content -FilePath $file)) {
                $skipFiles += $file
            }
        }
    }

    # Stage only safe files
    Write-Host "[auto-backup] Staging safe files..."
    git reset HEAD > $null 2>&1
    
    # Stage files individually, skipping secret files
    foreach ($file in $changedFiles) {
        if ($file -notin $skipFiles) {
            git add $file
        }
    }

    # Check if anything left to commit
    $remaining = git status --porcelain
    if (-not $remaining) {
        Write-Warning "[auto-backup] All changed files contained secrets. Nothing to commit."
        exit 0
    }

    # Configure git (needed for fresh clones)
    git config user.email "kal@openclaw"
    git config user.name "Kal Backup"

    # Set remote with token
    git remote set-url origin "https://x-access-token:${Token}@github.com/caribousun/kal-brain-backup.git"

    # Commit with timestamp
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $skipNote = ""
    if ($skipFiles.Count -gt 0) {
        $skipNote = " [SKIPPED: $($skipFiles.Count) files with secrets]"
    }
    git commit -m "Auto-backup $timestamp$skipNote"

    # Push to GitHub
    Write-Host "[auto-backup] Pushing to GitHub..."
    git push --force origin HEAD

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[auto-backup] Successfully pushed backup to GitHub."
        exit 0
    } else {
        Write-Error "[auto-backup] git push failed with exit code $LASTEXITCODE"
        exit 1
    }

} catch {
    Write-Error "[auto-backup] Unexpected error: $_"
    exit 1
}
