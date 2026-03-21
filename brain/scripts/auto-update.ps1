# Kal's Auto-Update Script
# Runs OpenClaw self-update and reports results
# Designed to run as a cron job (daily at 4am)

$ErrorActionPreference = "Continue"

$LogFile = "C:\Users\carib\.openclaw\brain\cortex\update-log.json"

function Write-UpdateLog {
    param([string]$Message, [string]$Level = "INFO")
    $entry = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Level = $Level
        Message = $Message
    }
    $log = @()
    if (Test-Path $LogFile) {
        try {
            $log = Get-Content $LogFile -Raw | ConvertFrom-Json
            if ($log -isnot [Array]) { $log = @($log) }
        } catch { $log = @() }
    }
    $log += $entry
    $log | Select-Object -Last 50 | ConvertTo-Json | Set-Content $LogFile
}

Write-UpdateLog "Starting OpenClaw auto-update..."

try {
    # Run openclaw update
    $updateOutput = openclaw update 2>&1
    $updateExit = $LASTEXITCODE
    
    Write-UpdateLog "Update command output: $($updateOutput -join '; ')" "DEBUG"
    
    if ($updateExit -ne 0) {
        Write-UpdateLog "Update command failed with exit code $updateExit" "ERROR"
        exit 1
    }
    
    Write-UpdateLog "OpenClaw update completed successfully"

    # Get current version
    $version = openclaw --version 2>&1
    Write-UpdateLog "Current version after update: $version" "INFO"

    # Restart gateway if running
    $gatewayStatus = openclaw gateway status 2>&1 | Select-String "Runtime: running"
    if ($gatewayStatus) {
        Write-UpdateLog "Restarting gateway..."
        openclaw gateway --force --auth none 2>&1
        Write-UpdateLog "Gateway restarted successfully"
    }

    # Update npm packages in mission-control if it exists
    $mcPath = "C:\Users\carib\.openclaw\mission-control"
    if (Test-Path "$mcPath\package.json") {
        Write-UpdateLog "Checking Mission Control for updates..."
        Set-Location $mcPath
        $mcUpdate = npm outdated 2>&1
        if ($LASTEXITCODE -eq 0 -and $mcUpdate -match '\w') {
            npm update 2>&1 | ForEach-Object { Write-UpdateLog "MC Update: $_" "DEBUG" }
            Write-UpdateLog "Mission Control updated"
        }
        Set-Location $BrainDir
    }

    Write-UpdateLog "Auto-update completed successfully" "INFO"
    exit 0

} catch {
    Write-UpdateLog "Auto-update failed: $_" "ERROR"
    exit 1
}
