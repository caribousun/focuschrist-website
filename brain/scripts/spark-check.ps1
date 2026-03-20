# spark-check.ps1
# Wyatt's Spark Earnings Pace Checker
# Run daily to check if on pace for $800/week goal

$LogPath = "$PSScriptRoot\..\knowledge\tools\spark-earnings-log.md"

# Goal constants
$WEEKLY_GOAL = 800
$MONTHLY_GOAL = 3200  # $800 x 4 weeks

function Get-Last7DaysEarnings {
    param([string]$LogPath)
    
    if (-not (Test-Path $LogPath)) {
        return $null
    }
    
    $content = Get-Content $LogPath -Raw
    
    # Parse the log - get entries from last 7 days
    $lines = $content -split "`n" | Where-Object { $_ -match '^\|\s*\d{4}-\d{2}-\d{2}' }
    
    $sevenDaysAgo = (Get-Date).AddDays(-7)
    $total = 0
    $daysWorked = 0
    $dayDetails = @()
    
    foreach ($line in $lines) {
        if ($line -match '^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*\$?([\d.]+)\s*\|') {
            $dateStr = $Matches[1]
            $amount = [double]$Matches[2]
            
            try {
                $date = [DateTime]::ParseExact($dateStr, "yyyy-MM-dd", $null)
                if ($date -ge $sevenDaysAgo -and $date -le (Get-Date)) {
                    $total += $amount
                    $daysWorked++
                    $dayDetails += [PSCustomObject]@{
                        Date = $dateStr
                        Amount = $amount
                    }
                }
            } catch { }
        }
    }
    
    return [PSCustomObject]@{
        Total = $total
        DaysWorked = $daysWorked
        DailyAvg = if ($daysWorked -gt 0) { $total / $daysWorked } else { 0 }
        Details = $dayDetails
    }
}

function Get-CurrentWeekEarnings {
    param([string]$LogPath)
    
    if (-not (Test-Path $LogPath)) {
        return $null
    }
    
    $content = Get-Content $LogPath -Raw
    $lines = $content -split "`n" | Where-Object { $_ -match '^\|\s*\d{4}-\d{2}-\d{2}' }
    
    # Get start of current week (Sunday)
    $today = Get-Date
    $dayOfWeek = [int]$today.DayOfWeek
    $weekStart = $today.AddDays(-$dayOfWeek).Date
    
    $total = 0
    $daysWorked = 0
    
    foreach ($line in $lines) {
        if ($line -match '^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*\$?([\d.]+)\s*\|') {
            $dateStr = $Matches[1]
            $amount = [double]$Matches[2]
            
            try {
                $date = [DateTime]::ParseExact($dateStr, "yyyy-MM-dd", $null)
                if ($date -ge $weekStart -and $date -le $today) {
                    $total += $amount
                    if ($amount -gt 0) { $daysWorked++ }
                }
            } catch { }
        }
    }
    
    $daysElapsed = [int]($today - $weekStart).TotalDays + 1
    $daysInWeek = 7
    $expectedAtPace = ($WEEKLY_GOAL / $daysInWeek) * $daysElapsed
    $projectedWeek = if ($daysElapsed -gt 0) { ($total / $daysElapsed) * 7 } else { 0 }
    
    return [PSCustomObject]@{
        Total = $total
        DaysWorked = $daysWorked
        DaysElapsed = $daysElapsed
        ExpectedAtPace = $expectedAtPace
        ProjectedWeek = $projectedWeek
        WeekStart = $weekStart
        OnPace = $total -ge $expectedAtPace
    }
}

