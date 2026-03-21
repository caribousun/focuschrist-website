# Kal Full System Backup Script
param([switch]$DryRun)
$ErrorActionPreference = "Continue"
$BackupRoot = "C:\Users\carib\.openclaw\backup-staging"
$TS = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BD = "$BackupRoot\kal-backup-$TS"
$Token = $env:GH_TOKEN

$Secrets = @("ghp_","gho_","github_pat_","AIza","sk-","sk-ant-","xAI-","Bearer","8705501920:","4035c7349be05fd01d02802cbc3e9623ed772c92c8020283")

function HasSecret($c,$f){ foreach($s in $Secrets){if($c-imatch$s){Write-Host "[SECRET] Skipped: $f";return$true}};return$false}

# Backup a folder
function Backup-Folder($src,$name,$destRoot){
    if(!(Test-Path $src)){Write-Host "[SKIP] $name - not found";return}
    $dest = "$destRoot\$name"
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    Get-ChildItem $src -Recurse -File | ForEach-Object{
        $rp = $_.FullName.Substring($src.Length).TrimStart("\")
        $content = Get-Content $_.FullName -Raw
        if($content -and (HasSecret $content $rp)){return}
        $dp = Join-Path $dest $rp
        $dg = Split-Path $dp -Parent
        if(!(Test-Path $dg)){New-Item -ItemType Directory -Path $dg -Force | Out-Null}
        Copy-Item $_.FullName -Destination $dp -Force
    }
    Write-Host "[OK] $name"
}

Write-Host "=== Kal Full Backup: $TS ==="

# Create dirs
@("$BD\openclaw","$BD\cron","$BD\workspace","$BD\brain","$BD\scripts","$BD\skills") | ForEach-Object{New-Item -ItemType Directory -Path $_ -Force | Out-Null}

# Config
$cfg = "C:\Users\carib\.openclaw\openclaw.json"
if(Test-Path $cfg){
    $c = Get-Content $cfg -Raw
    if(!$c){$c=""}
    if(!(HasSecret $c "openclaw.json")){Copy-Item $cfg "$BD\openclaw\openclaw.json" -Force;Write-Host "[OK] openclaw.json"}
}

# Cron
$cj = "C:\Users\carib\.openclaw\cron\jobs.json"
if(Test-Path $cj){Copy-Item $cj "$BD\cron\jobs.json" -Force;Write-Host "[OK] cron jobs"}

# Scripts
$scr = "C:\Users\carib\.openclaw\brain\scripts"
Get-ChildItem $scr -Filter "*.ps1" | ForEach-Object{
    $c = Get-Content $_.FullName -Raw
    if(!$c){$c=""}
    if(!(HasSecret $c $_.Name)){Copy-Item $_.FullName "$BD\scripts\$($_.Name)" -Force}
}
Write-Host "[OK] scripts"

# Workspace core files
$ws = "C:\Users\carib\.openclaw\workspace"
@("SOUL.md","USER.md","MEMORY.md","HEARTBEAT.md","TOOLS.md","IDENTITY.md","BRAIN-LOCATION.md") | ForEach-Object{
    $f = Join-Path $ws $_
    if(Test-Path $f){
        $c = Get-Content $f -Raw
        if(!$c){$c=""}
        if(!(HasSecret $c $_)){Copy-Item $f "$BD\workspace\$_" -Force}
    }
}
# Memory folder
$m = Join-Path $ws "memory"
if(Test-Path $m){
    New-Item -ItemType Directory -Path "$BD\workspace\memory" -Force | Out-Null
    Get-ChildItem $m -Filter "*.md" | ForEach-Object{Copy-Item $_.FullName "$BD\workspace\memory\$($_.Name)" -Force}
}
Write-Host "[OK] workspace"

# Brain
Backup-Folder "C:\Users\carib\.openclaw\brain" "brain" $BD

# Skills
$skDir = "C:\Users\carib\AppData\Roaming\npm\node_modules\openclaw\skills"
if(Test-Path $skDir){
    Get-ChildItem $skDir -Directory | ForEach-Object{
        $skf = Join-Path $_.FullName "SKILL.md"
        if(Test-Path $skf){
            $skDest = "$BD\skills\$($_.Name)"
            New-Item -ItemType Directory -Path $skDest -Force | Out-Null
            Copy-Item $skf "$skDest\SKILL.md" -Force
        }
    }
    Write-Host "[OK] skills"
}

# Manifest
@{
    Timestamp=$TS
    BackupDate=Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Version="1.0"
} | ConvertTo-Json | Set-Content "$BD\manifest.json" -Encoding UTF8

# Latest marker
@{
    LastBackup=$TS
    LastBackupDate=Get-Date -Format "yyyy-MM-dd HH:mm:ss"
} | ConvertTo-Json | Set-Content "$BackupRoot\LATEST-BACKUP.json" -Encoding UTF8

Write-Host ""
Write-Host "=== Backup Complete: $BD ==="
$sz = [math]::Round((Get-ChildItem $BD -Recurse | Measure-Object -Property Length -Sum).Sum/1MB,2)
Write-Host "Size: $sz MB"
