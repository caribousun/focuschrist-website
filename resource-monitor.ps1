$cpu = Get-CimInstance Win32_Processor | Select-Object -ExpandProperty LoadPercentage
$os = Get-CimInstance Win32_OperatingSystem
$memUsed = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/1MB, 1)
$memTotal = [math]::Round($os.TotalVisibleMemorySize/1MB, 1)
$memPct = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/$os.TotalVisibleMemorySize)*100, 1)

$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$diskUsed = [math]::Round($disk.Size/1GB - $disk.FreeSpace/1GB, 1)
$diskTotal = [math]::Round($disk.Size/1GB, 1)
$diskPct = [math]::Round((($disk.Size - $disk.FreeSpace)/$disk.Size)*100, 1)

Write-Output "CPU: $cpu%"
Write-Output "Memory: $memUsed GB / $memTotal GB ($memPct%)"
Write-Output "Disk C: $diskUsed GB / $diskTotal GB ($diskPct%)"
