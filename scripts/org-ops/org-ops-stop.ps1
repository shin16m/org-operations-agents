# Stop org-ops watch runner and dashboard (best-effort).
param(
    [int]$DashboardPort = 8765
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_common.ps1")

$stopped = 0

Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -and (
            $_.CommandLine -match "asana_ops_runner\.py" -or
            $_.CommandLine -match "asana_ops_poller\.py" -or
            $_.CommandLine -match "asana_ops_dashboard\.py"
        )
    } |
    ForEach-Object {
        Write-Host "STOP  pid=$($_.ProcessId)  $($_.Name)" -ForegroundColor Yellow
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        $stopped++
    }

$dashConn = Get-NetTCPConnection -LocalPort $DashboardPort -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $dashConn) {
    if ($conn.OwningProcess) {
        Write-Host "STOP  dashboard pid=$($conn.OwningProcess)  port=$DashboardPort" -ForegroundColor Yellow
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        $stopped++
    }
}

if ($stopped -eq 0) {
    Write-Host "OK  no org-ops runner/dashboard process found" -ForegroundColor Green
}
else {
    Write-Host "DONE  stopped $stopped process(es)" -ForegroundColor Green
}