function Get-MonthlyTotals {
    param([string]$LogPath)
    
    if (-not (Test-Path $LogPath)) {
        return $null
    }
    
    $content = Get-Content $LogPath -Raw
    $lines = $content -split "`n" | Where-Object { $_ -match '^\|\s*\d{4}-\d{2}-\d{2}' }
    
    $today = Get-Date
    $monthStart = [DateTime]::new($today.Year, $today.Month, 1)
    $daysInMonth = [DateTime]::DaysInMonth($today.Year, $today.Month)
    $daysElapsed = $today.Day
    $daysRemaining = $daysInMonth - $daysElapsed
    
    $total = 0
    $daysWorked = 0
    
    foreach ($line in $lines) {
        if ($line -match '^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*\$?([\d.]+)\s*\|') {
            $dateStr = $Matches[1]
            $amount = [double]$Matches[2]
            
            try {
                $date = [DateTime]::ParseExact($dateStr, "yyyy-MM-dd", $null)
                if ($date.Month -eq $today.Month -and $date.Year -eq $today.Year) {
                    $total += $amount
                    if ($amount -gt 0) { $daysWorked++ }
                }
            } catch { }
        }
    }
    
    $expectedAtPace = ($MONTHLY_GOAL / $daysInMonth) * $daysElapsed
    $projectedMonth = if ($daysElapsed -gt 0) { ($total / $daysElapsed) * $daysInMonth } else { 0 }
    $remainingNeeded = $MONTHLY_GOAL - $total
    $dailyNeededForGoal = if ($daysRemaining -gt 0) { $remainingNeeded / $daysRemaining } else { 0 }
    
    return [PSCustomObject]@{
        Total = $total
        DaysWorked = $daysWorked
        DaysElapsed = $daysElapsed
        DaysInMonth = $daysInMonth
        DaysRemaining = $daysRemaining
        ExpectedAtPace = $expectedAtPace
        ProjectedMonth = $projectedMonth
        RemainingNeeded = $remainingNeeded
        DailyNeededForGoal = $dailyNeededForGoal
        OnPace = $total -ge $expectedAtPace
        MonthName = $today.ToString("MMMM yyyy")
    }
}

# Main execution
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   SPARK EARNINGS CHECK" -ForegroundColor Cyan
Write-Host "   $(Get-Date -Format 'dddd, MMMM d, yyyy')" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Current Week
$week = Get-CurrentWeekEarnings -LogPath $LogPath
if ($week) {
    Write-Host "📅 CURRENT WEEK (since Sunday)" -ForegroundColor Yellow
    Write-Host "   Earned:       `$$($week.Total.ToString('N2'))"
    Write-Host "   Days worked:  $($week.DaysWorked) of $($week.DaysElapsed)"
    Write-Host "   Expected at pace: `$$($week.ExpectedAtPace.ToString('N2'))"
    Write-Host "   Projected week total: `$$($week.ProjectedWeek.ToString('N2'))"
    Write-Host ""
    
    if ($week.OnPace) {
        Write-Host "   ✅ STATUS: ON PACE FOR $800 THIS WEEK" -ForegroundColor Green
    } else {
        $shortfall = $week.ExpectedAtPace - $week.Total
        Write-Host "   ⚠️  STATUS: `$$($shortfall.ToString('N2')) BEHIND PACE" -ForegroundColor Red
        Write-Host "   Need `$$($week.DailyNeededForGoal.ToString('N2'))/day to catch up" -ForegroundColor Red
    }
}
Write-Host ""

# Monthly
$month = Get-MonthlyTotals -LogPath $LogPath
if ($month) {
    Write-Host "📆 $($month.MonthName.ToUpper())" -ForegroundColor Yellow
    Write-Host "   Earned so far:  `$$($month.Total.ToString('N2'))"
    Write-Host "   Days worked:    $($month.DaysWorked) of $($month.DaysElapsed)"
    Write-Host "   Expected at pace: `$$($month.ExpectedAtPace.ToString('N2'))"
    Write-Host "   Projected month: `$$($month.ProjectedMonth.ToString('N2'))"
    Write-Host "   Days remaining: $($month.DaysRemaining)"
    Write-Host ""
    
    if ($month.OnPace) {
        Write-Host "   ✅ MONTHLY STATUS: ON PACE" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  MONTHLY STATUS: BEHIND PACE" -ForegroundColor Red
        Write-Host "   Need `$$($month.DailyNeededForGoal.ToString('N2'))/day to reach $3,200" -ForegroundColor Red
    }
}
Write-Host ""

# Last 7 days
$last7 = Get-Last7DaysEarnings -LogPath $LogPath
if ($last7) {
    Write-Host "📊 LAST 7 DAYS" -ForegroundColor Yellow
    Write-Host "   Total: `$$($last7.Total.ToString('N2'))"
    Write-Host "   Days worked: $($last7.DaysWorked)"
    Write-Host "   Daily avg: `$$($last7.DailyAvg.ToString('N2'))"
    Write-Host ""
}

# Summary
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
if ($week.OnPace -and $month.OnPace) {
    Write-Host "🎉 YOU'RE ON TRACK! Keep it up!" -ForegroundColor Green
} elseif (-not $week.OnPace) {
    $weekMsg = if ($week) { "`$$($week.ExpectedAtPace.ToString('N0')) needed" } else { "check logs" }
    Write-Host "⚠️  ALERT: Behind pace this week" -ForegroundColor Red
    Write-Host "   Need $weekMsg by Sunday" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  ALERT: Behind pace this month" -ForegroundColor Red
}
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
