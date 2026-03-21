# Resource Monitor Script - Kal's Background Agent
# Monitors local PC resources and optimizes automatically

param(
    [switch]$AlertOnly,
    [switch]$Silent
)

$ErrorActionPreference = 'SilentlyContinue'
$log = @()

function Write-Log($msg, $level = 'INFO') {
    $ts = Get-Date -Format 'HH:mm:ss'
    $entry = "[$ts] [$level] $msg"
    if (-not $Silent) { Write-Host $entry }
    $script:log += $entry
}

# === RAM CHECK ===
$os = Get-CimInstance Win32_OperatingSystem
$totalRAM = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeRAM = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedRAM = [math]::Round($totalRAM - $freeRAM, 2)
$usedPct = [math]::Round(($usedRAM / $totalRAM) * 100, 1)

Write-Log "RAM: $usedRAM GB / $totalRAM GB ($usedPct% used)"

# === STALE NODE PROCESS CLEANUP ===
$staleNodes = Get-Process | Where-Object {
    $_.ProcessName -eq 'node' -and
    $_.WorkingSet64 -lt 200MB -and
    $_.StartTime -lt (Get-Date).AddMinutes(-10)
} | Select-Object Id, @{N='MB';E={[math]::Round($_.WorkingSet64 / 1MB, 0)}}, StartTime, @{N='AgeMin';E={[math]::Round(((Get-Date) - $_.StartTime).TotalMinutes, 0)}}

if ($staleNodes) {
    $staleCount = $staleNodes.Count
    $staleMB = ($staleNodes | Measure-Object MB -Sum).Sum
    Write-Log "Found $staleCount stale node processes ($staleMB MB) - cleaning..." 'WARN'
    
    # Only clean npx/npm cache processes (small ones)
    $toClean = Get-Process | Where-Object {
        $_.ProcessName -eq 'node' -and
        $_.WorkingSet64 -lt 150MB -and
        ((Get-Date) - $_.StartTime).TotalMinutes -gt 5
    }
    
    $cleaned = 0
    foreach ($p in $toClean) {
        $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
        if ($cmd -match 'npm|npx|_npx|cache') {
            Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
            $cleaned++
        }
    }
    if ($cleaned -gt 0) {
        Write-Log "Cleaned $cleaned stale npm/npx processes" 'INFO'
    }
}

# === HIGH MEMORY ALERT ===
if ($usedPct -gt 85) {
    Write-Log "HIGH MEMORY WARNING: $usedPct% used" 'CRIT'
    
    # Aggressive cleanup: all node processes under 100MB
    Get-Process | Where-Object {
        $_.ProcessName -eq 'node' -and $_.WorkingSet64 -lt 100MB
    } | ForEach-Object {
        $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
        if ($cmd -match 'npm|npx|cache') {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
} elseif ($usedPct -gt 80) {
    Write-Log "Memory elevated: $usedPct% used" 'WARN'
}

# === DISK SPACE CHECK ===
$disks = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
foreach ($disk in $disks) {
    $freeGB = [math]::Round($disk.FreeSpace / 1GB, 1)
    $totalGB = [math]::Round(($disk.Size) / 1GB, 1)
    $pct = [math]::Round(($disk.FreeSpace / $disk.Size) * 100, 1)
    if ($pct -lt 10) {
        Write-Log "DISK LOW: $($disk.DeviceID) $freeGB GB free ($pct%)" 'CRIT'
    }
}

# === MISSION CONTROL HEALTH ===
$mcRunning = Get-Process | Where-Object { $_.ProcessName -eq 'node' -and $_.WorkingSet64 -gt 300MB } | Measure-Object
if ($mcRunning.Count -eq 0) {
    Write-Log "Mission Control may not be running" 'WARN'
}

# === SUMMARY ===
$ramStatus = if ($usedPct -gt 85) { 'CRIT' } elseif ($usedPct -gt 80) { 'WARN' } else { 'OK' }
$result = @{
    Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
    RAM_Used_GB = $usedRAM
    RAM_Total_GB = $totalRAM
    RAM_Pct = $usedPct
    RAM_Status = $ramStatus
    Log = $log
}

if ($AlertOnly) {
    if ($ramStatus -ne 'OK') {
        return $result | ConvertTo-Json -Compress
    }
} else {
    return $result | ConvertTo-Json -Compress
}
