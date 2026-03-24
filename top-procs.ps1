$procs = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10
foreach ($p in $procs) {
    $mb = [math]::Round($p.WorkingSet64/1MB, 0)
    Write-Output "$($p.Name): $mb MB"
}
