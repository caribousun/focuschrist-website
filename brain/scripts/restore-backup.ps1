# Restore from Kal Backup
param([string]$Timestamp, [switch]$ListOnly)
$BR = "C:\Users\carib\.openclaw\backup-staging"
if($ListOnly){
    Get-ChildItem $BR -Directory | Where-Object{$_.Name -match"^kal-backup-"}|Sort-Object Name -Descending|FT Name,LastWriteTime -AutoSize
    exit
}
if(!$Timestamp){
    $b=Get-ChildItem $BR -Directory|Where-Object{$_.Name -match"^kal-backup-"}|Sort-Object Name -Descending|Select-Object -First 1
    if(!$b){Write-Host "No backups found";exit 1}
    $Timestamp=$b.Name -replace"kal-backup-",""
}
$BD="$BR\kal-backup-$Timestamp"
if(!(Test-Path $BD)){Write-Host "Backup not found: $BD";exit 1}
Write-Host "Restoring from: $Timestamp"
# OpenClaw config
if(Test-Path "$BD\openclaw\openclaw.json"){Copy-Item "$BD\openclaw\openclaw.json" "C:\Users\carib\.openclaw\openclaw.json" -Force;Write-Host "[OK] openclaw.json"}
# Cron jobs
if(Test-Path "$BD\cron\jobs.json"){Copy-Item "$BD\cron\jobs.json" "C:\Users\carib\.openclaw\cron\jobs.json" -Force;Write-Host "[OK] cron jobs"}
# Scripts
if(Test-Path "$BD\scripts"){Copy-Item "$BD\scripts\*" "C:\Users\carib\.openclaw\brain\scripts\" -Force;Write-Host "[OK] scripts"}
# Workspace
if(Test-Path "$BD\workspace"){Get-ChildItem "$BD\workspace" -File|Where-Object{$_.Extension -eq".md"}|ForEach-Object{Copy-Item $_.FullName "C:\Users\carib\.openclaw\workspace\$($_.Name)" -Force};Write-Host "[OK] workspace"}
# Brain
if(Test-Path "$BD\brain\brain"){Copy-Item "$BD\brain\brain\*" "C:\Users\carib\.openclaw\brain\" -Recurse -Force;Write-Host "[OK] brain"}
# Skills
if(Test-Path "$BD\skills"){
    $sk="C:\Users\carib\AppData\Roaming\npm\node_modules\openclaw\skills"
    Get-ChildItem "$BD\skills" -Directory|ForEach-Object{
        $d="$sk\$($_.Name)"
        New-Item -ItemType Directory -Path $d -Force|Out-Null
        if(Test-Path "$($_.FullName)\SKILL.md"){Copy-Item "$($_.FullName)\SKILL.md" "$d\SKILL.md" -Force}
    }
    Write-Host "[OK] skills"
}
Write-Host "Restore complete. Restart gateway: openclaw gateway --force --auth none"
